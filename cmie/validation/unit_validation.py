from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
import json


PLACEHOLDER_STRINGS = [
    "Add curated YouTube video here.",
    "Replace this placeholder before public release.",
]


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_lesson(lesson_path: Path) -> List[str]:
    data = _load_json(lesson_path)
    errors: List[str] = []

    title = data.get("lesson_title") or data.get("topic_title")
    if not title:
        errors.append("Missing lesson_title/topic_title")

    objectives = data.get("objectives", [])
    if not isinstance(objectives, list) or not objectives:
        errors.append("Missing or empty objectives list")

    slides = data.get("slides", [])
    if not isinstance(slides, list) or not slides:
        errors.append("Missing or empty slides list")
    else:
        if len(slides) > 20:
            errors.append(f"Too many slides ({len(slides)} > 20)")

        # Check for placeholder strings in slide bodies
        for idx, slide in enumerate(slides, start=1):
            body = (slide.get("body") or "").strip()
            for ph in PLACEHOLDER_STRINGS:
                if ph in body:
                    errors.append(f"Slide {idx} contains placeholder text: {ph}")

    return errors


def validate_assessment(assessment_dir: Path) -> List[str]:
    errors: List[str] = []
    assessment_json = assessment_dir / "assessment.json"
    rubric_json = assessment_dir / "rubric.json"
    marking_json = assessment_dir / "marking_guide.json"

    if not assessment_json.exists():
        return ["assessment.json missing"]

    assessment = _load_json(assessment_json)

    if not assessment.get("assessment_title"):
        errors.append("assessment_title missing")

    if not assessment.get("overview"):
        errors.append("overview missing")

    rubric = {}
    if rubric_json.exists():
        rubric = _load_json(rubric_json)
    else:
        errors.append("rubric.json missing")

    levels = rubric.get("levels", [])
    if levels and len(levels) != 4:
        errors.append(f"rubric.levels should have 4 entries, found {len(levels)}")

    criteria = rubric.get("criteria", [])
    if not criteria:
        errors.append("rubric.criteria missing or empty")
    else:
        required_levels = {"Exemplary", "Proficient", "Developing", "Beginning"}
        for crit in criteria:
            desc = crit.get("descriptors", {})
            missing = required_levels - set(desc.keys())
            if missing:
                errors.append(
                    f"rubric criterion '{crit.get('name', '?')}' missing descriptors for: "
                    + ", ".join(sorted(missing))
                )

    if not marking_json.exists():
        errors.append("marking_guide.json missing")

    return errors


def validate_unit(unit_root: Path) -> List[str]:
    """
    Run basic structural validation over a generated unit.

    Returns a list of human-readable error/warning strings.
    Empty list means "no structural problems detected" (not a guarantee of pedagogical quality).
    """
    errors: List[str] = []

    lessons_dir = unit_root / "lessons"
    assessment_dir = unit_root / "assessment"

    # Lessons
    if not lessons_dir.exists():
        errors.append("lessons directory missing")
    else:
        lesson_files = sorted(lessons_dir.glob("*.json"))
        if not lesson_files:
            errors.append("no lesson JSON files found in lessons dir")
        for lf in lesson_files:
            lesson_errors = validate_lesson(lf)
            for e in lesson_errors:
                errors.append(f"[lesson:{lf.name}] {e}")

    # Assessment
    if assessment_dir.exists():
        assessment_errors = validate_assessment(assessment_dir)
        for e in assessment_errors:
            errors.append(f"[assessment] {e}")
    else:
        errors.append("assessment directory missing")

    return errors