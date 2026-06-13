import json
import os
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict

class Storage:
    def __init__(self, filepath: str = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "data", "requests.json")
        self.filepath = filepath
        self._ensure_dir()
        self.data = self._load()

    def _ensure_dir(self):
        directory = os.path.dirname(self.filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _load(self) -> List[Dict]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error(f"Error decoding {self.filepath}, starting fresh.")
                return []
        return []

    def _is_recent(self, item: Dict, max_hours: int = 24) -> bool:
        """
        Return True if the request is recent enough to keep.
        Priority:
          1. publish_time_iso  — accurate UTC publish timestamp (always preferred)
          2. scraped_at        — when the scraper ran (fallback)
          3. Arabic text parse — last-resort heuristic
        """
        # ── 1. ISO publish time (most accurate) ──────────────────────────────
        iso = item.get("publish_time_iso")
        if iso:
            try:
                dt = datetime.fromisoformat(iso)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                return age_h <= max_hours
            except Exception:
                pass

        # ── 2. scraped_at fallback ────────────────────────────────────────────
        scraped_at = item.get("scraped_at", "")
        if scraped_at:
            try:
                dt = datetime.fromisoformat(scraped_at)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                return age_h <= max_hours
            except Exception:
                pass

        # ── 3. Arabic text heuristic (legacy data only) ───────────────────────
        time_str = str(item.get("publish_time", ""))
        old_keywords = ["أمس", "يوم", "أيام", "شهر", "شهور", "سنة", "سنوات", "يومين", "أسبوع"]
        if any(kw in time_str for kw in old_keywords):
            return False
        if any(w in time_str for w in ["ساعة", "ساعات", "ساعتين"]):
            match = re.search(r"(\d+)", time_str)
            if match:
                return int(match.group(1)) <= max_hours
            if "ساعتين" in time_str:
                return 2 <= max_hours
            return True # singular hour
        if any(w in time_str for w in ["دقيقة", "دقائق", "ثانية", "ثوانٍ"]):
            return True

        return True  # unknown → keep
    
    def purge_old_requests(self, max_hours: int = 24):
        """Remove old requests from the stored data and rewrite the file."""
        before = len(self.data)
        self.data = [item for item in self.data if self._is_recent(item, max_hours)]
        after = len(self.data)
        removed = before - after
        if removed > 0:
            logging.info(f"Purged {removed} old requests from storage (older than {max_hours}h).")
            self._write()
        else:
            logging.info("No old requests to purge.")

    def _write(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Failed to write data: {e}")

    def _is_valid_request(self, req: Dict) -> bool:
        """Validate that a request has the minimum required fields."""
        if not req or not isinstance(req, dict):
            return False
        url = req.get('url')
        title = req.get('title')
        # URL must be present and contain khamsat domain
        if not url or not isinstance(url, str) or 'khamsat.com' not in url:
            return False
        # Title must be present and not empty
        if not title or not isinstance(title, str) or not title.strip():
            return False
        return True

    def save_new_requests(self, new_requests: List[Dict]):
        existing_urls = {item.get('url') for item in self.data}
        added_count = 0
        skipped_count = 0

        for req in new_requests:
            if not self._is_valid_request(req):
                skipped_count += 1
                continue
            if req.get('url') not in existing_urls:
                self.data.append(req)
                added_count += 1

        if skipped_count > 0:
            logging.warning(f"Skipped {skipped_count} invalid requests (missing url/title).")

        if added_count > 0:
            try:
                self._write()
                logging.info("Successfully saved %d new requests to %s.", added_count, self.filepath)
            except Exception as e:
                logging.error("Failed to save data: %s", e)
        else:
            logging.info("No new requests to save. All scraped items are already in storage.")
