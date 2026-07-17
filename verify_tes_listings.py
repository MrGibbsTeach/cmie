"""
verify_tes_listings.py — post-publish integrity check for TES resources.
Mirrors verify_tpt_listings.py's checks, adapted to TES: reloads each
resource's edit page and reads the actual title/description field values
(TES's own markdown editor renders raw markdown natively, so unlike
TPT/Gumroad the risk here is empty fields or literal unescaped HTML, not
unrendered **bold**).

Usage:
    python verify_tes_listings.py --keyword "Unit 1"
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def find_resource_ids(page, keyword: str) -> list[dict]:
    """`keyword` is currently unused for pre-filtering -- the dashboard's
    "Edit" links don't reliably carry title text nearby, so this collects
    every resource ID and lets the per-resource title check (in
    check_resource) report what it actually finds instead. Filtering
    happens by reading the caller's output, not by guessing here."""
    page.goto(
        "https://www.tes.com/teaching-resources/dashboard/resource-management/uploads",
        wait_until="domcontentloaded", timeout=20000,
    )
    page.wait_for_timeout(3000)
    if page.get_by_text("Show all", exact=False).count() > 0:
        page.get_by_text("Show all", exact=False).first.click()
        page.wait_for_timeout(2500)
    hrefs = page.evaluate(
        """() => Array.from(document.querySelectorAll("a[href*='uploader/v2/']")).map(a => a.href)"""
    )
    seen, unique = set(), []
    for h in hrefs:
        rid_match = re.search(r"uploader/v2/(\d+)", h)
        if not rid_match:
            continue
        rid = rid_match.group(1)
        if rid not in seen:
            seen.add(rid)
            unique.append({"id": rid, "url": f"https://www.tes.com/uploader/v2/{rid}"})
    return unique


def check_resource(page, rid: str) -> dict:
    findings = []
    page.goto(f"https://www.tes.com/uploader/v2/{rid}", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2500)

    title = page.evaluate(
        """() => { const el = document.querySelector("input[placeholder*='Title' i], input#title, input[name='title']"); return el ? el.value : null; }"""
    )
    if not title:
        findings.append("Could not read title field -- resource may not exist or session expired.")
        return {"id": rid, "title": None, "findings": findings}

    desc = page.evaluate(
        """() => { const el = document.querySelector(".CodeMirror"); return el && el.CodeMirror ? el.CodeMirror.getValue() : (el ? el.innerText : ''); }"""
    ) or ""

    if len(desc.strip()) < 50:
        findings.append(f"Description looks empty/near-empty ({len(desc.strip())} chars).")

    if re.search(r"<[a-zA-Z][a-zA-Z0-9]*(\s|>)", desc):
        findings.append("Literal HTML tag characters found in description.")

    return {"id": rid, "title": title, "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keyword", default="Unit 1")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright
    import sys as _sys
    _sys.path.insert(0, str(PROJECT_ROOT))
    from publish_tes import _login
    from dotenv import load_dotenv
    load_dotenv()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        _login(page, context, os.getenv("TES_EMAIL", ""), os.getenv("TES_PASSWORD", ""))

        resources = find_resource_ids(page, args.keyword)
        print(f"Found {len(resources)} resource(s) total on the dashboard.\n")

        any_findings = False
        checked = 0
        for r in resources:
            result = check_resource(page, r["id"])
            title = result["title"] or ""
            if args.keyword and args.keyword not in title:
                continue
            checked += 1
            status = "OK" if not result["findings"] else "ISSUES FOUND"
            print(f"[{status}] {title[:70]}")
            print(f"         {r['url']}")
            for f in result["findings"]:
                print(f"         - {f}")
                any_findings = True
            print()
        print(f"Checked {checked} resource(s) matching {args.keyword!r}.\n")

        browser.close()

    if any_findings:
        print("Some resources need attention -- see findings above.")
        sys.exit(1)
    else:
        print("All checked resources look clean.")


if __name__ == "__main__":
    main()
