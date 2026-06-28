"""
CLI: publish a unit to Gumroad via Playwright browser automation.

Usage:
    python publish_gumroad.py --unit year7_ai_data_unit1
    python publish_gumroad.py --all
    python publish_gumroad.py --save-session   # log in once, cache session

Gumroad credentials: add GUMROAD_EMAIL and GUMROAD_PASSWORD to .env
OR run --save-session to log in manually and cache cookies.
"""
import argparse
import logging
import os
import sys
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

PROJECT_ROOT   = Path(__file__).parent
RELEASES_ROOT  = PROJECT_ROOT / "releases"
COOKIES_FILE   = PROJECT_ROOT / ".gumroad_session.json"
PRICE_AUD      = float(os.getenv("GUMROAD_PRICE", "29.99"))
LOGIN_URL      = "https://gumroad.com/login"
NEW_PRODUCT_URL = "https://app.gumroad.com/products/new"


# ---------------------------------------------------------------------------
# Listing parser
# ---------------------------------------------------------------------------

def _read_listing(unit_folder: Path) -> dict:
    md_path     = unit_folder / "listings" / "unit" / "gumroad_listing.md"
    legacy_path = unit_folder / "bundle_listings" / "gumroad_description.md"

    if md_path.exists():
        text  = md_path.read_text(encoding="utf-8").strip()
        lines = text.splitlines()
        title = lines[0].lstrip("#").strip() if lines else unit_folder.name
        description = text
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
        description = "\n".join(sections.get("DESCRIPTION", [])).strip() or text
    else:
        raise FileNotFoundError(f"No Gumroad listing found in {unit_folder}")

    if len(title) > 100:
        title = title[:100].rsplit(" ", 1)[0]

    return {"title": title, "description": description}


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def _save_session(context) -> None:
    cookies = context.cookies()
    COOKIES_FILE.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
    log.info(f"Session saved to {COOKIES_FILE}")


def _load_session(context) -> bool:
    if not COOKIES_FILE.exists():
        return False
    cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
    context.add_cookies(cookies)
    log.info("Gumroad session loaded from file.")
    return True


def _is_logged_in(page) -> bool:
    return "gumroad.com/login" not in page.url and "gumroad.com/signup" not in page.url


