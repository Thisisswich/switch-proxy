from flask import Flask, request, jsonify
import requests
import logging
import threading
import time
from config import DEVICE_MAP

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

    logging.info("Starting control_shelly thread...")
    threading.Thread(target=control_shelly, args=(device_ip, duration)).start()
    return jsonify({"status": f"shelly on for {duration} seconds"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
