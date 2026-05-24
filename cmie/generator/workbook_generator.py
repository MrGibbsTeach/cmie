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
        data["_source_path"] = str(path)
        lessons.append(data)

    return lessons

def _lesson_specific_task(title: str) -> List[str]:
    t = title.lower()

    if "bias" in t:
        return [
            "### Quick Task: Spot the Bias",
            "- Which example shows bias?",
            "- Why is it biased?",
            "- Who might be affected?",
            ""
        ]

    if "fair" in t:
        return [
            "### Quick Task: Fair or Unfair?",
            "- Decide if the AI decision is fair",
            "- Explain your reasoning",
            "- Suggest one improvement",
            ""
        ]

    if "responsible" in t:
        return [
            "### Quick Task: Who Is Responsible?",
            "- List all people involved",
            "- Who should be accountable?",
            "- Explain why",
            ""
        ]

    if "design" in t:
        return [
            "### Quick Task: Improve the System",
            "- What is one flaw?",
            "- How would you fix it?",
            "- How does your fix improve fairness?",
            ""
        ]

    return [
        "### Quick Task",
        "- Apply today’s idea to a real-world example",
        "- Explain your thinking",
        ""
    ]


def generate_student_workbook(
    unit_root: Path,
    unit_config: Dict[str, Any],
    lessons_dir: Path,
    assessment_dir: Optional[Path] = None,
) -> Path:
    """
    Generate a printable student workbook in a more structured worksheet style.
    """
    output_dir = unit_root / "workbook"
    output_dir.mkdir(parents=True, exist_ok=True)

    lessons = _load_lessons(lessons_dir)

    title = unit_config.get("title", "Unit workbook")
    year_level = unit_config.get("year_level", "")
    subject = unit_config.get("subject", "")

    lines: List[str] = []

    # Workbook front heading
    lines.append("NAME: ________________________________________________")
    lines.append("")
    lines.append("# STUDENT WORKBOOK")
    lines.append("")
    lines.append(f"## {title}")
    if year_level or subject:
        meta_bits = []
        if year_level:
            meta_bits.append(year_level)
        if subject:
            meta_bits.append(subject)
        lines.append("")
        lines.append(" / ".join(meta_bits))
    lines.append("")
    lines.append("---")
    lines.append("")

    for lesson in sorted(lessons, key=lambda l: l.get("lesson_number", 0)):
        ln = lesson.get("lesson_number", "")
        lt = lesson.get("lesson_title") or lesson.get("topic_title", "Lesson")
        eq = lesson.get("essential_question", "")
        objs = lesson.get("objectives", [])

        lines.append(f"## LESSON {ln}: {lt}")
        lines.append("")

        if eq:
            lines.append("### ESSENTIAL QUESTION")
            lines.append(eq)
            lines.append("")

        if objs:
            lines.append("### LEARNING GOALS")
            for o in objs[:3]:
                lines.append(f"- {o}")
            lines.append("")

        # Lesson-specific task
        lines.extend(_lesson_specific_task(lt))
        lines.append("")

        # Section 1
        lines.append("### Explain this idea in your own words:")
        lines.append("- Key idea:")
        lines.append("- Example from the lesson:")
        lines.append("- Why this matters in real life:")
        lines.append("")
        lines.append("[Write your response below]")
        lines.append("")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("")

        # Section 2
        lines.append("### Apply the idea to a new situation:")
        lines.append("- Describe a scenario where this idea appears:")
        lines.append("- What could go wrong in this scenario?")
        lines.append("- How could data or AI be used fairly here?")
        lines.append("")
        lines.append("[Write your response below]")
        lines.append("")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("")

        # Section 3
        lines.append("### Reflect on your learning:")
        lines.append("- What part of this lesson was easiest?")
        lines.append("- What part was hardest?")
        lines.append("- One question you still have:")
        lines.append("")
        lines.append("[Write your response below]")
        lines.append("")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("____________________________________________________________")
        lines.append("")

        lines.append("---")
        lines.append("")

    workbook_path = output_dir / "student_workbook.md"
    with workbook_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return workbook_path