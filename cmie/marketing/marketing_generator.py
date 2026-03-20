import json
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI


def ensure_openai_client() -> OpenAI:
    return OpenAI()


def _collect_lesson_summaries(lessons_dir: Path) -> List[Dict[str, Any]]:
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
    title = unit_meta["title"]
    year_level = unit_meta["year_level"]
    subject = unit_meta["subject"]

    lesson_lines = []
    for l in lessons:
        num = l.get("lesson_number")
        lt = l.get("lesson_title") or ""
        eq = l.get("essential_question") or ""
        objectives = l.get("objectives") or []

        lesson_lines.append(f"Lesson {num}: {lt}")
        lesson_lines.append(f"Essential question: {eq}")
        if objectives:
            lesson_lines.append("Objectives:")
            for obj in objectives[:3]:
                lesson_lines.append(f"- {obj}")
        lesson_lines.append("")

    lessons_block = "\n".join(lesson_lines)

    return f"""
You are a high-conversion curriculum product marketer.

You write listings that SELL to teachers on TPT, TES, and Gumroad.

Return ONLY valid JSON in this exact structure:

{{
  "unit": {{
    "tpt": {{ "title": "", "description": "", "tags": [], "price": "" }},
    "tes": {{ "title": "", "description": "", "tags": [], "price": "" }},
    "gumroad": {{ "title": "", "description": "", "tags": [], "price": "" }}
  }},
  "lessons": [
    {{
      "lesson_number": 1,
      "lesson_title": "",
      "tpt": {{ "title": "", "description": "", "tags": [], "price": "" }},
      "tes": {{ "title": "", "description": "", "tags": [], "price": "" }},
      "gumroad": {{ "title": "", "description": "", "tags": [], "price": "" }}
    }}
  ]
}}

CORE GOAL:
Every listing must clearly communicate:
- what the teacher gets
- what the students will learn or be able to do
- why this saves time and works in real classrooms

You are not describing lessons.
You are selling a solution to a teacher's problem.

MANDATORY CONTENT RULES:
Every listing must include:
1. A strong hook in the first 2 lines
   - must include “no prep” or “ready to teach”
   - must mention saving time or reducing workload
2. WHAT YOU GET section
   - editable slides (PPTX)
   - structured lesson flow
   - activities
   - teacher notes
   - reflection or workbook tasks
3. STUDENT OUTCOMES
   - what students will understand, identify, explain, analyse, or apply
4. WHY THIS WORKS
   - classroom practicality
   - clarity of content
   - progression across lessons for units
5. PERFECT FOR
   - year level range
   - subject area
   - teacher type
6. CROSS-SELL
   - every lesson must include that it is part of the full unit

TONE RULES:
- write like a teacher selling to another teacher
- be confident and direct
- avoid vague generic curriculum language

PLATFORM RULES:
TPT:
- strongest hook
- clear headings
- bullet points
- keyword-rich title

TES:
- slightly more formal
- still benefit-driven
- less formatting

Gumroad:
- clean markdown
- premium tone
- focus on completeness and value

PRICING:
- full unit should feel like strong value
- individual lessons should make the full unit feel like the better deal

PRODUCT:
Unit: "{title}"
Subject: {subject}
Year level: {year_level}
Total lessons: {len(lessons)}

Lessons:
{lessons_block}

FINAL RULES:
- do not return top-level keys like TPT, TES, Gumroad
- use exactly the keys "unit" and "lessons"
- "unit" must contain exactly "tpt", "tes", "gumroad"
- "lessons" must be a list with one object per lesson
- each lesson object must include lesson_number, lesson_title, tpt, tes, gumroad
- return JSON only
"""


def generate_marketing_assets(
    unit_meta: Dict[str, Any],
    lessons_dir: Path,
) -> Dict[str, Any]:
    client = ensure_openai_client()

    lessons = _collect_lesson_summaries(lessons_dir)
    prompt = _build_marketing_prompt(unit_meta, lessons)

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You write high-conversion curriculum product listings for TPT, TES, and Gumroad "
                    "and respond ONLY with valid JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
    )

    raw = resp.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start:end + 1])
        else:
            raise

    if "unit" not in data or "lessons" not in data:
        raise ValueError(
            f"Marketing output did not match required schema. Top-level keys were: {list(data.keys())}"
        )

    return data