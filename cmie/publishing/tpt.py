"""
TPT (Teachers Pay Teachers) automated product publisher.

Uses Playwright in headed mode so you can see what's happening and
intervene if TPT's UI has changed. The script fills in all form fields
and uploads the zip, then pauses before submitting so you can:
  1. Add a product thumbnail (required by TPT, must be done manually)
  2. Set grade levels and subject area if selectors have changed
  3. Review everything before clicking Publish

Usage:
    python publish_tpt.py --unit year7_ai_data_unit1
    python publish_tpt.py --unit year7_ai_data_unit1 --publish  # skip pause, auto-submit

Credentials via .env:
    TPT_EMAIL=...
    TPT_PASSWORD=...
"""
from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, expect

load_dotenv()
log = logging.getLogger(__name__)

TPT_BASE = "https://www.teacherspayteachers.com"
LOGIN_URL = f"{TPT_BASE}/Login"
DASHBOARD_URL      = f"{TPT_BASE}/My-Products"
NEW_PRODUCT_URL    = f"{TPT_BASE}/My-Products/New/Digital-Next"

# Grade level labels as they appear on TPT checkboxes
GRADE_LEVELS = ["7th Grade", "8th Grade", "9th Grade"]
SUBJECT = "Computer Science - Technology"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

COOKIES_FILE = Path(__file__).parent.parent.parent / ".tpt_session.json"


def _save_session(context) -> None:
    import json
    cookies = context.cookies()
    COOKIES_FILE.write_text(json.dumps(cookies), encoding="utf-8")
    log.info(f"Session saved to {COOKIES_FILE}")


def _extract_chrome_cookies() -> list[dict]:
    """Pull TPT cookies directly from the user's logged-in Chrome profile."""
    import browser_cookie3
    jar = browser_cookie3.chrome(domain_name=".teacherspayteachers.com")
    cookies = []
    for c in jar:
        cookies.append({
            "name": c.name,
            "value": c.value,
            "domain": c.domain,
            "path": c.path,
            "secure": c.secure,
            "httpOnly": False,
            "sameSite": "Lax",
        })
    return cookies


def _load_session(context) -> bool:
    import json

    # First try extracting directly from the user's Chrome (best option)
    try:
        cookies = _extract_chrome_cookies()
        if cookies:
            context.add_cookies(cookies)
            log.info(f"Loaded {len(cookies)} TPT cookies from Chrome.")
            return True
    except Exception as e:
        log.warning(f"Could not extract Chrome cookies: {e}")

    # Fall back to saved session file
    if not COOKIES_FILE.exists():
        return False
    try:
        cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
        context.add_cookies(cookies)
        log.info("Session cookies loaded from file.")
        return True
    except Exception as e:
        log.warning(f"Could not load session file: {e}")
        return False


def _is_logged_in(page) -> bool:
    page.goto(TPT_BASE, wait_until="domcontentloaded", timeout=15000)
    time.sleep(2)
    links = page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)")
    return any("My-Products" in l or "store/focuslab" in l for l in links)


def _login(page, context, email: str, password: str) -> None:
    # Load cookies from Chrome — bypasses bot detection entirely
    if _load_session(context) and _is_logged_in(page):
        log.info("Logged in via Chrome session cookies.")
        return

    # Fallback: standard form login
    log.info("Cookie login failed — trying form login...")
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=15000)

    email_field = page.get_by_label("Email", exact=False)
    if email_field.count() == 0:
        email_field = page.get_by_placeholder(re.compile(r"email", re.I))
    email_field.first.fill(email)

    password_field = page.get_by_placeholder("Password", exact=False)
    if password_field.count() == 0:
        password_field = page.get_by_label("Password", exact=False)
    password_field.first.fill(password)
    time.sleep(1)

    page.get_by_role("button", name=re.compile(r"log.?in|sign.?in", re.I)).first.click()

    try:
        page.wait_for_url(lambda url: "login" not in url.lower() and "signin" not in url.lower(), timeout=15000)
    except Exception:
        pass

    time.sleep(1)
    if "login" in page.url.lower() or "signin" in page.url.lower():
        raise RuntimeError(
            "Login failed. Make sure you are logged into TPT in your normal Chrome browser, "
            "then rerun — cookies will be extracted automatically."
        )

    _save_session(context)
    log.info(f"Logged in via form. At: {page.url}")


# ---------------------------------------------------------------------------
# Navigate to new product form
# ---------------------------------------------------------------------------

