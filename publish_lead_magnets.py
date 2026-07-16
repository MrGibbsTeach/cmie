"""
publish_lead_magnets.py — publish the free Lesson-1 sampler (built by
make_lead_magnet.py) for a unit, to TPT and/or TES.

TPT has no draft state: this makes the resource live immediately (price $0).
TES always stops at a draft (per this project's standing rule) — the final
"Publish now" click stays a manual, human step on TES's Author Dashboard.

Usage:
    python publish_lead_magnets.py --unit year7_networks_hardware_unit1 --platform tpt
    python publish_lead_magnets.py --unit year7_networks_hardware_unit1 --platform tes
"""
from __future__ import annotations

import argparse
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


def _short_topic(unit_title: str) -> str:
    topic = unit_title.split(":")[0].strip() if ":" in unit_title else unit_title.strip()
    return topic


def _read_unit_title(unit_id: str, version: str = "v001") -> str:
    listing = PUBLIC_ROOT / f"{unit_id}_{version}" / "06_Listings" / "unit" / "tpt_listing.md"
    first_line = listing.read_text(encoding="utf-8").splitlines()[0]
    title = first_line.lstrip("#").strip()
    # Drop the grade-band suffix in parentheses for the sampler's own title —
    # the full listing already carries that; the sampler title should stay short.
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title).strip()
    return title


def build_listing(unit_id: str, version: str = "v001") -> dict:
    unit_title = _read_unit_title(unit_id, version)
    topic = _short_topic(unit_title)
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


def publish_to_tpt(unit_id: str, version: str = "v001") -> None:
    from cmie.publishing.tpt import upload_unit

    zip_path = ARTIFACTS_ROOT / f"{unit_id}_lesson01_FREE_{version}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Lead magnet zip not found: {zip_path}. Run make_lead_magnet.py first.")

    raw = build_listing(unit_id, version)
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

    thumbnail_path = PROJECT_ROOT / "releases" / "thumbnails" / f"{unit_id}_thumbnail.png"
    if not thumbnail_path.exists():
        raise FileNotFoundError(
            f"No thumbnail found at {thumbnail_path} — TPT requires one "
            "(auto-generation fails for zip/pptx uploads)."
        )

    unit_folder = PROJECT_ROOT / "releases" / unit_id
    upload_unit(unit_folder, zip_path, thumbnail_path=thumbnail_path, auto_publish=True, listing=listing)


def publish_to_tes(unit_id: str, version: str = "v001") -> None:
    from cmie.publishing.browser import automation_chrome
    from publish_tes import (
        _navigate_to_upload, _step1_description, _step2_add_files,
        _step3_categories, _step4_licence, _take_debug_screenshot,
    )

    zip_path = ARTIFACTS_ROOT / f"{unit_id}_lesson01_FREE_{version}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Lead magnet zip not found: {zip_path}. Run make_lead_magnet.py first.")

    raw = build_listing(unit_id, version)

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

            _take_debug_screenshot(page, f"{unit_id}_lead_magnet_step5_preview")
            print("=" * 60)
            print("FORM FILLED — saved as a draft, NOT published.")
            print("Review on the TES Author Dashboard, then manually check")
            print("the copyright box and click 'Publish now'.")
            print("=" * 60)
        except Exception as e:
            _take_debug_screenshot(page, f"{unit_id}_lead_magnet_error")
            print(f"ERROR: {e}")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--version", default="v001")
    parser.add_argument("--platform", required=True, choices=["tpt", "tes"])
    args = parser.parse_args()

    if args.platform == "tpt":
        publish_to_tpt(args.unit, args.version)
    else:
        publish_to_tes(args.unit, args.version)


if __name__ == "__main__":
    main()
