import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def _load_lessons(lessons_dir: Path) -> List[Dict[str, Any]]:
    """
    Load all lesson JSON files from lessons_dir into a list.
    Each lesson dict gets a _source_path key for reference.
    """
    lessons: List[Dict[str, Any]] = []
    if not lessons_dir.exists():
        return lessons

    for path in sorted(lessons_dir.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        data["_source_path"] = str(path)
        lessons.append(data)

    return lessons


def _load_assessment(assessment_dir: Optional[Path]) -> Dict[str, Any]:
    """
    Load assessment.json from the assessment_dir if present.
    """
    if not assessment_dir:
        return {}
    path = assessment_dir / "assessment.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def generate_unit_roadmap(
    unit_root: Path,
    unit_config: Dict[str, Any],
    lessons_dir: Path,
    assessment_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Generate a unit roadmap markdown file summarising the lesson sequence
    and assessment.

    - Writes unit_roadmap.md into <unit_root>/roadmap.
    - Returns metadata dict with file path and basic unit info.
    """
    output_dir = unit_root / "roadmap"
    output_dir.mkdir(parents=True, exist_ok=True)

    lessons = _load_lessons(lessons_dir)
    assessment = _load_assessment(assessment_dir)

    unit_id = unit_config.get("unit_id", "")
    title = unit_config.get("title", "Unit roadmap")
    year_level = unit_config.get("year_level", "")
    subject = unit_config.get("subject", "")

    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    if year_level:
        lines.append(f"**Year level:** {year_level}")
    if subject:
        lines.append(f"**Subject:** {subject}")
    if year_level or subject:
        lines.append("")
    if unit_id:
        lines.append(f"**Unit ID:** {unit_id}")
        lines.append("")

    # Lesson sequence table at the top
    if lessons:
        lines.append("## Lesson sequence")
        lines.append("")
        lines.append("| Lesson | Title | Essential question |")
        lines.append("|---|---|---|")
        for lesson in sorted(lessons, key=lambda l: l.get("lesson_number", 0)):
            ln = lesson.get("lesson_number", "")
            lt = lesson.get("lesson_title") or lesson.get("topic_title", "")
            eq = lesson.get("essential_question", "")
            # Escape pipes in text so the markdown table does not break
            lt_sanitised = str(lt).replace("|", r"\|")
            eq_sanitised = str(eq).replace("|", r"\|")
            lines.append(f"| {ln} | {lt_sanitised} | {eq_sanitised} |")
        lines.append("")

    # Summative assessment overview
    if assessment:
        lines.append("## Summative assessment overview")
        lines.append("")
        if assessment.get("assessment_title"):
            lines.append(f"**Title:** {assessment['assessment_title']}")
            lines.append("")
        if assessment.get("overview"):
            lines.append(assessment["overview"])
            lines.append("")
        if assessment.get("essential_question"):
            lines.append("**Assessment driving question:**")
            lines.append("")
            lines.append(assessment["essential_question"])
            lines.append("")

    roadmap_path = output_dir / "unit_roadmap.md"
    with roadmap_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {
        "unit_id": unit_id,
        "title": title,
        "year_level": year_level,
        "subject": subject,
        "file": str(roadmap_path),
        "lesson_count": len(lessons),
    }