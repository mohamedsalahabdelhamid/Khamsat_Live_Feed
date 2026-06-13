import asyncio
import json
import logging
import logging.handlers
import os
import random
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Add root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.scraper import run_scraper
from scraper.storage import Storage

# ─── Logging Setup (with rotation) ────────────────────────────────────────────
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraper.log")
rotating_handler = logging.handlers.RotatingFileHandler(
    log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[rotating_handler, logging.StreamHandler()],
)

# ─── Constants ─────────────────────────────────────────────────────────────────
PORT = int(os.getenv("PORT", 8080))
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 120))  # seconds
API_KEY = os.getenv("API_KEY", "")  # Optional API key protection

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ─── State ─────────────────────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self.active_connections.discard(websocket)  # ✅ discard لا يرمي خطأ

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return

        data = json.dumps(message, ensure_ascii=False)
        dead_connections = set()

        async with self._lock:
            connections_snapshot = set(self.active_connections)

        for connection in connections_snapshot:
            try:
                await connection.send_text(data)
            except Exception:
                dead_connections.add(connection)

        # Remove dead connections
        if dead_connections:
            async with self._lock:
                self.active_connections -= dead_connections


manager = ConnectionManager()
_scraper_lock = asyncio.Lock()
is_scraping = False


# ─── Helper Functions ───────────────────────────────────────────────────────────
async def notify_new_item(item: dict):
    """Callback for the scraper to notify clients about new items."""
    await manager.broadcast(
        {"type": "new_item", "data": item, "timestamp": datetime.now().isoformat()}
    )


async def background_scraper_loop():
    """Runs the scraper on a fixed interval. Guarantees is_scraping is always reset."""
    global is_scraping
    logging.info("Starting background scraper loop...")
    while True:
        if not is_scraping:
            async with _scraper_lock:
                if is_scraping:  # double-check after acquiring lock
                    await asyncio.sleep(SCRAPE_INTERVAL)
                    continue
                is_scraping = True

            try:
                await manager.broadcast({"type": "status", "msg": "Scraping started..."})
                await run_scraper(callback=notify_new_item)
                await manager.broadcast(
                    {
                        "type": "status",
                        "msg": "Scraping complete.",
                        "last_updated": datetime.now().strftime("%H:%M:%S"),
                    }
                )
            except Exception as e:
                logging.error(f"Error in scraper loop: {e}")
                await manager.broadcast({"type": "status", "msg": f"خطأ في السكرابر: {str(e)[:100]}"})
            finally:
                is_scraping = False  # ✅ يُنفّذ دائماً حتى عند الخطأ

        await asyncio.sleep(SCRAPE_INTERVAL)


def update_identity(new_ua: str):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    with open(env_path, "w", encoding="utf-8") as f:
        found = False
        for line in lines:
            if line.startswith("SCRAPER_UA="):
                f.write(f'SCRAPER_UA="{new_ua}"\n')
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f'SCRAPER_UA="{new_ua}"\n')


# ─── Optional API Key Auth ──────────────────────────────────────────────────────
async def verify_api_key(x_api_key: str = None):
    """If API_KEY is set in .env, all mutation endpoints require it."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key.")


# ─── Lifespan (replaces deprecated on_event) ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(background_scraper_loop())
    yield
    # Shutdown (no-op for now)


app = FastAPI(title="Khamsat Pro Dashboard", lifespan=lifespan)

# ─── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ─── API Endpoints ──────────────────────────────────────────────────────────────
@app.get("/api/data")
async def get_data():
    storage = Storage()
    return sorted(storage.data, key=lambda x: x.get("scraped_at", ""), reverse=True)


@app.get("/api/status")
async def get_status():
    """Returns the current scraper status and AI availability."""
    ollama_ok = False
    try:
        import requests as req_lib
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        base = ollama_url.rsplit("/api/", 1)[0]
        r = req_lib.get(f"{base}/api/tags", timeout=2)
        ollama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "is_scraping": is_scraping,
        "ai_available": ollama_ok,
        "scrape_interval": SCRAPE_INTERVAL,
        "server_time": datetime.now().strftime("%H:%M:%S"),
    }


@app.get("/api/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    global is_scraping
    if is_scraping:
        return {"status": "busy", "msg": "السكرابر يعمل بالفعل"}

    async def run_once():
        global is_scraping
        is_scraping = True
        try:
            await run_scraper(callback=notify_new_item)
        finally:
            is_scraping = False

    background_tasks.add_task(run_once)
    return {"status": "started"}


@app.get("/api/change_identity")
async def change_identity():
    new_ua = random.choice(USER_AGENTS)
    update_identity(new_ua)
    name = (
        "Mobile Safari (iPhone)"
        if "iPhone" in new_ua
        else "Chrome Desktop (Windows)"
        if "Windows" in new_ua
        else "Android Chrome"
    )
    return {"status": "updated", "new_identity": name}


# ─── WebSocket Endpoint ─────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        await manager.disconnect(websocket)


# ─── Static Files ───────────────────────────────────────────────────────────────
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")


@app.get("/favicon.ico")
async def favicon():
    fav_path = "frontend/assets/favicon.ico"
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return FileResponse("frontend/index.html")  # fallback


# ─── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🚀 Khamsat Pro Dashboard running at http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
