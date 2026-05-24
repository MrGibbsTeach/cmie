from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from openai import OpenAI

from .ai_lesson_engine import BASE_OUTPUT_DIR, slugify
from .package_micro_unit import PACKAGES_DIR, MICRO_UNIT_NAME, YEAR_LEVEL

DEFAULT_MODEL = "gpt-4.1-mini"


# -----------------------------
# Helpers
# -----------------------------


def ensure_openai_client() -> OpenAI:
    """
    Return an OpenAI client. Assumes OPENAI_API_KEY is set in environment.
    """
    return OpenAI()


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_lessons_from_dir(lessons_dir: Path) -> List[Dict[str, Any]]:
    lessons: List[Dict[str, Any]] = []
    if not lessons_dir.exists():
        return lessons

    for lesson_path in sorted(lessons_dir.glob("*.json")):
        data = _load_json(lesson_path)
        if data:
            lessons.append(data)

    return lessons


def load_manifest() -> Dict[str, Any]:
    """
    Legacy manifest loader used by the standalone CLI.

    Behaviour:
    - First, try the slugified MICRO_UNIT_NAME (current pattern).
    - Second, try a legacy slug with any trailing "-year-..." dropped.
    - If no manifest is found, fall back to a minimal manifest
      built from the current constants instead of exiting.
    """
    unit_slug = slugify(MICRO_UNIT_NAME)

    candidate_paths: List[Path] = []

    candidate_paths.append(PACKAGES_DIR / unit_slug / "manifest.json")

    if "-year-" in unit_slug:
        legacy_slug = unit_slug.split("-year-")[0]
        candidate_paths.append(PACKAGES_DIR / legacy_slug / "manifest.json")

    for manifest_path in candidate_paths:
        if manifest_path.exists():
            with manifest_path.open(encoding="utf-8") as f:
                manifest = json.load(f)

            manifest.setdefault("micro_unit_name", MICRO_UNIT_NAME)
            manifest.setdefault("year_level", YEAR_LEVEL)
            manifest.setdefault("unit_slug", unit_slug)
            manifest.setdefault("lessons", [])
            return manifest

    return {
        "micro_unit_name": MICRO_UNIT_NAME,
        "year_level": YEAR_LEVEL,
        "unit_slug": unit_slug,
        "lessons": [],
    }


def build_manifest_from_pipeline_inputs(
    unit_id: str,
    title: str,
    year_level: str,
    subject: str,
    lessons_dir: Path,
) -> Dict[str, Any]:
    """
    Build a manifest directly from the current pipeline run, rather than relying
    on legacy package manifests.
    """
    lesson_payloads = _load_lessons_from_dir(lessons_dir)

    lessons: List[Dict[str, Any]] = []
    for idx, lesson in enumerate(lesson_payloads, start=1):
        lessons.append(
            {
                "lesson_number": lesson.get("lesson_number", idx),
                "lesson_title": lesson.get("lesson_title") or lesson.get("topic_title") or f"Lesson {idx}",
                "essential_question": lesson.get("essential_question", ""),
                "objectives": lesson.get("objectives", []),
            }
        )

    return {
        "unit_id": unit_id,
        "unit_slug": slugify(title),
        "micro_unit_name": title,
        "year_level": year_level,
        "subject": subject,
        "lessons": lessons,
    }


