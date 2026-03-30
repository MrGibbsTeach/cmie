import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def _count_lessons(lessons_dir: Path) -> int:
    if not lessons_dir.exists():
        return 0
    return len(list(lessons_dir.glob("*.json")))


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _load_assessment_summary(assessment_dir: Path) -> Dict[str, str]:
    data = _load_json(assessment_dir / "assessment.json")
    return {
        "assessment_title": data.get("assessment_title", ""),
        "overview": data.get("overview", ""),
    }


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def _lesson_display_title(data: Dict[str, Any], fallback_slug: str) -> str:
    return data.get("lesson_title") or data.get("topic_title") or _slug_to_title(fallback_slug)


def _lesson_essential_question(data: Dict[str, Any]) -> str:
    return data.get("essential_question", "").strip()


def _lesson_objectives(data: Dict[str, Any]) -> List[str]:
    objectives = data.get("objectives", []) or data.get("success_criteria", [])
    if not isinstance(objectives, list):
        return []
    return [str(x).strip() for x in objectives if str(x).strip()]


def _lesson_real_world_example(data: Dict[str, Any]) -> str:
    rwe = data.get("real_world_example", {})
    if not isinstance(rwe, dict):
        return ""
    return str(rwe.get("context", "")).strip()


def _lesson_activity_summary(data: Dict[str, Any]) -> str:
    slides = data.get("slides", [])
    if not isinstance(slides, list):
        return ""

    for slide in slides:
        if slide.get("type") == "activity":
            return str(slide.get("body", "")).strip()

    activity = data.get("activity", {})
    if isinstance(activity, dict):
        return str(activity.get("description", "")).strip()

    return ""


def _clean_activity_summary(text: str, max_len: int = 220) -> str:
    if not text:
        return ""

    text = " ".join(str(text).split())

    for stop in ["Output:", "You must:", "Success criteria:"]:
        if stop in text:
            text = text.split(stop)[0].strip()

    if len(text) > max_len:
        text = text[:max_len].rstrip()

    return text

def _build_unit_overview(title: str, subject: str) -> str:
    """
    Create a clean, sales-friendly unit overview (not assessment text).
    """

    base = title.lower()

    if "ai" in base and "data" in base:
        return (
            "This unit introduces students to how AI models use data to learn patterns, "
            "make predictions, and influence real-world decisions. Students explore key ideas "
            "like classification, training data, and recommendation systems through structured lessons "
            "and practical activities."
        )

def _build_hook_line(title: str, subject: str) -> str:
    """
    Short marketing hook for top of listing.
    """

    base = title.lower()

    if "ai" in base:
        return "Help students understand how AI systems learn from data and make decisions."

    return f"A ready-to-teach {subject} unit designed for clear understanding and engagement."

    # fallback (generic but safe)
    return (
        f"This unit develops student understanding of key concepts in {subject}. "
        "Lessons are structured around clear explanations, real-world examples, "
        "and practical classroom activities."
    )

def _build_unit_includes(
    lesson_count: int,
    has_slides_csv: bool,
    has_roadmap: bool,
    has_workbook: bool,
) -> List[str]:
    includes: List[str] = []
    includes.append(f"- {lesson_count} fully planned lessons with objectives and essential questions")
    if has_slides_csv:
        includes.append("- Canva-ready lesson slide CSV for fast template-based deck creation")
    if has_roadmap:
        includes.append("- Unit roadmap / scope and sequence")
    if has_workbook:
        includes.append("- Student workbook for print or digital use")
    includes.append("- Summative assessment task, rubric, and marking guide")
    return includes


def _build_unit_listing_lines(
    title: str,
    year_level: str,
    subject: str,
    overview: str,
    assessment_title: str,
    includes: List[str],
    platform_label: str,
) -> List[str]:
    short_title = f"{title} ({year_level})"

    hook = _build_hook_line(title, subject)

    lines: List[str] = []
    lines.append(f"# {short_title}")
    lines.append("")
    lines.append(hook)
    lines.append("")
    lines.append(f"{title} – complete micro-unit for {year_level} {subject}.")
    lines.append("")

    if overview:
        lines.append("Unit overview:")
        lines.append("")
        lines.append(overview)
        lines.append("")

    if assessment_title:
        lines.append(f"Summative assessment: **{assessment_title}**")
        lines.append("")

    if platform_label == "TES":
        lines.append("Resources included in this download:")
    elif platform_label == "GUMROAD":
        lines.append("Included in this resource pack:")
    else:
        lines.append("What’s included:")

    lines.append("")
    lines.extend(includes)
    return lines


