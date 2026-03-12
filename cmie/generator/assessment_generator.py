import json
from pathlib import Path
from typing import Dict, Any, Optional

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


def load_manifest() -> Dict[str, Any]:
    """
    Load the manifest.json for the current micro-unit.

    Behaviour:
    - First, try the slugified MICRO_UNIT_NAME (current pattern).
    - Second, try a legacy slug with any trailing "-year-..." dropped.
    - If no manifest is found, fall back to a minimal manifest
      built from the current constants instead of exiting.
    """
    unit_slug = slugify(MICRO_UNIT_NAME)

    candidate_paths: List[Path] = []

    # Current expected location
    candidate_paths.append(PACKAGES_DIR / unit_slug / "manifest.json")

    # Legacy: if the slug ends with "-year-7", "-year-8", etc., try the base part
    if "-year-" in unit_slug:
        legacy_slug = unit_slug.split("-year-")[0]
        candidate_paths.append(PACKAGES_DIR / legacy_slug / "manifest.json")

    # Try each candidate path in order
    for manifest_path in candidate_paths:
        if manifest_path.exists():
            with manifest_path.open(encoding="utf-8") as f:
                manifest = json.load(f)

            # Ensure some sensible defaults are present
            manifest.setdefault("micro_unit_name", MICRO_UNIT_NAME)
            manifest.setdefault("year_level", YEAR_LEVEL)
            return manifest

    # Fallback: no manifest file found anywhere.
    # Return a minimal manifest so the assessment generator can still run.
    return {
        "micro_unit_name": MICRO_UNIT_NAME,
        "year_level": YEAR_LEVEL,
        "unit_slug": unit_slug,
        # Topics can be pulled from elsewhere later if needed; keep it simple for now.
        "topics": [],
    }

# -----------------------------
# Prompt construction
# -----------------------------


def build_assessment_prompt(manifest: Dict[str, Any]) -> str:
    """
    Build a prompt to generate a unit-level summative assessment, rubric, and marking guide.
    """
    unit_name = manifest["micro_unit_name"]
    year_level = manifest["year_level"]
    lessons = manifest.get("lessons", [])

    lesson_lines = []
    for idx, lesson in enumerate(lessons, start=1):
        title = lesson.get("lesson_title") or f"Lesson {idx}"
        eq = lesson.get("essential_question") or ""
        objectives = lesson.get("objectives") or []
        lesson_lines.append(f"{idx}. {title}")
        if eq:
            lesson_lines.append(f"   EQ: {eq}")
        if objectives:
            lesson_lines.append("   Objectives:")
            for obj in objectives:
                lesson_lines.append(f"     - {obj}")
        lesson_lines.append("")

    lesson_block = "\n".join(lesson_lines)

    return (
        "You are an expert curriculum designer for middle school computing / digital technologies.\n\n"
        f"Design a single, coherent SUMMATIVE ASSESSMENT for the following micro-unit.\n\n"
        f"Unit name: {unit_name}\n"
        f"Year level: {year_level}\n"
        f"Lesson sequence:\n{lesson_block}\n\n"
        "Context:\n"
        "- This is a Lower Secondary AI & data literacy unit.\n"
        "- Students have explored data, personal data, structured vs unstructured data,\n"
        "  data quality, bias and fairness, recommendation systems, and fair data collection.\n"
        "- They have been using a reusable analytical framework (like DATA LENS) throughout.\n\n"
        "Design a performance-based assessment task that requires students to:\n"
        "- Apply what they have learned about data, AI systems, and fairness.\n"
        "- Use an analytical framework to evaluate or design an AI-related scenario.\n"
        "- Communicate their thinking clearly (written, visual, or oral).\n\n"
        "IMPORTANT: Respond ONLY with valid JSON matching this schema (no extra text):\n\n"
        "{\n"
        '  "unit_name": string,\n'
        '  "unit_slug": string,\n'
        '  "year_level": string,\n'
        '  "assessment_title": string,\n'
        '  "essential_question": string,\n'
        '  "overview": string,\n'
        '  "task_context": string,\n'
        '  "task_for_students": {\n'
        '    "brief": string,\n'
        '    "steps": [string],\n'
        '    "deliverables": [string]\n'
        "  },\n"
        '  "teacher_instructions": {\n'
        '    "preparation": [string],\n'
        '    "during": [string],\n'
        '    "after": [string]\n'
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
        '  "materials": [string],\n'
        '  "differentiation": {\n'
        '    "support": [string],\n'
        '    "extension": [string]\n'
        "  }\n"
        "}\n\n"
        "Constraints:\n"
        "- Keep language appropriate for Lower Secondary students and their teachers.\n"
        "- The task must be realistic for a 1–2 lesson in-class assessment plus some prep time.\n"
        "- The rubric should be 4-level: Exemplary, Proficient, Developing, Beginning.\n"
        "- Focus on data literacy, AI understanding, fairness, and critical thinking.\n"
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
                "content": "You design curriculum and respond ONLY with strict JSON when asked.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.4,
    )
    raw = resp.choices[0].message.content.strip()

    # Attempt to parse JSON directly.
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON block if the model accidentally wrapped it in text.
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start : end + 1])
        else:
            raise

    # Inject unit_slug / unit_name / year_level if not set
    unit_slug = slugify(manifest["micro_unit_name"])
    data.setdefault("unit_slug", unit_slug)
    data.setdefault("unit_name", manifest["micro_unit_name"])
    data.setdefault("year_level", manifest["year_level"])

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

    Parameters
    ----------
    unit_id : str
        Internal identifier for the unit (e.g. "year7_ai_data_unit1").
    title : str
        Human-readable unit title.
    year_level : str
        e.g. "Lower Secondary".
    subject : str
        e.g. "Digital Technologies".
    output_dir : Path
        Directory where assessment.json, rubric.json, and marking_guide.json will be written.
    extra : dict | None
        Optional context. If extra["manifest"] is provided, it will be used instead of
        load_manifest() to build the prompt.

    Returns
    -------
    Dict[str, Any]
        Simple metadata describing generated files, for inclusion in a build manifest.
    """
    extra = extra or {}

    manifest: Dict[str, Any] = extra.get("manifest") or load_manifest()

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