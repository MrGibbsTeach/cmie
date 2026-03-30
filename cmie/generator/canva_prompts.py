# LEGACY: Canva prompt generation system (replaced by CSV → Canva workflow)
# Do not delete yet. Still partially referenced in pipeline.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_lesson_engine import slugify


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _split_into_bullet_lines(body_text: str) -> List[str]:
    lines: List[str] = []

    for block in (body_text or "").split("\n"):
        block = block.strip()
        if not block:
            continue

        if block.lower().startswith("output:"):
            continue
        if block.lower().startswith("you must:"):
            continue

        parts = block.split(". ")

        for part in parts:
            part = part.strip().rstrip(".")
            part = part.lstrip("•").lstrip("-").strip()
            if part:
                lines.append(part)

    return lines


def _write_prompt_file(
    output_dir: Path,
    lesson_number: Optional[int],
    slug_source: str,
    suffix: str,
    content: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{lesson_number:02d}-" if isinstance(lesson_number, int) else ""
    topic_slug = slugify(slug_source)
    out_path = output_dir / f"{prefix}{topic_slug}-{suffix}.txt"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def _lesson_to_canva_prompt_text(lesson: Dict[str, Any]) -> str:
    title = lesson.get("lesson_title") or lesson.get("topic_title") or "Lesson"
    unit_name = lesson.get("unit_name", "")
    year_level = lesson.get("year_level", "")
    essential_question = lesson.get("essential_question", "")

    objectives = [
        o.strip()
        for o in lesson.get("objectives", [])
        if isinstance(o, str) and o.strip()
    ][:3]

    source_slides = lesson.get("slides", []) or []

    def first_slide_of_type(slide_type: str) -> Optional[Dict[str, Any]]:
        for s in source_slides:
            if (s.get("type") or "").strip() == slide_type:
                return s
        return None

    def all_slides_of_type(slide_type: str) -> List[Dict[str, Any]]:
        return [
            s for s in source_slides
            if (s.get("type") or "").strip() == slide_type
        ]

    hook_slide = first_slide_of_type("hook")
    content_slides = all_slides_of_type("content")[:3]
    real_world_slide = first_slide_of_type("real_world")
    activity_slide = first_slide_of_type("activity")
    reflection_slide = first_slide_of_type("reflection")

    lines: List[str] = []

    lines.append("Create a polished 10-slide classroom presentation.")
    lines.append("")
    lines.append("STYLE")
    lines.append("- modern classroom design")
    lines.append("- strong visual hierarchy")
    lines.append("- minimal text per slide")
    lines.append("- clean layouts with icons or simple diagrams where useful")
    lines.append("- student-facing language")
    lines.append("")
    lines.append("SLIDES")

    lines.append("1. Title slide")
    lines.append(f"Title: {title}")
    subtitle_parts = [p for p in [unit_name, year_level] if p]
    if subtitle_parts:
        lines.append(f"Subtitle: {' • '.join(subtitle_parts)}")
    lines.append("")

    lines.append("2. Lesson objectives")
    for obj in objectives:
        lines.append(f"- {obj}")
    lines.append("")

    lines.append("3. Essential question")
    if essential_question:
        lines.append(f"- {essential_question}")
    lines.append("")

    lines.append("4. Hook Scenario")
    if hook_slide and hook_slide.get("body"):
        for line in _split_into_bullet_lines(hook_slide.get("body", ""))[:4]:
            lines.append(f"- {line}")
    lines.append("")

    for idx, content_slide in enumerate(content_slides, start=5):
        lines.append(f"{idx}. {content_slide.get('title', 'Key Idea')}")
        for line in _split_into_bullet_lines(content_slide.get("body", ""))[:4]:
            lines.append(f"- {line}")
        lines.append("")

    next_slide_number = 5 + len(content_slides)

    if real_world_slide:
        lines.append(f"{next_slide_number}. {real_world_slide.get('title', 'Real-World Example')}")
        for line in _split_into_bullet_lines(real_world_slide.get("body", ""))[:4]:
            lines.append(f"- {line}")
        lines.append("")
        next_slide_number += 1

    if activity_slide:
        lines.append(f"{next_slide_number}. {activity_slide.get('title', 'Activity')}")
        for line in _split_into_bullet_lines(activity_slide.get("body", ""))[:6]:
            lines.append(f"- {line}")
        lines.append("")
        next_slide_number += 1

    if reflection_slide:
        lines.append(f"{next_slide_number}. {reflection_slide.get('title', 'Reflection')}")
        for line in _split_into_bullet_lines(reflection_slide.get("body", ""))[:4]:
            lines.append(f"- {line}")
        lines.append("")

    lines.append("Keep it visually polished, clear, and classroom-ready.")

    return "\n".join(lines)


def lesson_json_to_canva_prompt(
    lesson_json_path: Path,
    output_dir: Path | None = None,
) -> Path:
    lesson = _load_json(lesson_json_path)
    prompt_text = _lesson_to_canva_prompt_text(lesson)

    if output_dir is None:
        output_dir = lesson_json_path.parent

    return _write_prompt_file(
        output_dir=output_dir,
        lesson_number=lesson.get("lesson_number"),
        slug_source=lesson.get("topic_title", lesson.get("lesson_title", "lesson")),
        suffix="canva-prompt",
        content=prompt_text,
    )


def _assessment_to_canva_prompt_text(assessment: Dict[str, Any]) -> str:
    title = assessment.get("assessment_title", "Assessment")
    unit_name = assessment.get("unit_name", "")
    year_level = assessment.get("year_level", "")
    brief = assessment.get("task_for_students", {}).get("brief", "")
    steps = assessment.get("task_for_students", {}).get("steps", []) or []
    deliverables = assessment.get("task_for_students", {}).get("deliverables", []) or []
    success_criteria = assessment.get("success_criteria", []) or []

    lines: List[str] = []
    lines.append("Create a polished printable classroom assessment document.")
    lines.append("")
    lines.append("STYLE")
    lines.append("- clean worksheet layout")
    lines.append("- clear headings and question spacing")
    lines.append("- readable fonts")
    lines.append("- minimal decoration")
    lines.append("- student-friendly design")
    lines.append("")
    lines.append("CONTENT")
    lines.append(f"Title: {title}")

    subtitle_parts = [p for p in [unit_name, year_level] if p]
    if subtitle_parts:
        lines.append(f"Subtitle: {' • '.join(subtitle_parts)}")

    if brief:
        lines.append("")
        lines.append("Task overview")
        lines.append(brief)

    if steps:
        lines.append("")
        lines.append("Steps")
        for step in steps:
            lines.append(f"- {step}")

    if deliverables:
        lines.append("")
        lines.append("What to submit")
        for item in deliverables:
            lines.append(f"- {item}")

    if success_criteria:
        lines.append("")
        lines.append("Success criteria")
        for item in success_criteria:
            lines.append(f"- {item}")

    lines.append("")
    lines.append("Leave suitable space for student responses where appropriate.")

    return "\n".join(lines)

def assessment_json_to_canva_prompt(
    assessment_json_path: Path,
    output_dir: Path | None = None,
) -> Path:
    assessment = _load_json(assessment_json_path)
    if output_dir is None:
        output_dir = assessment_json_path.parent

    prompt_text = _assessment_to_canva_prompt_text(assessment)

    return _write_prompt_file(
        output_dir=output_dir,
        lesson_number=None,
        slug_source=assessment.get("assessment_title", "assessment"),
        suffix="canva-prompt",
        content=prompt_text,
    )


def workbook_markdown_to_canva_prompt(workbook_path: Path) -> Path:
    """
    Generate a Canva-friendly prompt for creating a student workbook.
    Uses a pattern-based structure instead of dumping full markdown.
    """
    text = workbook_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    unit_title = "Student Workbook"
    lesson_titles: List[str] = []

    for line in lines:
        if line.startswith("# "):
            unit_title = line.replace("# ", "").strip()
            break

    for line in lines:
        if line.startswith("## "):
            lesson_titles.append(line.replace("## ", "").strip())

    lesson_titles = lesson_titles[:10]

    prompt_lines: List[str] = []
    prompt_lines.append("Create a polished multi-page student workbook document.")
    prompt_lines.append("")
    prompt_lines.append("STYLE")
    prompt_lines.append("- clean educational worksheet design")
    prompt_lines.append("- modern layout with clear section headings")
    prompt_lines.append("- plenty of space for student responses")
    prompt_lines.append("- consistent formatting across all pages")
    prompt_lines.append("- suitable for printing or digital use")
    prompt_lines.append("")
    prompt_lines.append("CONTENT")
    prompt_lines.append(f"Unit: {unit_title}")
    prompt_lines.append("Audience: Lower Secondary")
    prompt_lines.append("")
    prompt_lines.append("Create one section per lesson using the SAME structure:")
    prompt_lines.append("- lesson title")
    prompt_lines.append("- essential question")
    prompt_lines.append("- 2–3 short learning goals")
    prompt_lines.append("- activity 1: explain the concept")
    prompt_lines.append("- activity 2: apply the concept")
    prompt_lines.append("- activity 3: reflect on learning")
    prompt_lines.append("- space for written responses")
    prompt_lines.append("")
    prompt_lines.append("Lessons:")

    for i, title in enumerate(lesson_titles, start=1):
        prompt_lines.append(f"{i}. {title}")

    prompt_lines.append("")
    prompt_lines.append("Ensure:")
    prompt_lines.append("- consistent layout across all lessons")
    prompt_lines.append("- clear separation between sections")
    prompt_lines.append("- student-friendly language")
    prompt_lines.append("- no overcrowding of content")

    prompt_path = workbook_path.with_name("student-workbook-canva-prompt.txt")
    prompt_path.write_text("\n".join(prompt_lines), encoding="utf-8")

    return prompt_path


def roadmap_markdown_to_canva_prompt(roadmap_path: Path) -> Path:
    """
    Generate a Canva-friendly prompt for a visual unit roadmap.
    Converts roadmap markdown into a short visual brief.
    """
    text = roadmap_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    unit_title = "Unit Roadmap"
    year_level = ""
    subject = ""
    lesson_titles: List[str] = []
    assessment_title = ""

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# "):
            unit_title = stripped.replace("# ", "").strip()

        elif stripped.startswith("**Year level:**"):
            year_level = stripped.replace("**Year level:**", "").strip()

        elif stripped.startswith("**Subject:**"):
            subject = stripped.replace("**Subject:**", "").strip()

        elif stripped.startswith("|") and not stripped.startswith("| Lesson |") and not stripped.startswith("|---|"):
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) >= 2:
                lesson_title = parts[1]
                if lesson_title and lesson_title.lower() != "title":
                    lesson_titles.append(lesson_title)

        elif stripped.startswith("**Title:**"):
            assessment_title = stripped.replace("**Title:**", "").strip()

    lesson_titles = lesson_titles[:10]

    prompt_lines: List[str] = []
    prompt_lines.append("Create a polished visual unit roadmap infographic.")
    prompt_lines.append("")
    prompt_lines.append("STYLE")
    prompt_lines.append("- clean and modern educational design")
    prompt_lines.append("- clear sequence or timeline layout")
    prompt_lines.append("- minimal clutter")
    prompt_lines.append("- strong visual hierarchy")
    prompt_lines.append("- suitable for teachers and students")
    prompt_lines.append("")
    prompt_lines.append("CONTENT")
    prompt_lines.append(f"Unit: {unit_title}")

    if year_level:
        prompt_lines.append(f"Audience: {year_level}")
    if subject:
        prompt_lines.append(f"Subject: {subject}")

    prompt_lines.append("")
    prompt_lines.append("Show this lesson sequence:")

    for i, title in enumerate(lesson_titles, start=1):
        prompt_lines.append(f"{i}. {title}")

    if assessment_title:
        prompt_lines.append("")
        prompt_lines.append("Assessment:")
        prompt_lines.append(assessment_title)

    prompt_lines.append("")
    prompt_lines.append("Include:")
    prompt_lines.append("- a clear title at the top")
    prompt_lines.append("- visual flow from start to end")
    prompt_lines.append("- simple icons or visual cues if appropriate")
    prompt_lines.append("")
    prompt_lines.append("Keep text concise and easy to read.")

    prompt_path = roadmap_path.with_name("unit-roadmap-canva-prompt.txt")
    prompt_path.write_text("\n".join(prompt_lines), encoding="utf-8")

    return prompt_path