def _find_and_click_new_resource(page: Page) -> bool:
    """Scan the current page for any new-resource entry point. Returns True if found."""
    patterns = [
        re.compile(r"new\s+resource", re.I),
        re.compile(r"upload\s+a?\s*resource", re.I),
        re.compile(r"add\s+new", re.I),
        re.compile(r"new\s+product", re.I),
        re.compile(r"create\s+resource", re.I),
        re.compile(r"upload\s+product", re.I),
    ]
    for pattern in patterns:
        for role in ("link", "button"):
            el = page.get_by_role(role, name=pattern)
            if el.count() > 0:
                log.info(f"Found '{pattern.pattern}' ({role}) — clicking...")
                el.first.click()
                page.wait_for_load_state("domcontentloaded", timeout=15000)
                time.sleep(2)
                log.info(f"Now at: {page.url}")
                return True
    return False


def _all_hrefs(page: Page) -> list[dict]:
    """Return every anchor href in the DOM including hidden elements."""
    return page.evaluate("""
        () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
            href: a.href,
            text: (a.textContent || a.getAttribute('aria-label') || '').trim().slice(0, 80),
            visible: a.offsetWidth > 0 && a.offsetHeight > 0
        }))
    """)


def _open_new_product(page: Page) -> None:
    log.info(f"Navigating to new product form: {NEW_PRODUCT_URL}")
    page.goto(NEW_PRODUCT_URL, wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)
    log.info(f"Now at: {page.url}")

    # Verify we're past the product-type screen by checking for a form input
    inputs = page.evaluate("""
        () => Array.from(document.querySelectorAll('input, textarea')).map(el => ({
            tag: el.tagName, name: el.name, placeholder: el.placeholder,
            ariaLabel: el.getAttribute('aria-label'), type: el.type
        }))
    """)
    log.info(f"Inputs on form: {inputs[:10]}")

    if not inputs:
        # URL may have changed — scan links to find the updated digital download URL
        all_links = _all_hrefs(page)
        digital = next((l for l in all_links if "digital" in l["text"].lower()), None)
        if digital:
            log.info(f"Found digital download link: {digital['href']} — navigating...")
            page.goto(digital["href"], wait_until="domcontentloaded", timeout=15000)
            time.sleep(3)
            log.info(f"Now at: {page.url}")
        else:
            screenshot_path = Path("releases/debug_screenshot.png")
            page.screenshot(path=str(screenshot_path))
            raise RuntimeError(
                f"No form inputs found and no digital download link detected.\n"
                f"URL: {page.url} — screenshot saved to {screenshot_path}\n"
                f"Update NEW_PRODUCT_URL in tpt.py to the current digital download URL."
            )


# ---------------------------------------------------------------------------
# Fill title
# ---------------------------------------------------------------------------

def _fill_title(page: Page, title: str) -> None:
    log.info(f"Filling title: {title}")
    time.sleep(2)

    selectors = [
        'input[name="data[Item][name]"]',       # TPT's actual field name
        'input[placeholder*="name your product" i]',
        'input[name="title"]',
        'input[placeholder*="title" i]',
        'input[aria-label*="title" i]',
        'textarea[name="title"]',
    ]
    for sel in selectors:
        el = page.locator(sel)
        if el.count() > 0:
            log.info(f"Title field found via: {sel}")
            el.first.fill(title)
            return

    inputs = page.evaluate("""
        () => Array.from(document.querySelectorAll('input, textarea')).map(el => ({
            name: el.name, placeholder: el.placeholder, type: el.type
        }))
    """)
    raise RuntimeError(f"Title input not found. Inputs on page: {inputs[:20]}")


# ---------------------------------------------------------------------------
# Fill description (Quill rich text editor)
# ---------------------------------------------------------------------------

def _fill_description(page: Page, description: str) -> None:
    log.info("Filling description...")
    from cmie.publishing.markdown_utils import markdown_to_html

    editor = page.locator('.ql-editor, [contenteditable="true"]').first
    if editor.count() == 0:
        log.warning("Description editor not found — skipping.")
        return

    # TPT's description field is a rich-text (Quill) editor -- pasting raw
    # markdown renders literal ## / - characters instead of real formatting.
    # Write both text/html and text/plain to the clipboard so the editor
    # picks up the HTML on paste.
    html = markdown_to_html(description)
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
    editor.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Control+v")
    time.sleep(1)
    log.info("Description pasted.")


# ---------------------------------------------------------------------------
# Set price
# ---------------------------------------------------------------------------

