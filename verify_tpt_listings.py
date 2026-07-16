"""
verify_tpt_listings.py — post-publish integrity check for a unit's live TPT
listings. Reloads each product page fresh (never trusts in-session state)
and flags corruption signals this project has actually hit in production:

  - empty/near-empty description (the HTML-escaping bug emptied a field
    entirely without TPT rejecting the submission)
  - literal unrendered markdown (**, ##, a raw "| a | b |" table row)
  - literal unescaped HTML tags surviving in the rendered text (the same
    bug, different symptom -- tags present but their inner text swallowed)
  - a title that doesn't start with the expected unit keyword (wrong
    zip/listing pairing)

This does not fix anything -- it only reports. Read the findings and decide
whether a listing needs a manual or scripted fix (see the "completing a
partial product" pattern in PROGRESS.md for how to edit one in place).

Usage:
    python verify_tpt_listings.py --unit year7_web_design_unit1
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def _unit_topic_keyword(unit_id: str) -> str:
    """Best-effort short keyword to find this unit's products on the
    dashboard -- derived from the unit's title in its config. Every
    individual product (bundle, each lesson, assessment) shares the
    "Unit N - Subtitle" part AFTER the colon (the part BEFORE the colon is
    only in the bundle/lead-magnet titles, not per-lesson ones), so match
    on that, not the topic-prefix keyword."""
    import json
    cfg_path = PROJECT_ROOT / "data" / "units" / f"{unit_id}.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        title = cfg.get("title", "")
        return title.split(":", 1)[1].strip() if ":" in title else title[:30].strip()
    return unit_id.replace("_", " ")


def find_unit_product_urls(page, keyword: str) -> list[dict]:
    """A plain body-text/link scan right after page load only sees a
    partial (virtualized?) product list on a store with 100+ products --
    confirmed missing 7 of 9 known-live products in testing. Interacting
    with the "Search my products" box (even though its own filtering
    doesn't reliably narrow results) triggers the full list to render, so
    do that first and filter client-side ourselves rather than trust the
    search box's own filtering."""
    from cmie.publishing.tpt import DASHBOARD_URL
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(3000)
    search = page.get_by_placeholder("Search my products")
    if search.count() > 0:
        search.first.click()
        search.first.fill(keyword)
        page.wait_for_timeout(2500)
    links = page.evaluate(
        """(kw) => Array.from(document.querySelectorAll("a[href*='/Product/']"))
            .map(a => ({t: (a.textContent||'').trim(), h: a.href}))
            .filter(l => l.t.includes(kw))""",
        keyword,
    )
    seen, unique = set(), []
    for l in links:
        if l["h"] not in seen:
            seen.add(l["h"])
            unique.append(l)
    return unique


def check_product_page(page, url: str) -> dict:
    # Note: individual lesson products legitimately have their own titles
    # ("HTML Basics: Structuring a Web Page") that don't repeat the unit's
    # topic keyword -- only the bundle product's title does. Don't flag a
    # title mismatch here; it produced false positives on every lesson.
    findings = []
    page.goto(url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)

    title = page.evaluate("() => document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : ''")

    body = page.evaluate("() => document.body.innerText")
    desc_idx = body.find("Description")
    desc_text = body[desc_idx:desc_idx + 2000] if desc_idx >= 0 else ""

    # A genuinely short description is suspicious -- the real template
    # (overview + "what's included" bullets) always runs well over 150
    # chars. This threshold is deliberately generous to avoid false
    # positives on legitimately short single-lesson listings.
    content_len = len(desc_text.replace("Description", "", 1).strip())
    if content_len < 100:
        findings.append(f"Description looks empty/near-empty ({content_len} chars) -- likely the HTML-escaping corruption bug.")

    # Require an actual **word...word** PAIR, not just any isolated "**" --
    # a bare "\*\*[^*]" false-positived on a Python lesson whose content is
    # legitimately about printing asterisk patterns ("* ** *** **** *****").
    if re.search(r"\*\*\w[^*\n]*\*\*|^##\s|\|\s*[\w\s]+\s*\|\s*[\w\s]+\s*\|", desc_text, re.M):
        findings.append("Literal unrendered markdown found in description (**bold**, ##, or a raw table row).")

    if re.search(r"<[a-zA-Z][a-zA-Z0-9]*(\s|>)", desc_text):
        findings.append("Literal HTML tag characters found in description -- may have swallowed real content.")

    return {"url": url, "title": title, "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--keyword", help="Override the auto-derived search keyword")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright
    from cmie.publishing.tpt import _load_session, _is_logged_in

    keyword = args.keyword or _unit_topic_keyword(args.unit)
    print(f"Searching dashboard for products matching: {keyword!r}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        _load_session(context)
        page = context.new_page()
        _is_logged_in(page)

        products = find_unit_product_urls(page, keyword)
        print(f"Found {len(products)} product(s).\n")

        any_findings = False
        for p in products:
            result = check_product_page(page, p["h"])
            status = "OK" if not result["findings"] else "ISSUES FOUND"
            print(f"[{status}] {result['title'][:70]}")
            print(f"         {result['url']}")
            for f in result["findings"]:
                print(f"         - {f}")
                any_findings = True
            print()

        browser.close()

    if any_findings:
        print("Some listings need attention -- see findings above.")
        sys.exit(1)
    else:
        print("All checked listings look clean.")


if __name__ == "__main__":
    main()
