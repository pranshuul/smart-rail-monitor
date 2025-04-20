import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# 1. Load CSV (make sure you've saved your CSV as this file)
csv_path = "feeds.csv"  # replace if your file is elsewhere
df = pd.read_csv(
    csv_path, usecols=["field1", "field2", "field3", "field4", "field5", "field6"]
)

# 2. Prepare features and labels
X = df[["field1", "field2", "field3", "field4"]]
y = df["field5"].astype(int)  # sensor_alert

# 3. Scale features
scaler = StandardScaler().fit(X)
X_scaled = scaler.transform(X)

# 4. Train IsolationForest
model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
model.fit(X_scaled)

# 5. Save artifacts
scaler_path = "./models/scaler.pkl"
model_path = "./models/isoforest_model.pkl"
joblib.dump(scaler, scaler_path)
joblib.dump(model, model_path)

print(f"Scaler saved to {scaler_path}")
print(f"Model  saved to {model_path}")
