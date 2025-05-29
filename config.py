import stripe

# Your Stripe webhook secret
STRIPE_WEBHOOK_SECRET = "whsec_XXXXXXX"

# Mapping Stripe price_id → Shelly config
DEVICE_MAP = {
    "price_123": {"device_ip": "192.168.1.101", "duration": 30, "pi_ip": "192.168.1.50"},
    "price_456": {"device_ip": "192.168.1.102", "duration": 60, "pi_ip": "192.168.1.50"},
}
