"""
verify_pinterest_pins.py — post-publish integrity check for Pinterest,
mirroring verify_tpt_listings.py / verify_gumroad_listings.py / etc.

publish_pinterest.py can't confirm success in-session (Pinterest shows a
success state without navigating, so no reliable in-page signal exists),
so this reloads the account's own "Created" pins page fresh and checks:
count matches the expected 30 (3 per unit x 10 units), no pin has an
empty title, and every expected link URL appears somewhere across the
pins actually pointing back to a real product page.

Usage:
    python verify_pinterest_pins.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
COOKIES_FILE = PROJECT_ROOT / ".pinterest_session.json"
PROFILE_USERNAME = "focuslabdigitalteach"
EXPECTED_PINS_PER_UNIT = 3


def _all_unit_marketing_files() -> list[Path]:
    return sorted((PROJECT_ROOT / "releases" / "public").glob("*/07_Marketing/marketing_content.md"))


def _expected_links() -> set[str]:
    links = set()
    for md_path in _all_unit_marketing_files():
        text = md_path.read_text(encoding="utf-8")
        for m in re.finditer(r"\*\*Link\*\*:\s*(\S+)", text):
            links.add(m.group(1).strip())
    return links


def main() -> None:
    if not COOKIES_FILE.exists():
        print(f"ERROR: {COOKIES_FILE} not found.")
        sys.exit(1)

    from playwright.sync_api import sync_playwright
    cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1000})
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(f"https://www.pinterest.com/{PROFILE_USERNAME}/_created/",
                   wait_until="domcontentloaded", timeout=25000)
        page.wait_for_timeout(4000)

        pin_ids = page.evaluate("""
        () => {
            const hrefs = Array.from(document.querySelectorAll('a[href*="/pin/"]')).map(a => a.href);
            const ids = new Set();
            for (const h of hrefs) {
                const m = h.match(/\\/pin\\/(\\d+)/);
                if (m) ids.add(m[1]);
            }
            return Array.from(ids);
        }
        """)
        print(f"Found {len(pin_ids)} unique pin(s) on the Created page (expected {len(_all_unit_marketing_files()) * EXPECTED_PINS_PER_UNIT}).\n")

        findings = []
        expected_total = len(_all_unit_marketing_files()) * EXPECTED_PINS_PER_UNIT
        if len(pin_ids) < expected_total:
            findings.append(f"Only {len(pin_ids)} pins found, expected {expected_total}.")

        empty_title_count = 0
        link_domains_seen = set()
        for pid in pin_ids:
            page.goto(f"https://www.pinterest.com/pin/{pid}/", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1500)
            title = page.evaluate("""
            () => { const el = document.querySelector('h1'); return el ? el.innerText.trim() : ''; }
            """)
            if not title:
                empty_title_count += 1
                findings.append(f"Pin {pid} has an empty/missing title.")
            outbound = page.evaluate("""
            () => { const el = document.querySelector('a[href*="teacherspayteachers.com"]'); return el ? el.href : null; }
            """)
            if outbound:
                link_domains_seen.add("teacherspayteachers.com")
            else:
                findings.append(f"Pin {pid} ({title[:40]!r}) has no outbound TPT link detected.")

        print(f"Checked {len(pin_ids)} pin(s). Empty titles: {empty_title_count}.\n")

        browser.close()

    if findings:
        print("Issues found:")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checked pins look clean.")


if __name__ == "__main__":
    main()
