from flask import Flask, request, jsonify
import stripe
import requests
import logging
from config import STRIPE_WEBHOOK_SECRET, DEVICE_MAP

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return f"Webhook error: {e}", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get("id")
        logging.info(f"Fetching full session for ID: {session_id}")

        try:
            # Retrieve line items explicitly, even if amount_total is 0
            line_items = stripe.checkout.Session.list_line_items(session_id, limit=1)
            price_id = line_items['data'][0]['price']['id']
        except Exception as e:
            logging.error(f"Failed to retrieve line_items from session: {e}")
            return jsonify({"error": "Session fetch failed"}), 400

        if price_id in DEVICE_MAP:
            target = DEVICE_MAP[price_id]
            logging.info(f"Triggering device for price ID {price_id}: {target}")

            tunnel_url = target.get("tunnel_url")
            if not tunnel_url:
                logging.error("Missing 'tunnel_url' in DEVICE_MAP entry.")
                return jsonify({"error": "Missing tunnel_url"}), 400

            try:
                response = requests.post(f"{tunnel_url}/trigger", json=target, timeout=5)
                response.raise_for_status()
                return jsonify({"status": "sent to Pi via tunnel"}), 200
            except Exception as e:
                logging.error(f"Error sending POST to Pi via tunnel: {e}")
                return jsonify({"error": "Failed to reach Pi via tunnel"}), 500
        else:
            logging.warning(f"Price ID not found in DEVICE_MAP: {price_id}")

    else:
        logging.info(f"Ignoring event type: {event['type']}")

    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
