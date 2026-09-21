"""
fix_short_titles.py — retroactively fix the extract_unit_short_title() bug
(cmie/generator/listing_generator.py, fixed 2026-09-21) on already-live TPT
products.

The bug: split(":")[-1] took the part AFTER the colon ("Unit 1 - Thinking
Like a Programmer") instead of the actual topic name BEFORE it
("Algorithms & Programming Logic") for every unit whose title uses the
"<Topic>: Unit N - <Subtitle>" format. That's 13 of this catalog's 15
units. It only affects TPT's per-lesson and per-assessment listings
(Gumroad/TES only ever get the bundle listing, which uses the full title
directly and was never affected).

Strategy: for each of the 13 units' 7 lessons + 1 assessment, find the
live product by a short keyword search (verify_tpt_listings.py's proven
find_unit_product_urls), then parse the REAL live title's own pipe-
delimited segments and replace ONLY the buggy middle segment -- never
substitute the config's topic wording for the lesson-title segment,
because it can have drifted from what was actually baked into the title
at generation time (found 2026-09-21: config says "Sequencing, Selection,
and Repetition", the live product is "Sequencing, Selection, Repetition",
no "and"). This keeps the fix surgical: only the part the bug actually
corrupted changes, nothing else.

Lead-magnet ("... FREE Sample ...") products use a completely different
title format and are never touched here -- make_lead_magnet.py reads the
unit title a different way and was never affected by this bug.

Never edits on an ambiguous match (0 or >1 dashboard hits, or a title
that doesn't fit the expected pipe-delimited shape) -- logs SKIPPED and
moves on rather than guessing. Prints a full summary table at the end.

Usage:
    python fix_short_titles.py                  # all 13 units
    python fix_short_titles.py --unit year7_algorithms_unit1   # one unit
    python fix_short_titles.py --dry-run         # compute + match only, no edits
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

PROJECT_ROOT = Path(__file__).parent
UNITS_ROOT = PROJECT_ROOT / "data" / "units"

AFFECTED_UNITS = [
    "year7_algorithms_unit1",
    "year7_cybersecurity_unit1",
    "year7_data_representation_unit1",
    "year7_digital_systems_unit1",
    "year7_game_design_unit1",
    "year7_networks_hardware_unit1",
    "year7_orientation_unit1",
    "year7_python_programming_unit1",
    "year7_robotics_physical_computing_unit1",
    "year7_spreadsheets_unit1",
    "year7_ux_design_unit1",
    "year7_web_design_unit1",
    "year7_ai_literacy_unit1",
]


def extract_unit_short_title(unit_title: str) -> str:
    """The FIXED version (mirrors cmie/generator/listing_generator.py)."""
    if ":" in unit_title:
        return unit_title.split(":")[0].strip()
    return unit_title.strip()


def old_buggy_short_title(unit_title: str) -> str:
    """The OLD, buggy version -- what's still actually live right now."""
    if ":" in unit_title:
        return unit_title.split(":")[-1].strip()
    return unit_title.strip()


def truncate_80(title: str) -> str:
    if len(title) > 80:
        return title[:80].rsplit(" ", 1)[0]
    return title


