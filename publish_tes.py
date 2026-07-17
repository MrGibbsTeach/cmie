"""
CLI: publish a unit's bundle to TES via Playwright.

Usage:
    python publish_tes.py --unit year7_networks_hardware_unit1
    python publish_tes.py --unit year7_networks_hardware_unit1 --price 9.99

TES upload is a 5-step wizard (Description -> Add Files -> Categories ->
Licence -> Publish). This script fills all 5 steps and stops at the final
"Publish" screen WITHOUT checking the copyright confirmation box or
clicking "Publish now" -- the resource is saved as a draft on your Author
Dashboard for manual review, same pattern as the TPT/Gumroad scripts.

Credentials: set TES_EMAIL and TES_PASSWORD in .env. Session cookies are
cached in .tes_session.json after the first successful login.
Pricing: set TES_PRICE_GBP in .env (default 9.99). TES uses GBP.
"""
import argparse
import logging
import os
import re
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

TES_BASE            = "https://www.tes.com"
TES_LOGIN_URL       = f"{TES_BASE}/authn/sign-in"
TES_UPLOAD_URL      = f"{TES_BASE}/my-resources"
TES_UPLOAD_FORM_URL = f"{TES_BASE}/teaching-resource/upload"
COOKIES_FILE        = PROJECT_ROOT / ".tes_session.json"

# Defaults that fit this project's content (Lower Secondary / Year 7
# Australian Digital Technologies units sold as a full unit bundle).
DEFAULT_AGE_RANGE  = "11-14"
DEFAULT_CURRICULUM = "Australian"
DEFAULT_SUBJECT    = "Computing"
DEFAULT_RESOURCE_TYPE = "Unit of work"


# ---------------------------------------------------------------------------
# Login (mirrors the cookie-cache + form-login fallback pattern used by
# publish_tpt.py / publish_gumroad.py, instead of relying solely on the
# manual browser.py::setup() flow)
# ---------------------------------------------------------------------------

def _save_session(context) -> None:
    import json
    cookies = context.cookies()
    COOKIES_FILE.write_text(json.dumps(cookies, indent=2), encoding="utf-8")
    log.info(f"Session saved to {COOKIES_FILE}")


def _load_session(context) -> bool:
    import json
    if not COOKIES_FILE.exists():
        return False
    try:
        cookies = json.loads(COOKIES_FILE.read_text(encoding="utf-8"))
        context.add_cookies(cookies)
        log.info("TES session cookies loaded from file.")
        return True
    except Exception as e:
        log.warning(f"Could not load TES session file: {e}")
        return False


def _check_logged_in(page) -> bool:
    # The real unauthenticated redirect target is /authn/sign-in.
    return "authn/sign-in" not in page.url and "tes.com/register" not in page.url