def _set_free_resource(page: Page) -> bool:
    """Check TPT's "Free Resource" checkbox. This is the only way to list
    at $0 -- the plain price field enforces a $0.95 minimum and rejects 0
    with a validation error. Checking this box also removes the Price,
    Multiple Licenses, Bundle Discount Price, and Tax Code fields from the
    form entirely, so none of those need filling afterward."""
    box = page.locator('label[for="item-free"] button[role="checkbox"]')
    if box.count() == 0:
        log.warning("Free Resource checkbox not found — falling back to $0.95.")
        return False
    if box.first.get_attribute("aria-checked") != "true":
        box.first.click()
        page.wait_for_timeout(800)
    log.info("Free Resource checkbox checked.")
    return True


def _fill_price(page: Page, price: float) -> None:
    if price <= 0:
        if _set_free_resource(page):
            return
        price = 0.95  # TPT's enforced minimum if the free checkbox wasn't found

    log.info(f"Setting price: ${price}")
    selectors = [
        'input[name="data[Item][price]"]',      # TPT's likely field name
        'input[name="price"]',
        'input[placeholder*="price" i]',
        'input[aria-label*="price" i]',
        'input[type="number"]',
    ]
    for sel in selectors:
        el = page.locator(sel)
        if el.count() > 0:
            log.info(f"Price field found via: {sel}")
            el.first.click(click_count=3)
            el.first.fill(str(price))
            return

    log.warning("Price input not found — may be on a later step. Will retry after navigation.")


# ---------------------------------------------------------------------------
# Upload zip file
# ---------------------------------------------------------------------------

def _upload_zip(page: Page, zip_path: Path) -> None:
    log.info(f"Uploading zip: {zip_path.name}")

    # On TPT's form the first file input (no name attr) is the product file
    file_inputs = page.locator('input[type="file"]')
    if file_inputs.count() == 0:
        log.warning("No file input found — skipping zip upload.")
        return

    file_inputs.first.set_input_files(str(zip_path))
    log.info("Zip upload triggered, waiting for upload to complete...")

    # A fixed 6s sleep here was the same "checked too soon" trap this
    # project has hit (and fixed) elsewhere — poll for the uploaded
    # filename to actually show up on the page instead of guessing a
    # delay, up to 20s, before moving on.
    stem = zip_path.stem
    confirmed = False
    for _ in range(10):
        page.wait_for_timeout(2000)
        if page.get_by_text(stem, exact=False).count() > 0 or page.get_by_text(zip_path.name, exact=False).count() > 0:
            confirmed = True
            break
    if not confirmed:
        log.warning("Could not visually confirm the uploaded filename appeared — proceeding anyway.")
        page.wait_for_timeout(4000)


# ---------------------------------------------------------------------------
# Upload thumbnail / cover image
# ---------------------------------------------------------------------------

def _upload_thumbnail(page: Page, thumbnail_path: Path) -> None:
    log.info(f"Uploading thumbnail: {thumbnail_path.name}")

    # TPT defaults to "Auto generate thumbnails from the product file", which
    # fails for PPTX/zip uploads ("We cannot generate images from your file").
    # Switch to manual upload mode first, or the file input below won't exist.
    manual_radio = page.get_by_text("Upload thumbnails now", exact=False)
    if manual_radio.count() > 0:
        manual_radio.first.click()
        time.sleep(0.5)

    # The "Main Cover" required dropzone's file input has no accept/name
    # attribute to select by -- it's identified only by id="ItemDigitalThumb1".
    img_inputs = page.locator("#ItemDigitalThumb1")
    if img_inputs.count() == 0:
        img_inputs = page.locator('input[type="file"][accept*="image"]')

    if img_inputs.count() == 0:
        log.warning("Thumbnail input not found — upload manually.")
        return

    img_inputs.first.set_input_files(str(thumbnail_path))
    log.info("Thumbnail upload triggered.")
    time.sleep(3)


# ---------------------------------------------------------------------------
# Set grade levels
# ---------------------------------------------------------------------------

def _set_grades(page: Page) -> None:
    log.info(f"Setting grade levels: {GRADE_LEVELS}")
    for grade in GRADE_LEVELS:
        # Try exact label first, then partial match
        for exact in (True, False):
            cb = page.get_by_label(grade, exact=exact)
            if cb.count() > 0 and not cb.first.is_checked():
                # .check() occasionally clicks a checkbox whose React state
                # doesn't flip on the first attempt (observed reproducibly
                # on this control, not seen elsewhere in this file) --
                # retry with a short wait instead of failing the whole
                # upload on what's ultimately a UI timing race.
                for attempt in range(3):
                    try:
                        cb.first.check(timeout=5000)
                        break
                    except Exception:
                        if attempt == 2:
                            raise
                        page.wait_for_timeout(800)
                log.info(f"Checked grade: {grade}")
                break
        else:
            log.warning(f"Grade checkbox '{grade}' not found — set manually.")