def build_search_plan(unit_id: str) -> list[dict]:
    """One entry per lesson + the assessment: just enough to find the
    right live product and know the correct short title to swap in.
    Deliberately does NOT carry a pre-built new title -- that's
    reconstructed from the matched product's own real title."""
    cfg = json.loads((UNITS_ROOT / f"{unit_id}.json").read_text(encoding="utf-8"))
    title = cfg["title"]
    topics = cfg["topics"]
    correct_short = extract_unit_short_title(title)
    buggy_short = old_buggy_short_title(title)
    # The part after the dash in "Unit N - Subtitle" -- unique per unit,
    # still present in the live (buggy) assessment title, so safe to
    # search on regardless of the bug. Keywords are short (first ~14-18
    # chars) since exact long phrases can miss real products whose
    # wording has drifted from the current config.
    subtitle = re.split(r"[–—-]", buggy_short)[-1].strip()

    disambiguate = subtitle[:20] if subtitle else correct_short[:20]

    plan = []
    for i, topic in enumerate(topics, start=1):
        lesson_title = topic["title"] if isinstance(topic, dict) else topic
        plan.append({
            "unit_id": unit_id,
            "part": f"lesson{i:02d}",
            "kind": "lesson",
            "lesson_num": i,
            "search_keyword": lesson_title[:16],
            # Some lesson-title prefixes are generic enough to collide
            # across units (found 2026-09-21: "Designing a Data" matches
            # both Databases' "Designing a Database" and Data
            # Representation's "Designing a Data Encoding Scheme").
            # Disambiguate by the unit's own subtitle fragment, which the
            # bug never touched and is still present in every affected
            # product's live title.
            "disambiguate": disambiguate,
            "correct_short": correct_short,
        })

    plan.append({
        "unit_id": unit_id,
        "part": "assessment",
        "kind": "assessment",
        "lesson_num": None,
        # Searching a lesson-style keyword for the assessment pulls back
        # every lesson product too (they all still carry the same buggy
        # "Unit 1 - Subtitle" segment) -- search the generic "Assessment
        # Pack" phrase instead (small, fixed result set across the whole
        # catalog) and disambiguate locally the same way.
        "search_keyword": "Assessment Pack",
        "disambiguate": disambiguate,
        "correct_short": correct_short,
    })
    return plan


