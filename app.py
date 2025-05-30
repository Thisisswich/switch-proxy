from flask import Flask, request, jsonify
import stripe
import requests
import os
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
        session_id = event['data']['object']['id']
        try:
            session = stripe.checkout.Session.retrieve(session_id, expand=['line_items'])
            price_id = session['line_items']['data'][0]['price']['id']
        except Exception as e:
            logging.error(f"Failed to retrieve session or price_id: {e}")
            return jsonify({"error": "Session fetch failed"}), 400

        if price_id in DEVICE_MAP:
            target = DEVICE_MAP[price_id]
            logging.info(f"Triggering device for price ID {price_id}: {target}")
            requests.post(f"http://{target['pi_ip']}:5000/trigger", json=target)
            return jsonify({"status": "sent to Pi"}), 200
        else:
            logging.warning(f"Price ID not found in DEVICE_MAP: {price_id}")
    else:
        logging.info(f"Ignoring event type: {event['type']}")

    return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
