# app.py – Flask tabanlı MCP listener
from flask import Flask, request, jsonify
from predict_with_model import predict_transaction
from email_utils import send_email
import pandas as pd
import os
import json
from flask import request

app = Flask(__name__)

# Anomalili işlemleri CSV’ye loglama
def log_transaction(data, result):
    log_file = "data/transactions_with_anomalies.csv"
    os.makedirs("data", exist_ok=True)

    full_data = data.copy()
    full_data["anomaly_score"] = result["anomaly_score"]
    full_data["is_anomaly"] = result["is_anomaly"]
    full_data["reason"] = result["reason"]
    full_data["is_fraud"] = result["is_fraud"]
    full_data["user_feedback"] = ""     # kullanıcıdan dönüş gelmedi varsayımı
    full_data["status"] = "pending"     # henüz işlem iptal/onaylanmadı

    df = pd.DataFrame([full_data])
    write_header = not os.path.isfile(log_file)
    df.to_csv(log_file, mode="a", header=write_header, index=False)

@app.route("/mcp/transaction", methods=["POST"])
def mcp_transaction():
    data = request.json
    result = predict_transaction(data)

    # CSV'ye logla
    log_transaction(data, result)

    # E-posta gönder (anomali varsa)
    if result["is_anomaly"]:
        bank = data.get("bank_name", "Bilinmeyen banka")
        hour = data.get("transaction_hour", "Bilinmiyor")
        transaction_id = data["transaction_id"]
        feedback_yes = f"http://localhost:5000/feedback?tid={transaction_id}&response=yes"
        feedback_no = f"http://localhost:5000/feedback?tid={transaction_id}&response=no"


        try:
            send_email(
                to_email=data["email"],
                subject=" Şüpheli İşlem Tespit Edildi",
                message_body=(
                    f"Sayın kullanıcı,\n\n"
                    f"Aşağıdaki işlem şüpheli olarak işaretlenmiştir:\n\n"
                    f"• Banka: {bank}\n"
                    f"• Transaction ID: {data['transaction_id']}\n"
                    f"• İşlem Saati: {hour}:00\n"
                    f"• Tespit Nedenleri: {result['reason']}\n"
                    f"• Anomali Skoru: {result['anomaly_score']:.3f}\n\n"
                    f"\n\n [İşlem bana ait]({feedback_yes})\n [İşlem bana ait değil]({feedback_no})\n\n"
                    f"Lütfen işleminizi kontrol ediniz.\n\n"
                    f"-- Açık Bankacılık Güvenlik Sistemi"
                )
            )
            print(f" E-posta gönderildi: {data['email']} | Transaction ID: {data['transaction_id']}")
        except Exception as e:
            print(f" E-posta gönderilemedi ({data['email']}): {e}")
    if result["is_fraud"]:
        print(" Yanıt:", json.dumps(result, ensure_ascii=False, indent=2))


    return jsonify(result)

@app.route("/feedback", methods=["GET"])
def feedback():
    transaction_id = request.args.get("tid")
    response = request.args.get("response")

    if not transaction_id or not response:
        return "Eksik bilgi gönderildi", 400

    # CSV dosyasını oku
    df = pd.read_csv("data/transactions_with_anomalies.csv")

    # İşlem varsa güncelle
    if transaction_id in df["transaction_id"].values:
        df.loc[df["transaction_id"] == transaction_id, "user_feedback"] = response
        df.to_csv("data/transactions_with_anomalies.csv", index=False)

        # Eğer kullanıcı "bana ait değil" dediyse işlem iptal edilir (örnek olarak flag ekleniyor)
        if response == "no":
            df.loc[df["transaction_id"] == transaction_id, "status"] = "cancelled"
            df.to_csv("data/transactions_with_anomalies.csv", index=False)
            return "İşleminiz iptal edildi. Teşekkürler.", 200
        else:
            return "İşlem onaylandı. Teşekkürler.", 200

    return "İşlem bulunamadı", 404
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
