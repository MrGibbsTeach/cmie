import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

from .ai_lesson_engine import BASE_OUTPUT_DIR, slugify

# Where packaged micro-units (manifest + teacher guide) are stored
PACKAGES_DIR = Path("packages")

# Legacy constants for the original micro-unit.
# These are kept ONLY for standalone packaging / manifest generation.
MICRO_UNIT_NAME: str = "AI & Data Literacy Series – Unit 1: Data Foundations (Lower Secondary)"
YEAR_LEVEL: str = "Lower Secondary"


def _load_lesson_jsons() -> List[Tuple[Path, Dict[str, Any]]]:
    """Load all lesson.json files for the configured micro-unit."""
    unit_slug = slugify(MICRO_UNIT_NAME)
    unit_dir = BASE_OUTPUT_DIR / unit_slug

    if not unit_dir.exists():
        raise SystemExit(
            f"No generated lessons found at {unit_dir}. "
            f"Run `python -m cmie.generator.batch_generate` first."
        )

    lessons: List[Tuple[Path, Dict[str, Any]]] = []
    for lesson_dir in sorted(unit_dir.iterdir()):
        lesson_json = lesson_dir / "lesson.json"
        if not lesson_json.exists():
            continue
        with lesson_json.open(encoding="utf-8") as f:
            data = json.load(f)
        lessons.append((lesson_json, data))

    if not lessons:
        raise SystemExit(
            f"No lesson.json files found under {unit_dir}. "
            f"Run the batch generator first."
        )

    return lessons


def build_manifest(lessons: List[Tuple[Path, Dict[str, Any]]]) -> Dict[str, Any]:
    manifest_lessons: List[Dict[str, Any]] = []

    for lesson_path, data in lessons:
        topic_slug = lesson_path.parent.name
        manifest_lessons.append(
            {
                "topic_slug": topic_slug,
                "lesson_title": data.get("lesson_title"),
                "objectives": data.get("objectives", []),
                "essential_question": data.get("essential_question"),
            }
        )

    manifest: Dict[str, Any] = {
        "micro_unit_name": MICRO_UNIT_NAME,
        "year_level": YEAR_LEVEL,
        "lesson_count": len(manifest_lessons),
        "lessons": manifest_lessons,
    }
    return manifest


def build_teacher_guide_text(manifest: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("Vertex Learning Studio")
    lines.append(f"{manifest['micro_unit_name']}  ({manifest['year_level']})")
    lines.append("")
    lines.append("Overview")
    lines.append("--------")
    lines.append(
        "This micro-unit introduces middle school students to data literacy "
        "for the AI age, focusing on how data is collected, structured, "
        "used, and sometimes misused in modern AI systems."
    )
    lines.append("")
    lines.append(f"Number of lessons: {manifest['lesson_count']}")
    lines.append("Recommended lesson length: 45–60 minutes")
    lines.append("Suggested sequence: teach in order, but individual lessons can stand alone.")
    lines.append("")

    lines.append("Lesson Outline")
    lines.append("--------------")

    for idx, lesson in enumerate(manifest["lessons"], start=1):
        title = lesson.get("lesson_title") or "Lesson"
        lines.append(f"{idx}. {title}")
        eq = lesson.get("essential_question")
        if eq:
            lines.append(f"   Essential question: {eq}")
        objs = lesson.get("objectives") or []
        if objs:
            lines.append("   Learning objectives:")
            for obj in objs:
                lines.append(f"     - {obj}")
        lines.append("")

    lines.append("Implementation Notes")
    lines.append("--------------------")
    lines.append(
        "• Slides are designed to be used directly with students, with clear "
        "objectives, an essential question, a reusable thinking framework, "
        "guided and independent tasks, and an exit ticket."
    )
    lines.append(
        "• Mix whole-class discussion with pair or small group work, especially "
        "around case studies and data ethics questions."
    )
    lines.append(
        "• Use the DATA LENS-style frameworks consistently across lessons so "
        "students recognise and reuse the same analytical moves."
    )
    lines.append(
        "• For assessment, combine exit tickets, short written reflections, "
        "and project work (e.g., a small data collection and analysis task)."
    )

    return "\n".join(lines)


def package_micro_unit() -> Tuple[Path, Path]:
    """
    Legacy / manual packaging entrypoint.

    - Loads lessons for MICRO_UNIT_NAME from generated_lessons.
    - Builds manifest.json and teacher_guide.txt under PACKAGES_DIR/<unit_slug>.
    """
    lessons = _load_lesson_jsons()
    manifest = build_manifest(lessons)

    unit_slug = slugify(MICRO_UNIT_NAME)
    out_dir = PACKAGES_DIR / unit_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    guide_text = build_teacher_guide_text(manifest)
    guide_path = out_dir / "teacher_guide.txt"
    with guide_path.open("w", encoding="utf-8") as f:
        f.write(guide_text)

    print(f"Saved manifest to: {manifest_path}")
    print(f"Saved teacher guide to: {guide_path}")
    return manifest_path, guide_path


if __name__ == "__main__":
    package_micro_unit()