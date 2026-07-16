"""
check_revenue.py — Pull earnings from TPT, Gumroad, and TES.

Usage:
    python check_revenue.py              # print summary, don't save
    python check_revenue.py --save       # print + write REVENUE.md
    python check_revenue.py --platform tpt
    python check_revenue.py --platform gumroad
    python check_revenue.py --platform tes
    python check_revenue.py --headless   # run browsers without a visible window

Credentials: copy .env.example to .env and fill in TPT_EMAIL/PASSWORD,
GUMROAD_TOKEN (or GUMROAD_EMAIL/PASSWORD), TES_EMAIL/PASSWORD.
Saved sessions from the publish scripts (.tpt_session.json etc.) are reused automatically.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles default to cp1252, which can't encode the box-drawing
# characters in the section headers below — crash-proof stdout/stderr.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
REVENUE_MD   = PROJECT_ROOT / "REVENUE.md"

TPT_COOKIES_FILE     = PROJECT_ROOT / ".tpt_session.json"
GUMROAD_COOKIES_FILE = PROJECT_ROOT / ".gumroad_session.json"
TES_COOKIES_FILE     = PROJECT_ROOT / ".tes_session.json"


# ── Playwright browser helper ─────────────────────────────────────────────────

def _make_context(pw, headless: bool):
    browser = pw.chromium.launch(
        headless=headless,
        slow_mo=50,
        channel="chrome",
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    )
    context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return browser, context


def _load_cookies(context, path: Path) -> bool:
    if not path.exists():
        return False
    try:
        cookies = json.loads(path.read_text(encoding="utf-8"))
        context.add_cookies(cookies)
        log.info(f"Session loaded from {path.name}")
        return True
    except Exception as e:
        log.warning(f"Could not load session {path.name}: {e}")
        return False


def _save_cookies(context, path: Path) -> None:
    path.write_text(json.dumps(context.cookies(), indent=2), encoding="utf-8")
    log.info(f"Session saved to {path.name}")


# ── TPT ───────────────────────────────────────────────────────────────────────

def check_tpt(headless: bool) -> dict:
    """
    Navigate to the TPT Seller Dashboard earnings page and extract:
    - total lifetime earnings
    - total sales count
    - current balance (unpaid)
    Returns a dict with keys: total_earnings, sales_count, balance, raw_text, error
    """
    from playwright.sync_api import sync_playwright

    result = {"platform": "TPT", "currency": "USD", "error": None}

    with sync_playwright() as pw:
        browser, context = _make_context(pw, headless)
        page = context.new_page()

        try:
            _load_cookies(context, TPT_COOKIES_FILE)

            # Login check first: /My-Products is a known-good authenticated
            # page (used by the publish flow). An expired session redirects
            # to /Request-Authorization?authModal=login. The old Earnings URL
            # 404s in place when logged out, which made the previous
            # URL-based login check silently pass and misreport
            # "page layout may have changed".
            log.info("TPT: checking login state via My-Products...")
            page.goto(
                "https://www.teacherspayteachers.com/My-Products",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            page.wait_for_timeout(4000)

            if re.search(r"Request-Authorization|authModal=login|/Login", page.url, re.I):
                # Session expired. Deliberately do NOT auto-attempt form
                # login: repeated automated TPT logins previously triggered
                # bot detection and temporarily locked the account.
                raise RuntimeError(
                    "TPT session expired (.tpt_session.json no longer valid). "
                    "Refresh it manually once: python publish_tpt.py --save-session "
                    "(automated form login is disabled here — it has triggered "
                    "TPT bot detection and an account lock before)."
                )

            # Both /Seller-Dashboard/Earnings and /My-Products were dead
            # ends for real numbers -- /My-Products only shows each
            # product's listing PRICE, not actual sales/earnings, which
            # made this silently report list prices as "revenue" before.
            # /My-Sales is the real sales report page (confirmed live: it
            # shows "Sales $X.XX Earnings $Y.YY ... Showing 1-N of N
            # results" as one line for the account's whole lifetime sales
            # history when no date filter is applied).
            log.info("TPT: navigating to Sales Reports (My-Sales)...")
            page.goto(
                "https://www.teacherspayteachers.com/My-Sales",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            page.wait_for_timeout(3000)
            page_text = page.inner_text("body")

            amounts = re.findall(r'\$[\d,]+\.?\d*', page_text)
            log.info(f"TPT: found dollar amounts on page: {amounts[:10]}")

            total_earnings = None
            total_sales_amount = None
            m = re.search(
                r'Sales\s*\$?([\d,]+\.?\d*)\s*Earnings\s*\$?([\d,]+\.?\d*)',
                page_text, re.IGNORECASE,
            )
            if m:
                total_sales_amount = float(m.group(1).replace(",", ""))
                total_earnings = float(m.group(2).replace(",", ""))

            # Balance (unpaid payout) is a separate real page, not the
            # sales-report figure -- lifetime earnings and current payable
            # balance are two different numbers (balance can be $0 after a
            # payout clears even with real lifetime earnings).
            balance = None
            page.goto(
                "https://www.teacherspayteachers.com/Account-Balance",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            page.wait_for_timeout(2000)
            balance_text = page.inner_text("body")
            m = re.search(r'Account Balance\s*\$?([\d,]+\.?\d*)', balance_text, re.IGNORECASE)
            if m:
                balance = float(m.group(1).replace(",", ""))

            # Sales count from "Showing 1-N of N results"
            sales_count = None
            m = re.search(r'Showing\s+[\d,]+-[\d,]+\s+of\s+([\d,]+)\s+results', page_text, re.IGNORECASE)
            if m:
                sales_count = int(m.group(1).replace(",", ""))

            result["total_earnings"]      = total_earnings
            result["total_sales_amount"]  = total_sales_amount
            result["balance"]             = balance
            result["sales_count"]         = sales_count
            result["raw_amounts"]         = amounts[:10]

            if total_earnings is None:
                result["error"] = "Could not extract earnings from /My-Sales — page layout may have changed. Check manually."
            else:
                log.info(f"TPT: total_earnings={total_earnings}, total_sales_amount={total_sales_amount}, balance={balance}, sales={sales_count}")

        except Exception as e:
            result["error"] = str(e)
            log.error(f"TPT error: {e}")
        finally:
            context.close()
            browser.close()

    return result


# ── Gumroad ───────────────────────────────────────────────────────────────────

def check_gumroad(headless: bool) -> dict:
    """
    Check Gumroad revenue via the API (preferred) or dashboard scrape.
    Uses GUMROAD_TOKEN from .env for the API call.
    Falls back to Playwright dashboard scrape if no token.
    Returns: total_revenue (AUD), sales_count, per_product list
    """
    import urllib.request, urllib.parse

    result = {"platform": "Gumroad", "currency": "AUD", "error": None}

    token = os.getenv("GUMROAD_TOKEN", "")

    if token:
        log.info("Gumroad: using API with GUMROAD_TOKEN...")
        try:
            sales      = []
            page_key   = None
            page_num   = 0

            while True:
                params = {"access_token": token, "page_key": page_key or ""}
                url    = "https://api.gumroad.com/v2/sales?" + urllib.parse.urlencode(
                    {k: v for k, v in params.items() if v}
                )
                req  = urllib.request.urlopen(url, timeout=15)
                data = json.loads(req.read().decode())

                if not data.get("success"):
                    raise RuntimeError(f"Gumroad API error: {data.get('message')}")

                batch = data.get("sales", [])
                sales.extend(batch)
                page_num += 1
                log.info(f"Gumroad API: page {page_num}, {len(batch)} sales fetched so far ({len(sales)} total)")

                page_key = data.get("next_page_key")
                if not page_key or not batch:
                    break

            # Sum revenue
            total_revenue = sum(
                float(s.get("price", 0)) / 100.0  # Gumroad price is in cents
                for s in sales
                if not s.get("refunded", False)
            )

            # Per-product breakdown
            by_product: dict[str, dict] = {}
            for s in sales:
                name = s.get("product_name", "Unknown")
                if name not in by_product:
                    by_product[name] = {"count": 0, "revenue": 0.0}
                if not s.get("refunded", False):
                    by_product[name]["count"]   += 1
                    by_product[name]["revenue"] += float(s.get("price", 0)) / 100.0

            result["total_revenue"] = total_revenue
            result["sales_count"]   = len([s for s in sales if not s.get("refunded", False)])
            result["by_product"]    = by_product
            log.info(f"Gumroad: total_revenue=A${total_revenue:.2f}, sales={result['sales_count']}")
            return result

        except Exception as e:
            log.warning(f"Gumroad API failed ({e}), falling back to Playwright...")

    # Fallback: Playwright dashboard scrape
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser, context = _make_context(pw, headless)
        page = context.new_page()
        try:
            _load_cookies(context, GUMROAD_COOKIES_FILE)
            page.goto("https://app.gumroad.com/dashboard", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)

            if "login" in page.url or "signup" in page.url:
                email    = os.getenv("GUMROAD_EMAIL", "")
                password = os.getenv("GUMROAD_PASSWORD", "")
                if not email or not password:
                    raise RuntimeError("Not logged in and no Gumroad credentials in .env.")
                page.locator("input[type='email']").first.fill(email)
                page.locator("input[type='password']").first.fill(password)
                page.locator("input[type='password']").first.press("Enter")
                page.wait_for_url(lambda u: "login" not in u, timeout=20000)
                _save_cookies(context, GUMROAD_COOKIES_FILE)
                page.goto("https://app.gumroad.com/dashboard", wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(3000)

            page_text = page.inner_text("body")
            amounts   = re.findall(r'A?\$[\d,]+\.?\d*|[\d,]+\.?\d*\s*AUD', page_text)
            log.info(f"Gumroad dashboard amounts: {amounts[:10]}")

            total_revenue = None
            m = re.search(r'(?:Total\s+Revenue|Revenue)\s*A?\$?([\d,]+\.?\d*)', page_text, re.IGNORECASE)
            if m:
                total_revenue = float(m.group(1).replace(",", ""))

            result["total_revenue"] = total_revenue
            result["raw_amounts"]   = amounts[:10]
            if total_revenue is None:
                result["error"] = "Could not extract revenue from dashboard — check manually."

        except Exception as e:
            result["error"] = str(e)
            log.error(f"Gumroad error: {e}")
        finally:
            context.close()
            browser.close()

    return result


# ── TES ───────────────────────────────────────────────────────────────────────

def check_tes(headless: bool) -> dict:
    """
    Navigate to TES Author Dashboard to extract earnings.
    TES shows earnings per resource in Resource Management.
    Returns: total_earnings (GBP), sales_count, per_product list
    """
    from playwright.sync_api import sync_playwright

    result = {"platform": "TES", "currency": "GBP", "error": None}

    with sync_playwright() as pw:
        browser, context = _make_context(pw, headless)
        page = context.new_page()

        try:
            # Reuse publish_tes.py's own _login() rather than a second,
            # weaker duplicate here -- this file's own inline login had no
            # session-refresh retry and was silently failing (zero £
            # amounts found) right when TES's session had died, which this
            # project has seen happen within an hour or two more than
            # once. _login() already handles session-cookie load, the
            # form-login fallback, and re-saving the refreshed session to
            # the same .tes_session.json this function reads.
            sys.path.insert(0, str(PROJECT_ROOT))
            from publish_tes import _login as _tes_login

            log.info("TES: navigating to author dashboard...")
            _tes_login(page, context, os.getenv("TES_EMAIL", ""), os.getenv("TES_PASSWORD", ""))
            page.goto(
                "https://www.tes.com/teaching-resources/dashboard/overview",
                wait_until="domcontentloaded",
                timeout=45000,
            )
            page.wait_for_timeout(5000)

            # Earnings live on the author dashboard (overview shows balance,
            # resource-management shows per-resource earnings).
            for url in [
                "https://www.tes.com/teaching-resources/dashboard/overview",
                "https://www.tes.com/teaching-resources/dashboard/resource-management/uploads",
            ]:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(5000)
                page_text = page.inner_text("body")

                # Look for GBP amounts
                gbp_amounts = re.findall(r'£[\d,]+\.?\d*', page_text)
                log.info(f"TES ({url}): found GBP amounts: {gbp_amounts[:10]}")

                if gbp_amounts:
                    break

            page_text = page.inner_text("body")

            # Extract total earnings
            total_earnings = None
            sales_count    = None

            for pattern in [
                # Dashboard overview shows "Your balances\nGBP\n£0.00"
                r'GBP\s*£([\d,]+\.?\d*)',
                r'(?:Total\s+)?(?:Earnings?|Revenue|Income)\s*£?([\d,]+\.?\d*)',
                r'£?([\d,]+\.?\d*)\s*(?:Total\s+)?(?:Earnings?|Revenue)',
            ]:
                m = re.search(pattern, page_text, re.IGNORECASE)
                if m:
                    val = float(m.group(1).replace(",", ""))
                    if val > 0 or total_earnings is None:
                        total_earnings = val
                    break

            # Sales count — dashboard overview shows "Purchases\n0" (label first)
            m = re.search(r'Purchases?\s*\n\s*([\d,]+)', page_text, re.IGNORECASE)
            if not m:
                m = re.search(r'([\d,]+)\s+(?:Sales?|Downloads?|Purchases?)', page_text, re.IGNORECASE)
            if m:
                sales_count = int(m.group(1).replace(",", ""))

            # Per-resource earnings: TES shows them in the resource list
            # Look for table rows with resource names + earnings
            by_product = {}
            rows = page.locator("tr, [data-testid*='resource'], .resource-item").all()
            for row in rows[:50]:
                try:
                    row_text = row.inner_text()
                    gbp_m    = re.search(r'£([\d,]+\.?\d*)', row_text)
                    if gbp_m:
                        earnings  = float(gbp_m.group(1).replace(",", ""))
                        # Use first chunk of text as product name
                        name_part = row_text.split("\n")[0].strip()[:80]
                        if name_part and earnings >= 0:
                            by_product[name_part] = {"revenue": earnings}
                except Exception:
                    pass

            result["total_earnings"] = total_earnings
            result["sales_count"]    = sales_count
            result["by_product"]     = by_product
            result["raw_amounts"]    = re.findall(r'£[\d,]+\.?\d*', page_text)[:10]

            if total_earnings is None:
                result["error"] = "Could not extract earnings from TES — page layout may have changed. Check manually at tes.com/author-dashboard."
            else:
                log.info(f"TES: total_earnings=£{total_earnings:.2f}, sales={sales_count}")

        except Exception as e:
            result["error"] = str(e)
            log.error(f"TES error: {e}")
        finally:
            context.close()
            browser.close()

    return result


# ── REVENUE.md writer ─────────────────────────────────────────────────────────

def write_revenue_md(results: list[dict]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# FocusLab Digital — Revenue Tracker",
        f"_Last updated: {now}_",
        "",
    ]

    for r in results:
        platform = r["platform"]
        currency = r.get("currency", "?")
        symbol   = {"USD": "$", "AUD": "A$", "GBP": "£"}.get(currency, currency)
        error    = r.get("error")

        lines.append(f"## {platform}")

        if error:
            lines.append(f"⚠️  {error}")
            lines.append("")
            continue

        # Revenue / earnings key differs by platform. Don't use `or` here —
        # a legitimate 0.0 is falsy and would hide the revenue line entirely.
        revenue = r.get("total_revenue")
        if revenue is None:
            revenue = r.get("total_earnings")
        sales = r.get("sales_count")

        if revenue is not None:
            lines.append(f"**Total revenue:** {symbol}{revenue:,.2f} {currency}")
        if sales is not None:
            lines.append(f"**Total sales:** {sales}")

        by_product = r.get("by_product", {})
        if by_product:
            lines.append("")
            lines.append("| Product | Sales | Revenue |")
            lines.append("|---------|-------|---------|")
            for name, data in sorted(by_product.items(), key=lambda x: -x[1].get("revenue", 0)):
                count   = data.get("count", "—")
                rev_val = data.get("revenue", 0)
                lines.append(f"| {name[:60]} | {count} | {symbol}{rev_val:.2f} |")

        raw = r.get("raw_amounts", [])
        if raw and revenue is None:
            lines.append(f"_Raw amounts found on page: {', '.join(raw[:8])}_")

        lines.append("")

    # Summary line
    tpt_r     = next((r for r in results if r["platform"] == "TPT"), {})
    gumroad_r = next((r for r in results if r["platform"] == "Gumroad"), {})
    tes_r     = next((r for r in results if r["platform"] == "TES"), {})

    tpt_usd    = tpt_r.get("total_earnings") or 0.0
    gumroad_aud = gumroad_r.get("total_revenue") or 0.0
    tes_gbp    = tes_r.get("total_earnings") or 0.0

    lines += [
        "---",
        "## Summary",
        f"| Platform | Revenue |",
        f"|----------|---------|",
        f"| TPT | ${tpt_usd:,.2f} USD |",
        f"| Gumroad | A${gumroad_aud:,.2f} AUD |",
        f"| TES | £{tes_gbp:,.2f} GBP |",
        "",
        "_Note: figures are in each platform's native currency. "
        "TPT pays in USD, Gumroad in AUD, TES in GBP._",
        "",
    ]

    REVENUE_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nREVENUE.md written to {REVENUE_MD}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Check FocusLab Digital revenue across platforms")
    parser.add_argument(
        "--platform", choices=["tpt", "gumroad", "tes"], default=None,
        help="Check only one platform (default: all three)",
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Write results to REVENUE.md",
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run browser without a visible window",
    )
    args = parser.parse_args()

    results = []

    if args.platform in (None, "tpt"):
        print("\n── TPT ──────────────────────────────────")
        r = check_tpt(headless=args.headless)
        results.append(r)
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
        else:
            te = r.get("total_earnings")
            tsa = r.get("total_sales_amount")
            print(f"  Gross sales    : {'$%.2f USD' % tsa if tsa is not None else '?'}")
            print(f"  Total earnings : {'$%.2f USD' % te if te is not None else '? (not found on page)'}")
            print(f"  Balance        : ${r.get('balance') or 0:.2f} USD")
            print(f"  Sales count    : {r.get('sales_count') if r.get('sales_count') is not None else '?'}")

    if args.platform in (None, "gumroad"):
        print("\n── Gumroad ──────────────────────────────")
        r = check_gumroad(headless=args.headless)
        results.append(r)
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
        else:
            print(f"  Total revenue : A${r.get('total_revenue') or 0:.2f} AUD")
            print(f"  Sales count   : {r.get('sales_count') if r.get('sales_count') is not None else '?'}")
            bp = r.get("by_product", {})
            if bp:
                print("  By product:")
                for name, data in sorted(bp.items(), key=lambda x: -x[1].get("revenue", 0)):
                    print(f"    {name[:55]:<55}  A${data['revenue']:.2f}  ({data['count']} sale{'s' if data['count'] != 1 else ''})")

    if args.platform in (None, "tes"):
        print("\n── TES ──────────────────────────────────")
        r = check_tes(headless=args.headless)
        results.append(r)
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
        else:
            print(f"  Total earnings : £{r.get('total_earnings') or 0:.2f} GBP")
            print(f"  Sales count    : {r.get('sales_count') if r.get('sales_count') is not None else '?'}")

    if args.save:
        write_revenue_md(results)

    print()


if __name__ == "__main__":
    main()
