import stripe

# Your Stripe webhook secret
STRIPE_WEBHOOK_SECRET = "whsec_cUSpoPShjKaFJmAtCr0oxtNrO7aoGKro"

# Mapping Stripe price_id → Shelly config
DEVICE_MAP = {
    "price_1RIDIh09QLR8NlKt2YfQ69vc": {"device_ip": "192.168.0.244", "duration": 1, "pi_ip": "192.168.0.154"},
    "price_456": {"device_ip": "192.168.1.102", "duration": 60, "pi_ip": "192.168.1.50"},
}
