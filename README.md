<div align="center">

# 🚀 Khamsat Deep Scanner PRO

### Smart Monitoring Tool for Khamsat Platform with Instant AI Analysis

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[English](#-features) | [العربية](README_AR.md)**

</div>

---

## 📸 Screenshot

> Modern dark mode dashboard featuring real-time updates and instant AI analysis

---

## ✨ Features

| Feature | Details |
|--------|----------|
| 🔍 **Deep Scanning** | Automatically browses and tracks all recent requests on Khamsat |
| 🤖 **AI Analysis** | Analyzes each request and calculates its compatibility score with your skills |
| ✍️ **Proposal Generation** | Automatically writes highly professional proposals customized for each request |
| ⚡ **Real-time Updates** | Instant data streaming via WebSocket without needing to refresh the page |
| 🛡️ **Anti-Ban System** | Implements automatic User-Agent rotation to prevent IP blocking |
| 🌙 **Dark/Light Mode** | Seamless transition between beautiful dark and light themes |
| 📱 **Fully Responsive** | Optimized to work flawlessly on both desktop and mobile devices |

---

## 🛠️ Requirements

Before running the project, ensure you have the following installed:

1. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** - Free, works across Windows, Mac, and Linux
2. **[Ollama](https://ollama.com/)** - To run the AI models locally for free

---

## 🚀 Getting Started (Only 2 Steps!)

### Step 1: Set Up the AI Model

After installing Ollama, open your terminal and run:

```bash
ollama pull llama3
# 1. Clone the repository
git clone [https://github.com/YOUR_USERNAME/khamsat-deep-scanner.git](https://github.com/YOUR_USERNAME/khamsat-deep-scanner.git)
cd khamsat-deep-scanner

# 2. Copy the environment configuration file
cp .env.example .env         # For Linux/Mac
copy .env.example .env       # For Windows

# 3. Write your professional skills into this file (Crucial step!)
notepad data\my_profile.txt    # Windows
nano data/my_profile.txt       # Linux/Mac

# 4. Launch the project using Docker
docker compose up -d

# 5. Open your browser
# Go to http://localhost:8080
# Target URL for community requests (Do not change)
KHAMSAT_URL="[https://khamsat.com/community/requests](https://khamsat.com/community/requests)"

# Scraper refresh interval in seconds (120 = 2 minutes)
SCRAPE_INTERVAL=120

# Server port configuration
PORT=8080
Role: Python Developer & Web Development Expert
Skills: Python, Django, React, PostgreSQL
Experience: 4 years of developing scalable web applications
Portfolio: Built an e-commerce platform with over 5,000 active users
Pricing: Offers competitive pricing starting from $50
Communication Style: Professional, welcoming, and objective
khamsat-deep-scanner/
├── 📄 server.py              # FastAPI server + WebSocket management
├── 📄 ai_processor.py        # Ollama AI model integration  
├── 📄 run.py                 # Application entry point
├── 📄 Dockerfile             # Docker container build config
├── 📄 docker-compose.yml     # Docker services composition
├── 📄 .env.example           # Template configuration file
├── scraper/
│   ├── 📄 scraper.py         # Playwright-based web scraper
│   ├── 📄 parser.py          # HTML parser and extractor
│   └── 📄 storage.py         # JSON data storage engine
├── frontend/
│   ├── 📄 index.html         # User Interface layout
│   ├── 📄 app.js             # Frontend client logic + WebSocket handler
│   └── 📄 style.css          # UI styles and layout design
└── data/
    └── 📄 my_profile.txt     # User profile data for AI context
# View real-time container logs
docker logs khamsat_pro_v2 -f

# Stop the project services
docker compose down

# Restart services after editing configurations
docker compose restart

# Pull latest updates and rebuild the project
git pull
docker compose up -d --build
