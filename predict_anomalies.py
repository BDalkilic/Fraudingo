import pandas as pd
import joblib

# Model ve scaler'ı yükle
model = joblib.load("models/isolation_forest.pkl")
scaler = joblib.load("models/scaler.pkl")

# Veriyi yükle
df = pd.read_csv("data/transactions.csv")

numeric_features = [
    "amount", "transaction_hour", "session_duration", "failed_login_attempts",
    "prev_transaction_amount", "avg_transaction_amount_last_7d",
    "foreign_transaction_count_last_30d", "total_foreign_transaction_count",
    "account_age_days", "transaction_frequency_last_30d", "avg_amount_last_30d",
    "device_trust_score", "distance_from_usual_location", "Risk_Score"
]

X = df[numeric_features]
X_scaled = scaler.transform(X)

# Tahmin yap
df['anomaly_score'] = model.decision_function(X_scaled)
df['is_anomaly'] = model.predict(X_scaled)  # -1 → Anomali, 1 → Normal
df['is_anomaly'] = df['is_anomaly'].map({1: 0, -1: 1})  # 1 = anomaly

# Sonuçları kaydet
df.to_csv("output/results_ml.csv", index=False)
print("📁 ML tabanlı anomali sonucu: output/results_ml.csv")
