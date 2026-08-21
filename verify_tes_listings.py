"""
verify_tes_listings.py — post-publish integrity check for TES resources.
Mirrors verify_tpt_listings.py's checks, adapted to TES: reloads each
resource's edit page and reads the actual title/description field values
(TES's own markdown editor renders raw markdown natively, so unlike
TPT/Gumroad the risk here is empty fields or literal unescaped HTML, not
unrendered **bold**).

Pass --lead-magnet-lesson N to additionally check a free lead magnet
specifically (matched by title containing "free"): title mentions
"Lesson N", no leftover AI-generation artifact language in the description
(the \bAI\b pattern produce_unit.py's QA stage already uses), and the
resource's price shows as £0.00 / free rather than TES's £1.00 "Sell my
resource" minimum.

Usage:
    python verify_tes_listings.py --keyword "Unit 1"
    python verify_tes_listings.py --keyword "Debugging" --lead-magnet-lesson 5
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def find_resource_ids(page, keyword: str) -> list[dict]:
    """`keyword` is currently unused for pre-filtering -- the dashboard's
    "Edit" links don't reliably carry title text nearby, so this collects
    every resource ID and lets the per-resource title check (in
    check_resource) report what it actually finds instead. Filtering
    happens by reading the caller's output, not by guessing here."""
    page.goto(
        "https://www.tes.com/teaching-resources/dashboard/resource-management/uploads",
        wait_until="domcontentloaded", timeout=20000,
    )
    page.wait_for_timeout(3000)
    # TES's OneTrust cookie-consent banner sits on top of the dashboard on a
    # fresh session (no prior consent cookie) and intercepts the "Show all"
    # click, timing it out even though the button itself is visible.
    accept_btn = page.locator("#onetrust-accept-btn-handler")
    if accept_btn.count() > 0:
        try:
            accept_btn.first.click(timeout=5000)
            page.wait_for_timeout(1000)
        except Exception:
            pass
    if page.get_by_text("Show all", exact=False).count() > 0:
        page.get_by_text("Show all", exact=False).first.click()
        page.wait_for_timeout(2500)
    hrefs = page.evaluate(
        """() => Array.from(document.querySelectorAll("a[href*='uploader/v2/']")).map(a => a.href)"""
    )
    seen, unique = set(), []
    for h in hrefs:
        rid_match = re.search(r"uploader/v2/(\d+)", h)
        if not rid_match:
            continue
        rid = rid_match.group(1)
        if rid not in seen:
            seen.add(rid)
            unique.append({"id": rid, "url": f"https://www.tes.com/uploader/v2/{rid}"})
    return unique


def _lead_magnet_findings(title: str, desc: str, body: str, lesson: int) -> list[str]:
    """Checks specific to a lead-magnet (free lesson sampler) resource --
    only run against a resource whose title looks like the lead magnet
    itself (contains "free"), so these never false-positive against a
    unit's other paid TES resources."""
    findings = []
    if not re.search(rf"\bLesson\s+{lesson}\b", title, re.I):
        findings.append(
            f"Lead magnet title doesn't mention 'Lesson {lesson}' -- wrong lesson number or stale title."
        )
    # Same AI-leftover-language pattern produce_unit.py's stage_qa uses
    # (\bAI\b) -- these are Digital Technologies units, not the shelved AI
    # series, so a literal "AI" mention in a lead magnet is a real leak.
    if re.search(r"\bAI\b", desc):
        findings.append("AI-leftover language found in lead magnet description (matched \\bAI\\b).")

    # TES lead magnets have previously landed at the "Sell my resource" tab's
    # £1.00 minimum instead of genuinely free (see PROGRESS.md/AUTONOMOUS_LOG.md:
    # "TES lead magnets are £1.00, not £0.00" -- publish_tes.py's
    # _step4_licence now selects the "Share for free" tab for price<=0 to
    # fix this at publish time; this is the post-publish check for it).
    # Deliberately not checking for the word "free" as a signal -- the
    # sampler's own marketing description always says "for FREE!" whether
    # or not the price actually landed at £0, so that word can't
    # distinguish a real £0.00 listing from a mispriced one. "£1.00" /
    # "£0.00" are numeric and specific, so those are what's used here.
    # Best-effort: TES's exact price page text for an *existing* resource's
    # edit view wasn't confirmed live while building this check -- treat a
    # finding as "verify manually", not certain proof either way.
    if "£1.00" in body:
        findings.append("Lead magnet page shows £1.00 -- looks like it landed on TES's paid minimum instead of genuinely free.")
    elif "£0.00" not in body:
        findings.append("Could not find '£0.00' on the page -- pricing may not be genuinely free; verify manually.")
    return findings


