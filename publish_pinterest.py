"""
publish_pinterest.py — posts pins to Pinterest for FocusLab Digital from
each unit's 07_Marketing/marketing_content.md (3 pins per unit: bundle
promo, lesson-pack promo, free-sample promo).

No dedicated marketing images exist anywhere in the pipeline yet, so this
reuses each unit's live Gumroad product thumbnail as the pin image (same
image already public on the storefront). Pins 1 & 2 (bundle/lesson-pack,
paid-oriented) go to the "Digital Technologies Lessons" board; pin 3
(free sample) goes to "Free Teacher Resources". Boards are created on
first use if they don't already exist.

Usage:
    python publish_pinterest.py --unit year7_algorithms_unit1
    python publish_pinterest.py --all
    python publish_pinterest.py --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
COOKIES_FILE = PROJECT_ROOT / ".pinterest_session.json"
SCRATCH_DIR = PROJECT_ROOT / ".pinterest_scratch"

BOARD_PAID = "Digital Technologies Lessons"
BOARD_FREE = "Free Teacher Resources"
PIN_BOARD_BY_INDEX = {0: BOARD_PAID, 1: BOARD_PAID, 2: BOARD_FREE}


def _load_env() -> dict:
    env = {}
    env_path = PROJECT_ROOT / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _all_unit_ids() -> list[str]:
    ids = []
    for md_path in sorted((PROJECT_ROOT / "releases" / "public").glob("*/07_Marketing/marketing_content.md")):
        ids.append(md_path.parent.parent.name.replace("_v001", ""))
    return ids


def _unit_release_dir(unit_id: str) -> Path:
    matches = sorted((PROJECT_ROOT / "releases" / "public").glob(f"{unit_id}_v*"))
    if not matches:
        raise FileNotFoundError(f"No release directory found for {unit_id}")
    return matches[-1]


def parse_marketing_pins(md_path: Path) -> list[dict]:
    text = md_path.read_text(encoding="utf-8")
    section_match = re.search(r"## Pinterest pins.*?(?=\n## |\Z)", text, re.DOTALL)
    if not section_match:
        raise ValueError(f"No 'Pinterest pins' section found in {md_path}")
    section = section_match.group(0)

    blocks = re.split(r"### Pin \d+\s*\n", section)[1:]
    pins = []
    for block in blocks:
        title_m = re.search(r"\*\*Title\*\*[^:]*:\s*(.+)", block)
        desc_m = re.search(r"\*\*Description\*\*:\s*(.+)", block)
        link_m = re.search(r"\*\*Link\*\*:\s*(.+)", block)
        if not (title_m and desc_m and link_m):
            raise ValueError(f"Could not parse a pin block in {md_path}")
        pins.append({
            "title": title_m.group(1).strip(),
            "description": desc_m.group(1).strip(),
            "link": link_m.group(1).strip(),
        })
    return pins


def fetch_gumroad_thumbnails(token: str) -> list[dict]:
    url = f"https://api.gumroad.com/v2/products?access_token={token}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    if not data.get("success"):
        raise RuntimeError(f"Gumroad API call failed: {data}")
    return data.get("products", [])


def _unit_keyword(unit_id: str) -> str:
    config_path = PROJECT_ROOT / "data" / "units" / f"{unit_id}.json"
    title = json.loads(config_path.read_text(encoding="utf-8"))["title"]
    return title.split(":")[0].strip()


def match_thumbnail(products: list[dict], keyword: str) -> str:
    for p in products:
        if keyword in (p.get("name") or ""):
            url = p.get("thumbnail_url")
            if url:
                return url
    raise ValueError(f"No Gumroad product thumbnail found matching keyword {keyword!r}")


def download_thumbnail(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:
        dest.write_bytes(resp.read())
    return dest


def _select_board(page, board_name: str) -> None:
    page.click('[data-test-id="board-dropdown-select-button"]')
    page.wait_for_timeout(1000)
    page.fill('input[placeholder="Search"]', board_name)
    page.wait_for_timeout(1500)
    option = page.get_by_text(board_name, exact=True)
    if option.count() > 0:
        option.first.click()
    else:
        page.get_by_text("Create board", exact=False).first.click()
        page.wait_for_timeout(1000)
        page.fill("#boardEditName", board_name)
        page.click('[data-test-id="board-form-submit-button"]')
    page.wait_for_timeout(1500)


def create_pin(page, image_path: Path, title: str, description: str, link: str,
               board_name: str, dry_run: bool) -> dict:
    page.goto("https://www.pinterest.com/pin-creation-tool/", wait_until="domcontentloaded", timeout=25000)
    page.wait_for_timeout(3000)

    page.set_input_files("#storyboard-upload-input", str(image_path))
    page.wait_for_timeout(6000)

    page.fill("#storyboard-selector-title", title)
    page.click('[aria-label="Describe your Pin"]')
    page.keyboard.type(description)
    page.fill("#WebsiteField", link)
    _select_board(page, board_name)

    if dry_run:
        log.info(f"[DRY RUN] Would publish pin: {title[:60]}")
        return {"status": "dry_run", "title": title}

    page.click('button:has-text("Publish"), [role="button"]:has-text("Publish")')
    page.wait_for_timeout(5000)
    # Pinterest shows a "Pin published" success state in place rather than
    # navigating away, so URL-based confirmation is unreliable -- the real
    # check is a post-hoc scan of the account's /_created/ page (see
    # verify_pinterest_pins.py), not anything observable here.
    log.info(f"Submitted: {title[:60]}")
    return {"status": "submitted", "title": title}


def publish_unit(page, unit_id: str, products: list[dict], dry_run: bool) -> list[dict]:
    release_dir = _unit_release_dir(unit_id)
    md_path = release_dir / "07_Marketing" / "marketing_content.md"
    pins = parse_marketing_pins(md_path)

    keyword = _unit_keyword(unit_id)
    thumb_url = match_thumbnail(products, keyword)
    thumb_path = SCRATCH_DIR / f"{unit_id}_thumb.jpg"
    if not thumb_path.exists():
        download_thumbnail(thumb_url, thumb_path)

    results = []
    for i, pin in enumerate(pins):
        board_name = PIN_BOARD_BY_INDEX.get(i, BOARD_PAID)
        result = create_pin(page, thumb_path, pin["title"], pin["description"],
                             pin["link"], board_name, dry_run)
        results.append(result)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--unit", help="Single unit_id to publish pins for")
    group.add_argument("--all", action="store_true", help="Publish pins for all units with marketing content")
    parser.add_argument("--dry-run", action="store_true", help="Fill pin forms but do not click Publish")
    args = parser.parse_args()

    if not COOKIES_FILE.exists():
        log.error(f"{COOKIES_FILE} not found. Export Pinterest cookies via Cookie-Editor first.")
        sys.exit(1)

    env = _load_env()
    token = env.get("GUMROAD_TOKEN")
    if not token:
        log.error("GUMROAD_TOKEN not found in .env")
        sys.exit(1)

    unit_ids = [args.unit] if args.unit else _all_unit_ids()
    log.info(f"Publishing pins for {len(unit_ids)} unit(s): {unit_ids}")

    products = fetch_gumroad_thumbnails(token)
    cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))

    from playwright.sync_api import sync_playwright
    all_results = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1000})
        context.add_cookies(cookies)
        page = context.new_page()

        for unit_id in unit_ids:
            log.info(f"--- {unit_id} ---")
            try:
                results = publish_unit(page, unit_id, products, args.dry_run)
                all_results[unit_id] = results
            except Exception as e:
                log.error(f"Failed to publish pins for {unit_id}: {e}")
                all_results[unit_id] = [{"status": "error", "error": str(e)}]

        browser.close()

    log.info("=== Summary ===")
    total_submitted = total_failed = total_dry_run = 0
    for unit_id, results in all_results.items():
        for r in results:
            status = r.get("status")
            if status == "submitted":
                total_submitted += 1
            elif status == "error":
                total_failed += 1
            elif status == "dry_run":
                total_dry_run += 1
        log.info(f"{unit_id}: {[r.get('status') for r in results]}")
    log.info(f"Submitted: {total_submitted}, Failed: {total_failed}, Dry-run: {total_dry_run}")
    log.info("Run verify_pinterest_pins.py to confirm actual live state.")


if __name__ == "__main__":
    main()
