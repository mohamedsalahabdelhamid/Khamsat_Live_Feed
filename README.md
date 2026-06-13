<div align="center">

# 🚀 Khamsat Deep Scanner PRO

### أداة مراقبة ذكية لطلبات منصة خمسات مع تحليل AI فوري

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[العربية](#-كيف-يعمل) | [Features](#-features)**

</div>

---

## 📸 لقطة شاشة

> لوحة تحكم عصرية بالوضع الداكن مع تحديث فوري وتحليل AI

---

## ✨ المميزات

| الميزة | التفاصيل |
|--------|----------|
| 🔍 **مسح عميق** | يتصفح جميع الطلبات الحديثة في خمسات تلقائياً |
| 🤖 **AI Analysis** | يحلل كل طلب ويعطيه نسبة توافق مع مهاراتك |
| ✍️ **كتابة عروض** | يكتب عرضاً احترافياً لكل طلب تلقائياً |
| ⚡ **Real-time** | تحديث فوري عبر WebSocket بدون تحديث الصفحة |
| 🛡️ **Anti-Ban** | تدوير User-Agent تلقائي للحماية من الحجب |
| 🌙 **Dark/Light Mode** | وضع داكن وفاتح |
| 📱 **Responsive** | يعمل على الجوال والكمبيوتر |

---

## 🛠️ المتطلبات

قبل التشغيل، تأكد من تثبيت:

1. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** - مجاني، يعمل على Windows/Mac/Linux
2. **[Ollama](https://ollama.com/)** - لتشغيل الذكاء الاصطناعي محلياً (مجاني)

---

## 🚀 تشغيل المشروع (خطوتين فقط!)

### الخطوة 1: تجهيز الذكاء الاصطناعي

بعد تثبيت Ollama، افتح Terminal وشغّل:

```bash
ollama pull llama3
```

> ⏳ سيقوم بتحميل نموذج Llama3 (حوالي 4GB) - مرة واحدة فقط

---

### الخطوة 2: تشغيل المشروع

```bash
# 1. استنسخ المشروع
git clone https://github.com/YOUR_USERNAME/khamsat-deep-scanner.git
cd khamsat-deep-scanner

# 2. انسخ ملف الإعدادات
cp .env.example .env        # على Linux/Mac
copy .env.example .env      # على Windows

# 3. اكتب مهاراتك في هذا الملف (مهم جداً!)
notepad data\my_profile.txt    # Windows
nano data/my_profile.txt       # Linux/Mac

# 4. شغّل المشروع
docker compose up -d

# 5. افتح المتصفح
# http://localhost:8080
```

**✅ هو ده! المشروع شغال على http://localhost:8080**

---

## ⚙️ الإعدادات

افتح ملف `.env` لتعديل الإعدادات:

```env
# رابط صفحة الطلبات (لا تغيّره)
KHAMSAT_URL="https://khamsat.com/community/requests"

# كل كم ثانية يتحدث السكرابر (120 = دقيقتان)
SCRAPE_INTERVAL=120

# منفذ الخادم
PORT=8080
```

---

## 📝 تخصيص الملف الشخصي (مهم!)

افتح `data/my_profile.txt` واملأه بمعلوماتك:

```
تخصصي: مبرمج بايثون وخبير تطوير ويب
المهارات: Python, Django, React, PostgreSQL
الخبرة: 4 سنوات في تطوير التطبيقات
نماذج أعمالي: بنيت منصة تجارة إلكترونية بـ 5000 مستخدم
الأسعار: أعمل بأسعار مناسبة تبدأ من 50 دولار
أسلوب الرد: احترافية وودودة
```

> 🔑 كلما كان الملف أكثر تفصيلاً، كلما كانت العروض التي يكتبها AI أفضل!

---

## 🏗️ هيكل المشروع

```
khamsat-deep-scanner/
├── 📄 server.py              # FastAPI server + WebSocket
├── 📄 ai_processor.py        # Ollama AI integration  
├── 📄 run.py                 # Entry point
├── 📄 Dockerfile             # Docker build config
├── 📄 docker-compose.yml     # Docker services
├── 📄 .env.example           # إعدادات نموذجية
├── scraper/
│   ├── 📄 scraper.py         # Playwright scraper
│   ├── 📄 parser.py          # HTML parser
│   └── 📄 storage.py         # JSON data storage
├── frontend/
│   ├── 📄 index.html         # واجهة المستخدم
│   ├── 📄 app.js             # Frontend logic + WebSocket
│   └── 📄 style.css          # التصميم
└── data/
    └── 📄 my_profile.txt     # ملفك الشخصي للـ AI
```

---

## 🔧 أوامر Docker المفيدة

```bash
# عرض اللوغ مباشرة
docker logs khamsat_pro_v2 -f

# إيقاف المشروع
docker compose down

# إعادة تشغيل بعد تعديل الإعدادات
docker compose restart

# تحديث المشروع
git pull
docker compose up -d --build
```

---

## ❓ مشاكل شائعة وحلولها

<details>
<summary><b>الذكاء الاصطناعي لا يعمل أو يظهر "غير متصل"</b></summary>

تأكد من:
1. تثبيت [Ollama](https://ollama.com/) على جهازك
2. تشغيل `ollama pull llama3` في Terminal
3. أن Ollama يعمل: افتح http://localhost:11434 في المتصفح

</details>

<details>
<summary><b>لا تظهر أي طلبات في اللوحة</b></summary>

1. انتظر دقيقتين بعد التشغيل - السكرابر يعمل تلقائياً
2. اضغط زر "تحديث لحظي" في اللوحة
3. تحقق من اللوغ: `docker logs khamsat_pro_v2 -f`

</details>

<details>
<summary><b>المشروع لا يعمل على Windows</b></summary>

1. تأكد أن Docker Desktop يعمل (الأيقونة في شريط المهام)
2. شغّل Command Prompt كـ Administrator
3. تأكد من تفعيل WSL2 في Docker Desktop

</details>

---

## 🤝 المساهمة

المشروع مفتوح المصدر ونرحب بأي مساهمات!

1. Fork المشروع
2. أنشئ branch جديد: `git checkout -b feature/amazing-feature`
3. Commit التغييرات: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. افتح Pull Request

---

## 📜 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

<div align="center">

**صُنع بـ ❤️ للمستقلين العرب على منصة خمسات**

⭐ **إذا أعجبك المشروع، لا تنسى الـ Star!**

</div>
