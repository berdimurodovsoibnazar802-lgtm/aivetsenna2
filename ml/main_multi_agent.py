import joblib
# Hamma agentlarni loyihamizga chaqiramiz
from avatar_agent import AvatarCoordinatorAgent
from agent_two import MedicalResearcherAgent
from agent_three import ChiefMedicalOfficerAgent

print("🚀 Multi-Agent Ekotizimi ishga tushmoqda...\n")

# =====================================================================
# 0. MODELNI YUKLASH (1-agent ishlashi uchun majburiy)
# =====================================================================
try:
    ml_model = joblib.load('diabet_detector_model.pkl')
    print("🧠 [Tizim]: ML Model muvaffaqiyatli yuklandi.")
except FileNotFoundError:
    print("❌ Xatolik: 'diabet_detector_model.pkl' topilmadi. Avval modelni yuklang!")
    exit()

# Agentlarni klonlashtiramiz (yaratamiz) va modelni yuklaymiz
agent1 = AvatarCoordinatorAgent(ai_model=ml_model)
agent2 = MedicalResearcherAgent()
agent3 = ChiefMedicalOfficerAgent()

# Shifokor kiritgan bemor ma'lumotlari va tahlillari
bemor_ismi = "Otabek"
# [Homiladorlik, Glyukoza, Qon_bosimi, Teri_qalinligi, Insulin, BMI_Vazn, Diabet_Pedigree, Yoshi]
yangi_bemor_tahlili = [2, 172, 88, 27, 0, 37.1, 0.82, 46] 

print(f"\n⚡️ [QADAM 1]: 1-Agent bemor tahlillarini diagnostika qilmoqda...")
# TO'G'RILANDI: Funksiya nomi asl holatiga qaytarildi va qaytgan 3 ta qiymat qabul qilindi
status, visual_prompt, foiz = agent1.process_patient_and_generate_avatar(bemor_ismi, yangi_bemor_tahlili)

# 3-Agent aynan dictionary (lug'at) kutgani uchun ma'lumotlarni paketlaymiz
agent1_paketi = {
    "status": status,
    "xavf_foizi": foiz,
    "prompt": visual_prompt
}

print(f"\n⚡️ [QADAM 2]: 2-Agent ilmiy maqolalar bazasidan (RAG) qidirmoqda...")
# 2-Agent 1-agentning natijasiga qarab ilmiy maqola qidiradi
agent2_natija = agent2.search_latest_research(agent1_paketi["status"])

print(f"\n⚡️ [QADAM 3]: 3-Agent hamma ma'lumotni birlashtirib, yakuniy protokol tayyorlamoqda...")
# TO'G'RILANDI: Shubhali 'if-else' olib tashlandi, paketlangan toza ma'lumotlar uzatildi
yakuniy_hisobot = agent3.generate_final_treatment_plan(
    bemor_ismi=bemor_ismi, 
    agent1_data=agent1_paketi, 
    agent2_data=agent2_natija
)

# Natijani terminalga chiqaramiz
print("\n" + yakuniy_hisobot)