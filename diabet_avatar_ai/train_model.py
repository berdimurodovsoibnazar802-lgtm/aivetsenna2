import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("1. Ma'lumotlar bazasi yuklanmoqda...")
# Ustunlar nomini belgilab olamiz (Kaggle dataset standarti)
columns = ['Homiladorlik_soni', 'Glyukoza', 'Qon_bosimi', 'Teri_qalinligi', 
           'Insulin', 'BMI_Vazn', 'Diabet_Pedigree', 'Yoshi', 'Diabet_Xavfi']

# CSV faylni o'qiymiz
df = pd.read_csv('diabetes.csv', names=columns)

print("2. Ma'lumotlar tayyorlanmoqda (Preprocessing)...")
# X - bu bemor tahlillari, Y - bu diabet bormi yoki yo'q (0 yoki 1)
X = df.drop('Diabet_Xavfi', axis=1)
y = df['Diabet_Xavfi']

# Ma'lumotlarni 80% o'rgatish (train) va 20% test qilish uchun bo'lamiz
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"O'rgatish uchun darsliklar soni: {len(X_train)} ta")
print(f"Test qilish uchun darsliklar soni: {len(X_test)} ta")

print("\n3. AI Model (Random Forest) lokal serverda o'rgatilmoqda (Training)...")
# Modelni yaratamiz va o'rgatamiz
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("4. Model sifati tekshirilmoqda...")
# Test ma'lumotlari orqali modelni tekshiramiz
y_pred = model.predict(X_test)
aniqlik = accuracy_score(y_test, y_pred)
print(f"--- MODEL ANIIQLIGI: {aniqlik * 100:.2f}% ---")

print("\n5. O'rgatilgan AI model lokal fayl sifatida saqlanmoqda...")
# Keyinchalik avatar tizimiga ulash uchun modelni saqlab qo'yamiz
joblib.dump(model, 'diabet_detector_model.pkl')
print("Muvaffaqiyatli saqlandi! Fayl nomi: diabet_detector_model.pkl")