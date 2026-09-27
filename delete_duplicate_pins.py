"""
delete_duplicate_pins.py -- one-off cleanup for a 2026-09-27 mistake: an
interactive session posted wave-3 Pinterest pins for 3 units
(year7_game_design_unit1, year7_python_programming_unit1,
year7_networks_hardware_unit1) without first pulling origin/main, missing
that the cloud "Marketing Push" routine (trig_01NNs1MXpfDNbwtmqisne9Br) had
already posted the identical wave 3 for those same 3 units on 2026-09-23.
Result: 9 pins live twice each (same title, same outbound TPT link).

Identified via a full board scrape (not log trust): every duplicate pair's
two pin ids share every digit except the last several -- the original
(2026-09-23) side always ends "...4833165xxx", the accidental repost
(2026-09-26) side always ends "...4833411xxx". Cross-checked against 2 pin
ids independently confirmed as originals in the 2026-09-23 run's own log
(1150599404833165795, 1150599404833165763) -- both fall on the "165xxx"
side, confirming the pattern rather than assuming it.

Deletes ONLY the 9 "411xxx" (2026-09-26, this session's) ids below, never
the originals. Explicitly authorized by the user (2026-09-27) after this
was found and reported -- this is the one case in this project where a
delete is warranted, per the "never delete without explicit authorization"
boundary in AUTONOMOUS_LOG.md.

Deletes one at a time, screenshots the Edit-Pin panel before each delete so
there is a visual record of exactly what was removed, and verifies removal
by re-requesting the pin's URL afterward (real 404 / removed-pin page).

Usage:
    python delete_duplicate_pins.py --dry-run
    python delete_duplicate_pins.py
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

SCRATCH = Path.home() / ".pinterest_scratch"

# (pin_id, title) -- the accidental 2026-09-26 duplicates only.
DUPLICATES = [
    ("1150599404833411738", "You Don't Need to Know How to Code to Teach Game Design"),
    ("1150599404833411763", "The Capstone: Students Design and Build a Complete Game"),
    ("1150599404833411714", "Playtesting & Iterating: The Lesson That Teaches Real Design"),
    ("1150599404833411786", "Loops in Python: The Lesson That Removes the Repetition"),
    ("1150599404833411805", "You Don't Need a Coding Background to Teach Python"),
    ("1150599404833411813", "The Capstone: Solving a Real Problem in Python"),
    ("1150599404833411977", "Network Security Basics: The Year 7 Lesson That Actually Matters"),
    ("1150599404833412004", "The Networking Capstone: Students Design Their Own Network"),
    ("1150599404833412038", "Turn Networking Theory Into Real Troubleshooting Skills"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    from cmie.publishing.browser import cloud_launch_kwargs, cloud_context_kwargs, normalize_cookies, block_known_ad_domains

    cookies_file = Path(".pinterest_session.json")
    if cookies_file.exists():
        cookies = json.loads(cookies_file.read_text(encoding="utf-8"))
    else:
        cookies = json.loads(os.environ["PINTEREST_SESSION_JSON"])

    SCRATCH.mkdir(exist_ok=True)
    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, **cloud_launch_kwargs())
        ctx = browser.new_context(viewport={"width": 1400, "height": 1000}, **cloud_context_kwargs())
        block_known_ad_domains(ctx)
        ctx.add_cookies(normalize_cookies(cookies))
        page = ctx.new_page()

        for pid, expected_title in DUPLICATES:
            page.goto(f"https://www.pinterest.com/pin/{pid}/", wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2500)
            live_title = page.title().split(" - ")[0].strip()
            if live_title != expected_title:
                print(f"[{pid}] SKIPPED -- live title {live_title!r} != expected {expected_title!r}, refusing to touch")
                results.append({"pid": pid, "status": "SKIPPED_TITLE_MISMATCH"})
                continue

            if args.dry_run:
                print(f"[{pid}] DRY-RUN would delete: {live_title}")
                results.append({"pid": pid, "status": "DRY_RUN"})
                continue

            page.get_by_role("button", name="More actions").first.click()
            page.wait_for_timeout(800)
            page.get_by_text("Edit Pin", exact=True).click()
            page.wait_for_timeout(2000)
            page.screenshot(path=str(SCRATCH / f"before_delete_{pid}.png"))

            page.get_by_role("button", name="Delete", exact=True).click()
            page.wait_for_timeout(1200)
            # Pinterest shows a confirmation dialog on top of the edit panel.
            confirm = page.get_by_role("button", name="Delete", exact=True)
            if confirm.count() > 0:
                confirm.last.click()
            page.wait_for_timeout(3000)
            page.screenshot(path=str(SCRATCH / f"after_delete_{pid}.png"))

            # Verify: reload the pin URL, it should no longer show the same title.
            page.goto(f"https://www.pinterest.com/pin/{pid}/", wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2500)
            after_title = page.title().split(" - ")[0].strip()
            deleted = after_title != expected_title
            print(f"[{pid}] {'DELETED' if deleted else 'STILL LIVE -- CHECK MANUALLY'}: was {expected_title!r}, now {after_title!r}")
            results.append({"pid": pid, "status": "DELETED" if deleted else "STILL_LIVE", "after_title": after_title})

        browser.close()

    out = SCRATCH / "delete_duplicate_pins_results.json"
    out.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
