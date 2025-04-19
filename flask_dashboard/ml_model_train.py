import os

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


# Fetch historical data from ThingSpeak REST API
def fetch_data(api_key, channel_id, n=8000):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.csv?api_key={api_key}&results={n}"
    df = pd.read_csv(url)
    df.dropna(subset=["field1", "field2", "field3", "field4"], inplace=True)
    return df[["field1", "field2", "field3", "field4"]]


# Train Isolation Forest for anomaly detection
if __name__ == "__main__":
    API_KEY = os.environ.get("YOUR_THINGSPEAK_READ_KEY")
    CHANNEL_ID = os.environ.get("YOUR_CHANNEL_ID")

    data = fetch_data(API_KEY, CHANNEL_ID)
    model = IsolationForest(contamination=0.02, random_state=42)
    model.fit(data)

    joblib.dump(model, "./models/isoforest_model.pkl")
    print("Model trained and saved.")