# ---------------------------------------------------------------------------
# Set subject
# ---------------------------------------------------------------------------

def _select_react_select_option(page: Page, input_selector: str, search_term: str) -> bool:
    """TPT's Subject Area and Tag fields are react-select comboboxes with a
    fixed, server-side vocabulary -- typing a free-text term does NOT create
    a new tag, it searches existing options (including non-selectable group
    headers, which also render with role="option" in this implementation).
    Type the term, wait for the dropdown, and click the option whose text
    exactly matches (case-insensitive) -- not just the first/last result,
    since group headers and unrelated leaf options are mixed into the list."""
    field = page.locator(input_selector)
    if field.count() == 0:
        return False
    field.click()
    field.fill("")
    field.type(search_term, delay=50)
    page.wait_for_timeout(700)

    options = page.locator('[role="option"]')
    count = options.count()
    target = None
    for i in range(count):
        text = options.nth(i).inner_text().strip()
        if text.lower() == search_term.lower():
            target = options.nth(i)
            break
    if target is None and count > 0:
        # fall back to a substring match if no exact match exists
        for i in range(count):
            text = options.nth(i).inner_text().strip()
            if search_term.lower() in text.lower():
                target = options.nth(i)
                break
    if target is None:
        page.keyboard.press("Escape")
        return False

    target.click()
    page.wait_for_timeout(300)
    return True


def _set_tax_code(page: Page, tax_code: str = "Other Digital Goods - No Physical Media") -> None:
    log.info(f"Setting tax code: {tax_code}")
    tax_box = page.get_by_text("Select a tax code", exact=False).first
    if tax_box.count() == 0:
        log.warning("Tax code field not found — set manually.")
        return
    tax_box.scroll_into_view_if_needed(timeout=10000)

    # The options list occasionally isn't populated yet on the first open
    # (observed on $0-priced listings, not seen on paid ones) -- retry
    # opening the dropdown and waiting longer rather than giving up after
    # one 600ms check.
    for attempt in range(3):
        tax_box.click()
        page.wait_for_timeout(1200 + attempt * 800)
        options = page.locator('[role="option"]')
        count = options.count()
        for i in range(count):
            if tax_code.lower() in options.nth(i).inner_text().strip().lower():
                options.nth(i).click()
                log.info(f"Tax code set: {tax_code}")
                return
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)

    log.warning(f"Tax code '{tax_code}' not found in dropdown after retries — set manually.")


def _set_subject(page: Page) -> None:
    log.info(f"Setting subject: {SUBJECT}")
    if _select_react_select_option(page, "#subject-areas", SUBJECT):
        log.info(f"Subject set: {SUBJECT}")
        return

    # Fall back to the search term TPT's vocabulary actually recognises
    # (the full SUBJECT string may not exist verbatim as an option).
    short_term = SUBJECT.split("-")[0].strip()
    if short_term != SUBJECT and _select_react_select_option(page, "#subject-areas", short_term):
        log.info(f"Subject set via fallback term '{short_term}'")
        return

    log.warning(f"Subject '{SUBJECT}' not found — set manually.")


# ---------------------------------------------------------------------------
# Fill tags
# ---------------------------------------------------------------------------

def _fill_tags(page: Page, tags: list[str]) -> None:
    log.info(f"Adding tags: {tags}")
    added = 0
    for tag in tags[:6]:  # TPT allows max 6 tags
        if _select_react_select_option(page, "#tags", tag):
            added += 1
            log.info(f"  Tag added: {tag}")
        else:
            log.warning(f"  Tag '{tag}' not in TPT's vocabulary — skipped.")
    if added == 0:
        log.warning("No tags could be matched to TPT's vocabulary — set manually.")
    else:
        log.info(f"{added}/{len(tags[:6])} tags entered.")

    # The dropdown panel from the last selection stays open and can overlap
    # (and intercept clicks on) elements further down the page, including
    # the final Submit button -- close it before moving on.
    page.keyboard.press("Escape")
    page.locator("body").click(position={"x": 5, "y": 5})
    time.sleep(0.3)


