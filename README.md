<div align="center">

# 🚀 Khamsat Deep Scanner PRO

### Smart Monitoring Tool for Khamsat Platform Requests with Instant AI Analysis

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[English](#-features) | [العربية](#-كيف-يعمل)**

</div>

---

## 📸 Screenshot

> Modern dark-mode dashboard featuring real-time updates and instant AI analysis.

---

## ✨ Features

| Feature | Details |
|--------|----------|
| 🔍 **Deep Scan** | Automatically browses all recent requests on Khamsat |
| 🤖 **AI Analysis** | Analyzes each request and calculates a compatibility score based on your skills |
| ✍️ **Proposal Writing** | Automatically drafts a professional proposal for each request |
| ⚡ **Real-time** | Instant updates via WebSockets without needing to refresh the page |
| 🛡️ **Anti-Ban** | Automatic User-Agent rotation to protect against IP blocking/banning |
| 🌙 **Dark/Light Mode** | Seamless dark and light theme support |
| 📱 **Responsive** | Fully optimized for both mobile and desktop screens |

---

## 🛠️ Prerequisites

Before running the project, make sure you have the following installed:

1. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** - Free, available for Windows/Mac/Linux
2. **[Ollama](https://ollama.com/)** - To run the AI models locally (Free)

---

## 🚀 Running the Project (Just 2 Steps!)

### Step 1: Prepare the AI Model

After installing Ollama, open your Terminal and run:

```bash
ollama pull llama3

⏳ This will download the Llama3 model (approx. 4GB) - Required only once.


Step 2: Launch the Project

# 1. Clone the repository
git clone [https://github.com/YOUR_USERNAME/khamsat-deep-scanner.git](https://github.com/YOUR_USERNAME/khamsat-deep-scanner.git)
cd khamsat-deep-scanner

# 2. Copy the environment configuration file
cp .env.example .env        # For Linux/Mac
copy .env.example .env      # For Windows

# 3. Add your skills to this file (Very Important!)
notepad data\my_profile.txt    # Windows
nano data/my_profile.txt       # Linux/Mac

# 4. Run the project using Docker
docker compose up -d

# 5. Open your browser
# http://localhost:8080



⚙️ Configuration
Open the .env file to customize your settings:

# URL for the requests page (Do not change)
KHAMSAT_URL="[https://khamsat.com/community/requests](https://khamsat.com/community/requests)"

# Scraper update interval in seconds (120 = 2 minutes)
SCRAPE_INTERVAL=120

# Server port
PORT=8080


📝 Profile Customization (Important!)
Open data/my_profile.txt and fill it with your professional details:

Specialization: Python Developer & Web Development Expert
Skills: Python, Django, React, PostgreSQL
Experience: 4 years in application development
Portfolio/Projects: Built an e-commerce platform with 5,000 active users
Pricing: Offers competitive rates starting from $50
Communication Style: Professional and friendly

🔑 The more detailed this file is, the more accurate and tailored the AI-generated proposals will be!

🏗️ Project Structure

khamsat-deep-scanner/
├── 📄 server.py              # FastAPI server + WebSocket
├── 📄 ai_processor.py        # Ollama AI integration  
├── 📄 run.py                 # Entry point
├── 📄 Dockerfile             # Docker build config
├── 📄 docker-compose.yml     # Docker services
├── 📄 .env.example           # Example settings template
├── scraper/
│   ├── 📄 scraper.py         # Playwright scraper
│   ├── 📄 parser.py          # HTML parser
│   └── 📄 storage.py         # JSON data storage
├── frontend/
│   ├── 📄 index.html         # User Interface
│   ├── 📄 app.js             # Frontend logic + WebSocket
│   └── 📄 style.css          # UI Styling
└── data/
    └── 📄 my_profile.txt     # Your personal profile for the AI



🔧 Useful Docker Commands

# View live logs
docker logs khamsat_pro_v2 -f

# Stop the project
docker compose down

# Restart after modifying settings
docker compose restart

# Update the project
git pull
docker compose up -d --build


❓ Troubleshooting & FAQ
Make sure that:

Ollama is installed and running on your machine.

You have successfully executed ollama pull llama3 in the terminal.

Ollama is accessible: Open http://localhost:11434 in your browser to verify.

Wait for 2 minutes after launching - the scraper runs automatically on an interval.

Click the "Instant Refresh" button on the dashboard.

Check the logs for errors: docker logs khamsat_pro_v2 -f

Ensure Docker Desktop is running (check the system tray icon).

Open your Command Prompt or PowerShell as Administrator.

Verify that WSL2 is enabled in your Docker Desktop settings.

🤝 Contributing
This project is open-source, and contributions are highly welcome!

Fork the project

Create a new branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add amazing feature'

Push to the branch: git push origin feature/amazing-feature

Open a Pull Request

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

Made with ❤️ for Arab Freelancers on the Khamsat Platform

⭐ If you like this project, don't forget to give it a Star!

