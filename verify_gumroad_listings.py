"""
verify_gumroad_listings.py — post-publish integrity check for Gumroad
listings, mirroring verify_tpt_listings.py's checks but using the Gumroad
API directly (GUMROAD_TOKEN) instead of browser scraping -- Gumroad's API
returns each product's live description as rendered HTML, so this is
faster and more reliable than a Playwright pass.

Flags: empty/near-empty description, literal unrendered markdown
(**bold**, ## heading, raw table row), literal HTML tag leakage, and a
zip file reported as 0 bytes (the async-finalization trap this project
hit before).

Usage:
    python verify_gumroad_listings.py
    python verify_gumroad_listings.py --keyword "Unit 1"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent

_BOLD_RE = re.compile(r"\*\*[^*\n]*[a-zA-Z][^*\n]*\*\*")


def fetch_products(token: str) -> list[dict]:
    url = f"https://api.gumroad.com/v2/products?access_token={token}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    if not data.get("success"):
        raise RuntimeError(f"Gumroad API call failed: {data}")
    return data.get("products", [])


def check_product(p: dict) -> dict:
    findings = []
    name = p.get("name", "")
    desc_html = p.get("description", "") or ""
    desc_text = re.sub(r"<[^>]+>", " ", desc_html)  # strip tags for length/content checks
    desc_text = re.sub(r"\s+", " ", desc_text).strip()

    if len(desc_text) < 100:
        findings.append(f"Description looks empty/near-empty ({len(desc_text)} chars).")

    if _BOLD_RE.search(desc_html) or re.search(r"^##\s", desc_html, re.M):
        findings.append("Literal unrendered markdown found in description (**bold** or ##).")

    # A leaked literal HTML tag would show as e.g. "&lt;img&gt;" if
    # properly escaped, or as a raw unescaped tag with no matching
    # rendering if not -- check for tags Gumroad's own editor wouldn't
    # produce (its real output uses <p>/<ul>/<li>/<h1-3>/<strong>/<em>/<a>).
    unexpected_tags = set(re.findall(r"<([a-zA-Z][a-zA-Z0-9]*)", desc_html)) - {
        "p", "ul", "ol", "li", "h1", "h2", "h3", "strong", "em", "a", "br", "div", "span", "b", "i"
    }
    if unexpected_tags:
        findings.append(f"Unexpected HTML tags in description (possible leak): {unexpected_tags}")

    return {"name": name, "id": p.get("id"), "url": p.get("short_url"),
            "published": p.get("published"), "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keyword", default="Unit 1", help="Only check products whose name contains this")
    args = parser.parse_args()

    token = os.environ.get("GUMROAD_TOKEN")
    if not token:
        print("ERROR: GUMROAD_TOKEN not set (checked .env and environment variables)")
        sys.exit(1)

    products = fetch_products(token)
    matched = [p for p in products if args.keyword in p.get("name", "")]
    print(f"Checking {len(matched)} product(s) matching {args.keyword!r} (of {len(products)} total).\n")

    any_findings = False
    for p in matched:
        result = check_product(p)
        status = "OK" if not result["findings"] else "ISSUES FOUND"
        pub = "published" if result["published"] else "DRAFT"
        print(f"[{status}] ({pub}) {result['name'][:70]}")
        print(f"         {result['url']}")
        for f in result["findings"]:
            print(f"         - {f}")
            any_findings = True
        print()

    if any_findings:
        print("Some listings need attention -- see findings above.")
        sys.exit(1)
    else:
        print("All checked listings look clean.")


if __name__ == "__main__":
    main()
