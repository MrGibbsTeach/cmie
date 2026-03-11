from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def load_bundle_marketing(bundle_root: Path) -> Dict[str, Any]:
    path = bundle_root / "bundle_marketing.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing bundle_marketing.json at {path}")

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def render_tpt_listing(data: Dict[str, Any]) -> str:
    title = data.get("bundle_title", "")
    subtitle = data.get("bundle_subtitle", "")
    short = data.get("short_description", "")
    long_desc = data.get("long_description", "")
    included = data.get("whats_included", [])
    outcomes = data.get("learning_outcomes", [])
    ideal = data.get("ideal_for", [])
    why = data.get("why_this_bundle", [])

    return f"""
{title} | AI Literacy | Middle School Computer Science | Grades 6-8

{subtitle}

{short}

--------------------------------------------------

⭐ WHAT’S INCLUDED:

{chr(10).join(f"• {item}" for item in included)}

--------------------------------------------------

🎯 STUDENT LEARNING OUTCOMES:

{chr(10).join(f"• {item}" for item in outcomes)}

--------------------------------------------------

🚀 WHY TEACHERS LOVE THIS BUNDLE:

{chr(10).join(f"• {item}" for item in why)}

--------------------------------------------------

👩‍🏫 PERFECT FOR:

{chr(10).join(f"• {item}" for item in ideal)}

--------------------------------------------------

📌 IDEAL FOR:
• Grades 6–8
• Middle School Computer Science
• Digital Technology
• STEM enrichment
• AI literacy units

--------------------------------------------------

{long_desc}

--------------------------------------------------

This resource is designed for global English-speaking classrooms.
Aligned with common middle school computer science standards.
Editable files included.
"""

def render_tes_listing(data: Dict[str, Any]) -> str:
    return f"""
{data.get("bundle_title", "")}

{data.get("long_description", "")}

Included:
{chr(10).join(f"- {item}" for item in data.get("whats_included", []))}

Perfect for:
{chr(10).join(f"- {item}" for item in data.get("ideal_for", []))}
"""

def render_gumroad_listing(data: Dict[str, Any]) -> str:
    return f"""
# {data.get("bundle_title", "")}

## {data.get("bundle_subtitle", "")}

{data.get("long_description", "")}

---

## What You Get

{chr(10).join(f"- {item}" for item in data.get("whats_included", []))}

---

## Learning Outcomes

{chr(10).join(f"- {item}" for item in data.get("learning_outcomes", []))}
"""


def generate_channel_files(bundle_root: Path) -> None:
    data = load_bundle_marketing(bundle_root)

    tpt = render_tpt_listing(data)
    tes = render_tes_listing(data)
    gumroad = render_gumroad_listing(data)

    (bundle_root / "tpt_listing.txt").write_text(tpt, encoding="utf-8")
    (bundle_root / "tes_listing.txt").write_text(tes, encoding="utf-8")
    (bundle_root / "gumroad_description.md").write_text(gumroad, encoding="utf-8")