def _build_lesson_listing_lines(
    unit_title: str,
    lesson_title: str,
    year_level: str,
    subject: str,
    essential_question: str,
    objectives: List[str],
    real_world_example: str,
    activity_summary: str,
    platform_label: str,
) -> List[str]:
    lines: List[str] = []
    lines.append(f"# {lesson_title} ({year_level})")
    lines.append("")
    lines.append(f"{lesson_title} – individual lesson from **{unit_title}** for {year_level} {subject}.")
    lines.append("")

    if essential_question:
        lines.append("Essential question:")
        lines.append("")
        lines.append(essential_question)
        lines.append("")

    if objectives:
        lines.append("Learning focus:")
        lines.append("")
        for obj in objectives[:3]:
            lines.append(f"- {obj}")
        lines.append("")

    if platform_label == "TES":
        includes_heading = "Resources included in this download:"
    elif platform_label == "GUMROAD":
        includes_heading = "Included in this lesson pack:"
    else:
        includes_heading = "What’s included:"

    lines.append(includes_heading)
    lines.append("")
    lines.append("- 1 fully planned lesson")
    lines.append("- Canva-ready slide content included in the unit CSV workflow")
    lines.append("- Hook, concept development, activity, reflection, and exit ticket")

    if real_world_example:
        lines.append("- Real-world example connected to the lesson topic")

    if activity_summary:
        lines.append("- Structured classroom activity")

    lines.append("")

    clean_activity = _clean_activity_summary(activity_summary)
    if clean_activity:
        lines.append("Classroom activity:")
        lines.append("")
        lines.append(clean_activity)
        lines.append("")

    return lines


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
    extra = extra or {}
    output_dir.mkdir(parents=True, exist_ok=True)

    lesson_count = _count_lessons(lessons_dir)
    assessment = _load_assessment_summary(assessment_dir)

    has_roadmap = (roadmap_dir / "unit_roadmap.md").exists()
    has_workbook = (workbook_dir / "student_workbook.md").exists()
    has_slides_csv = (lessons_dir.parent / "04_Slides_CSV").exists()

    overview = _build_unit_overview(title, subject)
    assessment_title = assessment.get("assessment_title", "").strip()

    includes = _build_unit_includes(
        lesson_count=lesson_count,
        has_slides_csv=has_slides_csv,
        has_roadmap=has_roadmap,
        has_workbook=has_workbook,
    )

    # Unit-level listings
    unit_dir = output_dir / "unit"
    unit_dir.mkdir(parents=True, exist_ok=True)

    tpt_unit_lines = _build_unit_listing_lines(
        title=title,
        year_level=year_level,
        subject=subject,
        overview=overview,
        assessment_title=assessment_title,
        includes=includes,
        platform_label="TPT",
    )

    tes_unit_lines = _build_unit_listing_lines(
        title=title,
        year_level=year_level,
        subject=subject,
        overview=overview,
        assessment_title=assessment_title,
        includes=includes,
        platform_label="TES",
    )

    gumroad_unit_lines = _build_unit_listing_lines(
        title=title,
        year_level=year_level,
        subject=subject,
        overview=overview,
        assessment_title=assessment_title,
        includes=includes,
        platform_label="GUMROAD",
    )

    tpt_unit_path = unit_dir / "tpt_listing.md"
    tes_unit_path = unit_dir / "tes_listing.md"
    gumroad_unit_path = unit_dir / "gumroad_listing.md"

    with tpt_unit_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(tpt_unit_lines))

    with tes_unit_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(tes_unit_lines))

    with gumroad_unit_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(gumroad_unit_lines))

    # Lesson-level listings
    lessons_output_dir = output_dir / "lessons"
    lessons_output_dir.mkdir(parents=True, exist_ok=True)

    lesson_files: List[Dict[str, str]] = []

    for idx, lesson_json_path in enumerate(sorted(lessons_dir.glob("*.json")), start=1):
        lesson_data = _load_json(lesson_json_path)
        slug = lesson_json_path.stem

        lesson_title = _lesson_display_title(lesson_data, slug)
        essential_question = _lesson_essential_question(lesson_data)
        objectives = _lesson_objectives(lesson_data)
        real_world_example = _lesson_real_world_example(lesson_data)
        activity_summary = _lesson_activity_summary(lesson_data)

        lesson_dir = lessons_output_dir / f"{idx:02d}-{slug}"
        lesson_dir.mkdir(parents=True, exist_ok=True)

        tpt_lesson_lines = _build_lesson_listing_lines(
            unit_title=title,
            lesson_title=lesson_title,
            year_level=year_level,
            subject=subject,
            essential_question=essential_question,
            objectives=objectives,
            real_world_example=real_world_example,
            activity_summary=activity_summary,
            platform_label="TPT",
        )

        tes_lesson_lines = _build_lesson_listing_lines(
            unit_title=title,
            lesson_title=lesson_title,
            year_level=year_level,
            subject=subject,
            essential_question=essential_question,
            objectives=objectives,
            real_world_example=real_world_example,
            activity_summary=activity_summary,
            platform_label="TES",
        )

        gumroad_lesson_lines = _build_lesson_listing_lines(
            unit_title=title,
            lesson_title=lesson_title,
            year_level=year_level,
            subject=subject,
            essential_question=essential_question,
            objectives=objectives,
            real_world_example=real_world_example,
            activity_summary=activity_summary,
            platform_label="GUMROAD",
        )

        tpt_lesson_path = lesson_dir / "tpt_listing.md"
        tes_lesson_path = lesson_dir / "tes_listing.md"
        gumroad_lesson_path = lesson_dir / "gumroad_listing.md"

        with tpt_lesson_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(tpt_lesson_lines))

        with tes_lesson_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(tes_lesson_lines))

        with gumroad_lesson_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(gumroad_lesson_lines))

        lesson_files.append(
            {
                "slug": slug,
                "lesson_title": lesson_title,
                "tpt_listing": str(tpt_lesson_path),
                "tes_listing": str(tes_lesson_path),
                "gumroad_listing": str(gumroad_lesson_path),
            }
        )

    return {
        "unit_id": unit_id,
        "title": title,
        "files": {
            "unit_tpt_listing": str(tpt_unit_path),
            "unit_tes_listing": str(tes_unit_path),
            "unit_gumroad_listing": str(gumroad_unit_path),
        },
        "lesson_files": lesson_files,
        "lesson_count": lesson_count,
    }


def generate_listings_for_unit(unit_root: Path, unit_config: Dict[str, Any]) -> Dict[str, Any]:
    return generate_marketplace_listings(
        unit_id=unit_config["unit_id"],
        title=unit_config["title"],
        year_level=unit_config["year_level"],
        subject=unit_config["subject"],
        lessons_dir=unit_root / "lessons",
        assessment_dir=unit_root / "assessment",
        roadmap_dir=unit_root / "roadmap",
        workbook_dir=unit_root / "workbook",
        output_dir=unit_root / "listings",
    )