def infer_unit_focus(unit_name: str, lessons: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Infer assessment framing from the unit title and lesson sequence so the task
    is specific to the actual unit being generated.
    """
    base = f"{unit_name} " + " ".join(
        str(lesson.get("lesson_title", "")) for lesson in lessons
    )
    text = base.lower()

    if "ethics" in text or "bias" in text or "fair" in text:
        return {
            "unit_context": (
                "This is a Lower Secondary AI ethics and bias unit. Students have explored "
                "how bias enters data and AI systems, how unfair outcomes affect people, "
                "who is responsible for AI decisions, and how fairer systems can be designed."
            ),
            "scenario": (
                "A school is trialling an AI-supported system to help recommend students for "
                "extension programs, interventions, and leadership opportunities. Some teachers "
                "and students are concerned that the system may unfairly advantage some groups "
                "while disadvantaging others."
            ),
            "assessment_title": "Evaluating Bias and Fairness in an AI Decision System",
            "driving_question": "How can we evaluate whether an AI system is fair, responsible, and trustworthy?",
            "task_focus": (
                "evaluate bias, fairness, responsibility, and ethical decision-making in an AI system"
            ),
        }

    if "model" in text or "prediction" in text or "classification" in text or "recommendation" in text:
        return {
            "unit_context": (
                "This is a Lower Secondary AI models unit. Students have explored how AI models "
                "learn from data, use training and testing data, find patterns, classify inputs, "
                "and generate recommendations or predictions."
            ),
            "scenario": (
                "A company has developed an AI recommendation system that suggests books to students "
                "based on reading history, ratings, and browsing behaviour."
            ),
            "assessment_title": "Evaluating an AI Recommendation Model",
            "driving_question": "How can we evaluate how well an AI model uses data to make decisions?",
            "task_focus": (
                "evaluate how an AI model uses data, patterns, and predictions to produce outputs"
            ),
        }

    return {
        "unit_context": (
            "This is a Lower Secondary AI and data literacy unit. Students have explored how data "
            "is collected, organised, interpreted, and used in AI systems."
        ),
        "scenario": (
            "A digital system is collecting and using student data to make recommendations and support decisions."
        ),
        "assessment_title": "Evaluating Data Use in an AI System",
        "driving_question": "How can we evaluate the quality, fairness, and usefulness of data in AI systems?",
        "task_focus": (
            "evaluate how data quality, fairness, and system design affect AI outcomes"
        ),
    }


# -----------------------------
# Prompt construction
# -----------------------------


def build_assessment_prompt(manifest: Dict[str, Any]) -> str:
    unit_name = manifest["micro_unit_name"]
    year_level = manifest["year_level"]
    subject = manifest.get("subject", "Digital Technologies")
    lessons = manifest.get("lessons", [])

    focus = infer_unit_focus(unit_name, lessons)

    lesson_lines: List[str] = []
    for idx, lesson in enumerate(lessons, start=1):
        title = lesson.get("lesson_title") or f"Lesson {idx}"
        eq = lesson.get("essential_question") or ""
        lesson_lines.append(f"{idx}. {title}")
        if eq:
            lesson_lines.append(f"   EQ: {eq}")
        lesson_lines.append("")

    lesson_block = "\n".join(lesson_lines)

    return (
        "You are an expert curriculum designer creating high-quality, classroom-ready assessments.\n\n"

        "Design a summative assessment that feels like a REAL classroom task, not generic AI content.\n\n"

        f"Unit name: {unit_name}\n"
        f"Year level: {year_level}\n"
        f"Subject: {subject}\n\n"

        f"Lesson sequence:\n{lesson_block}\n\n"

        "Unit context:\n"
        f"- {focus['unit_context']}\n"
        f"- Scenario: {focus['scenario']}\n"
        f"- Focus: {focus['task_focus']}\n"
        f"- Driving question: {focus['driving_question']}\n\n"

        "CRITICAL REQUIREMENTS:\n"
        "- The task must be SPECIFIC to this unit (no generic wording).\n"
        "- The task must include a clear student ROLE.\n"
        "- The task must include a realistic SCENARIO.\n"
        "- The task must include a STEP-BY-STEP STRUCTURE students can follow.\n"
        "- The task must clearly define OUTPUT FORMAT (report, presentation, etc).\n"
        "- The task must be doable in 1–2 lessons.\n\n"

        "TASK STRUCTURE MUST INCLUDE:\n"
        "- Task overview\n"
        "- Scenario\n"
        "- Student role\n"
        "- Step-by-step instructions (at least 4 steps)\n"
        "- Deliverables\n"
        "- Success checklist\n\n"

        "RUBRIC REQUIREMENTS:\n"
        "- Exactly 4 performance levels: Exemplary, Proficient, Developing, Beginning\n"
        "- 4–5 criteria only\n"
        "- Each level must scale clearly in:\n"
        "  accuracy → depth → clarity → use of evidence\n"
        "- Avoid vague phrases like 'good understanding'\n\n"

        "MARKING GUIDE REQUIREMENTS:\n"
        "- What strong responses include\n"
        "- What weak responses miss\n"
        "- Common misconceptions\n\n"

        "Respond ONLY with valid JSON using this schema:\n\n"

        "{\n"
        '  "unit_name": string,\n'
        '  "unit_slug": string,\n'
        '  "year_level": string,\n'
        '  "assessment_title": string,\n'
        '  "essential_question": string,\n'
        '  "overview": string,\n'
        '  "task_context": string,\n'
        '  "student_role": string,\n'
        '  "task_for_students": {\n'
        '    "brief": string,\n'
        '    "steps": [string],\n'
        '    "deliverables": [string]\n'
        "  },\n"
        '  "success_criteria": [string],\n'
        '  "rubric": {\n'
        '    "levels": [string],\n'
        '    "criteria": [\n'
        "      {\n"
        '        "name": string,\n'
        '        "descriptors": {\n'
        '          "Exemplary": string,\n'
        '          "Proficient": string,\n'
        '          "Developing": string,\n'
        '          "Beginning": string\n'
        "        }\n"
        "      }\n"
        "    ]\n"
        "  },\n"
        '  "marking_guide": {\n'
        '    "general_notes": [string],\n'
        '    "high_quality_response_features": [string],\n'
        '    "common_misconceptions": [string]\n'
        "  },\n"
        '  "timing": string,\n'
        '  "materials": [string]\n'
        "}\n"
    )


# -----------------------------
# Core generation
# -----------------------------


def generate_assessment_schema(
    manifest: Dict[str, Any],
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Call OpenAI to generate the assessment JSON matching the schema.
    """
    client = ensure_openai_client()
    prompt = build_assessment_prompt(manifest)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You design curriculum and respond ONLY with strict JSON when asked. "
                    "The assessment must align to the provided unit title and lesson sequence."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
    )
    raw = resp.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start : end + 1])
        else:
            raise

    unit_slug = manifest.get("unit_slug") or slugify(manifest["micro_unit_name"])
    data["unit_slug"] = unit_slug
    data["unit_name"] = manifest["micro_unit_name"]
    data["year_level"] = manifest["year_level"]

    return data