def _login(page, context, email: str, password: str) -> None:
    if _load_session(context):
        page.goto(TES_UPLOAD_URL, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        if _check_logged_in(page):
            log.info("Logged in via saved TES session cookies.")
            return
        log.info("Saved TES session expired — trying form login.")

    if not email or not password:
        raise RuntimeError(
            "No TES_EMAIL/TES_PASSWORD in .env and no saved session. "
            "Either set those in .env, or run: "
            "python -c \"from cmie.publishing.browser import setup; setup()\" to log in manually once."
        )

    page.goto(TES_LOGIN_URL, wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(1500)

    email_field = page.get_by_label("Email", exact=False)
    if email_field.count() == 0:
        email_field = page.locator("input[type='email'], input[name*='email' i], input[placeholder*='email' i]")
    email_field.first.fill(email)

    password_field = page.locator("input[type='password']")
    password_field.first.fill(password)
    page.wait_for_timeout(500)

    submit = page.get_by_role("button", name=re.compile(r"log.?in|sign.?in|continue", re.I))
    if submit.count() > 0:
        submit.first.click()
    else:
        password_field.first.press("Enter")

    try:
        page.wait_for_url(lambda u: "sign-in" not in u and "authn" not in u, timeout=15000)
    except Exception:
        pass

    page.wait_for_timeout(1500)
    if not _check_logged_in(page):
        raise RuntimeError(
            "TES login failed. Check TES_EMAIL/TES_PASSWORD in .env, or the login form's "
            "selectors may have changed -- check releases/debug_tes_login_error.png."
        )

    _save_session(context)
    log.info("TES form login succeeded.")


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
    else:
        raise FileNotFoundError(f"No TES listing found in {unit_folder}")

    if len(title) > 100:
        title = title[:100].rsplit(" ", 1)[0]

    return {"title": title, "description": description}


# ---------------------------------------------------------------------------
# TES upload flow -- a 5-step wizard, not a single-page form. Each step's
# fields only exist in the DOM once that step is reached, so this can't be
# filled out of order.
# ---------------------------------------------------------------------------

def _take_debug_screenshot(page, name: str) -> None:
    path = RELEASES_ROOT / f"debug_tes_{name}.png"
    page.screenshot(path=str(path))
    log.info(f"Screenshot: {path}")


def _navigate_to_upload(page, context, email: str, password: str) -> None:
    page.goto(TES_UPLOAD_URL, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    if not _check_logged_in(page):
        _login(page, context, email, password)

    # Navigate directly to the known upload-form URL -- the "Add resource"
    # nav link is not reliably the first match Playwright finds (a hidden
    # duplicate exists elsewhere in the page), so clicking it is flaky.
    page.goto(TES_UPLOAD_FORM_URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2000)
    log.info(f"Upload form (step 1, Description): {page.url}")


def _step1_description(page, title: str, description: str) -> None:
    title_input = page.locator("input[placeholder*='Title' i], input#title, input[name='title']")
    title_input.first.click()
    title_input.first.fill(title[:60])
    log.info(f"Title filled: {title[:60]}")

    # TES uses a markdown editor (CodeMirror) -- raw markdown (headings,
    # bullets, **bold**) is supported and rendered, so no HTML conversion
    # is needed here unlike Gumroad/TPT's rich-text editors.
    cm = page.locator(".CodeMirror")
    page.evaluate(
        "(text) => navigator.clipboard.writeText(text).catch(() => {})",
        description[:3000],
    )
    cm.first.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Control+v")
    page.wait_for_timeout(800)
    log.info("Description filled.")

    page.get_by_role("button", name="Continue").first.click()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(2000)
    log.info(f"Step 2 (Add Files): {page.url}")


def _step2_add_files(page, zip_path: Path, resource_type: str = DEFAULT_RESOURCE_TYPE) -> None:
    with page.expect_file_chooser(timeout=10000) as fc:
        page.get_by_role("button", name="Upload").first.click()
    fc.value.set_files(str(zip_path))
    log.info(f"Uploading: {zip_path.name}")

    # Wait for the upload progress bar to finish before continuing.
    page.wait_for_timeout(5000)

    type_select = page.locator("select").nth(2)
    type_select.select_option(label=resource_type)
    log.info(f"Resource type set: {resource_type}")
    page.wait_for_timeout(500)

    # Cover image upload is deliberately skipped here -- it shares its
    # file-input discovery with the zip upload in a way that's easy to mix
    # up (set_input_files on the wrong input would silently replace the
    # zip with the image instead). "Default preview" (auto-generated from
    # the uploaded file) is left as-is. Add a real cover image manually,
    # or revisit this once the cover-image input's selector is confirmed
    # safe to target independently.

    page.get_by_role("button", name="Continue").last.click()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(2000)
    log.info(f"Step 3 (Categories): {page.url}")


def _step3_categories(
    page,
    age_range: str = DEFAULT_AGE_RANGE,
    curriculum: str = DEFAULT_CURRICULUM,
    subject: str = DEFAULT_SUBJECT,
) -> None:
    # Select by element id, not position -- an "additional age range"
    # select sometimes mounts between the visible fields, shifting any
    # index-based locator and silently selecting the wrong dropdown.
    page.locator("#main-age-range").select_option(label=age_range)
    page.wait_for_timeout(400)
    page.locator("#curriculum").select_option(label=curriculum)
    page.wait_for_timeout(400)
    page.locator("#main-subject").select_option(label=subject)
    page.wait_for_timeout(400)
    log.info(f"Categories set: age={age_range}, curriculum={curriculum}, subject={subject}")

    page.get_by_role("button", name="Continue").last.click()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(2000)
    log.info(f"Step 4 (Licence): {page.url}")


def _step4_licence(page, price_gbp: float) -> None:
    if price_gbp <= 0:
        # "Sell my resource" (the default tab) enforces a £1.00 minimum --
        # true free requires the separate "Share for free" tab. Found
        # live: lead magnets built with price=0 were silently landing at
        # £1.00 because this function always used the Sell tab.
        page.get_by_text("Share for free", exact=False).first.click()
        log.info("Selected 'Share for free' tab (price <= 0).")
        page.wait_for_timeout(500)
    else:
        # "Sell my resource" is the default-selected tab; just set the price.
        price_input = page.locator("#spinner")
        price_input.click(click_count=3)
        price_input.fill(f"{price_gbp:.2f}")
        log.info(f"Price set: £{price_gbp:.2f}")
        page.wait_for_timeout(500)

    page.get_by_role("button", name="Continue").last.click()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(2000)
    log.info(f"Step 5 (Publish preview): {page.url}")


# ---------------------------------------------------------------------------
# Main publish flow
# ---------------------------------------------------------------------------

def publish_unit(unit_id: str, price_gbp: float = PRICE_GBP) -> None:
    from cmie.publishing.browser import automation_chrome

    unit_folder = RELEASES_ROOT / unit_id

    # Prefer the cleaned customer-facing "_PUBLIC" bundle zip -- a unit now
    # has 9 different zips (7 lessons + assessment + bundle), and picking
    # the alphabetically-last one is not reliable for selecting the bundle.
    public_candidates = sorted((RELEASES_ROOT / "artifacts").glob(f"{unit_id}_*_PUBLIC.zip"))
    if public_candidates:
        zip_path = public_candidates[-1]
    else:
        candidates = sorted((RELEASES_ROOT / "artifacts").glob(f"{unit_id}*.zip"))
        candidates = [c for c in candidates if "test" not in c.name.lower() and "_PUBLIC" not in c.name]
        if not candidates:
            raise FileNotFoundError(f"No zip found for {unit_id} in releases/artifacts/")
        zip_path = candidates[-1]
        log.warning(f"No cleaned _PUBLIC zip found for {unit_id} -- falling back to {zip_path.name}.")

    email    = os.environ.get("TES_EMAIL", "")
    password = os.environ.get("TES_PASSWORD", "")

    listing = _read_listing(unit_folder)
    log.info(f"Publishing to TES: {listing['title']} @ £{price_gbp:.2f}")
    log.info(f"Zip: {zip_path.name}")

    with automation_chrome() as (context, page):
        try:
            _navigate_to_upload(page, context, email, password)
            _step1_description(page, listing["title"], listing["description"])
            _step2_add_files(page, zip_path)
            _step3_categories(page)
            _step4_licence(page, price_gbp)

            _take_debug_screenshot(page, f"{unit_id}_step5_preview")
            log.info("")
            log.info("=" * 60)
            log.info("FORM FILLED — saved as a draft, NOT published.")
            log.info("  Review the draft on your TES Author Dashboard, then")
            log.info("  manually check the copyright box and click 'Publish now'.")
            log.info(f"  Screenshot: releases/debug_tes_{unit_id}_step5_preview.png")
            log.info("=" * 60)

        except Exception as e:
            _take_debug_screenshot(page, f"{unit_id}_error")
            log.error(f"Error: {e}")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a unit's bundle to TES")
    parser.add_argument("--unit", required=True, help="Unit ID, e.g. year7_networks_hardware_unit1")
    parser.add_argument("--price", type=float, default=PRICE_GBP, help="Price in GBP")
    args = parser.parse_args()

    publish_unit(args.unit, args.price)


if __name__ == "__main__":
    main()