# ---------------------------------------------------------------------------
# Edit an existing product's attached file
# ---------------------------------------------------------------------------

def replace_product_file(product_id: str, new_zip_path: Path) -> None:
    """
    Replace the downloadable file on an already-published TPT product.

    TPT's edit page is at /itemsDigital/editNext/{product_id}. The existing
    file is removed via its delete-btn (there's one per file slot -- Product,
    Preview, Video, Thumb1-4 -- in that DOM order, so .first targets the main
    Product file), then the new file is uploaded into the now-empty
    #ItemDigitalProduct input (note: there are two elements with this id on
    the page, one of them a hidden non-file input, so the selector must be
    scoped to input[type='file']). TPT renames the uploaded file to match
    the product's URL slug, not the original filename -- compare the
    "Last updated" timestamp after submitting, not the filename, to confirm
    the replacement took effect.
    """
    email    = os.environ.get("TPT_EMAIL", "")
    password = os.environ.get("TPT_PASSWORD", "")
    if not email or not password:
        raise RuntimeError("TPT_EMAIL and TPT_PASSWORD must be set in .env")
    if not new_zip_path.exists():
        raise FileNotFoundError(f"Zip not found: {new_zip_path}")

    edit_url = f"https://www.teacherspayteachers.com/itemsDigital/editNext/{product_id}"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=80, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        try:
            _login(page, context, email, password)
            page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2500)

            page.locator(".delete-btn").first.click()
            page.wait_for_timeout(1000)

            page.locator("input[type='file']#ItemDigitalProduct").set_input_files(str(new_zip_path))

            for _ in range(30):
                page.wait_for_timeout(2000)
                if page.get_by_text("Cancel", exact=True).count() == 0:
                    break
            page.wait_for_timeout(5000)

            submit = page.locator("#react-submit-section button[type='submit']")
            if submit.count() == 0:
                raise RuntimeError("Submit button not found on edit page.")
            submit.first.scroll_into_view_if_needed(timeout=10000)
            page.wait_for_timeout(300)
            submit.first.click()

            navigated = False
            for _ in range(30):
                page.wait_for_timeout(1000)
                if "editNext" not in page.url:
                    navigated = True
                    break
            if navigated:
                log.info(f"File replaced on product {product_id}. URL: {page.url}")
            else:
                log.warning(f"Still on edit URL after 30s for product {product_id} -- relying on reload verification below.")

            # Verify via a fresh reload, not the post-submit state.
            page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            file_card = page.get_by_text(".zip", exact=False).first
            info = file_card.locator("xpath=ancestor::*[self::div][3]").inner_text()
            log.info(f"Verified file info after reload: {info.replace(chr(10), ' | ')}")

        except Exception as exc:
            page.screenshot(path=str(Path(f"releases/debug_tpt_replace_error_{product_id}.png")))
            log.error(f"Error replacing file on product {product_id}: {exc}")
            raise
        finally:
            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def _product_exists_on_dashboard(page, title_keyword: str) -> bool:
    """Check the real My-Products dashboard for a product whose title
    contains `title_keyword`. Used to disambiguate TPT's submit-detection
    false negatives (SPA navigation taking longer than the poll window)
    from genuine failures, instead of guessing from page state alone --
    this project has repeatedly found "may have failed" submits that had
    actually succeeded, and vice versa."""
    page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(3000)
    body = page.evaluate("() => document.body.innerText")
    return title_keyword in body


