import os

import joblib
import paho.mqtt.client as mqtt
import pandas as pd
import requests
from flask import Flask, jsonify, render_template, request

# --- Setup ---
env = os.path.dirname(__file__)
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load artifacts
model = joblib.load(os.path.join(env, "models", "isoforest_model.pkl"))
scaler = joblib.load(os.path.join(env, "models", "scaler.pkl"))

# ThingSpeak settings
ts_ch_id = 2925813
ts_read_key = "NDF06NG7FIFAWDNK"
TS_URL = f"https://api.thingspeak.com/channels/{ts_ch_id}/feeds.json"

# MQTT for manual triggers
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.username_pw_set("3GDTO22V308LUSY5")
mqtt_client.connect("mqtt3.thingspeak.com", 1883)
mqtt_client.loop_start()

# Topics
SENSOR_TOPIC = "rail/alerts/sensor"
ML_TOPIC = "rail/alerts/ml"


# --- Routes ---
@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/data")
def data():
    # Attempt to fetch live data from ThingSpeak
    params = dict(api_key=ts_read_key)
    try:
        resp = requests.get(TS_URL, params=params, timeout=5)
        resp.raise_for_status()
        feeds = resp.json().get("feeds", [])
    except Exception as e:
        app.logger.error(f"TS fetch failed: {e}. Falling back to local cache.")
        # Fallback: read from local CSV if live fetch fails
        local_csv = os.path.join(env, "feeds.csv")
        if os.path.exists(local_csv):
            df = pd.read_csv(local_csv)
            for f in ["field1", "field2", "field3", "field4", "field5", "field6"]:
                df[f] = pd.to_numeric(df[f], errors="coerce")
            if "created_at" in df:
                df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
            feeds = df.to_dict(orient="records")
        else:
            app.logger.error(f"No local cache found at {local_csv}")
            feeds = []
    # Process feeds into DataFrame
    df = pd.DataFrame(feeds)
    if df.empty:
        return jsonify([])
    for f in ["field1", "field2", "field3", "field4", "field5", "field6"]:
        df[f] = pd.to_numeric(df[f], errors="coerce")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    # Apply ML prediction
    X = df[["field1", "field2", "field3", "field4"]]
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    df["predicted"] = [1 if p == -1 else 0 for p in preds]

    import json

    print(
        json.dumps(df.to_dict(orient="records"), indent=2, default=str)
    )  # use default=str for datetime

    return jsonify(df.to_dict(orient="records"))


@app.route("/accuracy")
def accuracy():
    resp = data().json
    df = pd.DataFrame(resp)
    matches = (df["predicted"] == df["field5"]).sum()
    acc = round(matches / len(df) * 100, 2)
    return jsonify({"accuracy": acc})


@app.route("/trigger", methods=["POST"])
def trigger():
    t = request.json.get("type")  # 'sensor' or 'ml'
    topic = SENSOR_TOPIC if t == "sensor" else ML_TOPIC
    mqtt_client.publish(topic, "1")
    return jsonify({"status": "ok", "triggered": t})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
