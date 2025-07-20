import pandas as pd
import time
import requests
import json  # Türkçe karakterleri düzgün göstermek için

# Veriyi yükle
df = pd.read_csv("data/transactions.csv", sep=";")

# Her satırı MCP API'ye gönder
for _, row in df.iterrows():
    payload = row.to_dict()

    try:
        response = requests.post("http://localhost:5000/mcp/transaction", json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get("is_fraud") == 1:
                print("✅ Fraud Tespit Edildi:")
                print(json.dumps(result, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Hata: {e}")

    time.sleep(1)
