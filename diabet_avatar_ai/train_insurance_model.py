import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

print("1. Sug'urta modeli uchun ma'lumotlar yuklanmoqda...")
# CSV faylimizni o'qiymiz
df = pd.read_csv('insurance_data.csv')

# X - kiruvchi ko'rsatkichlar (Yoshi, BMI, Risk foizi)
X = df[['Yoshi', 'BMI', 'Diabet_Xavfi_Foizi']]
# y - chiquvchi natija (Sug'urta badali summasi)
y = df['Sugurta_Badali']

print("2. 2-AI Model lokal serverda o'rgatilmoqda...")
# Modelni yaratamiz va o'rgatamiz
insurance_model = LinearRegression()
insurance_model.fit(X, y)

print("3. O'rgatilgan 2-AI model lokal fayl sifatida saqlanmoqda...")
# Modelni keyinchalik ishlatish uchun saqlaymiz
joblib.dump(insurance_model, 'insurance_price_model.pkl')

print("🚀 Muvaffaqiyatli tugadi! Fayl nomi: insurance_price_model.pkl")
