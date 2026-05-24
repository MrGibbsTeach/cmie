from pathlib import Path
import json
from typing import Dict, Any


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def render_assessment_markdown(assessment_dir: Path) -> Dict[str, str]:
    """
    Read assessment.json, rubric.json, marking_guide.json from assessment_dir and
    emit teacher-friendly markdown files in the same folder:

    - assessment_task.md
    - assessment_rubric_marking.md

    Returns paths as strings in a dict.
    """
    assessment_path = assessment_dir / "assessment.json"
    rubric_path = assessment_dir / "rubric.json"
    marking_path = assessment_dir / "marking_guide.json"

    assessment = _load_json(assessment_path)
    rubric = _load_json(rubric_path)
    marking = _load_json(marking_path)

    unit_name = assessment.get("unit_name", "")
    year_level = assessment.get("year_level", "")
    title = assessment.get("assessment_title", "")
    overview = assessment.get("overview", "")
    task_ctx = assessment.get("task_context", "")
    tf = assessment.get("task_for_students", {})
    teacher = assessment.get("teacher_instructions", {})
    success_criteria = assessment.get("success_criteria", [])
    timing = assessment.get("timing", "")
    materials = assessment.get("materials", [])
    differentiation = assessment.get("differentiation", {})

    # -----------------------------
    # Task markdown
    # -----------------------------
    lines_task = []
    lines_task.append(f"# {title}")
    lines_task.append("")
    if unit_name:
        lines_task.append(f"**Unit:** {unit_name} ({year_level})")
        lines_task.append("")
    if overview:
        lines_task.append("## Task overview")
        lines_task.append("")
        lines_task.append(overview)
        lines_task.append("")
    if task_ctx:
        lines_task.append("## Context")
        lines_task.append("")
        lines_task.append(task_ctx)
        lines_task.append("")

    # Student-facing instructions
    lines_task.append("## Task instructions for students")
    lines_task.append("")
    brief = tf.get("brief") or ""
    if brief:
        lines_task.append(brief)
        lines_task.append("")

    steps = tf.get("steps") or []
    if steps:
        lines_task.append("### Steps")
        lines_task.append("")
        for step in steps:
            lines_task.append(f"- {step}")
        lines_task.append("")

    deliverables = tf.get("deliverables") or []
    if deliverables:
        lines_task.append("### What you will submit")
        lines_task.append("")
        for d in deliverables:
            lines_task.append(f"- {d}")
        lines_task.append("")

    # Student checklist (from success criteria)
    if success_criteria:
        lines_task.append("## Student checklist")
        lines_task.append("")
        lines_task.append("Before you submit, check that you have:")
        lines_task.append("")
        for sc in success_criteria:
            lines_task.append(f"- {sc}")
        lines_task.append("")

    # Practical details
    if timing or materials:
        lines_task.append("## Practical details")
        lines_task.append("")
        if timing:
            lines_task.append(f"**Timing:** {timing}")
        if materials:
            lines_task.append("")
            lines_task.append("**Materials:**")
            for m in materials:
                lines_task.append(f"- {m}")
        lines_task.append("")

    task_path = assessment_dir / "assessment_task.md"
    with task_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines_task))

    # -----------------------------
    # Rubric + marking markdown
    # -----------------------------
    lines_rm: list[str] = []
    lines_rm.append("# Assessment rubric and marking guide")
    lines_rm.append("")

    levels = rubric.get("levels", [])
    criteria = rubric.get("criteria", [])

    if levels and criteria:
        lines_rm.append("## Rubric")
        lines_rm.append("")
        # Table header
        header = "| Criterion | " + " | ".join(levels) + " |"
        sep = "|---" * (len(levels) + 1) + "|"
        lines_rm.append(header)
        lines_rm.append(sep)

        for crit in criteria:
            name = crit.get("name", "")
            desc = crit.get("descriptors", {})
            row = [name] + [desc.get(level, "") for level in levels]
            lines_rm.append("| " + " | ".join(row) + " |")

        lines_rm.append("")

    # Marking guide sections
    if marking:
        lines_rm.append("## Marking guide")
        lines_rm.append("")
        general = marking.get("general_notes", [])
        features = marking.get("high_quality_response_features", [])
        misconceptions = marking.get("common_misconceptions", [])

        if general:
            lines_rm.append("### General notes")
            lines_rm.append("")
            for g in general:
                lines_rm.append(f"- {g}")
            lines_rm.append("")

        if features:
            lines_rm.append("### Features of high-quality responses")
            lines_rm.append("")
            for ftr in features:
                lines_rm.append(f"- {ftr}")
            lines_rm.append("")

        if misconceptions:
            lines_rm.append("### Common misconceptions")
            lines_rm.append("")
            for m in misconceptions:
                lines_rm.append(f"- {m}")
            lines_rm.append("")

    rm_path = assessment_dir / "assessment_rubric_marking.md"
    with rm_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines_rm))

    return {
        "task_markdown": str(task_path),
        "rubric_markdown": str(rm_path),
    }