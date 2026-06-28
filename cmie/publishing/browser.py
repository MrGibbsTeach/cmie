"""
Shared browser context using a dedicated CMIE automation Chrome profile.

This uses a SEPARATE Chrome profile directory from the user's main Chrome,
so the automation browser can run alongside regular Chrome with no conflicts.

First-time setup:
    python -c "from cmie.publishing.browser import setup; setup()"

This opens a Chrome window where you log in to TPT, TES, Gumroad etc.
Cookies are saved in the automation profile. All future runs use them.

Usage:
    from cmie.publishing.browser import automation_chrome

    with automation_chrome() as (context, page):
        page.goto("https://example.com")
        ...
"""
import logging
import os
from contextlib import contextmanager
from pathlib import Path

log = logging.getLogger(__name__)

# Dedicated profile directory — separate from main Chrome so both can coexist
AUTOMATION_PROFILE = Path(os.environ.get(
    "CMIE_CHROME_PROFILE",
    str(Path.home() / "AppData" / "Local" / "CMIEChrome"),
))


@contextmanager
def automation_chrome(headless: bool = False, slow_mo: int = 200):
    """
    Yields (context, page) using the dedicated CMIE automation Chrome profile.
    Can run alongside regular Chrome with no conflicts.
    """
    from playwright.sync_api import sync_playwright

    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(AUTOMATION_PROFILE),
            channel="chrome",
            headless=headless,
            slow_mo=slow_mo,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.new_page()
        try:
            yield context, page
        finally:
            page.close()
            context.close()


def setup() -> None:
    """
    Open the automation browser for manual login.
    Log in to TES, Gumroad, and TPT in the browser that opens.
    Cookies are persisted in the automation profile for all future runs.
    Close the browser window when done -- the script exits automatically.
    """
    from playwright.sync_api import sync_playwright

    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)

    print(f"\nOpening CMIE automation browser (profile: {AUTOMATION_PROFILE})")
    print("Log in to TES, Gumroad, and TPT in the browser that opens.")
    print("Close the browser window when you are done with all logins.\n")

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(AUTOMATION_PROFILE),
            channel="chrome",
            headless=False,
            slow_mo=0,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.new_page()
        page.goto("https://www.tes.com/login")
        # Wait until the browser is closed by the user
        context.wait_for_event("close", timeout=0)

    print("\nSetup complete. All future automation runs will use these sessions.")
