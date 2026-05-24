from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def load_marketing_assets(unit_root: Path) -> Dict[str, Any]:
    path = unit_root / "marketing" / "marketing_assets.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing marketing_assets.json at {path}")

    with path.open(encoding="utf-8") as f:
        return json.load(f)


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


def generate_channel_files(unit_root: Path) -> None:
    data = load_marketing_assets(unit_root)
    unit_data = data.get("unit", {})

    if not unit_data:
        raise ValueError("marketing_assets.json missing 'unit' section")

    listings_root = unit_root / "bundle_listings"
    listings_root.mkdir(parents=True, exist_ok=True)

    tpt_data = unit_data.get("tpt", {})
    tes_data = unit_data.get("tes", {})
    gumroad_data = unit_data.get("gumroad", {})

    (listings_root / "tpt_listing.txt").write_text(
        _format_listing_block(tpt_data),
        encoding="utf-8",
    )

    (listings_root / "tes_listing.txt").write_text(
        _format_listing_block(tes_data),
        encoding="utf-8",
    )

    (listings_root / "gumroad_description.md").write_text(
        _format_listing_block(gumroad_data),
        encoding="utf-8",
    )