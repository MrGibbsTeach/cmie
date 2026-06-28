from __future__ import annotations

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
        "assessment_title": data.get("assessment_title", "").strip(),
        "overview": data.get("overview", "").strip(),
    }


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").title()


def extract_unit_short_title(unit_title: str) -> str:
    if ":" in unit_title:
        return unit_title.split(":")[-1].strip()
    return unit_title.strip()


def _lesson_display_title(data: Dict[str, Any], fallback_slug: str) -> str:
    return data.get("lesson_title") or data.get("topic_title") or _slug_to_title(fallback_slug)


def _lesson_essential_question(data: Dict[str, Any]) -> str:
    return str(data.get("essential_question", "")).strip()


def _lesson_objectives(data: Dict[str, Any]) -> List[str]:
    objectives = data.get("objectives", []) or data.get("success_criteria", [])
    if not isinstance(objectives, list):
        return []
    return [str(x).strip() for x in objectives if str(x).strip()]

def _upgrade_listing_objectives(objectives: List[str]) -> List[str]:
    upgraded: List[str] = []

    replacements = [
        ("Name ", "Identify "),
        ("Spot ", "Explain "),
        ("Create ", "Design "),
        ("List ", "Describe "),
    ]

    for obj in objectives:
        text = str(obj).strip()

        # basic verb upgrade
        for old, new in replacements:
            if text.startswith(old):
                text = new + text[len(old):]
                break

        # 🔥 NEW: strengthen weak phrasing
        if "everyday ai examples" in text.lower():
            text = "Identify real-world applications of AI systems"

        elif "ai myths" in text.lower():
            text = "Explain common misconceptions about how AI systems work"

        elif "benefits and limits" in text.lower():
            text = "Evaluate the benefits and limitations of AI systems in real-world contexts"

        upgraded.append(text)

    return upgraded


def _lesson_real_world_example(data: Dict[str, Any]) -> str:
    rwe = data.get("real_world_example", {})
    if not isinstance(rwe, dict):
        return ""
    return str(rwe.get("context", "")).strip()


def _lesson_activity_summary(data: Dict[str, Any]) -> str:
    slides = data.get("slides", [])
    if isinstance(slides, list):
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
    base = title.lower()

    if "ethics" in base or "bias" in base:
        return (
            "This unit helps students explore how AI systems can create unfair outcomes, how bias enters "
            "data and decision-making, and how responsibility and accountability matter in real-world AI use."
        )

    if "model" in base or "models" in base:
        return (
            "This unit introduces students to how AI models use data to learn patterns, make predictions, "
            "and influence decisions. Students explore core ideas through structured lessons and practical activities."
        )

    if "systems" in base or "applications" in base:
        return (
            "This unit helps students understand what AI systems are, how they work in everyday life, "
            "how they make decisions, and what their strengths and limits are in real-world contexts."
        )

    if "ai" in base and "data" in base:
        return (
            "This unit introduces students to key AI and data literacy concepts through structured lessons, "
            "real-world examples, and practical classroom activities."
        )

    return (
        f"This unit develops student understanding of key concepts in {subject}. "
        "Lessons are structured around clear explanations, real-world examples, and practical classroom activities."
    )


def _build_hook_line(title: str, subject: str) -> str:
    base = title.lower()

    if "ethics" in base or "bias" in base:
        return "Help students explore fairness, responsibility, and bias in real-world AI systems."

    if "systems" in base or "applications" in base:
        return "Help students understand how AI systems work, where they appear, and how they influence daily life."

    if "model" in base or "models" in base:
        return "Help students understand how AI models learn from data and make predictions."

    if "ai" in base:
        return "Help students understand how AI systems use data and influence decisions."

    return f"A ready-to-teach {subject} unit designed for clear understanding and engagement."


