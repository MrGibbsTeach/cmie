"""
audit_lesson_numbers.py — verify every lesson product fixed by
fix_short_titles.py actually has the CORRECT lesson number in its title.

fix_short_titles.py derived each lesson's number from its position in the
unit config's topics array. Found live 2026-09-21 (game_design unit,
product 17047379): a same-unit keyword collision ("Building a Game" is a
substring of both topic 4's real title "Building a Game with Scratch"
AND topic 7's real live product title "Designing and Building a Game")
caused a product to be matched under the WRONG plan item and get the
WRONG lesson number baked into its new title (labeled "Lesson 4" when
its real content -- per its own description field, built once at
original publish time and never touched by this bug or by
fix_short_titles.py -- is genuinely Lesson 7).

The description field is the reliable ground truth: unlike the title
(which TPT truncates at 80 chars, and which fix_short_titles.py just
rewrote), the description was never edited by anything today, is not
length-limited, and its own first line is literally the full pre-bug
listing title including "| Lesson N" -- always intact.

For every one of the 13 affected units, finds all lesson products by
searching the unit's own (now-correct) short title, reads each one's
description ground truth, and fixes the title's lesson number if it
doesn't match. Reports every check, not just mismatches, so a clean run
is visible, not just silence.

Usage:
    python audit_lesson_numbers.py                # all 13 units
    python audit_lesson_numbers.py --unit year7_game_design_unit1
    python audit_lesson_numbers.py --dry-run
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

from fix_short_titles import AFFECTED_UNITS, extract_unit_short_title, truncate_80


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", help="Single unit_id (default: all 13 affected units)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    units = [args.unit] if args.unit else AFFECTED_UNITS

    import os
    from cmie.publishing.browser import automation_chrome
    from cmie.publishing.tpt import _login, edit_product_title
    from verify_tpt_listings import find_unit_product_urls

    email = os.environ.get("TPT_EMAIL", "")
    password = os.environ.get("TPT_PASSWORD", "")

    checked = 0
    mismatches = 0
    fixed = 0
    errors = 0

    with automation_chrome() as (context, page):
        _login(page, context, email, password)

        for unit_id in units:
            cfg = json.loads((UNITS_ROOT / f"{unit_id}.json").read_text(encoding="utf-8"))
            correct_short = extract_unit_short_title(cfg["title"])

            raw = find_unit_product_urls(page, correct_short)
            lesson_products = [
                p for p in raw
                if "free" not in p["t"].lower()
                and re.search(r"\|\s*Lesson\s*\d+\s*$", p["t"])
            ]
            print(f"\n=== {unit_id} ({len(lesson_products)} lesson products found) ===")

            for p in lesson_products:
                m_id = re.search(r"-(\d+)/?$", p["h"].rstrip("/"))
                m_title_num = re.search(r"Lesson\s*(\d+)\s*$", p["t"])
                if not m_id or not m_title_num:
                    continue
                product_id = m_id.group(1)
                title_lesson_num = int(m_title_num.group(1))

                edit_url = f"https://www.teacherspayteachers.com/itemsDigital/editNext/{product_id}"
                page.goto(edit_url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2000)
                body = page.inner_text("body")
                # The description's own first line is the untruncated
                # original title -- find its "| Lesson N" ground truth.
                desc_match = re.search(r"Lesson\s*(\d+)\s*\n\s*Essential question", body)
                checked += 1
                if not desc_match:
                    print(f"  [{product_id}] {p['t']!r} -- could not find ground-truth lesson number in description, SKIPPING")
                    continue
                true_lesson_num = int(desc_match.group(1))

                if true_lesson_num == title_lesson_num:
                    print(f"  [{product_id}] OK -- Lesson {title_lesson_num}: {p['t']!r}")
                    continue

                mismatches += 1
                lesson_title = p["t"].split("|")[0].strip()
                corrected = truncate_80(f"{lesson_title} | {correct_short} | Lesson {true_lesson_num}")
                print(f"  [{product_id}] MISMATCH -- title says Lesson {title_lesson_num}, description says Lesson {true_lesson_num}")
                print(f"    current: {p['t']!r}")
                print(f"    correct: {corrected!r}")

                if args.dry_run:
                    continue
                try:
                    edit_product_title(page, product_id, corrected)
                    fixed += 1
                    print(f"    FIXED.")
                except Exception as e:
                    errors += 1
                    print(f"    ERROR: {e}")

    print("\n" + "=" * 70)
    print(f"Checked: {checked}  Mismatches found: {mismatches}  Fixed: {fixed}  Errors: {errors}")


if __name__ == "__main__":
    main()
