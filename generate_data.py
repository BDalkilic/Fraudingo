import pandas as pd 
import random
import uuid
from datetime import datetime, timedelta

user_passwords = {} 
# Sabit veri havuzları
currencies = ['TRY', 'USD', 'EUR']
transaction_types = ['POS', 'EFT', 'Havale', 'Yatırım', 'Ödeme']
device_types = ['mobile', 'desktop', 'atm']
login_methods = ['biometric', 'password', '2FA']
countries = ['TR', 'DE', 'FR', 'US', 'GB', 'NL']
user_types = ['individual', 'corporate', 'student', 'expat']
merchant_categories = ['electronics', 'clothing', 'grocery', 'travel', 'restaurants']
card_types = ['credit', 'debit', 'prepaid']

def random_time():
    base = datetime(2023, 1, 1)
    delta = timedelta(seconds=random.randint(0, 31536000))
    return int((base + delta).timestamp())

def random_location():
    cities = ['Istanbul', 'Berlin', 'Paris', 'New York', 'London', 'Amsterdam']
    return random.choice(cities)

def generate_row(user_id):
    user_country = random.choice(['TR', 'TR', 'TR', 'DE'])
    is_foreign = random.choice([True, False, False])
    transaction_country = random.choice([c for c in countries if c != user_country]) if is_foreign else user_country
    usual_country = 'TR' if user_country == 'TR' else transaction_country
    mismatch_flag = transaction_country != user_country
    transaction_hour = random.randint(0, 23)
    usual_time_range = "08-18"
    is_unusual_time = not (8 <= transaction_hour <= 18)

    # 🔐 E-posta ve fraud ayarı (özelleştirilmiş kullanıcı)
    if user_id == "user_63":
        email = "fbbatuhan656@gmail.com"
        is_fraud = 1  # test için fraud işaretle
    else:
        email = f"{user_id}@example.com"
        is_fraud = random.choices([0, 1], weights=[95, 5])[0]
    # ✅ Kullanıcıya özel sabit şifre atama
    if user_id not in user_passwords:
        user_passwords[user_id] = f"pass{random.randint(1000, 9999)}"
    password = f"{user_id}_pass"

    

    row = {
        "transaction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "email": email,
        "password": password,
        "timestamp": random_time(),
        "amount": round(random.uniform(10, 5000), 2),
        "currency": random.choice(currencies),
        "transaction_type": random.choice(transaction_types),
        "device_type": random.choice(device_types),
        "location": random_location(),
        "login_method": random.choice(login_methods),
        "bank_name": random.choice(["Fibabanka", "QNB Finansbank", "İş Bankası", "Yapı Kredi", "Garanti BBVA"]),
        "transaction_hour": transaction_hour,
        "session_duration": round(random.uniform(1, 1800), 2),
        "device_id": str(uuid.uuid4()),
        "ip_address": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
        "prev_transaction_amount": round(random.uniform(10, 3000), 2),
        "avg_transaction_amount_last_7d": round(random.uniform(10, 2000), 2),
        "usual_location_flag": random.choice([True, False]),
        "unusual_time_flag": is_unusual_time,
        "failed_login_attempts": random.randint(0, 5),
        "is_foreign_transaction": is_foreign,
        "foreign_transaction_count_last_30d": random.randint(0, 10),
        "total_foreign_transaction_count": random.randint(0, 50),
        "has_recent_travel_history": random.choice([True, False]),
        "frequent_country": usual_country,
        "transaction_country": transaction_country,
        "user_registered_country": user_country,
        "distance_from_usual_location": round(random.uniform(0, 5000), 2),
        "recent_foreign_login_flag": random.choice([True, False]),
        "user_type": random.choice(user_types),
        "account_age_days": random.randint(1, 1500),
        "transaction_frequency_last_30d": random.randint(1, 100),
        "avg_amount_last_30d": round(random.uniform(10, 3000), 2),
        "usual_login_time_range": usual_time_range,
        "device_trust_score": round(random.uniform(0, 1), 2),
        "num_of_login_countries_last_7d": random.randint(1, 4),
        "login_country_mismatch_flag": mismatch_flag,

        # Ek kolonlar
        "Transaction_ID": str(uuid.uuid4()),
        "User_ID": user_id,
        "Transaction_Amount": round(random.uniform(10, 5000), 2),
        "Transaction_Type": random.choice(transaction_types),
        "Timestamp": random_time(),
        "Account_Balance": round(random.uniform(0, 20000), 2),
        "Device_Type": random.choice(device_types),
        "Location": random_location(),
        "Merchant_Category": random.choice(merchant_categories),
        "IP_Address_Flag": random.choice([0, 1]),
        "Previous_Fraudulent_Activity": random.choice([0, 1]),
        "Daily_Transaction_Count": random.randint(1, 20),
        "Avg_Transaction_Amount_7d": round(random.uniform(10, 5000), 2),
        "Failed_Transaction_Count_7d": random.randint(0, 5),
        "Card_Type": random.choice(card_types),
        "Card_Age": random.randint(1, 3650),
        "Transaction_Distance": round(random.uniform(0.5, 1000.0), 2),
        "Authentication_Method": random.choice(login_methods),
        "Risk_Score": round(random.uniform(0.1, 1.0), 2),
        "Is_Weekend": random.choice([0, 1]),
        "role": 1 if email == "fbbatuhan656@gmail.com" else 0,
    }

    return row

# 🔄 Veri üretimi
num_rows = 50000
data = [generate_row(user_id=f"user_{random.randint(1, 100)}") for _ in range(num_rows - 1)]

# Test verisi olarak user_99'u sona ekle
data.append(generate_row("user_99"))

# 📁 Kaydet
df = pd.DataFrame(data)
df.to_csv("data/transactions.csv", index=False, sep=";")
df.to_excel("data/transactions.xlsx", index=False)
print(f"✅ {num_rows} satırlık CSV ve Excel dosyası oluşturuldu.")
