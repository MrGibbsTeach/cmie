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

    `channel="chromium"` is a THIRD fix, found the same day after the above
    two turned out unreliable on their own: Playwright silently substitutes
    a completely different binary (chrome-headless-shell, not full Chromium)
    whenever launch(headless=True) is called with no explicit channel or
    executable_path -- which is every verify_*.py script and anything else
    that launches headless. That shell binary ignores --ssl-version-max
    entirely (packet-capture confirmed: still sends a full TLS 1.3
    ClientHello with key_share/ECH) and hits the identical
    ERR_CONNECTION_RESET. Pinning channel="chromium" forces the real
    Chromium binary even in headless mode, where the flag is honored
    (packet-capture-verified, twice, against a real teacherspayteachers.com
    load). This is why the fix "worked once" (automation_chrome(), which is
    always headless=False and never hit the substitution) and "failed later"
    (a headless=True verify script, which did).

    2026-08-21: `channel="chromium"` alone stopped working in this same cloud
    sandbox -- the pip `playwright` package installed at session start
    (1.62.0) expects a Chromium revision under Playwright's own registry that
    doesn't match the revision actually pre-installed at
    `$PLAYWRIGHT_BROWSERS_PATH/chromium` (a plain symlink, not a
    registry-registered "chromium" channel), so `channel="chromium"` looks
    for a binary that was never downloaded (and re-downloading it is blocked
    in this sandbox). Passing `executable_path` directly at that symlink
    sidesteps the channel lookup entirely and launches the exact same real
    Chromium binary the channel fix was pinning to, so the TLS-1.2-cap flag
    is still honored. Falls back to the old channel="chromium" behavior when
    no such pre-installed binary is present (e.g. a differently-provisioned
    sandbox), so this doesn't regress the fix above.
    """
    proxy = cloud_proxy_config()
    if not proxy:
        return {}
    kwargs = {
        "proxy": proxy,
        "args": ["--ignore-certificate-errors", "--ssl-version-max=tls1.2"],
    }
    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    preinstalled = Path(browsers_path) / "chromium" if browsers_path else None
    if preinstalled and preinstalled.exists():
        kwargs["executable_path"] = str(preinstalled)
    else:
        kwargs["channel"] = "chromium"
    return kwargs


def cloud_context_kwargs() -> dict:
    """Context-level counterpart to cloud_launch_kwargs() -- pass as **kwargs
    to new_context() (or merge into launch_persistent_context(), which takes
    both launch- and context-level args together)."""
    return {"ignore_https_errors": True} if cloud_proxy_config() else {}


_SAME_SITE_MAP = {
    "no_restriction": "None",
    "lax": "Lax",
    "strict": "Strict",
    "unspecified": "Lax",
    "none": "None",
}


def normalize_cookies(raw_cookies: list[dict]) -> list[dict]:
    """
    Convert a raw browser-extension cookie export (e.g. Cookie-Editor) into
    the exact shape Playwright's BrowserContext.add_cookies() requires.
    Already-correct Playwright-format cookies pass through unchanged.

    Cookie-Editor exports use `expirationDate` (unix seconds) instead of
    Playwright's `expires`, and lowercase/differently-named `sameSite` values
    ("no_restriction", "lax", "strict", "unspecified") instead of Playwright's
    exact "None"/"Lax"/"Strict" -- add_cookies() raises if sameSite isn't one
    of those three exact strings. First hit as a live failure on TPT_SESSION_JSON
    in the Claude Code cloud environment (2026-08-19); applied everywhere cookies
    get loaded from a file or env var so it can't recur on Gumroad/TES/Pinterest.
    """
    normalized = []
    for c in raw_cookies:
        same_site = c.get("sameSite", "Lax")
        if same_site not in ("Strict", "Lax", "None"):
            same_site = _SAME_SITE_MAP.get(str(same_site).lower(), "Lax")
        cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c.get("path", "/"),
            "httpOnly": bool(c.get("httpOnly", False)),
            "secure": bool(c.get("secure", False)),
            "sameSite": same_site,
        }
        if c.get("session"):
            cookie["expires"] = -1
        else:
            expires = c.get("expires", c.get("expirationDate", -1))
            cookie["expires"] = expires if expires is not None else -1
        normalized.append(cookie)
    return normalized


def _ensure_display() -> "subprocess.Popen | None":
    """
    headless=False (needed for form-fill scripts like publish_tes.py that
    rely on a real rendered page) has no X server to attach to in this cloud
    sandbox -- Chromium exits immediately with "Missing X server or
    $DISPLAY" (first hit 2026-08-21, previously worked around by manually
    wrapping the whole script in `xvfb-run`). Starting a throwaway Xvfb
    server here whenever $DISPLAY isn't already set means every headed
    launch site (not just the one that happened to be run under
    xvfb-run manually) works unattended. No-op wherever a real/virtual
    display already exists (a normal desktop run, or one already wrapped in
    xvfb-run).
    """
    import os
    import shutil
    import subprocess
    import time

    if os.environ.get("DISPLAY") or not shutil.which("Xvfb"):
        return None
    display = ":99"
    proc = subprocess.Popen(
        ["Xvfb", display, "-screen", "0", "1280x1024x24", "-nolisten", "tcp"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    os.environ["DISPLAY"] = display
    return proc


def _alternate_local_chromium(exclude: str | None) -> str | None:
    """Find another locally-installed Chromium build's executable, excluding
    the one at `exclude` (a full path). Playwright's default browser
    resolution can point at a build that's specifically broken for
    launch_persistent_context() while working fine for plain launch() --
    confirmed live 2026-08-22 on this machine, chromium-1208 crashed every
    persistent-context launch (exitCode -2147483645, no useful message)
    while chromium-1223, installed alongside it, worked immediately. Rather
    than hardcode a revision number that goes stale the next time
    Playwright's pinned version changes, scan the standard ms-playwright
    cache dir for any other chromium-* build and use whichever isn't the
    one that just failed."""
    base = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or (Path.home() / "AppData" / "Local" / "ms-playwright"))
    if not base.exists():
        return None
    exclude_norm = str(Path(exclude)).lower() if exclude else None
    for entry in sorted(base.glob("chromium-*"), reverse=True):
        for exe_name in ("chrome.exe", "chrome", "headless_shell.exe", "headless_shell"):
            candidate = entry / "chrome-win64" / exe_name
            if not candidate.exists():
                candidate = entry / "chrome-linux" / exe_name
            if candidate.exists() and str(candidate).lower() != exclude_norm:
                return str(candidate)
    return None


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

    xvfb = None if headless else _ensure_display()
    try:
        with sync_playwright() as pw:
            try:
                context = pw.chromium.launch_persistent_context(
                    user_data_dir=str(AUTOMATION_PROFILE),
                    headless=headless,
                    slow_mo=slow_mo,
                    args=extra_args,
                    ignore_default_args=["--enable-automation"],
                    **cloud_kwargs,
                    **cloud_context_kwargs(),
                )
            except Exception as e:
                failed_exe = cloud_kwargs.get("executable_path")
                alternate = _alternate_local_chromium(failed_exe)
                if not alternate:
                    raise
                log.warning(
                    f"launch_persistent_context failed with the default Chromium build "
                    f"({e}) -- retrying with an alternate local build: {alternate}"
                )
                retry_kwargs = dict(cloud_kwargs)
                retry_kwargs.pop("channel", None)
                retry_kwargs["executable_path"] = alternate
                context = pw.chromium.launch_persistent_context(
                    user_data_dir=str(AUTOMATION_PROFILE),
                    headless=headless,
                    slow_mo=slow_mo,
                    args=extra_args,
                    ignore_default_args=["--enable-automation"],
                    **retry_kwargs,
                    **cloud_context_kwargs(),
                )
            page = context.new_page()
            try:
                yield context, page
            finally:
                page.close()
                context.close()
    finally:
        if xvfb:
            xvfb.terminate()
            xvfb.wait(timeout=5)


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