def _build_unit_includes(
    lesson_count: int,
    has_slides_csv: bool,
    has_pptx_slides: bool,
    has_roadmap: bool,
    has_workbook: bool,
) -> List[str]:
    includes: List[str] = []
    includes.append(f"- {lesson_count} fully planned lessons with objectives and essential questions")
    if has_pptx_slides:
        includes.append("- Fully editable PowerPoint (PPTX) slide deck for every lesson")
    elif has_slides_csv:
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
    lines: List[str] = []
    lines.append(f"# {title} ({year_level})")
    lines.append("")
    lines.append(_build_hook_line(title, subject))
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
        includes_heading = "Resources included in this download:"
    elif platform_label == "GUMROAD":
        includes_heading = "Included in this resource pack:"
    else:
        includes_heading = "What’s included:"

    lines.append(includes_heading)
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
    lesson_number: Optional[int] = None,
    has_pptx_slides: bool = False,
) -> List[str]:
    unit_short_title = extract_unit_short_title(unit_title)

    if lesson_number is not None:
        listing_title = f"{lesson_title} | {unit_short_title} | Lesson {lesson_number}"
    else:
        listing_title = f"{lesson_title} | {unit_short_title}"

    lines: List[str] = []
    lines.append(f"# {listing_title}")
    lines.append("")

    if essential_question:
        lines.append("Essential question:")
        lines.append("")
        lines.append(essential_question)
        lines.append("")

    if objectives:
        lines.append("Learning focus:")
        lines.append("")
        upgraded_objectives = _upgrade_listing_objectives(objectives[:3])
        for obj in upgraded_objectives:
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
    if has_pptx_slides:
        lines.append("- Fully editable PowerPoint (PPTX) slide deck")
    else:
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


def generate_workbook_listing(unit_title: str, lesson_count: int = 7) -> str:
    unit_short_title = extract_unit_short_title(unit_title)
    base = unit_short_title.lower()

    lines: List[str] = []
    lines.append(f"# {unit_short_title} | Student Workbook | Lower Secondary")
    lines.append("")

    lines.append("🔹 What’s included")
    lines.append(f"Complete student workbook for all {lesson_count} lessons")
    lines.append("Structured reflection, application, and understanding tasks")
    lines.append("Consistent format across each lesson")
    lines.append("Ready-to-print and classroom-friendly layout")
    lines.append("")

    lines.append("🔹 What students will do")
    if "ethics" in base or "bias" in base:
        lines.append("Explain key AI ethics concepts in their own words")
        lines.append("Apply ideas to real-world scenarios")
        lines.append("Reflect on learning and identify questions")
        lines.append("Explore fairness and bias in AI systems")
    elif "systems" in base or "applications" in base:
        lines.append("Explain how AI systems work in everyday contexts")
        lines.append("Apply AI concepts to real-world scenarios")
        lines.append("Identify how AI makes decisions using data")
        lines.append("Evaluate strengths and limitations of AI systems")
    elif "model" in base or "models" in base:
        lines.append("Explain how AI models use data to make decisions")
        lines.append("Apply ideas to real-world scenarios")
        lines.append("Reflect on learning and identify questions")
        lines.append("Explore patterns, predictions, and recommendations")
    else:
        lines.append("Explain key concepts from the unit in their own words")
        lines.append("Apply ideas to real-world scenarios")
        lines.append("Reflect on learning and identify questions")
        lines.append("Explore core ideas from the unit")

    lines.append("")
    lines.append("🔹 Why teachers love this resource")
    lines.append("No prep required")
    lines.append("Reinforces lesson content")
    lines.append("Supports deeper thinking and reflection")
    lines.append("Easy to use alongside slides and activities")
    lines.append("")

    lines.append("🔹 Part of a complete unit")
    lines.append(f"{unit_short_title} Unit")
    lines.append("→ Bundle available")

    return "\n".join(lines)

