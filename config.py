import stripe

stripe.api_key = "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"

STRIPE_WEBHOOK_SECRET = "whsec_cUSpoPShjKaFJmAtCr0oxtNrO7aoGKro"

DEVICE_MAP = {
    "price_1RIDIh09QLR8NlKt2YfQ69vc": {
        "device_ip": "192.168.0.244",
        "duration": 60,
        "tunnel_url": "https://pi.swichswich.com"
    },
    "price_456": {
        "device_ip": "192.168.1.102",
        "duration": 60,
        "tunnel_url": "https://pi.swichswich.com"
    },
}
