import pandas as pd
import joblib
import os

# Model ve scaler'ı yükle
model = joblib.load("models/isolation_forest.pkl")
scaler = joblib.load("models/scaler.pkl")

def predict_transaction(data):
    df = pd.DataFrame([data])

    # Feature mühendisliği
    df["avg_amount_user"] = df["amount"]  # sadece kendi verisi var
    df["amount_dev"] = 0
    df["avg_hour_user"] = df["transaction_hour"]
    df["hour_dev"] = 0
    df["failed_login_risk"] = df["failed_login_attempts"] >= 3
    df["night_transaction_flag"] = df["transaction_hour"].apply(lambda x: x < 6 or x > 22)

    # Model inputu
    X = df[["amount_dev", "hour_dev", "failed_login_risk", "night_transaction_flag"]].copy()
    X["failed_login_risk"] = X["failed_login_risk"].astype(int)
    X["night_transaction_flag"] = X["night_transaction_flag"].astype(int)

    # Ölçekleme uygula (Scaler varsa)
    X_scaled = scaler.transform(X) if scaler else X

    # Tahmin ve skor
    score = model.decision_function(X_scaled)[0]
    label = model.predict(X_scaled)[0]
    is_fraud = int(label == -1)

    # Sebep çıkarımı
    reasons = []
    if df["failed_login_risk"].values[0]:
        reasons.append("Çoklu başarısız giriş denemesi.")
    if df["night_transaction_flag"].values[0]:
        reasons.append("Alışılmadık saatte işlem.")
    if df["amount_dev"].values[0] > 1000:
        reasons.append("Alışılmadık harcama miktarı.")

    return {
        "transaction_id": data["transaction_id"],
        "anomaly_score": float(score),
        "is_anomaly": is_fraud,
        "is_fraud": is_fraud,
        "reason": ", ".join(reasons) if reasons else "genel davranış anomali"
    }

def log_transaction(data, result):
    log_file = "data/transactions_with_anomalies.csv"
    os.makedirs("data", exist_ok=True)

    full_data = data.copy()
    full_data["anomaly_score"] = result["anomaly_score"]
    full_data["is_anomaly"] = result["is_anomaly"]
    full_data["is_fraud"] = result["is_fraud"]
    full_data["reason"] = result["reason"]

    df = pd.DataFrame([full_data])
    df.to_csv(log_file, mode="a", header=not os.path.exists(log_file), index=False)