def generate_assessment_listing(unit_title: str) -> str:
    unit_short_title = extract_unit_short_title(unit_title)
    base = unit_short_title.lower()

    lines: List[str] = []
    lines.append(f"# {unit_short_title} | Assessment Pack | Lower Secondary")
    lines.append("")

    lines.append("🔹 What’s included")
    lines.append("Summative assessment task")
    lines.append("Rubric and marking guide")
    lines.append("Ready-to-use classroom assessment")
    lines.append("Aligned to the unit learning goals")
    lines.append("")

    lines.append("🔹 What students will do")
    if "ethics" in base or "bias" in base:
        lines.append("Evaluate bias and fairness in a real-world AI scenario")
        lines.append("Use evidence to explain ethical concerns and impacts")
        lines.append("Suggest improvements to make AI systems more fair and responsible")
        lines.append("Demonstrate understanding through a structured written task")
    elif "systems" in base or "applications" in base:
        lines.append("Apply key AI concepts to a real-world scenario")
        lines.append("Explain how AI systems use data and make decisions")
        lines.append("Evaluate strengths and limitations of AI systems")
        lines.append("Demonstrate understanding through a structured written task")
    elif "model" in base or "models" in base:
        lines.append("Apply key AI model concepts to a real-world scenario")
        lines.append("Explain how data influences predictions and recommendations")
        lines.append("Evaluate model outputs using evidence")
        lines.append("Demonstrate understanding through a structured written task")
    else:
        lines.append("Apply key concepts from the unit to a real-world scenario")
        lines.append("Explain decisions using evidence")
        lines.append("Show understanding through a structured task")
        lines.append("Reflect on how the unit's ideas work in practice")

    lines.append("")
    lines.append("🔹 Why teachers love this resource")
    lines.append("No prep required")
    lines.append("Easy to assess with included rubric")
    lines.append("Clear structure for classroom use")
    lines.append("Works alongside slides and workbook")
    lines.append("")

    lines.append("🔹 Part of a complete unit")
    lines.append(f"{unit_short_title} Unit")
    lines.append("→ Bundle available")

    return "\n".join(lines)



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
    has_pptx_slides = any((lessons_dir.parent / "slides").glob("*.pptx")) if (lessons_dir.parent / "slides").exists() else False

    overview = _build_unit_overview(title, subject)
    assessment_title = assessment.get("assessment_title", "")

    includes = _build_unit_includes(
        lesson_count=lesson_count,
        has_slides_csv=has_slides_csv,
        has_pptx_slides=has_pptx_slides,
        has_roadmap=has_roadmap,
        has_workbook=has_workbook,
    )

    output_files: Dict[str, str] = {}

    # Unit listing files
    unit_dir = output_dir / "unit"
    unit_dir.mkdir(parents=True, exist_ok=True)

    tpt_unit_path = unit_dir / "tpt_listing.md"
    tes_unit_path = unit_dir / "tes_listing.md"
    gumroad_unit_path = unit_dir / "gumroad_listing.md"

    with tpt_unit_path.open("w", encoding="utf-8") as f:
        f.write(
            "\n".join(
                _build_unit_listing_lines(
                    title=title,
                    year_level=year_level,
                    subject=subject,
                    overview=overview,
                    assessment_title=assessment_title,
                    includes=includes,
                    platform_label="TPT",
                )
            )
        )

    with tes_unit_path.open("w", encoding="utf-8") as f:
        f.write(
            "\n".join(
                _build_unit_listing_lines(
                    title=title,
                    year_level=year_level,
                    subject=subject,
                    overview=overview,
                    assessment_title=assessment_title,
                    includes=includes,
                    platform_label="TES",
                )
            )
        )

    with gumroad_unit_path.open("w", encoding="utf-8") as f:
        f.write(
            "\n".join(
                _build_unit_listing_lines(
                    title=title,
                    year_level=year_level,
                    subject=subject,
                    overview=overview,
                    assessment_title=assessment_title,
                    includes=includes,
                    platform_label="GUMROAD",
                )
            )
        )

    output_files["unit_tpt_listing"] = str(tpt_unit_path)
    output_files["unit_tes_listing"] = str(tes_unit_path)
    output_files["unit_gumroad_listing"] = str(gumroad_unit_path)

    # Lesson listing files
    lessons_output_dir = output_dir / "lessons"
    lessons_output_dir.mkdir(parents=True, exist_ok=True)

    lesson_files: List[Dict[str, str]] = []

    # Sort by each lesson's actual lesson_number, not alphabetically by
    # filename/slug -- filenames are slugified topic titles, so alphabetical
    # order does not match the real lesson sequence and previously caused
    # listings to display the wrong "Lesson N" label (e.g. lesson 1 labelled
    # "Lesson 6"). Fall back to alphabetical only if lesson_number is absent.
    def _lesson_sort_key(p: Path):
        data = _load_json(p)
        num = data.get("lesson_number")
        return (0, num) if isinstance(num, int) else (1, p.name)

    sorted_lesson_paths = sorted(lessons_dir.glob("*.json"), key=_lesson_sort_key)

    for idx, lesson_json_path in enumerate(sorted_lesson_paths, start=1):
        lesson_data = _load_json(lesson_json_path)
        slug = lesson_json_path.stem

        lesson_title = _lesson_display_title(lesson_data, slug)
        essential_question = _lesson_essential_question(lesson_data)
        objectives = _lesson_objectives(lesson_data)
        real_world_example = _lesson_real_world_example(lesson_data)
        activity_summary = _lesson_activity_summary(lesson_data)

        lesson_dir = lessons_output_dir / f"{idx:02d}-{slug}"
        lesson_dir.mkdir(parents=True, exist_ok=True)

        tpt_lesson_path = lesson_dir / "tpt_listing.md"
        tes_lesson_path = lesson_dir / "tes_listing.md"
        gumroad_lesson_path = lesson_dir / "gumroad_listing.md"

        with tpt_lesson_path.open("w", encoding="utf-8") as f:
            f.write(
                "\n".join(
                    _build_lesson_listing_lines(
                        unit_title=title,
                        lesson_title=lesson_title,
                        year_level=year_level,
                        subject=subject,
                        essential_question=essential_question,
                        objectives=objectives,
                        real_world_example=real_world_example,
                        activity_summary=activity_summary,
                        platform_label="TPT",
                        lesson_number=idx,
                        has_pptx_slides=has_pptx_slides,
                    )
                )
            )

        with tes_lesson_path.open("w", encoding="utf-8") as f:
            f.write(
                "\n".join(
                    _build_lesson_listing_lines(
                        unit_title=title,
                        lesson_title=lesson_title,
                        year_level=year_level,
                        subject=subject,
                        essential_question=essential_question,
                        objectives=objectives,
                        real_world_example=real_world_example,
                        activity_summary=activity_summary,
                        platform_label="TES",
                        lesson_number=idx,
                        has_pptx_slides=has_pptx_slides,
                    )
                )
            )

        with gumroad_lesson_path.open("w", encoding="utf-8") as f:
            f.write(
                "\n".join(
                    _build_lesson_listing_lines(
                        unit_title=title,
                        lesson_title=lesson_title,
                        year_level=year_level,
                        subject=subject,
                        essential_question=essential_question,
                        objectives=objectives,
                        real_world_example=real_world_example,
                        activity_summary=activity_summary,
                        platform_label="GUMROAD",
                        lesson_number=idx,
                        has_pptx_slides=has_pptx_slides,
                    )
                )
            )

        lesson_files.append(
            {
                "slug": slug,
                "lesson_title": lesson_title,
                "tpt_listing": str(tpt_lesson_path),
                "tes_listing": str(tes_lesson_path),
                "gumroad_listing": str(gumroad_lesson_path),
            }
        )

    # Workbook listing file
    workbook_listing_path = output_dir / "workbook_listing.md"
    with workbook_listing_path.open("w", encoding="utf-8") as f:
        f.write(generate_workbook_listing(title, lesson_count=lesson_count))

    output_files["workbook_listing"] = str(workbook_listing_path)

     # Assessment listing file
    assessment_listing_path = output_dir / "assessment_listing.md"
    with assessment_listing_path.open("w", encoding="utf-8") as f:
        f.write(generate_assessment_listing(title))

    output_files["assessment_listing"] = str(assessment_listing_path)

    return {
        "unit_id": unit_id,
        "title": title,
        "files": output_files,
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