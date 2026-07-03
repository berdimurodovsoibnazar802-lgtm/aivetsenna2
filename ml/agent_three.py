class ChiefMedicalOfficerAgent:
    def __init__(self):
        print("👨‍⚕️ [3-Agent]: Chief Medical Officer tizimga qo'shildi.")

    def generate_final_treatment_plan(self, bemor_ismi, agent1_data, agent2_data):
        """Ikkala agent ma'lumotlarini yagona tizimga birlashtirish"""
        
        xavf = agent1_data["xavf_foizi"]
        status = agent1_data["status"]
        manba = agent2_data["manba"]
        ilmiy_tavsiya = agent2_data["ilmiy_tavsiya"]

        # Birlashtirilgan yakuniy protokol matni
        final_protocol = f"""
============================================================
🏥 CHIEF MEDICAL OFFICER — YAKUNIY SHAXSIY DAVOLASH REJASI
============================================================
👤 BEMOR: {bemor_ismi}
📊 DIAGNOSTIKA STATUSI: {status}
🎯 METABOLIK XAVF DARAJASI: {xavf:.1f}%

📚 ASOSLANGAN ILMIY TADQIQOT (RAG 2-Agent):
   "{manba}"

📌 KLINIK PROTOKOL VA KUNDALIK KO'RSATMALAR:
1. [TERAPIYA]: {ilmiy_tavsiya}
2. [MONITORING]: Raqamli Egizak (Avatar) vizualizatsiyasidagi qizil zonalarni kamaytirish uchun har 3 kunda glyukoza o'lchansin.
3. [PROGNOZ]: Ko'rsatkichlar normaga tushsa, asoratlar ehtimoli avtomatik ravishda kamayadi.
============================================================
        """
        return final_protocol.strip()
