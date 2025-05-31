from flask import Flask, request, jsonify
import stripe
import requests
import os
import logging
import threading
import time
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
            full_session = stripe.checkout.Session.retrieve(session_id, expand=["line_items"])
            price_id = full_session["line_items"]["data"][0]["price"]["id"]
        except Exception as e:
            logging.error(f"Failed to retrieve line_items from session: {e}")
            return jsonify({"error": "Session fetch failed"}), 400

        if price_id in DEVICE_MAP:
            target = DEVICE_MAP[price_id]
            logging.info(f"Triggering device for price ID {price_id}: {target}")

            pi_ip = target.get("pi_ip")
            if not pi_ip:
                logging.error("Missing 'pi_ip' in DEVICE_MAP entry.")
                return jsonify({"error": "Missing pi_ip"}), 400

            try:
                response = requests.post(f"http://{pi_ip}:5000/trigger", json=target, timeout=5)
                response.raise_for_status()
                return jsonify({"status": "sent to Pi"}), 200
            except Exception as e:
                logging.error(f"Error sending POST to Pi /trigger: {e}")
                return jsonify({"error": "Failed to reach Pi"}), 500
        else:
            logging.warning(f"Price ID not found in DEVICE_MAP: {price_id}")

    else:
        logging.info(f"Ignoring event type: {event['type']}")

    return jsonify({"status": "ignored"}), 200

@app.route("/trigger", methods=["POST"])
def trigger():
    data = request.get_json(force=True)
    logging.info(f"/trigger endpoint received payload: {data}")

    device_ip = data.get("device_ip")
    duration = data.get("duration", 1800)

    if not device_ip:
        logging.error("Missing 'device_ip' in payload.")
        return jsonify({"error": "Missing device_ip"}), 400

    def control_shelly(device_ip, duration):
        try:
            on_url = f"http://{device_ip}/relay/0?turn=on"
            off_url = f"http://{device_ip}/relay/0?turn=off"

            logging.info(f"Turning ON Shelly at {on_url}")
            requests.get(on_url, timeout=5)

            logging.info(f"Sleeping for {duration} seconds")
            time.sleep(duration)

            logging.info(f"Turning OFF Shelly at {off_url}")
            requests.get(off_url, timeout=5)
        except Exception as e:
            logging.error(f"Error during Shelly control thread: {e}")

    threading.Thread(target=control_shelly, args=(device_ip, duration)).start()
    return jsonify({"status": f"shelly on for {duration} seconds"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
