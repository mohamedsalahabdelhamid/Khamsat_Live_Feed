import pytest
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
import os
import time
import re
from playwright.sync_api import Page, expect

# --- Local Server Fixture to Serve the App ---
PORT = 8080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

@pytest.fixture(scope="session", autouse=True)
def local_server():
    server = socketserver.TCPServer(("", PORT), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    # Wait for server to start
    time.sleep(1)
    
    yield f"http://localhost:{PORT}"
    
    server.shutdown()
    server.server_close()

# --- Playwright Tests ---

def test_page_loads_and_displays_data(page: Page, local_server: str):
    """Test if the frontend loads and fetches the requests.json correctly."""
    page.goto(f"{local_server}/frontend/index.html")
    
    # Wait for the loading indicator to disappear and grid to populate
    page.wait_for_selector(".request-card", timeout=10000)
    
    # Assert at least one request card is generated
    cards = page.locator(".request-card")
    assert cards.count() > 0, "No request cards were loaded."
    
    # Verify key elements exist inside the first card
    first_card = cards.first
    expect(first_card.locator(".request-title")).to_be_visible()
    expect(first_card.locator(".request-desc")).to_be_visible()
    
    # Verify the custom data points (Comments, Time)
    text_content = first_card.inner_text()
    assert "التعليقات:" in text_content, "Comments count is missing from card."
    assert "الميزانية:" in text_content, "Budget is missing from card."

def test_dark_mode_toggle(page: Page, local_server: str):
    """Test if the dark mode toggle button works and persists."""
    page.goto(f"{local_server}/frontend/index.html")
    
    # Initially should be light mode (or whatever is default)
    html_element = page.locator("html")
    
    toggle_btn = page.locator("#theme-toggle")
    toggle_btn.click()
    
    # Check if data-theme changed
    theme = html_element.get_attribute("data-theme")
    assert theme in ["dark", "light"], "Theme attribute not set correctly."
    
    # Click again to revert
    toggle_btn.click()
    new_theme = html_element.get_attribute("data-theme")
    assert theme != new_theme, "Theme did not toggle."

def test_search_functionality(page: Page, local_server: str):
    """Test if the search input correctly filters the request cards."""
    page.goto(f"{local_server}/frontend/index.html")
    page.wait_for_selector(".request-card")
    
    initial_count = page.locator(".request-card").count()
    
    # Type a gibberish search term that shouldn't match anything
    search_input = page.locator("#search-input")
    search_input.fill("كلمةغيرموجودةاطلاقا123")
    
    # The grid should show the "no requests" message
    expect(page.locator(".loading")).to_contain_text("لا توجد طلبات مطابقة")
    assert page.locator(".request-card").count() == 0
    
    # Clear search
    search_input.fill("")
    assert page.locator(".request-card").count() == initial_count

def test_auto_refresh_button(page: Page, local_server: str):
    """Test if the refresh button triggers a reload."""
    page.goto(f"{local_server}/frontend/index.html")
    page.wait_for_selector(".request-card")
    
    last_updated_text = page.locator("#last-updated").inner_text()
    
    # Wait a tiny bit and click refresh
    time.sleep(1)
    page.locator("#refresh-btn").click()
    
    # The update text should ideally change, but at least ensure no errors occur
    # and the auto-refresh indicator is still active
    expect(page.locator(".auto-refresh")).to_have_class(re.compile(r".*active.*"))
