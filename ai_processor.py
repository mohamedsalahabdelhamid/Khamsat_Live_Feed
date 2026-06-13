import requests
import json
import os
import logging

class AIProcessor:
    def __init__(self, model="llama3"):
        self.model = model
        # Use environment variable for Ollama URL, fallback to localhost for local dev
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.profile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "my_profile.txt")

    def _load_profile(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, "r", encoding="utf-8") as f:
                return f.read()
        return "No profile defined."

    def process_request(self, request_data):
        """
        Takes a single request (title + description) and returns:
        {
           "match_score": 85,
           "recommendation": "Short text why this is good",
           "proposal": "Professional pitch"
        }
        """
        profile = self._load_profile()
        prompt = f"""
أنت مساعد خبير في منصة خمسات. وظيفتك هي تحليل طلب خدمة وكتابة عرض (Proposal) احترافي.

معلومات المتقدم (أنا):
{profile}

تفاصيل الطلب:
العنوان: {request_data.get('title')}
الوصف: {request_data.get('description')}

المطلوب منك هو الرد بتنسيق JSON حصراً يحتوي على:
1. match_score: رقم من 0 لـ 100 يمثل مدى مناسبة الطلب لمهاراتي.
2. recommendation: جملة واحدة تشرح لماذا هذا الطلب مناسب لي أو لا.
3. proposal: عرض احترافي مقنع وجذاب مخصص لهذا العميل باللغة العربية، يبرز مهاراتي المذكورة في ملفي بما يخدم طلبه.

ملاحظة: لا تكتب أي نص خارج الـ JSON. رد بالـ JSON فقط.
"""
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=10 # Reduced timeout for responsiveness
            )
            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", "{}"))
            elif response.status_code == 404:
                return {"error": "Model not found. Please run 'ollama run llama3' first."}
            else:
                return {"error": f"Ollama error: {response.status_code}"}
        except Exception as e:
            logging.error(f"AI Processing error: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Test
    processor = AIProcessor()
    test_req = {"title": "مطلوب مبرمج سكرابنج", "description": "محتاج حد يسحب بيانات من موقع تجارة الكترونية باستخدام بايثون"}
    print(processor.process_request(test_req))
