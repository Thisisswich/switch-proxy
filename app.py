from flask import Flask, request, jsonify
import stripe
import requests
from config import STRIPE_WEBHOOK_SECRET, DEVICE_MAP

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return f"Webhook error: {e}", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        price_id = session['display_items'][0]['price']['id'] if 'display_items' in session else session['line_items']['data'][0]['price']['id']
        if price_id in DEVICE_MAP:
            target = DEVICE_MAP[price_id]
            requests.post(f"http://{target['pi_ip']}:5000/trigger", json=target)
            return jsonify({"status": "sent to Pi"}), 200
    return jsonify({"status": "ignored"}), 200
