from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def _load_lessons(lessons_dir: Path) -> List[Dict[str, Any]]:
    lessons: List[Dict[str, Any]] = []
    if not lessons_dir.exists():
        return lessons

    for path in sorted(lessons_dir.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        lessons.append(data)

    return lessons


def _load_assessment(assessment_dir: Optional[Path]) -> Dict[str, Any]:
    if not assessment_dir:
        return {}

    path = assessment_dir / "assessment.json"
    if not path.exists():
        return {}

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def generate_unit_readme(
    unit_root: Path,
    unit_config: Dict[str, Any],
    lessons_dir: Path,
    assessment_dir: Optional[Path] = None,
) -> Path:
    """
    Generate a teacher-facing README markdown file for the unit.
    """
    output_dir = unit_root / "teacher_guide"
    output_dir.mkdir(parents=True, exist_ok=True)

    lessons = _load_lessons(lessons_dir)
    assessment = _load_assessment(assessment_dir)

    title = unit_config.get("title", "Unit")
    year_level = unit_config.get("year_level", "")
    subject = unit_config.get("subject", "")
    version = unit_config.get("version", "")

    lines: List[str] = []

    lines.append(f"# {title}")
    lines.append("")
    lines.append("## README")
    lines.append("")

    if year_level:
        lines.append(f"**Year level:** {year_level}")
    if subject:
        lines.append(f"**Subject:** {subject}")
    if version:
        lines.append(f"**Version:** {version}")
    lines.append("")

    lines.append("## What’s included")
    lines.append("")
    lines.append(f"- {len(lessons)} structured lesson slide decks")
    lines.append("- Student workbook")
    lines.append("- Summative assessment task")
    lines.append("- Unit roadmap")
    lines.append("")

    lines.append("## How to use this unit")
    lines.append("")
    lines.append("Each lesson is designed to follow a clear sequence:")
    lines.append("- introduce the essential question")
    lines.append("- teach core ideas using the slide deck")
    lines.append("- complete workbook tasks")
    lines.append("- review key learning through discussion or reflection")
    lines.append("")

    lines.append("## Suggested lesson timing")
    lines.append("")
    lines.append("- 45–60 minutes per lesson")
    lines.append("- 7 lessons in total")
    lines.append("- Assessment: 1–2 lessons")
    lines.append("")

    if lessons:
        lines.append("## Lesson sequence")
        lines.append("")
        for lesson in sorted(lessons, key=lambda l: l.get("lesson_number", 0)):
            num = lesson.get("lesson_number", "")
            lesson_title = lesson.get("lesson_title") or lesson.get("topic_title", "Lesson")
            lines.append(f"- Lesson {num}: {lesson_title}")
        lines.append("")

    if assessment:
        lines.append("## Assessment")
        lines.append("")
        if assessment.get("assessment_title"):
            lines.append(f"**Task:** {assessment['assessment_title']}")
            lines.append("")
        if assessment.get("overview"):
            lines.append(assessment["overview"])
            lines.append("")

    lines.append("## Flexibility")
    lines.append("")
    lines.append("This unit can be used:")
    lines.append("- as a full sequence")
    lines.append("- as individual lessons")
    lines.append("- for relief teaching")
    lines.append("- for revision or catch-up work")
    lines.append("")

    lines.append("## Notes for teachers")
    lines.append("")
    lines.append("- No specialist background in the topic is required to teach this unit")
    lines.append("- Materials are designed for lower secondary learners")
    lines.append("- Slides, workbook, and assessment are intended to work together as one package")
    lines.append("")

    readme_path = output_dir / "readme.md"
    with readme_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return readme_path