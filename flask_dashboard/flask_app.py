import os

import joblib
import paho.mqtt.client as mqtt
import pandas as pd
import requests
from flask import Flask, jsonify, render_template

app = Flask(__name__)


class DummyModel:
    def predict(self, X):
        import numpy as np

        X = np.asarray(X)
        preds = []
        for row in X:
            d1, d2, ir1, ir2 = row
            if ir1 == 1 or ir2 == 1 or d1 > 6 or d1 <= 2 or d2 > 6 or d2 <= 2:
                preds.append(-1)
            else:
                preds.append(1)
        return np.array(preds)


model = joblib.load("models/isoforest_model.pkl")

# ThingSpeak & MQTT
ts_API_KEY = os.environ.get("YOUR_THINGSPEAK_READ_KEY")
ts_CHANNEL_ID = os.environ.get("YOUR_CHANNEL_ID")
MQTT_SERVER = "mqtt3.thingspeak.com"
MQTT_PORT = 1883
MQTT_USER = os.environ.get("YOUR_THINGSPEAK_API_KEY")
MQTT_PASS = ""
ml_alert_pub_topic = "rail/alerts/ml"  # ML-only publish topic

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.connect(MQTT_SERVER, MQTT_PORT)
mqtt_client.loop_start()


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/data")
def data():
    url = f"https://api.thingspeak.com/channels/{ts_CHANNEL_ID}/feeds.json?api_key={ts_API_KEY}&results=50"
    response = requests.get(url).json()
    print("RESPONSE DATA!!!!!!!")
    print(response)
    df = pd.DataFrame(requests.get(url).json()["feeds"]).astype(
        {"field1": float, "field2": float, "field3": float, "field4": float}
    )
    df["anomaly"] = model.predict(df[["field1", "field2", "field3", "field4"]])
    df["anomaly"] = df["anomaly"].apply(lambda x: 1 if x == -1 else 0)

    # Publish latest ML-only alert
    latest_ml = df["anomaly"].iloc[-1]
    mqtt_client.publish(ml_alert_pub_topic, str(latest_ml))

    return jsonify(df.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)
