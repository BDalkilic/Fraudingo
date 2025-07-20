import pandas as pd

def detect_rule_based_anomalies(df):
    df['anomaly_reason'] = ""

    # Örnek kurallar
    df.loc[df['transaction_hour'] < 6, 'anomaly_reason'] += "Gece saati işlemi | "
    df.loc[df['amount'] > 4000, 'anomaly_reason'] += "Yüksek harcama | "
    df.loc[df['transaction_country'] != df['user_registered_country'], 'anomaly_reason'] += "Farklı ülke | "
    df.loc[df['failed_login_attempts'] > 3, 'anomaly_reason'] += "Çoklu başarısız giriş | "
    df.loc[df['session_duration'] > 1000, 'anomaly_reason'] += "Uzun oturum süresi | "
    df.loc[df['is_foreign_transaction'], 'anomaly_reason'] += "Yurt dışı işlem | "

    # Gerçek anomali etiketi
    df['is_anomaly'] = df['anomaly_reason'] != ""
    return df
