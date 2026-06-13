import logging
import re
from datetime import datetime, timezone, timedelta
from playwright.sync_api import Page


class RequestParser:

    @staticmethod
    async def get_requests_from_list_page_async(page) -> list[dict]:
        """Async version of get_requests_from_list_page."""
        try:
            await page.wait_for_load_state("domcontentloaded")
            results = []
            
            # Use a more resilient selector to find rows
            rows = page.locator("tr.forum_post, tr.topic-list-item, .topic-list-item")
            count = await rows.count()

            logging.info(f"Found {count} potential rows on listing page.")

            for i in range(count):
                try:
                    row = rows.nth(i)
                    
                    # Find any link that looks like a request URL
                    link_els = row.locator("a[href*='/community/requests/']")
                    if await link_els.count() == 0:
                        continue
                        
                    link_el = link_els.first
                    href = await link_el.get_attribute("href") or ""
                    if href.startswith("/"):
                        href = "https://khamsat.com" + href

                    title = (await link_el.inner_text()).strip()
                    publish_time_raw = "N/A"
                    publish_time_iso = None

                    try:
                        # Improved selector to find the timestamp span regardless of screen-size classes
                        time_els = row.locator("span[title], li span[title], .time span[title], td span[title]")
                        if await time_els.count() > 0:
                            time_el = time_els.first
                            gmt_str = await time_el.get_attribute("title") or ""
                            arabic_text = (await time_el.inner_text()).strip()
                            publish_time_raw = arabic_text or gmt_str
                            if gmt_str:
                                publish_time_iso = RequestParser._parse_gmt_to_iso(gmt_str)
                    except Exception as e:
                        logging.warning("Error extracting time: %s", e)

                    comments_count = 0
                    try:
                        reply_els = row.locator(".posts.num, .num.posts, td.posts, .replies, .posts-count")
                        if await reply_els.count() > 0:
                            txt = (await reply_els.first.inner_text()).strip()
                            m = re.search(r"\d+", txt)
                            if m:
                                comments_count = int(m.group())
                    except Exception:
                        pass

                    results.append({
                        "url": href,
                        "title": title,
                        "publish_time_raw": publish_time_raw,
                        "publish_time_iso": publish_time_iso,
                        "comments_count": comments_count,
                    })
                except Exception:
                    continue
            return results
        except Exception as e:
            logging.error(f"Error extracting listing page: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────────
    # Helper: parse Khamsat's GMT datetime string to ISO 8601
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _parse_gmt_to_iso(gmt_str: str) -> str | None:
        """
        Convert Khamsat GMT datetime → ISO 8601 UTC string.
        Handles multiple formats with validation. Returns None on failure.
        """
        if not gmt_str or not isinstance(gmt_str, str):
            return None
        
        gmt_str = gmt_str.strip()
        
        # List of possible formats (DD/MM and MM/DD both attempted)
        formats = [
            "%d/%m/%Y %H:%M:%S GMT",
            "%d/%m/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S GMT",
            "%d-%m-%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S GMT",
            "%m/%d/%Y %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d-%m-%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
        ]
        
        now = datetime.now(timezone.utc)
        min_reasonable = datetime(2020, 1, 1, tzinfo=timezone.utc)
        max_reasonable = now + timedelta(hours=1)  # slight buffer for clock skew
        
        for fmt in formats:
            try:
                dt = datetime.strptime(gmt_str, fmt)
                dt = dt.replace(tzinfo=timezone.utc)
                # Validate date is reasonable
                if dt < min_reasonable or dt > max_reasonable:
                    continue
                return dt.isoformat()
            except ValueError:
                continue
        
        # Try ISO format directly
        try:
            dt = datetime.fromisoformat(gmt_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if min_reasonable <= dt <= max_reasonable:
                return dt.isoformat()
        except Exception:
            pass
        
        return None

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def is_request_recent(item: dict, max_hours: int = 24) -> bool:
        """
        Return True if the request was published within max_hours.
        Prefers ISO datetime; falls back to Arabic relative text.
        """
        iso = item.get("publish_time_iso")
        if iso:
            try:
                dt = datetime.fromisoformat(iso)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                age_hours = (now - dt).total_seconds() / 3600
                return age_hours <= max_hours
            except Exception:
                pass

        # Arabic text fallback
        time_str = str(item.get("publish_time_raw", "")).lower()

        # Definitely OLD keywords (months, years, weeks)
        old_keywords = ["شهر", "شهور", "سنة", "سنوات", "أسبوع", "أسابيع"]
        if any(kw in time_str for kw in old_keywords):
            return False

        # Days → old unless very recent
        day_keywords = ["أمس", "يوم", "يومين", "أيام"]
        if any(kw in time_str for kw in day_keywords):
            return False

        # Hours
        if any(w in time_str for w in ["ساعة", "ساعات", "ساعتين"]):
            m = re.search(r"(\d+)", time_str)
            if m:
                return int(m.group(1)) <= max_hours
            if "ساعتين" in time_str:
                return 2 <= max_hours
            if "ساعة" in time_str:   # singular = 1 hour
                return 1 <= max_hours
            return False

        # Minutes / seconds → always recent
        if any(w in time_str for w in ["دقيقة", "دقائق", "ثانية", "ثوان", "الآن", "لحظات"]):
            return True

        return True  # Unknown format → keep to be safe

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    async def parse_request_detail_async(page, url: str, list_item: dict) -> dict:
        """Async version of parse_request_detail."""
        title = list_item.get("title", "N/A")
        comments_count = list_item.get("comments_count", 0)
        publish_time_iso = list_item.get("publish_time_iso")
        publish_time_raw = list_item.get("publish_time_raw", "N/A")
        publish_time_display = RequestParser._format_publish_time(publish_time_iso) if publish_time_iso else publish_time_raw

        try:
            # ── Description ─────────────────────────────────────────────────
            description = "N/A"
            desc_els = page.locator("article.replace_urls, .replace_urls, .cooked, .post-content")
            if await desc_els.count() > 0:
                description = (await desc_els.first.inner_text()).strip()

            # ── Budget ──────────────────────────────────────────────────────
            budget = "N/A"
            budget_selectors = ["[data-budget]", ".budget-value", ".service-budget", ".meta-item:has-text('الميزانية')"]
            for sel in budget_selectors:
                els = page.locator(sel)
                if await els.count() > 0:
                    budget_text = (await els.first.inner_text()).strip()
                    m = re.search(r'[\d,]+(?:\.\d+)?', budget_text)
                    if m:
                        budget = m.group()
                        break
            
            if budget == "N/A" and description != "N/A":
                budget_match = re.search(r'الميزانية[:\s]*([\d,]+(?:\.\d+)?\s*(?:دولار|ريال|جنيه|درهم)?)', description)
                if budget_match:
                    budget = budget_match.group(1).strip()

            # ── Replies ─────────────────────────────────────────────────────
            comments_data = []
            comment_wrappers = page.locator(".discussion-item.comment, .discussion-item, .comment-item")
            wrapper_count = await comment_wrappers.count()
            
            for j in range(min(wrapper_count, 20)):
                try:
                    wrapper = comment_wrappers.nth(j)
                    text = ""
                    for body_sel in ["article.comment.reply_content.replace_urls", ".reply_content", ".cooked"]:
                        body_els = wrapper.locator(body_sel)
                        if await body_els.count() > 0:
                            text = (await body_els.first.inner_text()).strip()
                            break
                    if text:
                        comments_data.append({"content": text})
                except Exception:
                    continue

            return {
                "title": title,
                "description": description,
                "budget": budget,
                "url": url,
                "publish_time": publish_time_display,
                "publish_time_iso": publish_time_iso,
                "comments_count": max(comments_count, len(comments_data)),
                "comments_data": comments_data,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logging.error(f"Error parsing detail page {url}: {e}")
            return {"url": url, "title": title, "description": "Error", "publish_time": publish_time_display}

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _format_publish_time(raw: str) -> str:
        """Convert ISO UTC datetime to human-readable Arabic time string."""
        if not raw or raw == "N/A":
            return "غير محدد"
        try:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = now - dt
            total_seconds = int(diff.total_seconds())

            if total_seconds < 60:
                return "منذ لحظات"
            elif total_seconds < 3600:
                mins = total_seconds // 60
                return f"منذ {mins} دقيقة"
            elif total_seconds < 86400:
                hours = total_seconds // 3600
                return f"منذ {hours} ساعة"
            else:
                days = total_seconds // 86400
                return f"منذ {days} يوم"
        except Exception:
            return raw
