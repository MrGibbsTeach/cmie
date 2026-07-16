"""
CLI: publish a unit to TPT.

Usage:
    python publish_tpt.py --unit year7_ai_data_unit1
    python publish_tpt.py --unit year7_ai_data_unit2 --publish
    python publish_tpt.py --save-session          # log in manually, saves cookies for future runs

Credentials: copy .env.example to .env and fill in TPT_EMAIL and TPT_PASSWORD.
If automated login is blocked by TPT, run --save-session once to manually log in and cache the session.
"""
import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

PROJECT_ROOT = Path(__file__).parent
RELEASES_ROOT = PROJECT_ROOT / "releases"


def save_session() -> None:
    """Open a browser, let the user log in manually, then save the session cookies."""
    from playwright.sync_api import sync_playwright
    from cmie.publishing.tpt import LOGIN_URL, _save_session

    print("Opening browser — log in manually, then press Enter here to save the session.")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=50, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        page.goto(LOGIN_URL)
        input("Press Enter once you are logged in...")
        _save_session(context)
        print("Session saved. Future runs will use these cookies.")
        context.close()
        browser.close()


def _publish_part(unit_id: str, part: str, auto_publish: bool, default_tags: str = None) -> None:
    """Publish a single part of a multi-part unit: a numbered lesson
    ('lesson01'..'lesson07'), the 'assessment', or the 'bundle'."""
    from cmie.publishing.tpt import upload_unit
    from cmie.publishing.listing_reader import read_tpt_listing_from_markdown

    unit_folder = RELEASES_ROOT / unit_id
    artifacts = RELEASES_ROOT / "artifacts"

    if part == "bundle":
        zip_path = artifacts / f"{unit_id}_v001_BUNDLE.zip"
        md_path = unit_folder / "listings" / "unit" / "tpt_listing.md"
        price = float(os.getenv("TPT_BUNDLE_PRICE", "12.99"))
    elif part == "assessment":
        zip_path = artifacts / f"{unit_id}_assessment_v001.zip"
        md_path = unit_folder / "listings" / "assessment_listing.md"
        price = float(os.getenv("TPT_ASSESSMENT_PRICE", "3.50"))
    elif part.startswith("lesson"):
        num = part.replace("lesson", "")
        zip_path = artifacts / f"{unit_id}_lesson{num}_v001.zip"
        # The listing folders are numbered alphabetically by slug (from
        # listing_generator.py's sorted glob), NOT by actual lesson sequence
        # -- so match by slug derived from the real pptx filename, never by
        # number, or you'll attach lesson 1's zip to lesson 6's listing.
        slides_glob = sorted((RELEASES_ROOT / "public" / f"{unit_id}_v001" / "01_Lesson_Slides").glob(f"{num}-*.pptx"))
        if not slides_glob:
            print(f"ERROR: No slide deck found for lesson {num}")
            sys.exit(1)
        slug = slides_glob[0].stem[len(num) + 1:]  # strip "NN-" prefix
        lesson_listing_dirs = [
            d for d in (unit_folder / "listings" / "lessons").glob("*")
            if d.name.endswith(slug)
        ]
        if not lesson_listing_dirs:
            print(f"ERROR: No listing folder found matching slug '{slug}' for lesson {num}")
            sys.exit(1)
        md_path = lesson_listing_dirs[0] / "tpt_listing.md"
        price = float(os.getenv("TPT_LESSON_PRICE", "2.50"))
    else:
        print(f"ERROR: Unknown part '{part}'. Use lesson01..lesson07, assessment, or bundle.")
        sys.exit(1)

    if not zip_path.exists():
        print(f"ERROR: Zip not found: {zip_path}")
        sys.exit(1)
    if not md_path.exists():
        print(f"ERROR: Listing not found: {md_path}")
        sys.exit(1)

    listing = read_tpt_listing_from_markdown(md_path, price=price, tags=default_tags)
    thumbnail_path = RELEASES_ROOT / "thumbnails" / f"{unit_id}_thumbnail.png"
    print(f"Part        : {part}")
    print(f"Zip file    : {zip_path}")
    print(f"Listing     : {md_path}")
    print(f"Thumbnail   : {thumbnail_path} (exists={thumbnail_path.exists()})")
    print(f"Title       : {listing['title']}")
    print(f"Price       : ${listing['price']}")
    print()

    return upload_unit(
        unit_folder, zip_path,
        thumbnail_path=thumbnail_path if thumbnail_path.exists() else None,
        auto_publish=auto_publish, listing=listing,
    )