def _login(page, context) -> None:
    email    = os.environ.get("GUMROAD_EMAIL", "")
    password = os.environ.get("GUMROAD_PASSWORD", "")

    if _load_session(context):
        page.goto("https://app.gumroad.com/dashboard", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        if _is_logged_in(page):
            log.info("Cookie login succeeded.")
            return
        log.info("Saved session expired — trying form login.")

    if not email or not password:
        raise RuntimeError(
            "No GUMROAD_EMAIL/GUMROAD_PASSWORD in .env and no saved session. "
            "Run: python publish_gumroad.py --save-session"
        )

    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(1000)
    page.locator("input[type='email'], input[name*='email'], input[autocomplete='email']").first.fill(email)
    pw_field = page.locator("input[type='password']").first
    pw_field.fill(password)
    pw_field.press("Enter")
    page.wait_for_url(lambda u: "login" not in u, timeout=20000)
    _save_session(context)
    log.info("Form login succeeded.")


# ---------------------------------------------------------------------------
# Product creation
# ---------------------------------------------------------------------------

def _fill_field(page, label: str, value: str, timeout: int = 5000) -> bool:
    try:
        field = page.get_by_label(label, exact=False).first
        field.click()
        field.fill(value)
        return True
    except Exception:
        return False


def _create_product_via_api(token: str, title: str, price: float) -> str:
    """Create product via API. Returns the Gumroad edit URL."""
    import urllib.request, urllib.parse, json
    data = urllib.parse.urlencode({
        "name":     title,
        "price":    int(round(price * 100)),
        "currency": "aud",
    }).encode()
    req = urllib.request.Request(
        "https://api.gumroad.com/v2/products",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    if not result.get("success"):
        raise RuntimeError(f"API product creation failed: {result}")
    short_url = result["product"]["short_url"]
    slug = short_url.rstrip("/").split("/")[-1]
    edit_url = f"https://gumroad.com/products/{slug}/edit"
    log.info(f"Product created via API: {short_url} → edit: {edit_url}")
    return edit_url


def _navigate_to_edit(page, context, edit_url: str) -> None:
    """Navigate to the product edit page, logging in if needed."""
    page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)
    if "login" in page.url:
        _login(page, context)
        page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
    log.info(f"Edit page ready: {page.url}")


from cmie.publishing.markdown_utils import markdown_to_html as _markdown_to_html


def _fill_description(page, description: str) -> None:
    try:
        desc_area = page.locator("[contenteditable='true'], [role='textbox']").first
        desc_area.wait_for(state="visible", timeout=8000)
        desc_area.click()
        html = _markdown_to_html(description[:3000])
        # Write both HTML and plain-text clipboard entries so the rich-text
        # editor picks up formatting on paste instead of literal markdown.
        page.evaluate(
            """(html) => {
                const plain = html.replace(/<[^>]+>/g, '');
                const item = new ClipboardItem({
                    'text/html': new Blob([html], {type: 'text/html'}),
                    'text/plain': new Blob([plain], {type: 'text/plain'}),
                });
                return navigator.clipboard.write([item]);
            }""",
            html,
        )
        page.keyboard.press("Control+v")
        page.wait_for_timeout(1000)
        log.info("Description filled.")
    except Exception as e:
        log.warning(f"Description fill failed (non-fatal): {e}")


def _save_changes(page) -> None:
    """Gumroad's Product/Content tabs each have their own Save button and
    do NOT auto-persist text/content edits (only direct file inputs, like
    the Thumbnail uploader, save immediately). Must click Save on each tab
    before navigating away or the edits are silently lost on reload."""
    try:
        save_btn = page.locator("button:has-text('Save changes'), button:has-text('Save and continue')").first
        save_btn.click(timeout=5000)
        page.wait_for_timeout(2000)
        log.info("Saved.")
    except Exception as e:
        log.warning(f"Save click failed (non-fatal, verify manually): {e}")


def _upload_content_zip(page, zip_path: Path) -> None:
    # Gumroad's edit page now has a separate "Content" tab for the sellable
    # file -- it's no longer in the Product tab's Cover section.
    log.info(f"Uploading zip via Content tab: {zip_path.name}")
    try:
        page.get_by_role("tab", name="Content").click()
        page.wait_for_timeout(1500)
        page.get_by_text("Upload your files", exact=False).first.click()
        page.wait_for_timeout(500)
        with page.expect_file_chooser(timeout=10000) as fc:
            page.get_by_text("Computer files", exact=False).first.click()
        fc.value.set_files(str(zip_path))

        # The client-side "Cancel" button disappearing only means the
        # browser->Gumroad transfer finished -- Gumroad still finalizes the
        # file server-side afterward (file shows "0 byte" if you save too
        # early, silently losing the attachment). Wait for "Cancel" to be
        # gone, then add a generous buffer before saving.
        for _ in range(40):
            page.wait_for_timeout(2000)
            if page.get_by_text("Cancel", exact=True).count() == 0:
                break
        page.wait_for_timeout(20000)

        log.info("Zip uploaded via Content tab.")
        _save_changes(page)
    except Exception as e:
        raise RuntimeError(f"Could not upload zip: {e}")


def _pad_to_square(image_path: Path) -> Path:
    """Gumroad's Thumbnail field requires a square image. Our marketing
    thumbnails are 4:3 landscape with text/content spread across the full
    width, so center-cropping cuts off important text. Pad to square with
    the design's own background color instead, preserving the full image."""
    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    side = max(w, h)
    bg_color = img.getpixel((0, 0))
    canvas = Image.new("RGB", (side, side), bg_color)
    canvas.paste(img, ((side - w) // 2, (side - h) // 2))
    out_path = image_path.parent / f"_square_{image_path.name}"
    canvas.save(out_path)
    return out_path


def _upload_thumbnail_on_product_tab(page, thumbnail_path: Path) -> None:
    if not thumbnail_path.exists():
        log.warning(f"Thumbnail not found: {thumbnail_path} — skipping.")
        return
    log.info(f"Uploading thumbnail: {thumbnail_path.name}")
    try:
        page.get_by_role("tab", name="Product").click()
        page.wait_for_timeout(1500)
        square_path = _pad_to_square(thumbnail_path)
        thumb_heading = page.get_by_text("Thumbnail", exact=False).first
        thumb_heading.scroll_into_view_if_needed(timeout=10000)
        page.wait_for_timeout(500)
        section = thumb_heading.locator("xpath=ancestor::section[1]")
        # If a thumbnail is already set, the upload <input> is replaced by
        # an <img> + "Remove" button -- clear it first to get the input back.
        remove_btn = section.get_by_role("button", name="Remove")
        if remove_btn.count() > 0:
            remove_btn.first.click()
            page.wait_for_timeout(500)
        thumb_input = section.locator("input[type='file']").first
        thumb_input.set_input_files(str(square_path))
        page.wait_for_timeout(3000)
        square_path.unlink(missing_ok=True)
        log.info("Thumbnail uploaded.")
    except Exception as e:
        log.warning(f"Thumbnail upload failed (non-fatal): {e}")


def _verify_after_reload(page, edit_url: str, zip_path: Path) -> None:
    """Reload the edit page and confirm the zip actually persisted with its
    real size -- screenshots taken before a reload are not proof anything
    was saved. Found the hard way: Gumroad shows "0 byte" if you check too
    soon after upload, because it finalizes the file server-side after the
    client-side transfer (and progress bar) is already done."""
    for attempt in range(4):
        page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        page.get_by_role("tab", name="Content").click()
        page.wait_for_timeout(1500)
        card_text = page.locator(f"text={zip_path.stem}").locator(
            "xpath=ancestor::*[self::div or self::section][3]"
        )
        if card_text.count() == 0:
            log.error(f"VERIFY FAILED: zip {zip_path.name} not found in Content tab after reload.")
            return
        text = card_text.first.inner_text(timeout=3000)
        if "0 byte" not in text:
            log.info(f"Verified after reload: {text.replace(chr(10), ' | ')}")
            return
        log.warning(f"Zip still shows 0 byte (attempt {attempt + 1}/4) -- backend still finalizing, waiting...")
        page.wait_for_timeout(30000)
    log.error(f"VERIFY FAILED: zip still shows 0 byte after retries -- upload did not persist. Check {edit_url} manually.")


# ---------------------------------------------------------------------------
# Main publish flow
# ---------------------------------------------------------------------------

def publish_unit(unit_id: str, price_aud: float = PRICE_AUD) -> None:
    from playwright.sync_api import sync_playwright

    unit_folder    = RELEASES_ROOT / unit_id
    thumbnail_path = RELEASES_ROOT / "thumbnails" / f"{unit_id}_thumbnail.png"

    # Prefer the cleaned customer-facing "_PUBLIC" zip (built from
    # releases/public/<unit>_v001/) over the old internal zip, which
    # contains raw production files (JSON, Canva prompts, QA reports)
    # that should never ship to a customer.
    public_candidates = sorted((RELEASES_ROOT / "artifacts").glob(f"{unit_id}_*_PUBLIC.zip"))
    if public_candidates:
        zip_path = public_candidates[-1]
    else:
        candidates = sorted((RELEASES_ROOT / "artifacts").glob(f"{unit_id}*.zip"))
        candidates = [c for c in candidates if "test" not in c.name.lower() and "_PUBLIC" not in c.name]
        if not candidates:
            raise FileNotFoundError(f"No zip found for {unit_id} in releases/artifacts/")
        zip_path = candidates[-1]
        log.warning(f"No cleaned _PUBLIC zip found for {unit_id} -- falling back to internal zip {zip_path.name}. This may contain internal-only files.")

    listing = _read_listing(unit_folder)
    log.info(f"Publishing: {listing['title']} @ ${price_aud} AUD")
    log.info(f"Zip: {zip_path.name}")

    from cmie.publishing.browser import automation_chrome

    with automation_chrome() as (context, page):
        try:
            _login(page, context)
            token = os.environ.get("GUMROAD_TOKEN", "")
            edit_url = _create_product_via_api(token, listing["title"], price_aud)
            _navigate_to_edit(page, context, edit_url)

            _upload_content_zip(page, zip_path)
            _upload_thumbnail_on_product_tab(page, thumbnail_path)
            _fill_description(page, listing["description"])
            _save_changes(page)
            _verify_after_reload(page, edit_url, zip_path)

            screenshot = RELEASES_ROOT / f"debug_gumroad_{unit_id}.png"
            page.screenshot(path=str(screenshot))
            log.info(f"Screenshot saved: {screenshot}")
            log.info(f"Product URL: {page.url}")
            log.info(f"Done: {unit_id}")

        except Exception as e:
            page.screenshot(path=str(RELEASES_ROOT / "debug_gumroad_error.png"))
            log.error(f"Screenshot: {RELEASES_ROOT / 'debug_gumroad_error.png'}")
            raise


def save_session() -> None:
    from playwright.sync_api import sync_playwright

    print("Opening browser — log in to Gumroad manually, then press Enter.")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page    = context.new_page()
        page.goto(LOGIN_URL)
        input("Press Enter once logged in...")
        _save_session(context)
        print("Session saved.")
        context.close()
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish units to Gumroad")
    parser.add_argument("--unit", help="Unit ID, e.g. year7_ai_data_unit1")
    parser.add_argument("--all", action="store_true", help="Publish all 8 units")
    parser.add_argument("--price", type=float, default=PRICE_AUD, help="Price in AUD")
    parser.add_argument("--save-session", action="store_true", help="Log in manually and save session")
    args = parser.parse_args()

    if args.save_session:
        save_session()
        return

    if args.all:
        units = [f"year7_ai_data_unit{i}" for i in range(1, 9)]
    elif args.unit:
        units = [args.unit]
    else:
        parser.error("Provide --unit <id>, --all, or --save-session")

    for unit_id in units:
        try:
            publish_unit(unit_id, args.price)
        except Exception as e:
            log.error(f"Failed {unit_id}: {e}")


if __name__ == "__main__":
    main()
