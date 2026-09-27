"""
add_follow_cta.py -- appends a "Follow the store" call-to-action to every
live lead-magnet (free sample) product's description.

Followers get a TPT notification email whenever the store publishes a new
listing, so this is the cheapest lever this catalog has for turning a free
download into a repeat visitor instead of a one-off. The 20 lead magnets are
the highest-intent place to ask, since a teacher who already downloaded one
free lesson is the person most likely to want the next one.

Product ids come from data/tpt_retag_log.json (kind == "leadmagnet"), so
retag_tpt_catalog.py must have run at least once first. Uses the same
read/apply/verify path as retag_tpt_catalog.py (see edit_product_title() in
cmie/publishing/tpt.py for why the "Upload thumbnails now" radio matters).

Usage:
    python add_follow_cta.py --dry-run
    python add_follow_cta.py
"""
from __future__ import annotations

import argparse
import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

FOLLOW_MARKER = "FocusLab Digital"
FOLLOW_LINE = (
    "⭐ Like this free lesson? Click the Follow button on our store page "
    "(FocusLab Digital) to get notified the moment new free lessons and full "
    "units go live -- no spam, just new resources."
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ids", help="Comma-separated product ids (default: all logged lead magnets)")
    args = ap.parse_args()

    import retag_tpt_catalog as retag
    from cmie.publishing.browser import automation_chrome
    from cmie.publishing.tpt import _login

    log = retag.load_log()
    if args.ids:
        ids = [i.strip() for i in args.ids.split(",")]
    else:
        ids = [pid for pid, v in log.items() if v.get("kind") == "leadmagnet" and v.get("status") == "OK"]
    print(f"{len(ids)} lead magnet(s) to process (dry_run={args.dry_run})", flush=True)

    with automation_chrome() as (ctx, page):
        _login(page, ctx, os.environ.get("TPT_EMAIL", ""), os.environ.get("TPT_PASSWORD", ""))

        for pid in ids:
            try:
                st = retag.read_state(page, pid)
                if not st["has_editor"]:
                    print(f"[{pid}] SKIPPED (no description editor)", flush=True)
                    continue
                if FOLLOW_LINE[:30] in st["desc"]:
                    print(f"[{pid}] SKIPPED (already has the CTA)", flush=True)
                    continue

                plan = {
                    "kind": "leadmagnet",
                    "old_title": st["title"],
                    "new_title": st["title"],
                    "grades_to_tick": [],
                    "tick_au": False,
                    "append_desc": False,  # this script appends its OWN line below
                }

                if args.dry_run:
                    print(f"[{pid}] DRY-RUN would append CTA. Current desc tail: {st['desc'][-150:]!r}", flush=True)
                    continue

                ed = page.locator('[contenteditable="true"]').first
                ed.click()
                page.keyboard.press("Control+End")
                page.keyboard.press("Enter")
                page.keyboard.type(FOLLOW_LINE, delay=0)
                page.wait_for_timeout(500)

                page.get_by_text("Upload thumbnails now", exact=False).first.click()
                page.wait_for_timeout(800)
                submit = page.locator("#react-submit-section button[type='submit']").first
                submit.scroll_into_view_if_needed(timeout=10000)
                submit.click()
                page.wait_for_url(re.compile(r"/Product/"), timeout=60000)

                st2 = retag.read_state(page, pid)
                if FOLLOW_LINE[:30] not in st2["desc"]:
                    raise RuntimeError("CTA not found in description after save")

                log.setdefault(pid, {}).update({"status": "OK", "follow_cta": True})
                retag.save_log(log)
                print(f"[{pid}] OK", flush=True)
            except Exception as e:
                log.setdefault(pid, {}).update({"follow_cta_error": str(e)[:300]})
                retag.save_log(log)
                print(f"[{pid}] ERROR {str(e)[:300]}", flush=True)
            page.wait_for_timeout(1000)


if __name__ == "__main__":
    main()
