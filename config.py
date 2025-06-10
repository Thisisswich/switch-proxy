import os
from dotenv import load_dotenv
import json
import stripe

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
DEVICE_MAP = json.loads(os.getenv("DEVICE_MAP"))
