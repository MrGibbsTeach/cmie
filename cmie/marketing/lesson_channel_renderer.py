from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List


def load_marketing_assets(unit_root: Path) -> Dict[str, Any]:
    path = unit_root / "marketing" / "marketing_assets.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing marketing_assets.json at {path}")

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _slugify(value: str) -> str:
    value = value.strip().lower()
    out = []
    for ch in value:
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _format_listing_block(data: Dict[str, Any]) -> str:
    lines = [
        f"TITLE:\n{data.get('title', '').strip()}",
        "",
        f"PRICE:\n{data.get('price', '').strip()}",
        "",
        f"DESCRIPTION:\n{data.get('description', '').strip()}",
    ]

    tags = data.get("tags", [])
    if tags:
        lines.extend([
            "",
            "TAGS:",
            ", ".join(str(tag) for tag in tags),
        ])

    return "\n".join(lines).strip()


def generate_lesson_channel_files(unit_root: Path) -> None:
    data = load_marketing_assets(unit_root)
    lessons: List[Dict[str, Any]] = data.get("lessons", [])

    if not lessons:
        raise ValueError("marketing_assets.json missing 'lessons' section")

    listings_root = unit_root / "lesson_listings"
    listings_root.mkdir(parents=True, exist_ok=True)

    for lesson in lessons:
        lesson_number = lesson.get("lesson_number", "")
        lesson_title = lesson.get("lesson_title", "lesson")
        lesson_slug = f"{int(lesson_number):02d}-{_slugify(lesson_title)}" if str(lesson_number).isdigit() else _slugify(lesson_title)

        lesson_folder = listings_root / lesson_slug
        lesson_folder.mkdir(parents=True, exist_ok=True)

        tpt_data = lesson.get("tpt", {})
        tes_data = lesson.get("tes", {})
        gumroad_data = lesson.get("gumroad", {})

        (lesson_folder / "tpt_listing.txt").write_text(
            _format_listing_block(tpt_data),
            encoding="utf-8",
        )

        (lesson_folder / "tes_listing.txt").write_text(
            _format_listing_block(tes_data),
            encoding="utf-8",
        )

        (lesson_folder / "gumroad_description.md").write_text(
            _format_listing_block(gumroad_data),
            encoding="utf-8",
        )