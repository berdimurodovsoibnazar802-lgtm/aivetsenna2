import joblib
import numpy as np

# 1. Ikkala lokal AI modelni yuklab olamiz
model1_diabet = joblib.load('diabet_detector_model.pkl')
model2_insurance = joblib.load('insurance_price_model.pkl')
print("🧠 Ikkala lokal AI model tizimga muvaffaqiyatli yuklandi!\n")

# Bemor tahlillari (Kiritilgan ma'lumotlar)
bemor_ismi = "Otabek"
yoshi = 45
bmi = 34.2
glyukoza = 168
qon_bosimi = 85
insulin = 0
homiladorlik = 0
teri = 25
pedigree = 0.78

# --- 1-AI MODEL VA 1-AGENT: Diabet va Avatar xavfini aniqlash ---
# Model 1 uchun ma'lumot to'plami
bemor_tahlil_m1 = [[homiladorlik, glyukoza, qon_bosimi, teri, insulin, bmi, pedigree, yoshi]]
diabet_risk_kodi = model1_diabet.predict(bemor_tahlil_m1)[0]
# Xavf ehtimolligini foizda olamiz
diabet_risk_foizi = model1_diabet.predict_proba(bemor_tahlil_m1)[0][1] * 100

print(f"🤖 1-AGENT REAKSIYASI (Avatar Coordinator):")
if diabet_risk_kodi == 1:
    print(f"  -> AVATAR STATUSI: CRITICAL RED (Xavf yuqori: {diabet_risk_foizi:.1f}%)")
    print(f"  -> Prompt log: 'Pulsating red light filaments in eye and kidney areas.'")
else:
    print(f"  -> AVATAR STATUSI: HEALTHY GREEN (Xavf past)")

# --- 2-AI MODEL VA 2-AGENT: Sug'urta narxini dinamik hisoblash ---
# Model 2 uchun ma'lumot (Yoshi, BMI, 1-modeldan chiqqan xavf foizi)
bemor_tahlil_m2 = [[yoshi, bmi, diabet_risk_foizi]]
hisoblangan_badal = model2_insurance.predict(bemor_tahlil_m2)[0]

# Turmush tarzi o'zgargandagi simulyatsiya (Masalan risk foizi 20% ga tushsa)
bemor_tahlil_m2_optimallashgan = [[yoshi, 24.5, 20.0]] # BMI normada, risk past
optimallashgan_badal = model2_insurance.predict(bemor_tahlil_m2_optimallashgan)[0]

print(f"\n💰 2-AGENT REAKSIYASI (Smart Insurance):")
print(f"  -> 2-AI Model tomonidan belgilangan yillik sug'urta badali: ${hisoblangan_badal:.2f}")
print(f"  -> 🔄 RAQAMLI EGIZAK SIMULYATSIYASI (Agar bemor vazn va glyukozani tushirsa):")
print(f"     Yangi optimallashgan sug'urta badali: ${optimallashgan_badal:.2f}")
print(f"     Bemor yiliga tejaydi: ${hisoblangan_badal - optimallashgan_badal:.2f}")
