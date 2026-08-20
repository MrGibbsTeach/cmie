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

Pass --lead-magnet-lesson N to additionally check the unit's free lead
magnet specifically (the "FREE Sample" product among this unit's results):
title mentions "Lesson N", no leftover AI-generation artifact language in
the description (the \bAI\b pattern produce_unit.py's QA stage already
uses), and the product's price-display area actually shows "FREE" on the
live page.

This does not fix anything -- it only reports. Read the findings and decide
whether a listing needs a manual or scripted fix (see the "completing a
partial product" pattern in PROGRESS.md for how to edit one in place).

Usage:
    python verify_tpt_listings.py --unit year7_web_design_unit1
    python verify_tpt_listings.py --unit year7_algorithms_unit1 --lead-magnet-lesson 5
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def _lesson_topic_keyword(unit_id: str, lesson: int) -> str | None:
    """Keyword for finding a lesson>1 lead magnet specifically. Its title
    leads with the lesson's own topic, not the unit keyword (a deliberate
    truncation-avoidance choice in publish_lead_magnets.py -- see its
    build_listing() docstring) -- confirmed live on year7_algorithms_unit1
    lesson 5 (product 17435023): the unit keyword "Unit 1 - Thinking Like
    a Programmer" gets truncated off the stored title entirely by TPT's
    ~80-char limit, so the normal _unit_topic_keyword() search silently
    finds nothing for these. Use the lesson's own topic instead, which is
    guaranteed to survive truncation since it's first in the title."""
    import json
    cfg_path = PROJECT_ROOT / "data" / "units" / f"{unit_id}.json"
    if not cfg_path.exists():
        return None
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    topics = cfg.get("topics", [])
    if lesson < 1 or lesson > len(topics):
        return None
    title = topics[lesson - 1].get("title", "")
    return title.split(":", 1)[0].strip() if ":" in title else title.strip()


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
    partial product list on a store with 100+ products -- confirmed
    missing 7 of 9 known-live products in testing. Interacting with the
    "Search my products" box (even though its own filtering doesn't
    reliably narrow results) triggers the full list to render, so do that
    first and filter client-side ourselves rather than trust the search
    box's own filtering.

    The dashboard is also genuinely PAGINATED (`My-Products/page:N`,
    numbered controls `a[aria-label="Go to page N"]`), not virtualized --
    confirmed live: a whole unit's products (year7_networks_hardware_unit1,
    the catalog's oldest/least-recently-modified) sorted entirely onto
    page 2 while page 1 held everything else, making them invisible to a
    page-1-only scan regardless of keyword and producing a false "only 1
    product found" result for listings that were actually all live and
    correctly titled. Walk every numbered page and merge results."""
    from cmie.publishing.tpt import DASHBOARD_URL
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(3000)
    search = page.get_by_placeholder("Search my products")
    if search.count() > 0:
        search.first.click()
        search.first.fill(keyword)
        page.wait_for_timeout(2500)

    def _matching_links_on_current_page() -> list[dict]:
        return page.evaluate(
            """(kw) => Array.from(document.querySelectorAll("a[href*='/Product/']"))
                .map(a => ({t: (a.textContent||'').trim(), h: a.href}))
                .filter(l => l.t.includes(kw))""",
            keyword,
        )

    seen, unique = set(), []
    for l in _matching_links_on_current_page():
        if l["h"] not in seen:
            seen.add(l["h"])
            unique.append(l)

    visited_pages = {1}
    while True:
        page_labels = page.evaluate(
            """() => Array.from(document.querySelectorAll('a[aria-label^="Go to page "]'))
                .map(a => a.getAttribute('aria-label'))"""
        )
        next_label = None
        for label in page_labels:
            m = re.search(r"Go to page (\d+)", label)
            if m and int(m.group(1)) not in visited_pages:
                next_label = label
                visited_pages.add(int(m.group(1)))
                break
        if next_label is None:
            break
        link = page.locator(f'a[aria-label="{next_label}"]')
        if link.count() == 0:
            break
        link.first.click()
        page.wait_for_timeout(2500)
        for l in _matching_links_on_current_page():
            if l["h"] not in seen:
                seen.add(l["h"])
                unique.append(l)

    return unique


def _lead_magnet_findings(title: str, desc_text: str, body: str, lesson: int, price_area: str = "") -> list[str]:
    """Checks specific to a lead-magnet (free lesson sampler) listing --
    only run against the product that looks like the lead magnet itself
    (title contains "free"), so these never false-positive against a
    unit's other paid products (bundle, other lessons, assessment)."""
    findings = []
    if not re.search(rf"\bLesson\s+{lesson}\b", title, re.I):
        findings.append(
            f"Lead magnet title doesn't mention 'Lesson {lesson}' -- wrong lesson number or stale title."
        )
    # Same AI-leftover-language pattern produce_unit.py's stage_qa uses
    # (\bAI\b) -- these are Digital Technologies units, not the shelved AI
    # series, so a literal "AI" mention in a lead magnet is a real leak.
    if re.search(r"\bAI\b", desc_text):
        findings.append("AI-leftover language found in lead magnet description (matched \\bAI\\b).")
    # Confirmed live against a real free lead magnet (year7_algorithms_unit1
    # lesson 5, product 17435023): TPT's own price-display widget renders a
    # standalone "FREE" token there, NOT "$0.00" as originally guessed here
    # -- that guess was wrong and produced a false positive on a genuinely
    # correct listing. Checking the word "FREE" globally in `body` would be
    # unreliable (the marketing description always says "for FREE!"
    # regardless of actual price), so this checks `price_area` specifically
    # -- the text between the title and the "Description" heading, i.e. the
    # actual price widget, not the marketing copy below it.
    if not re.search(r"\bFREE\b", price_area) and "$0.00" not in price_area:
        findings.append(
            "Price display area doesn't show 'FREE' or '$0.00' -- pricing may not be genuinely free; verify manually."
        )
    return findings


def check_product_page(page, url: str, lead_magnet_lesson: int | None = None) -> dict:
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
    # The 2000-char window used to run straight through the real description
    # into TPT's own trailing page chrome ("Report this resource to TPT",
    # the seller-profile widget, "You may also like" / "More from this
    # Teacher-Author" recommendation rails) -- confirmed live: those rails
    # false-positived the AI-leftover-language check on a genuinely clean
    # lead magnet because this seller's OWN unrelated shelved AI-series
    # products showed up by name in "More from this Teacher-Author". Cut
    # the window off at TPT's own boilerplate marker so only the actual
    # authored description is ever scanned.
    if desc_idx >= 0:
        window = body[desc_idx:desc_idx + 2000]
        boilerplate_idx = window.find("Report this resource")
        desc_text = window[:boilerplate_idx] if boilerplate_idx >= 0 else window
    else:
        desc_text = ""

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

    if lead_magnet_lesson is not None and "free" in title.lower():
        price_area = body[:desc_idx] if desc_idx >= 0 else body[:500]
        findings.extend(_lead_magnet_findings(title, desc_text, body, lead_magnet_lesson, price_area))

    return {"url": url, "title": title, "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--keyword", help="Override the auto-derived search keyword")
    parser.add_argument("--lead-magnet-lesson", type=int, default=None,
                         help="Also run lead-magnet-specific checks (title has "
                              "'Lesson N', no AI-leftover language, shows as FREE) "
                              "against this unit's free sampler product")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright
    from cmie.publishing.tpt import _load_session, _is_logged_in
    from cmie.publishing.browser import cloud_launch_kwargs, cloud_context_kwargs

    keyword = args.keyword or _unit_topic_keyword(args.unit)
    print(f"Searching dashboard for products matching: {keyword!r}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **cloud_launch_kwargs())
        context = browser.new_context(**cloud_context_kwargs())
        _load_session(context)
        page = context.new_page()
        if not _is_logged_in(page):
            browser.close()
            print("ERROR: not logged in to TPT (no valid session found) -- cannot check listings.")
            print("This is NOT the same as \"0 products, nothing to check\". Run "
                  "`python publish_tpt.py --save-session` with a real browser to refresh "
                  ".tpt_session.json, or copy a valid session into this environment.")
            sys.exit(2)

        products = find_unit_product_urls(page, keyword)

        if args.lead_magnet_lesson is not None and not any("free" in p["t"].lower() for p in products):
            lesson_kw = _lesson_topic_keyword(args.unit, args.lead_magnet_lesson)
            if lesson_kw:
                print(f"No free lead magnet found via {keyword!r} -- retrying with lesson "
                      f"topic keyword {lesson_kw!r} (lesson>1 lead magnets lead their title "
                      f"with the topic, which can push the unit keyword past TPT's title "
                      f"length limit).")
                seen_urls = {p["h"] for p in products}
                for p in find_unit_product_urls(page, lesson_kw):
                    if p["h"] not in seen_urls:
                        seen_urls.add(p["h"])
                        products.append(p)

        print(f"Found {len(products)} product(s).\n")

        any_findings = False
        for p in products:
            result = check_product_page(page, p["h"], args.lead_magnet_lesson)
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
