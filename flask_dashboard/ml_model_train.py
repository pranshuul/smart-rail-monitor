import os

import joblib
import pandas as pd
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --- Configuration ---
CHANNEL_ID = 2925813
API_KEY = "NDF06NG7FIFAWDNK"
BASE_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")


# --- Fetch Data ---
def fetch_data(results=800):
    url = f"{BASE_URL}?api_key={API_KEY}&results={results}"
    resp = requests.get(url)
    resp.raise_for_status()
    feeds = resp.json().get("feeds", [])
    return pd.DataFrame(feeds)


# --- Preprocess ---
def preprocess(df):
    # Cast types
    for f in ["field1", "field2", "field3", "field4", "field5"]:
        df[f] = pd.to_numeric(df[f], errors="coerce")
    df = df.dropna(subset=["field1", "field2", "field3", "field4", "field5"])

    X = df[["field1", "field2", "field3", "field4"]]
    y = df["field5"].astype(int)  # sensor_alert as ground truth
    return X, y


# --- Train & Save ---
def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)

    df_raw = fetch_data()
    X, y = preprocess(df_raw)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Isolation Forest for anomaly detection
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X_scaled)

    # Save artifacts
    joblib.dump(model, os.path.join(MODEL_DIR, "isoforest_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    print("Model and scaler saved to 'models/' directory.")


if __name__ == "__main__":
    train_and_save()
