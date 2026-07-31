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


def cloud_proxy_config() -> dict | None:
    """
    Explicit proxy server for Playwright, read from the standard env vars.

    Playwright/Chromium does NOT auto-respect HTTP_PROXY/HTTPS_PROXY the way
    curl/urllib/requests do -- it has to be passed explicitly at launch, or
    outbound connections from a proxied sandbox (e.g. the Claude Code cloud
    environment) get reset. No-op on a machine with no proxy configured
    (i.e. every local run), so safe to apply unconditionally.
    """
    server = (
        os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    )
    if not server:
        return None
    return {"server": server}


def cloud_launch_kwargs() -> dict:
    """
    Extra kwargs to merge into any chromium.launch()/launch_persistent_context()
    call so it works behind a proxied sandbox that does TLS-terminating
    interception (its own root CA Chromium doesn't trust out of the box).
    `--ignore-certificate-errors` is the pragmatic cert-trust fix -- avoids
    needing to import the sandbox's CA into Chromium's NSS store, which is
    fragile and environment-specific.

    `--ssl-version-max=tls1.2` is a second, separate fix for a distinct
    failure mode found by a live diagnostic run in the Claude Code cloud
    sandbox (2026-07-31): the reset happens BEFORE any certificate is ever
    exchanged -- the proxy resets the connection right after Chromium's own
    TLS 1.3 ClientHello, so --ignore-certificate-errors alone never even gets
    a chance to matter. Capping Chromium to TLS 1.2 avoids whatever about
    Chromium 141's TLS 1.3 ClientHello (tested: not just the PQ/Kyber key
    share) the sandbox's proxy can't handle. No-op locally (no proxy =>
    nothing changes).
    """
    proxy = cloud_proxy_config()
    if not proxy:
        return {}
    return {
        "proxy": proxy,
        "args": ["--ignore-certificate-errors", "--ssl-version-max=tls1.2"],
    }


def cloud_context_kwargs() -> dict:
    """Context-level counterpart to cloud_launch_kwargs() -- pass as **kwargs
    to new_context() (or merge into launch_persistent_context(), which takes
    both launch- and context-level args together)."""
    return {"ignore_https_errors": True} if cloud_proxy_config() else {}


@contextmanager
def automation_chrome(headless: bool = False, slow_mo: int = 200):
    """
    Yields (context, page) using the dedicated CMIE automation Chrome profile.
    Can run alongside regular Chrome with no conflicts.
    """
    from playwright.sync_api import sync_playwright

    AUTOMATION_PROFILE.mkdir(parents=True, exist_ok=True)

    extra_args = ["--disable-blink-features=AutomationControlled"]
    cloud_kwargs = cloud_launch_kwargs()
    if "args" in cloud_kwargs:
        extra_args += cloud_kwargs.pop("args")

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(AUTOMATION_PROFILE),
            headless=headless,
            slow_mo=slow_mo,
            args=extra_args,
            ignore_default_args=["--enable-automation"],
            **cloud_kwargs,
            **cloud_context_kwargs(),
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
