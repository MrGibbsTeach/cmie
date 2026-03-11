import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def _count_lessons(lessons_dir: Path) -> int:
    if not lessons_dir.exists():
        return 0
    return len(list(lessons_dir.glob("*.json")))


def _load_assessment_summary(assessment_dir: Path) -> Dict[str, str]:
    assessment_path = assessment_dir / "assessment.json"
    if not assessment_path.exists():
        return {}

    try:
        with assessment_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    return {
        "assessment_title": data.get("assessment_title", ""),
        "overview": data.get("overview", ""),
    }


def generate_marketplace_listings(
    unit_id: str,
    title: str,
    year_level: str,
    subject: str,
    lessons_dir: Path,
    assessment_dir: Path,
    roadmap_dir: Path,
    workbook_dir: Path,
    output_dir: Path,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate TPT / TES style listing copy.

    - Writes two markdown files: tpt_listing.md and tes_listing.md.
    - Uses counts and existing assets to describe what's included.
    """
    extra = extra or {}
    output_dir.mkdir(parents=True, exist_ok=True)

    lesson_count = _count_lessons(lessons_dir)
    assessment = _load_assessment_summary(assessment_dir)

    has_roadmap = (roadmap_dir / "unit_roadmap.md").exists()
    has_workbook = (workbook_dir / "student_workbook.md").exists()

    # Common description pieces
    overview = assessment.get("overview", "").strip()
    assessment_title = assessment.get("assessment_title", "").strip()

    short_title = f"{title} ({year_level})"

    base_description: List[str] = []
    base_description.append(f"{title} – complete micro-unit for {year_level} {subject}.")
    base_description.append("")
    if overview:
        base_description.append("Unit overview:")
        base_description.append("")
        base_description.append(overview)
        base_description.append("")
    if assessment_title:
        base_description.append(f"Summative assessment: **{assessment_title}**")
        base_description.append("")

    includes: List[str] = []
    includes.append(f"- {lesson_count} fully planned lessons with objectives and essential questions")
    includes.append("- Editable slide decks (PPTX) for each lesson")
    if has_roadmap:
        includes.append("- Unit roadmap / scope & sequence (markdown)")
    if has_workbook:
        includes.append("- Printable / digital student workbook (markdown)")

    includes.append("- Summative assessment task, rubric, and marking guide (JSON)")

    # TPT listing
    tpt_lines: List[str] = []
    tpt_lines.append(f"# {short_title}")
    tpt_lines.append("")
    tpt_lines.extend(base_description)
    tpt_lines.append("What’s included:")
    tpt_lines.append("")
    tpt_lines.extend(includes)

    # TES listing (slightly different heading)
    tes_lines: List[str] = []
    tes_lines.append(f"# {short_title}")
    tes_lines.append("")
    tes_lines.extend(base_description)
    tes_lines.append("Resources included in this download:")
    tes_lines.append("")
    tes_lines.extend(includes)

    tpt_path = output_dir / "tpt_listing.md"
    tes_path = output_dir / "tes_listing.md"

    with tpt_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(tpt_lines))

    with tes_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(tes_lines))

    return {
        "unit_id": unit_id,
        "title": title,
        "files": {
            "tpt_listing": str(tpt_path),
            "tes_listing": str(tes_path),
        },
        "lesson_count": lesson_count,
    }