def reconstruct_title(item: dict, live_title: str) -> str | None:
    """Replace ONLY the buggy middle segment of a real live title with
    the correct short title, preserving the real lesson-title segment
    exactly as it is live. Returns None if the live title doesn't fit a
    recognizable shape (never guess on an unfamiliar format).

    The old buggy short title ("Unit 1 - Thinking Like a Programmer", the
    full subtitle) is much longer than the correct one (the actual topic
    name, e.g. "Algorithms & Programming Logic"), so many live titles hit
    TPT's 80-char field limit and got word-boundary-truncated with the
    trailing "| Lesson N" dropped entirely, sometimes leaving a dangling
    "| " with nothing after it (confirmed live 2026-09-21: a real stored
    title reads 'Sequencing, Selection, Repetition | Unit 1 - Thinking
    Like a Programmer |'). The lesson number doesn't need to survive in
    the live title to reconstruct correctly -- it's already known
    independently from the unit config's topic order (item['lesson_num']),
    so this only trusts the live title for the one thing config wording
    can't be trusted for: the real lesson-title segment itself."""
    segments = [s.strip() for s in live_title.split("|")]

    if item["kind"] == "lesson":
        # Expected first segment: the real lesson title, e.g.
        # "Sequencing, Selection, Repetition". Reject if implausibly
        # long (something unfamiliar going on) or missing entirely.
        if len(segments) < 2 or not segments[0] or len(segments[0]) > 75:
            return None
        real_lesson_title = segments[0]
        return truncate_80(
            f"{real_lesson_title} | {item['correct_short']} | Lesson {item['lesson_num']}"
        )

    # Assessment: "<buggy short> | Assessment Pack | Lower Secondary",
    # possibly truncated the same way -- the suffix is fixed/known
    # regardless of what survived live, so just rebuild it outright.
    return truncate_80(f"{item['correct_short']} | Assessment Pack | Lower Secondary")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", help="Single unit_id (default: all 13 affected units)")
    parser.add_argument("--dry-run", action="store_true", help="Compute + match only, no edits")
    args = parser.parse_args()

    units = [args.unit] if args.unit else AFFECTED_UNITS
    full_plan = []
    for u in units:
        full_plan.extend(build_search_plan(u))

    print(f"Plan: {len(full_plan)} products across {len(units)} unit(s).\n")

    import os
    from cmie.publishing.browser import automation_chrome
    from cmie.publishing.tpt import _login, edit_product_title
    from verify_tpt_listings import find_unit_product_urls

    email = os.environ.get("TPT_EMAIL", "")
    password = os.environ.get("TPT_PASSWORD", "")

    results = []
    with automation_chrome() as (context, page):
        _login(page, context, email, password)

        for item in full_plan:
            def _search(keyword: str, require_disambiguate: bool = True, require_startswith: bool = False) -> list[dict]:
                raw = find_unit_product_urls(page, keyword)
                # Never touch lead-magnet ("FREE Sample") products --
                # different title format entirely, unaffected by this bug.
                out = [p for p in raw if "free" not in p["t"].lower()]
                if require_disambiguate:
                    out = [p for p in out if item["disambiguate"] in p["t"]]
                if require_startswith:
                    out = [p for p in out if p["t"].startswith(keyword)]
                return out

            matches = _search(item["search_keyword"])
            # Lesson-title wording can drift further than a short prefix
            # survives (found 2026-09-21: config "Debugging: Finding and
            # Fixing Logic Errors" vs live "Debugging Logic Errors") --
            # retry once with just the first word before giving up. Still
            # requires disambiguate -- a short first word alone
            # (`.includes()` matches anywhere in the title, not just the
            # start) is dangerous without it: "Adding" alone matched
            # Digital Media's unrelated ".. and Adding Music or Sound
            # Effects" lesson, found live 2026-09-21 via dry-run before
            # any edit was made.
            if len(matches) == 0 and item["kind"] == "lesson":
                first_word = item["search_keyword"].split(":")[0].split(" ")[0]
                if first_word and first_word != item["search_keyword"]:
                    matches = _search(first_word)
            # A title truncated hard enough to drop even the unit
            # subtitle (found 2026-09-21 on 3 AI Literacy lessons, whose
            # own topic titles run close to 80 chars alone) means the
            # disambiguate filter can never match -- retry once without
            # it, but require the match to START with the full-length
            # keyword (never the short first-word fallback) as the
            # substitute safety net, so an incidental mid-title substring
            # can never qualify.
            if len(matches) == 0:
                matches = _search(item["search_keyword"], require_disambiguate=False, require_startswith=True)

            if len(matches) != 1:
                status = f"SKIPPED ({len(matches)} non-free matches for '{item['search_keyword']}')"
                results.append({**item, "status": status, "old_title": "", "new_title": ""})
                print(f"[{item['unit_id']} {item['part']}] {status}")
                continue

            match = matches[0]
            new_title = reconstruct_title(item, match["t"])
            if new_title is None:
                status = f"SKIPPED (unexpected title shape: {match['t']!r})"
                results.append({**item, "status": status, "old_title": match["t"], "new_title": ""})
                print(f"[{item['unit_id']} {item['part']}] {status}")
                continue

            if new_title.strip() == match["t"].strip():
                status = "SKIPPED (already correct)"
                results.append({**item, "status": status, "old_title": match["t"], "new_title": new_title})
                print(f"[{item['unit_id']} {item['part']}] {status}")
                continue

            m = re.search(r"-(\d+)/?$", match["h"].rstrip("/"))
            if not m:
                status = f"SKIPPED (could not parse product id from {match['h']})"
                results.append({**item, "status": status, "old_title": match["t"], "new_title": new_title})
                print(f"[{item['unit_id']} {item['part']}] {status}")
                continue
            product_id = m.group(1)

            if args.dry_run:
                status = "DRY-RUN (would edit)"
                results.append({**item, "status": status, "old_title": match["t"], "new_title": new_title})
                print(f"[{item['unit_id']} {item['part']}] {status}: {match['t']!r} -> {new_title!r}")
                continue

            try:
                edit_product_title(page, product_id, new_title)
                status = "FIXED"
                results.append({**item, "status": status, "old_title": match["t"], "new_title": new_title})
                print(f"[{item['unit_id']} {item['part']}] {status}: {match['t']!r} -> {new_title!r}")
            except Exception as e:
                status = f"ERROR: {e}"
                results.append({**item, "status": status, "old_title": match["t"], "new_title": ""})
                print(f"[{item['unit_id']} {item['part']}] {status}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    fixed = [r for r in results if r["status"].startswith("FIXED")]
    skipped = [r for r in results if r["status"].startswith("SKIPPED")]
    errors = [r for r in results if r["status"].startswith("ERROR")]
    dry = [r for r in results if r["status"].startswith("DRY-RUN")]
    print(f"Fixed: {len(fixed)}  Skipped: {len(skipped)}  Errors: {len(errors)}  Dry-run: {len(dry)}")
    if skipped:
        print("\nSkipped (needs manual review):")
        for r in skipped:
            print(f"  {r['unit_id']} {r['part']}: {r['status']}")
    if errors:
        print("\nErrors:")
        for r in errors:
            print(f"  {r['unit_id']} {r['part']}: {r['status']}")


if __name__ == "__main__":
    main()
