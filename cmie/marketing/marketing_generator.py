import json
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI


def ensure_openai_client() -> OpenAI:
    return OpenAI()


def _collect_lesson_summaries(lessons_dir: Path) -> List[Dict[str, Any]]:
    """
    Read each lesson JSON in lessons_dir and pull out high-level info
    for the marketing prompt.
    """
    summaries: List[Dict[str, Any]] = []

    for path in sorted(lessons_dir.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        summaries.append(
            {
                "filename": path.name,
                "lesson_number": data.get("lesson_number"),
                "lesson_title": data.get("lesson_title") or data.get("topic_title"),
                "essential_question": data.get("essential_question", ""),
                "objectives": data.get("objectives", []),
            }
        )

    return summaries


def _build_marketing_prompt(unit_meta: Dict[str, Any], lessons: List[Dict[str, Any]]) -> str:
    """
    Build the prompt for generating marketplace-ready marketing copy.
    """
    title = unit_meta["title"]
    year_level = unit_meta["year_level"]
    subject = unit_meta["subject"]

    lesson_lines = []
    for l in lessons:
        num = l.get("lesson_number")
        lt = l.get("lesson_title") or ""
        eq = l.get("essential_question") or ""
        lesson_lines.append(f"- Lesson {num}: {lt} — EQ: {eq}")

    lessons_block = "\n".join(lesson_lines)

    return (
        "You are an expert in writing curriculum product listings for teacher marketplaces "
        "(e.g. TPT, TES, Etsy for teachers).\n\n"
        "Write marketing copy for a DIGITAL DOWNLOAD unit using ONLY this JSON schema:\n"
        "{\n"
        '  "seo_title": string,\n'
        '  "subtitle": string,\n'
        '  "short_description": string,\n'
        '  "long_description": string,\n'
        '  "tags": [string],\n'
        '  "whats_included": [string],\n'
        '  "learning_outcomes": [string],\n'
        '  "ideal_for": [string],\n'
        '  "why_this_unit": [string],\n'
        '  "bundle_cross_sell": string,\n'
        '  "price_recommendation": string\n'
        "}\n\n"
        "Rules:\n"
        "- Audience: busy Digital Technologies teachers in Australian and international schools.\n"
        "- Focus on AI and data literacy, aligned to lower secondary.\n"
        "- Short description: max 150 words, marketplace friendly.\n"
        "- Long description: 600–900 words, scannable with headings and bullet points.\n"
        "- Tags: 12–18 phrases, no leading '#', all lower case.\n"
        "- Whats_included: concrete file types (PowerPoint slides, student workbook, assessment, etc.).\n"
        "- Learning_outcomes: student-facing outcomes, not generic fluff.\n"
        "- Ideal_for: mention year levels, subjects, and teaching contexts.\n"
        "- Why_this_unit: specific reasons this product stands out from generic AI lessons.\n"
        "- Bundle_cross_sell: one paragraph suggesting how this unit fits into a larger AI course bundle.\n"
        "- Price_recommendation: give a single price in AUD for a standard commercial marketplace.\n\n"
        "Product to describe:\n"
        f'- Unit title: "{title}"\n'
        f"- Subject: {subject}\n"
        f"- Year level: {year_level}\n\n"
        "Lessons in this unit:\n"
        f"{lessons_block}\n"
    )


def generate_marketing_assets(
    unit_meta: Dict[str, Any],
    lessons_dir: Path,
) -> Dict[str, Any]:
    """
    Main public API: returns a dict with marketing copy ready for saving as JSON.
    """
    client = ensure_openai_client()

    lessons = _collect_lesson_summaries(lessons_dir)
    prompt = _build_marketing_prompt(unit_meta, lessons)

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You write curriculum product listings and respond ONLY with valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )

    raw = resp.choices[0].message.content.strip()

    # Defensive JSON parse
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start : end + 1])
        else:
            raise

    return data