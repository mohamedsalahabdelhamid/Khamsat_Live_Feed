import os
import sys
import logging
import logging.handlers
import time
import asyncio
from datetime import datetime, timezone

# Ensure scraper package and root directory are on sys.path
_SCRAPER_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_SCRAPER_DIR)
if _SCRAPER_DIR not in sys.path:
    sys.path.insert(0, _SCRAPER_DIR)
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from parser import RequestParser   # local scraper/parser.py
from storage import Storage        # local scraper/storage.py
from ai_processor import AIProcessor # AI integration

# Setup logging with rotation (max 5MB per file, keep 3 backups)
_log_path = os.path.join(_ROOT_DIR, "scraper.log")
_rotating_handler = logging.handlers.RotatingFileHandler(
    _log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        _rotating_handler,
        logging.StreamHandler()
    ]
)

# Configuration
MAX_HOURS = 48 # Scan up to 48 hours back
MAX_PAGES = 50 # High limit to allow deep scrolling
CONCURRENT_REQUESTS = 5 
LISTING_TIMEOUT = 60000
DETAIL_TIMEOUT = 30000

async def scrape_detail_safe(context, url, list_item):
    """Scrape a single detail page with its own tab to avoid interference."""
    page = await context.new_page()
    try:
        logging.info(f"Scraping detail: {url}")
        response = await page.goto(url, wait_until="domcontentloaded", timeout=DETAIL_TIMEOUT)
        await asyncio.sleep(1) # Small breath for rendering
        
        if response and response.status >= 400:
            logging.warning(f"Skipping {url} - HTTP {response.status}")
            return None
            
        # Use our parser (the parser needs to be adapted for async if it uses page methods)
        # But RequestParser methods currently take 'page' object which works for both sync/async 
        # as long as we don't await them. However, Playwright Async Page methods MUST be awaited.
        # Let's check if we need to make a RequestParserAsync.
        
        # Actually, let's just implement the detail parsing here or make RequestParser methods async.
        # I will update RequestParser to be async in the next step.
        data = await RequestParser.parse_request_detail_async(page, url, list_item)
        return data
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None
    finally:
        await page.close()

async def run_scraper(callback=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, ".env")
    load_dotenv(dotenv_path=env_path)

    start_url = os.getenv("KHAMSAT_URL", "https://khamsat.com/community/requests")
    storage = Storage()

    logging.info(f"Starting ASYNC PRO scraper for {start_url}")

    # Step 1: Purge very old requests
    storage.purge_old_requests(max_hours=MAX_HOURS * 2)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Load identity from .env or fallback
        user_agent = os.getenv("SCRAPER_UA", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        
        logging.info(f"Using Identity: {user_agent[:50]}...")
        
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            locale="ar-SA"
        )
        
        page = await context.new_page()
        
        try:
            logging.info(f"Navigating to listing page: {start_url}")
            await page.goto(start_url, wait_until="domcontentloaded", timeout=LISTING_TIMEOUT)
            await asyncio.sleep(3)

            # Step 2: Deep Scroll
            logging.info("Starting deep scroll...")
            last_item_count = 0
            for i in range(MAX_PAGES):
                items = await RequestParser.get_requests_from_list_page_async(page)
                current_count = len(items)
                
                existing_urls = {item['url'] for item in storage.data}
                found_existing = any(item['url'] in existing_urls for item in items[-3:]) 
                
                if found_existing and i > 1: 
                    break
                    
                if current_count == last_item_count:
                    break
                    
                last_item_count = current_count
                load_more_btn = page.locator("#community_loadmore_btn")
                if await load_more_btn.is_visible():
                    await load_more_btn.click()
                    await asyncio.sleep(2)
                else:
                    break

            list_items = await RequestParser.get_requests_from_list_page_async(page)
            logging.info(f"Captured {len(list_items)} items from the list.")

            # Step 4: Filter items
            existing_urls = {item['url'] for item in storage.data}
            items_to_scrape = [item for item in list_items if item['url'] not in existing_urls and RequestParser.is_request_recent(item, max_hours=MAX_HOURS)]
            items_to_scrape = items_to_scrape[:50] 
            
            logging.info(f"Processing {len(items_to_scrape)} new items.")

            # Step 5: Scrape details in parallel chunks
            ai = AIProcessor()
            for i in range(0, len(items_to_scrape), chunk_size := 3):
                chunk = items_to_scrape[i:i + chunk_size]
                tasks = [scrape_detail_safe(context, item['url'], item) for item in chunk]
                results = await asyncio.gather(*tasks)
                
                processed_chunk = []
                for item in results:
                    if not item: continue
                    
                    # AI Enrichment
                    try:
                        analysis = ai.process_request(item)
                        if analysis and not analysis.get('error'):
                            item['ai_analysis'] = analysis
                            logging.info(f"AI matched: {item['title'][:20]} -> {analysis.get('match_score', 0)}%")
                    except Exception as e:
                        logging.warning(f"AI error: {e}")
                    
                    processed_chunk.append(item)
                    if callback:
                        await callback(item) # REAL-TIME CALLBACK

                # Save chunk immediately
                if processed_chunk:
                    storage.save_new_requests(processed_chunk)
                
                if i + chunk_size < len(items_to_scrape):
                    await asyncio.sleep(1)

            logging.info(f"Scraper cycle complete.")

        except Exception as e:
            logging.error(f"Scraper encountered an issue: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
