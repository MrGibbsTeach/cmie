from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def load_lesson_json(lesson_path: Path) -> Dict[str, Any]:
    with lesson_path.open(encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# TPT LISTING
# ------------------------------------------------------------

def render_lesson_tpt(data: Dict[str, Any]) -> str:
    title = data.get("lesson_title", "")
    eq = data.get("essential_question", "")
    objectives = data.get("objectives", [])

    return f"""
{title} | AI Literacy | Middle School Computer Science | Grades 6–8

ESSENTIAL QUESTION
{eq}

--------------------------------------------------
LEARNING OBJECTIVES

{chr(10).join(f"- {o}" for o in objectives)}

--------------------------------------------------
WHAT YOU GET

- Fully editable lesson slides (PPTX)
- Structured lesson flow (Explore → Learn → Apply → Reflect)
- Real-world AI example
- Reflection questions
- Teacher notes for teacher-facing guidance

--------------------------------------------------
IDEAL FOR

- Grades 6–8 Computer Science / Digital Technology
- STEM and AI literacy units
- Teachers introducing ethical and fair use of AI

This lesson is part of the AI Data Foundations unit.
Search for the full unit to get assessments and student workbook included.
""".strip()


# ------------------------------------------------------------
# TES LISTING
# ------------------------------------------------------------

def render_lesson_tes(data: Dict[str, Any]) -> str:
    title = data.get("lesson_title", "")
    eq = data.get("essential_question", "")
    objectives = data.get("objectives", [])

    return f"""
{title}

Essential Question
{eq}

This fully editable lesson introduces key AI and data literacy concepts using a clear Explore–Learn–Apply–Reflect structure suitable for Grades 6–8.

Learning Objectives
{chr(10).join(f"- {o}" for o in objectives)}

Includes
- PowerPoint lesson slides (PPTX)
- Real-world AI example
- Reflection questions
- Teacher notes
""".strip()


# ------------------------------------------------------------
# GUMROAD LISTING
# ------------------------------------------------------------

def render_lesson_gumroad(data: Dict[str, Any]) -> str:
    title = data.get("lesson_title", "")
    objectives = data.get("objectives", [])

    return f"""
# {title}

Editable middle school AI lesson for Grades 6–8.

## Students will

{chr(10).join(f"- {o}" for o in objectives)}

## What is included

- PowerPoint lesson slides (PPTX)
- Structured teaching flow (Explore, Learn, Apply, Reflect)
- Real-world AI example and reflection questions
- Teacher notes to support delivery
""".strip()


# ------------------------------------------------------------
# GENERATE FILES
# ------------------------------------------------------------

def generate_lesson_channel_files(unit_root: Path) -> None:
    lessons_dir = unit_root / "lessons"

    if not lessons_dir.exists():
        raise FileNotFoundError(f"No lessons directory found at {lessons_dir}")

    for lesson_json in lessons_dir.glob("*.json"):
        data = load_lesson_json(lesson_json)
        lesson_slug = lesson_json.stem

        lesson_folder = unit_root / "lesson_listings" / lesson_slug
        lesson_folder.mkdir(parents=True, exist_ok=True)

        (lesson_folder / "tpt_listing.txt").write_text(
            render_lesson_tpt(data), encoding="utf-8"
        )

        (lesson_folder / "tes_listing.txt").write_text(
            render_lesson_tes(data), encoding="utf-8"
        )

        (lesson_folder / "gumroad_description.md").write_text(
            render_lesson_gumroad(data), encoding="utf-8"
        )