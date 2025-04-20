import joblib

scaler = joblib.load("./models/scaler.pkl")
model = joblib.load("./models/isoforest_model.pkl")

print("MEANS =", list(scaler.mean_))
print("SCALES=", list(scaler.scale_))
print("OFFSET=", model.offset_)
