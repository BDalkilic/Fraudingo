import streamlit as st
import pandas as pd
from PIL import Image
from predict_with_model import predict_transaction
# Sayfa ayarları
st.set_page_config(page_title="Fraudingo - Güvenlik Paneli", layout="wide")
# Özel stil (tema, yazı, logo hizalama)
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
        }
        .stApp {
            background-color: #F5F5F0;
        }
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
            margin-bottom: 0px;
        }
        .sub-header {
            text-align: center;
            font-size: 25px;
            color: #004080;
            margin-bottom: 30px;
        }
        .metric-card {
            border-left: 6px solid #004080;
            padding: 1rem 1.5rem;
            background-color: #FFFFFF;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            font-size: 18px;
        }
        div.stButton > button:first-child {
            background-color: #004080;
            color: white;
            border: none;
            padding: 0.5em 1em;
            border-radius: 8px;
            font-size: 20px;
        }
        div.stButton > button:hover {
            background-color: #24598D;
        }
            
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
# Logo (her zaman üstte görünür)
with st.container():
    col_logo, col_spacer, col_logo2 = st.columns([4.78, 6, 1])
    with col_spacer:
        logo = Image.open("images/logo.png")
        st.image(logo, width=250)
# Veri yükle
df = pd.read_csv("data/transactions_with_anomalies.csv")
login_df = df[["email", "password", "role"]].drop_duplicates()
# Oturum yönetimi
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False
if "aktif_kullanici" not in st.session_state:
    st.session_state.aktif_kullanici = None
if "aktif_rol" not in st.session_state:
    st.session_state.aktif_rol = None
# Giriş ekranı
if not st.session_state.giris_yapildi:
    st.markdown("<div class='sub-header'>Anomali Takip Sistemi</div>", unsafe_allow_html=True)
    email = st.text_input("E-posta")
    sifre = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap", type="primary"):
        user = login_df[(login_df["email"] == email) & (login_df["password"] == sifre)]
        if not user.empty:
            st.session_state.giris_yapildi = True
            st.session_state.aktif_kullanici = email
            st.session_state.aktif_rol = user["role"].values[0]
            st.rerun()
        else:
            st.error("Giriş başarısız. Bilgileri kontrol edin.")
# Ana panel
if st.session_state.giris_yapildi:
    st.markdown("<div class='sub-header'>Finansal İşlem Güvenliği Paneli</div>", unsafe_allow_html=True)
    rol = st.session_state.aktif_rol
    email = st.session_state.aktif_kullanici
    if rol == 1:
        st.subheader("Yönetici Paneli")
        selected_user = st.selectbox("Kullanıcı Seçin", sorted(df["user_id"].unique()))
        filtered = df[df["user_id"] == selected_user]
    else:
        st.subheader("İşlem Geçmişiniz")
        filtered = df[df["email"] == email]
        kolonlar = [
            "transaction_id", "user_id", "email", "amount", "currency",
            "transaction_type", "device_type", "transaction_country",
            "bank_name", "transaction_hour", "is_anomaly"
        ]
        filtered = filtered[[k for k in kolonlar if k in filtered.columns]]
        filtered = filtered.rename(columns={
            "transaction_id": "İşlem ID",
            "user_id": "Kullanıcı",
            "email": "E-posta",
            "amount": "Tutar",
            "currency": "Döviz",
            "transaction_type": "İşlem Tipi",
            "device_type": "Cihaz Tipi",
            "transaction_country": "Konum",
            "bank_name": "Banka",
            "transaction_hour": "İşlem Saati",
            "is_anomaly": "Şüpheli"
        })
    anomaly_col = "Şüpheli" if "Şüpheli" in filtered.columns else "is_anomaly"
    # Metrikler
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='metric-card'><strong>Toplam İşlem:</strong><br>{len(filtered)}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><strong>Şüpheli İşlem:</strong><br>{int(filtered[anomaly_col].sum())}</div>", unsafe_allow_html=True)
    # İşlem seçimi
    selected_index = st.selectbox(
        "İşlem Seçin",
        filtered.index,
        format_func=lambda i: f"{filtered.at[i, 'İşlem ID'] if 'İşlem ID' in filtered.columns else filtered.at[i, 'transaction_id']} – {filtered.at[i, 'Tutar'] if 'Tutar' in filtered.columns else filtered.at[i, 'amount']} ₺"
    )
    selected_row = filtered.loc[selected_index]
    # Tablo vurgulama
    def highlight_selected_and_anomaly(row):
        is_anomaly = row.get("Şüpheli") if "Şüpheli" in row else row.get("is_anomaly", 0)
        if row.name == selected_index:
            return ["background-color: #E6F0FF"] * len(row)
        elif is_anomaly == 1:
            return ["background-color: #FFE6E6; color: red"] * len(row)
        return [""] * len(row)
    st.markdown("İşlem Listesi")
    st.dataframe(filtered.style.apply(highlight_selected_and_anomaly, axis=1), use_container_width=True)
    # Şüpheli işlem detayları
    selected_is_anomaly = selected_row.get("Şüpheli") if "Şüpheli" in selected_row else selected_row.get("is_anomaly", 0)
    selected_transaction_id = selected_row.get("İşlem ID") or selected_row.get("transaction_id")
    if selected_is_anomaly == 1:
        match = df[df["transaction_id"] == selected_transaction_id]
        if not match.empty:
            data_dict = match.iloc[0].to_dict()
            prediction = predict_transaction(data_dict)
            if prediction.get("reason"):
                st.info(f"Şüphe Sebebi: {prediction['reason']}")
            else:
                st.warning("Sebep üretilemedi.")
        else:
            st.error("İşlem bulunamadı.")
    st.markdown("---")
    if st.button("Oturumu Kapat"):
        st.session_state.giris_yapildi = False
        st.session_state.aktif_kullanici = None
        st.session_state.aktif_rol = None
        st.rerun()