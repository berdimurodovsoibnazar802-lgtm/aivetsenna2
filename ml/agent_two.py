import json

class MedicalResearcherAgent:
    def __init__(self, database_path='medical_papers.json'):
        """Lokal tibbiy ilmiy maqolalar bazasini yuklash (RAG asosi)"""
        try:
            with open(database_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
            print("🔬 [2-Agent]: Tibbiy ilmiy maqolalar bazasi (RAG) yuklandi.")
        except FileNotFoundError:
            print("❌ [2-Agent] Xatolik: 'medical_papers.json' topilmadi!")
            self.database = []

    def search_latest_research(self, status_text):
        """Bemorning holatiga qarab bazadan eng so'nggi tadqiqotni qidirib topish"""
        # Oddiy Semantic/Keyword qidiruv mantiqi (RAG Retrieval)
        for paper in self.database:
            if paper["kasallik"].lower() in status_text.lower():
                return {
                    "manba": paper["maqola_nomi"],
                    "ilmiy_tavsiya": paper["tibbiy_tavsiya"]
                }
        
        return {
            "manba": "Umumiy tibbiy qo'llanma",
            "ilmiy_tavsiya": "Standart sog'lom turmush tarzi qoidalariga rioya qilish."
        }

# Agentni alohida tekshirish uchun test qismi:
if __name__ == "__main__":
    researcher = MedicalResearcherAgent()
    # 1-agentdan "Xavfli (Diabet / Giperglikemiya asoratlari)" degan status keldi deb tasavvur qilamiz
    topilgan_ilm = researcher.search_latest_research("XAVFLI (Diabet / Giperglikemiya asoratlari)")
    print(f"\n🔎 Topilgan ilmiy manba: {topilgan_ilm['manba']}")
    print(f"📖 Ilmiy tavsiya: {top完整_ilm['ilmiy_tavsiya']}")