ALL_PARTS = [f"lesson{n:02d}" for n in range(1, 8)] + ["assessment", "bundle"]


def _publish_part_with_retry(unit_id: str, part: str, auto_publish: bool, default_tags: str = None,
                              max_retries: int = 1) -> str:
    """Publish one part, retrying only on a CONFIRMED failure (dashboard
    checked, product genuinely absent) -- never retries on "uncertain",
    since a blind retry there is exactly how a duplicate product has
    happened before in this project."""
    for attempt in range(max_retries + 1):
        status = _publish_part(unit_id, part, auto_publish, default_tags=default_tags)
        if status in ("submitted", "draft"):
            return status
        if status == "uncertain":
            print(f"WARNING: {part} status uncertain — not retrying automatically. Check the dashboard manually.")
            return status
        # status == "failed": confirmed absent, safe to retry
        if attempt < max_retries:
            print(f"{part}: confirmed not created, retrying ({attempt + 1}/{max_retries})...")
        else:
            print(f"ERROR: {part} failed after {max_retries + 1} attempts.")
    return status


def publish_all_parts(unit_id: str, auto_publish: bool, default_tags: str = None) -> dict:
    """Publish all 9 standard parts (7 lessons + assessment + bundle) for a
    unit in sequence, with confirmed-failure retry built in. Returns a dict
    of part -> final status; check for any "failed"/"uncertain" values
    before assuming the unit is fully live."""
    results = {}
    for part in ALL_PARTS:
        print(f"\n{'=' * 60}\n{part}\n{'=' * 60}")
        results[part] = _publish_part_with_retry(unit_id, part, auto_publish, default_tags=default_tags)
    print(f"\n{'=' * 60}\nSummary for {unit_id}\n{'=' * 60}")
    for part, status in results.items():
        print(f"  {part:12s} : {status}")
    failed = [p for p, s in results.items() if s not in ("submitted", "draft")]
    if failed:
        print(f"\nNEEDS ATTENTION: {', '.join(failed)} did not confirm success.")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a unit to TPT")
    parser.add_argument("--unit", help="Unit ID, e.g. year7_ai_data_unit1")
    parser.add_argument("--zip", help="Path to zip file (auto-detected if omitted)")
    parser.add_argument(
        "--part",
        help="For multi-part units: lesson01..lesson07, assessment, or bundle. "
             "Pass 'all' to publish all 9 parts in sequence with confirmed-failure "
             "retry built in. Omit to publish the unit-level listing as a single "
             "product (legacy behaviour).",
    )
    parser.add_argument("--max-retries", type=int, default=1,
                         help="Retries per part on a CONFIRMED failure only (default 1). "
                              "Never retries on an uncertain status.")
    parser.add_argument("--tags", help="Comma-separated tags override (avoids stale defaults for non-AI topics)")
    parser.add_argument("--publish", action="store_true", help="Auto-publish without pausing")
    parser.add_argument("--save-session", action="store_true", help="Manually log in and save session cookies")
    args = parser.parse_args()

    if args.save_session:
        save_session()
        return

    if not args.unit:
        parser.error("--unit is required unless using --save-session")

    unit_id = args.unit
    unit_folder = RELEASES_ROOT / unit_id

    if not unit_folder.exists():
        print(f"ERROR: Unit folder not found: {unit_folder}")
        sys.exit(1)

    if args.part == "all":
        publish_all_parts(unit_id, args.publish, default_tags=args.tags)
        return

    if args.part:
        _publish_part_with_retry(unit_id, args.part, args.publish, default_tags=args.tags,
                                  max_retries=args.max_retries)
        return

    if args.zip:
        zip_path = Path(args.zip)
    else:
        candidates = sorted((RELEASES_ROOT / "artifacts").glob(f"{unit_id}*.zip"))
        candidates = [c for c in candidates if "test" not in c.name.lower()]
        if not candidates:
            print(f"ERROR: No zip found for {unit_id} in releases/artifacts/")
            sys.exit(1)
        zip_path = candidates[-1]

    print(f"Unit folder : {unit_folder}")
    print(f"Zip file    : {zip_path}")
    print(f"Auto-publish: {args.publish}")
    print()

    from cmie.publishing.tpt import upload_unit
    upload_unit(unit_folder, zip_path, auto_publish=args.publish)


if __name__ == "__main__":
    main()