# -----------------------------
# Saving
# -----------------------------


def save_assessment_assets(
    assessment: Dict[str, Any],
    out_dir: Path,
) -> Dict[str, Path]:
    """
    Save the full assessment plus split-out rubric and marking guide to JSON files.

    Returns a dict with the paths to each file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    assessment_path = out_dir / "assessment.json"
    with assessment_path.open("w", encoding="utf-8") as f:
        json.dump(assessment, f, ensure_ascii=False, indent=2)

    rubric = assessment.get("rubric", {})
    rubric_path = out_dir / "rubric.json"
    with rubric_path.open("w", encoding="utf-8") as f:
        json.dump(rubric, f, ensure_ascii=False, indent=2)

    marking_guide = assessment.get("marking_guide", {})
    marking_path = out_dir / "marking_guide.json"
    with marking_path.open("w", encoding="utf-8") as f:
        json.dump(marking_guide, f, ensure_ascii=False, indent=2)

    return {
        "assessment": assessment_path,
        "rubric": rubric_path,
        "marking_guide": marking_path,
    }


def save_assessment_schema(assessment: Dict[str, Any]) -> Path:
    """
    Legacy helper used by the standalone CLI.

    Writes assets under BASE_OUTPUT_DIR/<unit_slug>/assessment and returns
    the path to assessment.json.
    """
    unit_slug = slugify(assessment["unit_name"])
    out_dir = BASE_OUTPUT_DIR / unit_slug / "assessment"
    paths = save_assessment_assets(assessment, out_dir)
    return paths["assessment"]


# -----------------------------
# Pipeline entrypoint
# -----------------------------


def generate_summative_assessment(
    unit_id: str,
    title: str,
    year_level: str,
    subject: str,
    output_dir: Path,
    extra: Optional[Dict[str, Any]] = None,
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Pipeline-friendly entry point.

    Intended to be called by full_product_pipeline.py.
    """
    extra = extra or {}

    manifest: Dict[str, Any]
    if extra.get("manifest"):
        manifest = extra["manifest"]
    else:
        lessons_dir = output_dir.parent / "lessons"
        manifest = build_manifest_from_pipeline_inputs(
            unit_id=unit_id,
            title=title,
            year_level=year_level,
            subject=subject,
            lessons_dir=lessons_dir,
        )

    assessment = generate_assessment_schema(manifest, model=model)
    paths = save_assessment_assets(assessment, output_dir)

    return {
        "unit_id": unit_id,
        "title": title,
        "year_level": year_level,
        "subject": subject,
        "files": {
            "assessment": str(paths["assessment"]),
            "rubric": str(paths["rubric"]),
            "marking_guide": str(paths["marking_guide"]),
        },
    }


# -----------------------------
# Standalone CLI
# -----------------------------


def generate_and_save_assessment(model: str = DEFAULT_MODEL) -> Path:
    """
    High-level entry point for manual use:
    - Load manifest (from PACKAGES_DIR)
    - Generate assessment schema via OpenAI
    - Save to disk under BASE_OUTPUT_DIR/<unit_slug>/assessment
    - Return path to assessment.json
    """
    manifest = load_manifest()
    assessment = generate_assessment_schema(manifest, model=model)
    path = save_assessment_schema(assessment)

    print(f"Generated assessment for unit '{manifest['micro_unit_name']}'")
    print(f"Saved assessment (incl. rubric & marking guide) to: {path.parent}")
    return path


if __name__ == "__main__":
    generate_and_save_assessment()