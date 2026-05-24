import re
from typing import List, Dict
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright

from .base import BaseConnector
from ..config import USER_AGENT


class TPTConnector(BaseConnector):
    marketplace = "tpt"
    BASE_SEARCH_URL = "https://www.teacherspayteachers.com/Browse/Search"

    def _fetch_html_playwright(self, url: str) -> str:
        """
        Use Playwright to render the JS page and return full HTML.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(url, wait_until="networkidle")
            html = page.content()
            browser.close()
            return html

    def fetch_listings(self, query: str, page: int = 1) -> List[Dict]:
        params = {
            "search": query,
            "page": page,
        }

        url = f"{self.BASE_SEARCH_URL}?{urlencode(params)}"

        html = self._fetch_html_playwright(url)
        soup = self.html_parser(html)

        listings: List[Dict] = []
        seen_ids = set()

        # Grab all product links that point to /Product/
        product_links = soup.select('a[href*="/Product/"]')

        for link in product_links:
            href = link.get("href") or ""
            title = link.get_text(strip=True)

            if not href or not title:
                continue

            # Normalise URL
            if href.startswith("/"):
                product_url = "https://www.teacherspayteachers.com" + href
            else:
                product_url = href

            # Extract ID-like suffix (digits at the end if present)
            m_id = re.search(r"(\d+)$", product_url)
            external_id = m_id.group(1) if m_id else product_url

            # Avoid duplicates
            if external_id in seen_ids:
                continue
            seen_ids.add(external_id)

            # Try to find a nearby price in the same container
            price = None
            currency = "USD"

            card = link.find_parent("article") or link.find_parent("div")
            if card:
                text = card.get_text(" ", strip=True)
                m_price = re.search(r"\$(\d+(?:\.\d+)?)", text)
                if m_price:
                    try:
                        price = float(m_price.group(1))
                    except ValueError:
                        price = None

            listings.append(
                {
                    "marketplace": self.marketplace,
                    "external_id": external_id,
                    "url": product_url,
                    "title": title,
                    "author": None,
                    "description": None,
                    "subject_raw": None,
                    "grade_levels_raw": None,
                    "resource_type_raw": None,
                    "price": price,
                    "currency": currency,
                    "rating_avg": None,
                    "rating_count": None,
                    "is_bundle": False,
                    "has_video_preview": False,
                    "is_editable": False,
                    "has_standards_alignment": False,
                }
            )

        return listings
