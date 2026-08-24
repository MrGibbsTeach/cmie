"""
check_tpt_backlog.py -- surfaces exactly what's live on Gumroad/TES but
still missing from TPT, since TPT publishing is local-only (Cloudflare
blocks the cloud sandbox's browser fingerprint regardless of cookie
validity -- see AUTONOMOUS_LOG.md's 2026-08-24 entry, not fixable via
session refresh). Meant to be run on this machine whenever catching up
on the TPT backlog, instead of piecing it together from AUTONOMOUS_LOG.md.

Two checks:
  - Units (data/units/UPCOMING_QUEUE.md): file-based, instant -- a
    completed unit without a matching entry in bundle_urls.json (which
    only ever gets written as part of a successful TPT publish) hasn't
    reached TPT yet.
  - Lead magnets (data/units/RESOURCE_DROP_QUEUE.md): no equivalent
    tracking file exists for these, so this does a live TPT dashboard
    search per completed item using this machine's trusted local
    browser session (the same one every other local TPT automation in
    this project relies on).

Usage:
    python check_tpt_backlog.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
UPCOMING_QUEUE = PROJECT_ROOT / "data" / "units" / "UPCOMING_QUEUE.md"
RESOURCE_DROP_QUEUE = PROJECT_ROOT / "data" / "units" / "RESOURCE_DROP_QUEUE.md"
BUNDLE_URLS = PROJECT_ROOT / "data" / "units" / "bundle_urls.json"


def _checked_units() -> list[str]:
    text = UPCOMING_QUEUE.read_text(encoding="utf-8")
    return re.findall(r"- \[x\].*\((year7_\w+)\)", text)


def _checked_lead_magnets() -> list[tuple[str, int]]:
    text = RESOURCE_DROP_QUEUE.read_text(encoding="utf-8")
    return [(m[0], int(m[1])) for m in
            re.findall(r"- \[x\] (year7_\w+) — Lesson (\d+)", text)]


def main() -> None:
    bundle_urls = json.loads(BUNDLE_URLS.read_text(encoding="utf-8"))

    checked_units = _checked_units()
    missing_units = [u for u in checked_units if u not in bundle_urls]
    lead_magnets = _checked_lead_magnets()

    print(f"Queues: {len(checked_units)} completed unit(s), "
          f"{len(lead_magnets)} completed lead magnet(s).\n")

    if missing_units:
        print(f"UNITS missing a TPT bundle URL ({len(missing_units)}):")
        for u in missing_units:
            print(f"  - {u}")
    else:
        print("UNITS: all completed units have a TPT bundle URL on file.")

    lead_magnet_backlog: list[tuple[str, int]] = []
    if lead_magnets:
        print(f"\nChecking TPT live for {len(lead_magnets)} lead magnet(s) "
              f"(opens a browser window briefly)...")
        from cmie.publishing.browser import automation_chrome
        from cmie.publishing.tpt import _is_logged_in
        from verify_tpt_listings import (
            _unit_topic_keyword, _lesson_topic_keyword, find_unit_product_urls,
        )

        with automation_chrome() as (context, page):
            if not _is_logged_in(page):
                print("  Not logged in to TPT locally -- can't verify lead magnets.")
                print("  Run: python publish_tpt.py --save-session")
            else:
                for unit_id, lesson in lead_magnets:
                    keyword = _lesson_topic_keyword(unit_id, lesson) or _unit_topic_keyword(unit_id)
                    products = find_unit_product_urls(page, keyword)
                    found = any("free" in p["t"].lower() for p in products)
                    print(f"  - {unit_id} lesson {lesson}: {'found' if found else 'MISSING'}")
                    if not found:
                        lead_magnet_backlog.append((unit_id, lesson))

    total = len(missing_units) + len(lead_magnet_backlog)
    print(f"\n=== TPT backlog: {total} item(s) ===")
    if not total:
        print("Nothing to do -- TPT is fully caught up.")
        return

    for u in missing_units:
        print(f"  UNIT   {u}")
        print(f"         python produce_unit.py --unit-config data/units/{u}.json  "
              f"(if not already built)")
        print(f"         python publish_tpt.py --unit {u} --part all --publish")
    for u, l in lead_magnet_backlog:
        print(f"  LESSON {u} lesson {l}")
        print(f"         python make_lead_magnet.py --unit {u} --lesson {l}")
        print(f"         python publish_lead_magnets.py --unit {u} --lesson {l} --platform tpt")


if __name__ == "__main__":
    main()
