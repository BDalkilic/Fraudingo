import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from email_utils import send_email
import os
import joblib
import time  # ✅ Zaman gecikmesi için eklendi

# 📥 Veriyi oku
file_path = "data/transactions.csv"
df = pd.read_csv(file_path, sep=";")
print("✅ Veri başarıyla yüklendi:", df.shape)

# Kopya veri (email, bank gibi orijinal bilgiler için)
df_original = df.copy()

# 🔍 Kullanıcı bazlı davranışsal istatistikler
df["avg_amount_user"] = df.groupby("user_id")["amount"].transform("mean")
df["amount_dev"] = abs(df["amount"] - df["avg_amount_user"])
df["avg_hour_user"] = df.groupby("user_id")["transaction_hour"].transform("mean")
df["hour_dev"] = abs(df["transaction_hour"] - df["avg_hour_user"])
df["failed_login_risk"] = df["failed_login_attempts"] >= 3
df["night_transaction_flag"] = df["transaction_hour"].apply(lambda x: x < 6 or x > 22)

# 🎯 Özellik seti (davranışsal)
X = df[["amount_dev", "hour_dev", "failed_login_risk", "night_transaction_flag"]].copy()
X["failed_login_risk"] = X["failed_login_risk"].astype(int)
X["night_transaction_flag"] = X["night_transaction_flag"].astype(int)

# 📊 Standartlaştırma
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 🌲 Model eğitimi
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
model.fit(X_scaled)

# 🔍 Tahmin ve skorlar
df["anomaly_score"] = model.decision_function(X_scaled)
df["anomaly_label"] = model.predict(X_scaled)
df["is_anomaly"] = df["anomaly_label"].map({1: 0, -1: 1})

# 💾 Sonuçları kaydet
output_path = "data/transactions_with_anomalies.csv"
os.makedirs("data", exist_ok=True)
df.to_csv(output_path, index=False)
print("📊 Anomali sayısı:", df['is_anomaly'].sum())
print(f"✅ Anomalili veri kaydedildi: {output_path}")

# 📧 Anomali varsa e-posta gönder (gecikmeli)
for idx, row in df[df["is_anomaly"] == 1].iterrows():
    to_email = df_original.loc[idx, "email"]
    transaction_id = df_original.loc[idx, "transaction_id"]
    bank = df_original.loc[idx, "bank_name"] if "bank_name" in df_original.columns else "Bilinmiyor"
    hour = df_original.loc[idx, "transaction_hour"]

    if to_email and "@" in to_email:
        reasons = []
        if row["failed_login_risk"]:
            reasons.append("çoklu başarısız giriş denemesi")
        if row["night_transaction_flag"]:
            reasons.append("alışılmadık saatte işlem")
        if row["amount_dev"] > 1000:
            reasons.append("alışılmadık harcama miktarı")

        reason_text = ", ".join(reasons) if reasons else "genel davranış anomali"

        message = (
            f"Sayın kullanıcı,\n\n"
            f"Aşağıdaki işlem şüpheli olarak işaretlenmiştir:\n\n"
            f"🏦 Banka: {bank}\n"
            f"Transaction ID: {transaction_id}\n"
            f"İşlem Saati: {hour}:00\n"
            f"Tespit Nedenleri: {reason_text}\n"
            f"Anomali Skoru: {row['anomaly_score']:.3f}\n\n"
            f"Lütfen işleminizi kontrol ediniz.\n\n"
            f"-- Açık Bankacılık Güvenlik Sistemi"
        )


# 💾 Model ve scaler'ı kaydet
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/isolation_forest.pkl")
print("✅ Model kaydedildi: models/isolation_forest.pkl")

joblib.dump(scaler, "models/scaler.pkl")
print("✅ Scaler kaydedildi: models/scaler.pkl")
