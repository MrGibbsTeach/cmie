"""
publish_lead_magnets.py — publish a free lesson sampler (built by
make_lead_magnet.py) for a unit, to TPT and/or TES.

Defaults to the Lesson-1 sampler (the original behavior); pass --lesson N
to publish the sampler built from any other lesson (e.g. the "2nd free
lesson per unit" items in data/units/RESOURCE_DROP_QUEUE.md).

TPT has no draft state: this makes the resource live immediately (price $0).
TES always stops at a draft (per this project's standing rule) — the final
"Publish now" click stays a manual, human step on TES's Author Dashboard.
This is existing, pre-existing behavior for every TES publish in this
project (not lead-magnet-specific and not a new gate being added here).

Usage:
    python publish_lead_magnets.py --unit year7_networks_hardware_unit1 --platform tpt
    python publish_lead_magnets.py --unit year7_algorithms_unit1 --platform tpt --lesson 5
    python publish_lead_magnets.py --unit year7_networks_hardware_unit1 --platform tes
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Without this, cmie.publishing.tpt's log.info() calls (including the
# "Submitted successfully" / "Submit may have failed" lines) are silently
# dropped by Python's default WARNING-level root logger -- this script
# would only ever show warnings/errors and look like every run failed
# even when it succeeded, which is exactly what happened once already.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

PROJECT_ROOT = Path(__file__).parent
ARTIFACTS_ROOT = PROJECT_ROOT / "releases" / "artifacts"
PUBLIC_ROOT = PROJECT_ROOT / "releases" / "public"

# See make_lead_magnet.py's TRACKED_SOURCE_ROOT comment: releases/ is
# gitignored, so in a fresh clone (e.g. the cloud sandbox) only the subset
# of units the Resource Drop queue actually needs has been separately
# committed here, mirroring releases/public's sub-path layout.
TRACKED_SOURCE_ROOT = PROJECT_ROOT / "data" / "units" / "lead_magnet_source"
TRACKED_THUMBNAILS = TRACKED_SOURCE_ROOT / "thumbnails"


def _unit_root(unit_id: str, version: str) -> Path:
    local = PUBLIC_ROOT / f"{unit_id}_{version}"
    if local.exists():
        return local
    tracked = TRACKED_SOURCE_ROOT / f"{unit_id}_{version}"
    if tracked.exists():
        return tracked
    raise FileNotFoundError(
        f"No source folder for {unit_id}_{version} in either {local} or {tracked}"
    )


def _thumbnail_path(unit_id: str) -> Path:
    local = PROJECT_ROOT / "releases" / "thumbnails" / f"{unit_id}_thumbnail.png"
    if local.exists():
        return local
    return TRACKED_THUMBNAILS / f"{unit_id}_thumbnail.png"


def _short_topic(unit_title: str) -> str:
    topic = unit_title.split(":")[0].strip() if ":" in unit_title else unit_title.strip()
    return topic


def _read_unit_title(unit_id: str, version: str = "v001") -> str:
    listing = _unit_root(unit_id, version) / "06_Listings" / "unit" / "tpt_listing.md"
    first_line = listing.read_text(encoding="utf-8").splitlines()[0]
    title = first_line.lstrip("#").strip()
    # Drop the grade-band suffix in parentheses for the sampler's own title —
    # the full listing already carries that; the sampler title should stay short.
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
    return title


def _read_lesson_topics(unit_id: str) -> list[str]:
    """Real lesson topic titles, in order, from the unit's own config —
    used so a Lesson-N sampler's title/description name the actual lesson
    ("Debugging: Finding and Fixing Logic Errors") instead of a generic
    "Lesson N"."""
    config_path = PROJECT_ROOT / "data" / "units" / f"{unit_id}.json"
    if not config_path.exists():
        return []
    try:
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [t.get("title", "").strip() for t in cfg.get("topics", []) if t.get("title")]


def _read_lesson_topic(unit_id: str, lesson: int) -> str:
    topics = _read_lesson_topics(unit_id)
    if 1 <= lesson <= len(topics):
        return topics[lesson - 1]
    return f"Lesson {lesson}"


def build_listing(unit_id: str, version: str = "v001", lesson: int = 1) -> dict:
    unit_title = _read_unit_title(unit_id, version)
    topic = _short_topic(unit_title)

    if lesson == 1:
        # Kept byte-for-byte identical to the original text -- this is the
        # format already live for all 10 existing Lesson-1 free samples.
        sampler_title = f"{unit_title} — Lesson 1 FREE Sample"
        description = (
            f"Try Lesson 1 of \"{unit_title}\" for FREE!\n\n"
            f"This is the exact first lesson from our full 7-lesson {topic} unit — "
            "a complete, ready-to-teach PowerPoint deck, no prep required.\n\n"
            "Like what you see? The full unit includes:\n\n"
            "- 7 fully planned lessons with objectives and essential questions\n"
            "- Fully editable PowerPoint (PPTX) slide deck for every lesson\n"
            "- Unit roadmap / scope and sequence\n"
            "- Student workbook for print or digital use\n"
            "- Summative assessment task, rubric, and marking guide\n\n"
            "A quick review on this free sample helps a small independent "
            "teacher-store more than you'd think — thank you for the support!"
        )
        return {"title": sampler_title, "description": description}

    lesson_topic = _read_lesson_topic(unit_id, lesson)
    num_lessons = len(_read_lesson_topics(unit_id)) or 7

    # The unit title alone already blows past TPT's 80-char and TES's
    # 60-char title limits for Lesson 1 (both truncate at a word boundary).
    # Leading with the lesson topic instead of the unit title means the
    # part that's unique to this specific sampler ("Lesson N" + what it's
    # actually about) survives truncation on both platforms; only the
    # parenthetical unit context gets clipped, which is an acceptable loss.
    sampler_title = f"{lesson_topic} — Lesson {lesson} FREE Sample ({topic})"
    description = (
        f"Try Lesson {lesson} — \"{lesson_topic}\" — from \"{unit_title}\" for FREE!\n\n"
        f"This is the exact Lesson {lesson} deck from our full {num_lessons}-lesson "
        f"{topic} unit — a complete, ready-to-teach PowerPoint deck, no prep required.\n\n"
        "Like what you see? The full unit includes:\n\n"
        f"- {num_lessons} fully planned lessons with objectives and essential questions\n"
        "- Fully editable PowerPoint (PPTX) slide deck for every lesson\n"
        "- Unit roadmap / scope and sequence\n"
        "- Student workbook for print or digital use\n"
        "- Summative assessment task, rubric, and marking guide\n\n"
        "A quick review on this free sample helps a small independent "
        "teacher-store more than you'd think — thank you for the support!"
    )
    return {"title": sampler_title, "description": description}


def publish_to_tpt(unit_id: str, version: str = "v001", lesson: int = 1) -> str:
    from cmie.publishing.tpt import upload_unit

    zip_path = ARTIFACTS_ROOT / f"{unit_id}_lesson{lesson:02d}_FREE_{version}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Lead magnet zip not found: {zip_path}. Run make_lead_magnet.py first.")

    raw = build_listing(unit_id, version, lesson)
    title = raw["title"]
    if len(title) > 80:
        title = title[:80].rsplit(" ", 1)[0]

    listing = {
        "title": title,
        "description": raw["description"],
        "price": 0.0,
        "tags": ["Lessons", "Activities", "Career and Technical Education",
                 "Critical Thinking and Problem Solving"],
    }

    thumbnail_path = _thumbnail_path(unit_id)
    if not thumbnail_path.exists():
        raise FileNotFoundError(
            f"No thumbnail found for {unit_id} in releases/thumbnails/ or "
            f"{TRACKED_THUMBNAILS} — TPT requires one (auto-generation "
            "fails for zip/pptx uploads)."
        )

    unit_folder = PROJECT_ROOT / "releases" / unit_id
    status = upload_unit(unit_folder, zip_path, thumbnail_path=thumbnail_path, auto_publish=True, listing=listing)
    if status == "failed":
        print(f"Confirmed not created — retrying once for {unit_id}...")
        status = upload_unit(unit_folder, zip_path, thumbnail_path=thumbnail_path, auto_publish=True, listing=listing)
    if status != "submitted":
        print(f"WARNING: lead magnet publish for {unit_id} ended with status '{status}' — verify manually.")
    return status


def publish_to_tes(unit_id: str, version: str = "v001", lesson: int = 1) -> None:
    from cmie.publishing.browser import automation_chrome
    from publish_tes import (
        _navigate_to_upload, _step1_description, _step2_add_files,
        _step3_categories, _step4_licence, _take_debug_screenshot,
    )

    zip_path = ARTIFACTS_ROOT / f"{unit_id}_lesson{lesson:02d}_FREE_{version}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Lead magnet zip not found: {zip_path}. Run make_lead_magnet.py first.")

    raw = build_listing(unit_id, version, lesson)

    email = os.environ.get("TES_EMAIL", "")
    password = os.environ.get("TES_PASSWORD", "")

    print(f"Publishing lead magnet to TES: {raw['title']} @ £0.00")
    with automation_chrome() as (context, page):
        try:
            _navigate_to_upload(page, context, email, password)
            _step1_description(page, raw["title"], raw["description"])
            _step2_add_files(page, zip_path)
            _step3_categories(page)
            _step4_licence(page, 0.00)

            _take_debug_screenshot(page, f"{unit_id}_lead_magnet_l{lesson:02d}_step5_preview")
            print("=" * 60)
            print("FORM FILLED — saved as a draft, NOT published.")
            print("Review on the TES Author Dashboard, then manually check")
            print("the copyright box and click 'Publish now'.")
            print("=" * 60)
        except Exception as e:
            _take_debug_screenshot(page, f"{unit_id}_lead_magnet_l{lesson:02d}_error")
            print(f"ERROR: {e}")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--version", default="v001")
    parser.add_argument("--lesson", type=int, default=1,
                         help="Lesson number of the sampler to publish (default: 1)")
    parser.add_argument("--platform", required=True, choices=["tpt", "tes"])
    args = parser.parse_args()

    if args.platform == "tpt":
        publish_to_tpt(args.unit, args.version, args.lesson)
    else:
        publish_to_tes(args.unit, args.version, args.lesson)


if __name__ == "__main__":
    main()
