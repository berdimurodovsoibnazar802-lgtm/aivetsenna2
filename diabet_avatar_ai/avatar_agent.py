import os
import joblib
import numpy as np

print("🚀 Multi-Agent Ekotizimi ishga tushmoqda...\n")

# =====================================================================
# 1. LOKAL SERVERDAGI MODELNI YUKLASH
# =====================================================================
try:
    # Model obyektini yuklab olamiz
    model = joblib.load('diabet_detector_model.pkl')
    print("🧠 Lokal AI model muvaffaqiyatli yuklandi!\n")
except FileNotFoundError:
    print("❌ Xatolik: 'diabet_detector_model.pkl' fayli topilmadi.")
    print("Iltimos, fayl shu papkada yoki yo'li to'g'ri ko'rsatilganini tekshiring!")
    exit()

# =====================================================================
# 2. AVATAR COORDINATOR AGENT KLASSI
# =====================================================================
class AvatarCoordinatorAgent:
    # ai_model=model qo'yildi: qavs ichi bo'sh qolsa ham tepdagi modelni avtomatik oladi
    def __init__(self, ai_model=model):
        self.model = ai_model

    def process_patient_and_generate_avatar(self, bemor_ismi, tahlillar):
        # Tahlillarni model tushunadigan shaklga keltiramiz (2D array)
        input_data = np.array([tahlillar])
        
        # Lokal model orqali xavfni aniqlaymiz (0 yoki 1)
        xavf_prediction = self.model.predict(input_data)[0]
        
        # Modelning qanchalik ishonchi komilligi (foizda)
        xavf_probability = self.model.predict_proba(input_data)[0][xavf_prediction] * 100

        # Avatar uchun vizual prompt logikasi
        prompt_base = f"A highly detailed 3D digital twin avatar of a patient named {bemor_ismi}, composed of glowing holographic wireframes and neural network lines."

        if xavf_prediction == 1:
            # Agar model diabet/asorat xavfi yuqori deb topsa
            visual_prompt = f"""
            {prompt_base} 
            The avatar is illuminated in WARNING ORANGE AND CRITICAL RED colors. 
            The internal organs, specifically the kidneys and cardiovascular circulatory system, are pulsating with high-stress chaotic red light filaments, indicating advanced metabolic danger. 
            A futuristic digital UI matrix display above the avatar shows: 'DIABETES RISK ALERT: {xavf_probability:.1f}%' in clean tech typography. Dark background, cyberpunk medical interface style.
            """
            status = "XAVFLI (Giperglikemiya / Organlar zo'riqishi)"
        else:
            # Agar model tahlillarni xavfsiz deb topsa
            visual_prompt = f"""
            {prompt_base} 
            The avatar is glowing with HEALTHY CYAN AND EMERALD GREEN light. 
            The entire biological grid is harmonious, balanced, and calm, showing stable metabolic functions. 
            The futuristic UI display above the avatar calmly shows: 'SYSTEM STATUS: STABLE (Diabetic Risk: {100 - xavf_probability:.1f}%)'. Clean clinical presentation, dark background.
            """
            status = "SOG'LOM / STABIL"

        return status, visual_prompt, xavf_probability

# =====================================================================
# 3. AGENTLARNI ISHGA TUSHIRISH (TEST MATRIX)
# =====================================================================

# TO'G'RILANDI: Agent obyektini yaratishda yuklangan 'model' argument sifatida berildi
agent1 = AvatarCoordinatorAgent(ai_model=model)

# Test uchun bemor ma'lumotlari
bemor_ismi = "Otabek"
# Ustunlar: [Homiladorlik, Glyukoza, Qon_bosimi, Teri_qalinligi, Insulin, BMI_Vazn, Diabet_Pedigree, Yoshi]
yangi_bemor_tahlili = [2, 168, 85, 25, 0, 38.2, 0.78, 45] 

print(f"📊 {bemor_ismi}ning tahlillari lokal AI modelga yuborilmoqda...")

# Agentni ishga tushiramiz
status, prompt, foiz = agent1.process_patient_and_generate_avatar(bemor_ismi, yangi_bemor_tahlili)

# Natijalarni konsolga chiroyli chiqarish
print("\n" + "="*60)
print(f"🤖 AGENT DIAGNOSTIKASI: {status}")
print(f"🎯 Model ishonchliligi: {foiz:.1f}%")
print("="*60)
print("\n🎨 VIZUAL AVATAR PROMPT (Frontend / Midjourney / DALL-E uchun):")
print(prompt.strip())
print("="*60)