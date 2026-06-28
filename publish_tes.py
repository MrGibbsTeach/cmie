"""
CLI: publish a unit to TES via Playwright (persistent Chrome profile).

Usage:
    python publish_tes.py --unit year7_ai_data_unit1
    python publish_tes.py --all
    python publish_tes.py --scout          # open TES upload page for inspection

IMPORTANT: Close Chrome before running. Two instances cannot share the profile.
Set CHROME_PROFILE env var if you want to use a different profile directory.

Pricing: set TES_PRICE_GBP in .env (default 9.99). TES uses GBP.
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
log = logging.getLogger(__name__)

PROJECT_ROOT  = Path(__file__).parent
RELEASES_ROOT = PROJECT_ROOT / "releases"
PRICE_GBP     = float(os.getenv("TES_PRICE_GBP", "9.99"))

TES_UPLOAD_URL = "https://www.tes.com/my-resources"


# ---------------------------------------------------------------------------
# Listing parser
# ---------------------------------------------------------------------------

def _read_listing(unit_folder: Path) -> dict:
    md_path     = unit_folder / "listings" / "unit" / "tes_listing.md"
    legacy_path = unit_folder / "bundle_listings" / "tes_listing.txt"

    if md_path.exists():
        text  = md_path.read_text(encoding="utf-8").strip()
        lines = text.splitlines()
        title = lines[0].lstrip("#").strip() if lines else unit_folder.name
        # First non-blank line after title = tagline
        tagline = ""
        for line in lines[1:]:
            if line.strip():
                tagline = line.strip()
                break
        description = "\n".join(lines[1:]).strip()
    elif legacy_path.exists():
        text = legacy_path.read_text(encoding="utf-8").strip()
        sections: dict[str, list[str]] = {}
        current_key = None
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.endswith(":") and stripped.rstrip(":").isupper():
                current_key = stripped.rstrip(":")
                sections[current_key] = []
            elif current_key is not None:
                sections[current_key].append(line)
        title       = "\n".join(sections.get("TITLE", [])).strip()
        description = "\n".join(sections.get("DESCRIPTION", [])).strip()
        tagline     = description.split("\n")[0] if description else ""
    else:
        raise FileNotFoundError(f"No TES listing found in {unit_folder}")

    if len(title) > 100:
        title = title[:100].rsplit(" ", 1)[0]

    return {"title": title, "tagline": tagline, "description": description}


# ---------------------------------------------------------------------------
# TES upload flow
# ---------------------------------------------------------------------------

def _check_logged_in(page) -> bool:
    return "tes.com/login" not in page.url and "tes.com/register" not in page.url


def _navigate_to_upload(page) -> None:
    page.goto(TES_UPLOAD_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    if not _check_logged_in(page):
        raise RuntimeError(
            "Not logged in to TES. Run setup first: "
            "python -c \"from cmie.publishing.browser import setup; setup()\""
        )
    log.info(f"My resources page: {page.url}")

    # Click "Add resource" link in the sidebar
    try:
        page.get_by_text("Add resource", exact=True).first.click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        log.info(f"Upload form: {page.url}")
    except Exception as e:
        log.warning(f"Could not click 'Add resource': {e} — proceeding from {page.url}")


def _take_debug_screenshot(page, name: str) -> None:
    path = RELEASES_ROOT / f"debug_tes_{name}.png"
    page.screenshot(path=str(path))
    log.info(f"Screenshot: {path}")


def _fill_title(page, title: str) -> None:
    selectors = [
        "input[name='title']",
        "input[placeholder*='title' i]",
        "input[placeholder*='Title']",
        "input[id*='title' i]",
        "[aria-label*='title' i]",
    ]
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if el.count() and el.is_visible():
                el.click(click_count=3)
                el.fill(title)
                log.info(f"Title filled: {title}")
                return
        except Exception:
            continue
    # Fallback: first text input
    page.locator("input[type='text']").first.fill(title)
    log.info(f"Title filled (fallback): {title}")


def _fill_description(page, description: str) -> None:
    # TES uses SimpleMDE — raw textarea is hidden, must interact with CodeMirror
    try:
        page.evaluate(
            "(text) => navigator.clipboard.writeText(text).catch(() => {})",
            description[:4000],
        )
        cm = page.locator(".CodeMirror")
        cm.click()
        page.keyboard.press("Control+a")
        page.keyboard.press("Control+v")
        page.wait_for_timeout(800)
        log.info("Description filled.")
        return
    except Exception as e:
        log.warning(f"CodeMirror fill failed: {e}")
    log.warning("Could not find description field.")


def _upload_file(page, zip_path: Path) -> None:
    log.info(f"Uploading: {zip_path.name}")
    try:
        # Most upload forms have a file input or a button that triggers one
        file_inputs = page.locator("input[type='file']")
        if file_inputs.count() > 0:
            file_inputs.first.set_input_files(str(zip_path))
            page.wait_for_timeout(3000)
            log.info("File uploaded via file input.")
            return
    except Exception:
        pass

    # Try clicking an upload button / dropzone
    for text in ["Upload", "Add file", "Choose file", "Browse"]:
        try:
            btn = page.get_by_text(text, exact=False).first
            if btn.is_visible():
                with page.expect_file_chooser(timeout=8000) as fc:
                    btn.click()
                fc.value.set_files(str(zip_path))
                page.wait_for_timeout(3000)
                log.info(f"File uploaded via '{text}' button.")
                return
        except Exception:
            continue

    raise RuntimeError("Could not find a file upload input on TES upload page.")


def _upload_thumbnail(page, thumbnail_path: Path) -> None:
    if not thumbnail_path.exists():
        log.warning(f"Thumbnail not found: {thumbnail_path} — skipping.")
        return
    log.info(f"Uploading thumbnail: {thumbnail_path.name}")
    try:
        file_inputs = page.locator("input[type='file'][accept*='image'], input[type='file']")
        if file_inputs.count() > 1:
            # Second file input is usually the thumbnail
            file_inputs.nth(1).set_input_files(str(thumbnail_path))
            page.wait_for_timeout(2000)
            log.info("Thumbnail uploaded.")
            return
    except Exception as e:
        log.warning(f"Thumbnail upload failed (non-fatal): {e}")


def _set_price(page, price_gbp: float) -> None:
    selectors = [
        "input[name*='price' i]",
        "input[placeholder*='price' i]",
        "input[id*='price' i]",
        "input[type='number']",
    ]
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if el.count() and el.is_visible():
                el.click(click_count=3)
                el.fill(f"{price_gbp:.2f}")
                log.info(f"Price set: £{price_gbp:.2f}")
                return
        except Exception:
            continue
    log.warning("Could not find price field — may need manual entry.")


def _submit(page) -> None:
    for name in ["Publish", "Submit", "Save and publish", "Upload resource"]:
        try:
            btn = page.get_by_role("button", name=name, exact=False)
            if btn.count() and btn.first.is_visible():
                btn.first.click()
                page.wait_for_timeout(5000)
                log.info(f"Submitted via '{name}' button.")
                return
        except Exception:
            continue
    log.warning("Could not find submit button — resource may need manual publish.")


# ---------------------------------------------------------------------------
# Main publish flow
# ---------------------------------------------------------------------------

def publish_unit(unit_id: str, price_gbp: float = PRICE_GBP, scout: bool = False) -> None:
    from cmie.publishing.browser import automation_chrome

    unit_folder    = RELEASES_ROOT / unit_id
    thumbnail_path = RELEASES_ROOT / "thumbnails" / f"{unit_id}_thumbnail.png"

    candidates = sorted((RELEASES_ROOT / "artifacts").glob(f"{unit_id}*.zip"))
    candidates = [c for c in candidates if "test" not in c.name.lower()]
    if not candidates:
        raise FileNotFoundError(f"No zip found for {unit_id} in releases/artifacts/")
    zip_path = candidates[-1]

    listing = _read_listing(unit_folder)
    log.info(f"Publishing to TES: {listing['title']} @ £{price_gbp:.2f}")
    log.info(f"Zip: {zip_path.name}")

    with automation_chrome() as (context, page):
        try:
            _navigate_to_upload(page)
            _take_debug_screenshot(page, f"{unit_id}_upload_page")

            if scout:
                log.info("Scout mode — screenshot taken, stopping here.")
                try:
                    context.wait_for_event("close", timeout=0)
                except Exception:
                    pass
                return

            _fill_title(page, listing["title"])
            _upload_file(page, zip_path)
            _upload_thumbnail(page, thumbnail_path)
            _fill_description(page, listing["description"])
            _set_price(page, price_gbp)

            _take_debug_screenshot(page, f"{unit_id}_before_submit")
            log.info("Review the browser window, then the script will submit.")
            page.wait_for_timeout(3000)

            _submit(page)
            _take_debug_screenshot(page, f"{unit_id}_after_submit")
            log.info(f"Done: {unit_id} — check TES dashboard to confirm listing is live.")

        except Exception as e:
            _take_debug_screenshot(page, "error")
            raise


TES_NEW_RESOURCE_URL = "https://www.tes.com/teaching-resource/upload"


def scout() -> None:
    """Step through TES upload flow with screenshots at each stage."""
    from cmie.publishing.browser import automation_chrome

    log.info("Scout mode: mapping TES upload flow...")
    with automation_chrome() as (context, page):
        # Step 1: dashboard confirmation
        page.goto(TES_UPLOAD_URL, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        _take_debug_screenshot(page, "scout_1_dashboard")
        log.info(f"Step 1: {page.url}")

        if not _check_logged_in(page):
            log.error("Not logged in to TES. Re-run setup.")
            return

        # Step 2: navigate directly to upload URL
        page.goto(TES_NEW_RESOURCE_URL, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(3000)
        _take_debug_screenshot(page, "scout_2_step1_description")
        log.info(f"Step 2 (description form): {page.url}")

        # Fill title
        title_input = page.locator("input[placeholder='Title your resource']")
        title_input.click()
        title_input.fill("SCOUT TEST — DO NOT PUBLISH")

        # Description uses SimpleMDE — interact with CodeMirror, not the hidden textarea
        page.evaluate(
            "(text) => navigator.clipboard.writeText(text).catch(() => {})",
            "Scout test description. Not a real resource.",
        )
        page.locator(".CodeMirror").click()
        page.keyboard.press("Control+a")
        page.keyboard.press("Control+v")
        page.wait_for_timeout(500)

        # Click Continue
        page.get_by_role("button", name="Continue").click()
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        _take_debug_screenshot(page, "scout_3_step2_add_files")
        log.info(f"Step 3 (Add Files): {page.url}")

        # Scroll to see full file upload step
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(500)
        _take_debug_screenshot(page, "scout_4_step2_scrolled")

        # Upload a real zip to enable Continue
        zip_path = RELEASES_ROOT / "artifacts" / "year7_ai_data_unit2_v001.zip"
        thumbnail_path = RELEASES_ROOT / "thumbnails" / "year7_ai_data_unit2_thumbnail.png"

        log.info(f"Uploading zip: {zip_path.name}")
        try:
            with page.expect_file_chooser(timeout=10000) as fc:
                page.get_by_role("button", name="Upload").click()
            fc.value.set_files(str(zip_path))
            page.wait_for_timeout(5000)
            _take_debug_screenshot(page, "scout_5_after_zip_upload")
            log.info("Zip uploaded.")
        except Exception as e:
            log.warning(f"Zip upload failed: {e}")

        # Upload thumbnail
        if thumbnail_path.exists():
            log.info(f"Uploading thumbnail: {thumbnail_path.name}")
            try:
                with page.expect_file_chooser(timeout=10000) as fc:
                    page.get_by_role("button", name="Upload image").click()
                fc.value.set_files(str(thumbnail_path))
                page.wait_for_timeout(3000)
                _take_debug_screenshot(page, "scout_6_after_thumbnail")
                log.info("Thumbnail uploaded.")
            except Exception as e:
                log.warning(f"Thumbnail upload failed: {e}")

        # Click Continue to step 3 (Categories)
        try:
            page.get_by_role("button", name="Continue").click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            _take_debug_screenshot(page, "scout_7_step3_categories")
            log.info(f"Step 3 (Categories): {page.url}")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            page.wait_for_timeout(500)
            _take_debug_screenshot(page, "scout_8_categories_scrolled")
        except Exception as e:
            log.warning(f"Could not advance to categories: {e}")

        # Click Continue to step 4 (Licence)
        try:
            page.get_by_role("button", name="Continue").click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            _take_debug_screenshot(page, "scout_9_step4_licence")
            log.info(f"Step 4 (Licence): {page.url}")
        except Exception as e:
            log.warning(f"Could not advance to licence: {e}")

        # Click Continue to step 5 (Publish / price)
        try:
            page.get_by_role("button", name="Continue").click()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            _take_debug_screenshot(page, "scout_10_step5_publish")
            log.info(f"Step 5 (Publish): {page.url}")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            page.wait_for_timeout(500)
            _take_debug_screenshot(page, "scout_11_publish_scrolled")
        except Exception as e:
            log.warning(f"Could not advance to publish: {e}")

        log.info("Full scout complete. Close the browser window when done.")
        try:
            context.wait_for_event("close", timeout=0)
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish units to TES")
    parser.add_argument("--unit", help="Unit ID, e.g. year7_ai_data_unit1")
    parser.add_argument("--all", action="store_true", help="Publish all 8 units")
    parser.add_argument("--price", type=float, default=PRICE_GBP, help="Price in GBP")
    parser.add_argument("--scout", action="store_true", help="Open upload page and take screenshot only")
    args = parser.parse_args()

    if args.scout:
        scout()
        return

    if args.all:
        units = [f"year7_ai_data_unit{i}" for i in range(1, 9)]
    elif args.unit:
        units = [args.unit]
    else:
        parser.error("Provide --unit <id>, --all, or --scout")

    for unit_id in units:
        try:
            publish_unit(unit_id, args.price)
        except Exception as e:
            log.error(f"Failed {unit_id}: {e}")


if __name__ == "__main__":
    main()