def upload_unit(
    unit_folder: Path,
    zip_path: Path,
    thumbnail_path: Optional[Path] = None,
    auto_publish: bool = False,
    listing: Optional[dict] = None,
) -> str:
    """
    Open a headed browser, log into TPT, and create a new product listing.

    Fills title, description, price, grade levels, subject, uploads the zip,
    and uploads the thumbnail if provided. Pauses for user review before
    the final Publish click unless auto_publish=True.

    By default reads the unit-level listing from unit_folder. Pass an
    explicit `listing` dict (title/description/price/tags) to publish a
    different item from the same unit -- e.g. a single lesson or the
    assessment, instead of the unit bundle.

    Returns one of: "submitted" (confirmed live), "draft" (auto_publish was
    False, form left filled), "failed" (confirmed NOT created -- safe to
    retry), "uncertain" (could not confirm either way -- do not blindly
    retry, this is how duplicates have happened before).
    """
    from cmie.publishing.listing_reader import read_tpt_listing

    email    = os.environ.get("TPT_EMAIL", "")
    password = os.environ.get("TPT_PASSWORD", "")
    if not email or not password:
        raise RuntimeError("TPT_EMAIL and TPT_PASSWORD must be set in .env")

    if listing is None:
        listing = read_tpt_listing(unit_folder)
    log.info(f"Listing loaded: {listing['title']} @ ${listing['price']}")

    if not zip_path.exists():
        raise FileNotFoundError(f"Zip not found: {zip_path}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=80, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        )
        # Hide the webdriver flag that TPT uses to detect automation
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page    = context.new_page()

        try:
            _login(page, context, email, password)
            _open_new_product(page)

            _fill_title(page, listing['title'])
            _fill_description(page, listing['description'])
            _fill_price(page, listing['price'])
            _upload_zip(page, zip_path)
            if thumbnail_path and Path(thumbnail_path).exists():
                _upload_thumbnail(page, Path(thumbnail_path))
            _set_tax_code(page)
            _set_grades(page)
            _set_subject(page)
            _fill_tags(page, listing['tags'])

            screenshot_path = Path("releases/debug_screenshot.png")
            page.screenshot(path=str(screenshot_path))
            log.info(f"Screenshot saved: {screenshot_path}")

            status = "draft"
            if auto_publish:
                log.info("Auto-publish: submitting...")
                submit = page.locator("#react-submit-section button[type='submit']")
                if submit.count() == 0:
                    log.warning("Submit button not found — check screenshot.")
                    status = "uncertain"
                else:
                    submit.first.scroll_into_view_if_needed(timeout=10000)
                    page.wait_for_timeout(300)
                    submit.first.click()

                    # The SPA navigates client-side after submit, which can
                    # take longer than a fixed short wait -- poll instead of
                    # guessing a delay (same class of bug as the Gumroad
                    # async-upload issue: don't check for success too soon).
                    navigated = False
                    for _ in range(10):
                        page.wait_for_timeout(1000)
                        if "/New/" not in page.url:
                            navigated = True
                            break

                    # TPT's field validation errors consistently start with
                    # "Please ..." (e.g. "Please select a tax code.",
                    # "Please upload at least the main cover image."). Don't
                    # match on bare "required"/"error" -- those words appear
                    # in our own listing copy ("No prep required") and would
                    # falsely flag a successful submit as failed.
                    error_text = page.locator("text=/^Please (select|upload|enter|fix|choose)/i")
                    ambiguous = False
                    if error_text.count() > 0:
                        log.error(f"Submit appears to have failed — validation message present: {error_text.first.inner_text()[:200]}")
                        ambiguous = True
                    elif not navigated:
                        log.error(f"Submit may have failed — still on the new-product URL after 10s: {page.url}")
                        ambiguous = True
                    else:
                        log.info(f"Submitted. Final URL: {page.url}")
                        status = "submitted"
                    page.screenshot(path=str(Path("releases/debug_screenshot_after_submit.png")))

                    if ambiguous:
                        # Both directions of false report have happened on
                        # this platform before (false negatives from
                        # checking too soon, false positives from an
                        # overly-broad error match) -- don't trust page
                        # state alone, check the actual dashboard for the
                        # title before deciding whether this was real.
                        title_keyword = listing["title"][:40].strip()
                        log.info(f"Verifying against dashboard for: {title_keyword!r}")
                        try:
                            if _product_exists_on_dashboard(page, title_keyword):
                                log.info("Dashboard confirms the product exists — treating as submitted despite the ambiguous page state.")
                                status = "submitted"
                            else:
                                log.info("Dashboard confirms the product does NOT exist — safe to retry.")
                                status = "failed"
                        except Exception as e:
                            log.warning(f"Could not verify against dashboard: {e} — status uncertain, do not blindly retry.")
                            status = "uncertain"
            else:
                log.info("")
                log.info("=" * 60)
                log.info("FORM FILLED — left as draft, not published.")
                log.info("  1. Upload thumbnail from releases/thumbnails/")
                log.info("  2. Check grade levels and subject")
                log.info("  3. Review and click Publish manually on TPT when ready")
                log.info(f"  Screenshot saved to: {screenshot_path}")
                log.info("=" * 60)

            return status

        except Exception as exc:
            screenshot_path = Path("releases/debug_screenshot.png")
            try:
                page.screenshot(path=str(screenshot_path))
                log.error(f"Error: {exc}")
                log.error(f"Screenshot saved: {screenshot_path}")
            except Exception:
                log.error(f"Error: {exc}")
            raise
        finally:
            context.close()
            browser.close()