def check_resource(page, rid: str, lead_magnet_lesson: int | None = None) -> dict:
    findings = []
    page.goto(f"https://www.tes.com/uploader/v2/{rid}", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(2500)

    title = page.evaluate(
        """() => { const el = document.querySelector("input[placeholder*='Title' i], input#title, input[name='title']"); return el ? el.value : null; }"""
    )
    if not title:
        findings.append("Could not read title field -- resource may not exist or session expired.")
        return {"id": rid, "title": None, "findings": findings}

    desc = page.evaluate(
        """() => { const el = document.querySelector(".CodeMirror"); return el && el.CodeMirror ? el.CodeMirror.getValue() : (el ? el.innerText : ''); }"""
    ) or ""

    if len(desc.strip()) < 50:
        findings.append(f"Description looks empty/near-empty ({len(desc.strip())} chars).")

    if re.search(r"<[a-zA-Z][a-zA-Z0-9]*(\s|>)", desc):
        findings.append("Literal HTML tag characters found in description.")

    if lead_magnet_lesson is not None and "free" in title.lower():
        # Price only ever renders on the Licence step (step 4) of the
        # uploader -- the base /uploader/v2/{id} URL this function already
        # navigated to for the title/description fields is step 1
        # (Description), whose innerText never contains "£0.00" or "£1.00"
        # regardless of actual pricing. Checking step 1's body text (as this
        # did before) made the price finding below fire as a false positive
        # on every lead magnet, confirmed 2026-08-21 (real price is genuinely
        # free per publish_tes.py's own "Selected 'Share for free' tab" log
        # line, but body had no £ sign at all because it was still on step
        # 1). Navigate to the licence step specifically for this check.
        page.goto(f"https://www.tes.com/uploader/v2/{rid}/licence-editor",
                  wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(2000)
        body = page.evaluate("() => document.body.innerText") or ""
        findings.extend(_lead_magnet_findings(title, desc, body, lead_magnet_lesson))

    return {"id": rid, "title": title, "findings": findings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keyword", default="Unit 1")
    parser.add_argument("--lead-magnet-lesson", type=int, default=None,
                         help="Also run lead-magnet-specific checks (title has "
                              "'Lesson N', no AI-leftover language, shows as free) "
                              "against resources whose title contains 'free'")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright
    import sys as _sys
    _sys.path.insert(0, str(PROJECT_ROOT))
    from publish_tes import _login
    from cmie.publishing.browser import cloud_launch_kwargs, cloud_context_kwargs
    from dotenv import load_dotenv
    load_dotenv()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **cloud_launch_kwargs())
        context = browser.new_context(**cloud_context_kwargs())
        page = context.new_page()
        _login(page, context, os.getenv("TES_EMAIL", ""), os.getenv("TES_PASSWORD", ""))

        resources = find_resource_ids(page, args.keyword)
        print(f"Found {len(resources)} resource(s) total on the dashboard.\n")

        any_findings = False
        checked = 0
        for r in resources:
            result = check_resource(page, r["id"], args.lead_magnet_lesson)
            title = result["title"] or ""
            if args.keyword and args.keyword not in title:
                continue
            checked += 1
            status = "OK" if not result["findings"] else "ISSUES FOUND"
            print(f"[{status}] {title[:70]}")
            print(f"         {r['url']}")
            for f in result["findings"]:
                print(f"         - {f}")
                any_findings = True
            print()
        print(f"Checked {checked} resource(s) matching {args.keyword!r}.\n")

        browser.close()

    if any_findings:
        print("Some resources need attention -- see findings above.")
        sys.exit(1)
    else:
        print("All checked resources look clean.")


if __name__ == "__main__":
    main()
