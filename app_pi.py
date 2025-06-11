from flask import Flask, request, jsonify
import requests
import logging
import threading
import os
import json
from dotenv import load_dotenv

load_dotenv()
DEVICE_MAP = json.loads(os.getenv("DEVICE_MAP"))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Tracks active timers by device IP
active_timers = {}

def turn_off(device_ip):
    try:
        logging.info(f"Turning OFF Shelly at {device_ip}")
        requests.get(f"http://{device_ip}/relay/0?turn=off", timeout=5)
    except Exception as e:
        logging.error(f"Failed to turn off {device_ip}: {e}")

def activate_plug(device_ip, duration):
    try:
        logging.info(f"Turning ON Shelly at {device_ip} for {duration} seconds")
        requests.get(f"http://{device_ip}/relay/0?turn=on", timeout=5)
    except Exception as e:
        logging.error(f"Failed to turn on {device_ip}: {e}")
        return

    # Cancel existing timer if it exists
    if device_ip in active_timers:
        logging.info(f"Cancelling existing timer for {device_ip}")
        active_timers[device_ip].cancel()

    # Create new timer and store it
    timer = threading.Timer(duration, turn_off, args=[device_ip])
    timer.start()
    active_timers[device_ip] = timer
    logging.info(f"New timer started for {device_ip} for {duration} seconds")

@app.route("/trigger", methods=["POST"])
def trigger():
    data = request.get_json(force=True)
    logging.info(f"/trigger endpoint received payload: {data}")

    device_ip = data.get("device_ip")
    duration = data.get("duration", 1800)  # default to 30 min

    if not device_ip:
        logging.error("Missing 'device_ip' in payload.")
        return jsonify({"error": "Missing device_ip"}), 400

    activate_plug(device_ip, duration)
    return jsonify({"status": f"shelly on for {duration} seconds"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

