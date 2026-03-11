import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

# Where all generated lesson JSONs live
BASE_OUTPUT_DIR = Path("generated_lessons")


# --------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------


def slugify(value: str) -> str:
    """
    Convert a string to a filesystem-friendly slug.
    """
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def ensure_openai_client() -> OpenAI:
    """
    Return an OpenAI client. Requires OPENAI_API_KEY in environment.
    """
    return OpenAI()


@dataclass
class LessonConfig:
    micro_unit_name: str
    year_level: str
    topic_title: str
    lesson_number: int
    video_url: Optional[str] = None


# --------------------------------------------------------------------
# Prompt + schema
# --------------------------------------------------------------------


def build_lesson_prompt(cfg: LessonConfig) -> str:
    """
    Build a prompt that returns a structured JSON lesson schema.
    We will post-process into a fixed slide deck structure.
    """
    return (
        "You are an expert middle school Digital Technologies teacher.\n\n"
        f"Design a single lesson for this micro-unit:\n"
        f"- Unit: {cfg.micro_unit_name}\n"
        f"- Year level: {cfg.year_level}\n"
        f"- Lesson number: {cfg.lesson_number}\n"
        f"- Topic: {cfg.topic_title}\n\n"
        "The lesson must support a Year 7 AI & data literacy unit.\n"
        "Students have been working with data, personal data, structured vs "
        "unstructured data, data quality, bias and fairness, recommendation "
        "systems, and fair data collection.\n\n"
        "IMPORTANT: Respond ONLY with valid JSON (no extra text) using this schema:\n"
        "{\n"
        '  "lesson_title": string,\n'
        '  "essential_question": string,\n'
        '  "objectives": [string],\n'
        '  "hook_scenario": string,\n'
        '  "core_sections": [\n'
        "    {\n"
        '      "heading": string,\n'
        '      "content": string\n'
        "    }\n"
        "  ],\n"
        '  "real_world_example": {\n'
        '    "heading": string,\n'
        '    "context": string,\n'
        '    "takeaways": [string]\n'
        "  },\n"
        '  "activity": {\n'
        '    "title": string,\n'
        '    "description": string,\n'
        '    "output_description": string,\n'
        '    "success_criteria": [string]\n'
        "  },\n"
        '  "reflection_questions": [string],\n'
        '  "teacher_notes": {\n'
        '    "misconceptions": [string],\n'
        '    "differentiation": [string],\n'
        '    "extension": [string]\n'
        "  }\n"
        "}\n\n"
        "Constraints:\n"
        "- Objectives must be concise and student-facing.\n"
        "- Hook scenario should be short, concrete, and relatable.\n"
        "- Core sections should be 2–4 focused chunks, not walls of text.\n"
        "- Real world example must be specific to the topic (not generic AI).\n"
        "- Activity must include a clear output and success criteria.\n"
        "- Reflection questions should invite explanation and examples.\n"
        "- Teacher notes must list misconceptions, differentiation, and extension ideas.\n"
    )

def _call_openai_for_lesson(cfg: LessonConfig, model: str = "gpt-4.1-mini") -> Dict[str, Any]:
    client = ensure_openai_client()
    prompt = build_lesson_prompt(cfg)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You write curriculum and respond ONLY with strict JSON when asked.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.4,
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

    return data

# --------------------------------------------------------------------
# Presenter notes enhancement
# --------------------------------------------------------------------


def _build_presenter_notes_prompt(
    cfg: LessonConfig,
    lesson_title: str,
    essential_question: str,
    slides: List[Dict[str, str]],
) -> str:
    """
    Build a single prompt that asks the model to improve presenter notes
    for every slide in the lesson at once.
    """
    slide_lines: List[str] = []

    for idx, slide in enumerate(slides, start=1):
        slide_title = (slide.get("title") or "").strip()
        slide_type = (slide.get("type") or "").strip()
        slide_body = (slide.get("body") or "").strip()

        slide_lines.append(f"Slide {idx}")
        slide_lines.append(f"Title: {slide_title}")
        slide_lines.append(f"Type: {slide_type}")
        slide_lines.append("Visible slide content:")
        slide_lines.append(slide_body if slide_body else "(no visible body text)")
        slide_lines.append("")

    slide_block = "\n".join(slide_lines)

    return (
        "You are an expert Year 7 Digital Technologies teacher, instructional coach, and classroom presenter.\n\n"
        "Your task is to write premium-quality presenter notes for each slide in a lesson.\n\n"
        f"Lesson context:\n"
        f"- Unit: {cfg.micro_unit_name}\n"
        f"- Year level: {cfg.year_level}\n"
        f"- Lesson number: {cfg.lesson_number}\n"
        f"- Topic: {cfg.topic_title}\n"
        f"- Lesson title: {lesson_title}\n"
        f"- Essential question: {essential_question}\n\n"
        "These notes are for the TEACHER, not for students.\n"
        "They should help the teacher know what to say, what to emphasise, what to ask, and what to watch for.\n\n"
        "Write notes that feel like they were created by an experienced teacher who understands:\n"
        "- classroom explanation\n"
        "- questioning\n"
        "- misconceptions\n"
        "- transitions between ideas\n"
        "- student engagement\n"
        "- practical classroom delivery\n\n"
        "IMPORTANT DIFFERENTIATION BY SLIDE TYPE:\n"
        "- section slides: briefly explain the purpose of the phase and how to transition into it\n"
        "- hook slides: set up curiosity, prediction, or discussion\n"
        "- video slides: tell the teacher what students should listen or look for during the video\n"
        "- content slides: explain the concept clearly, include a helpful example or comparison, and identify a likely misconception\n"
        "- real_world slides: help the teacher unpack the example and connect it back to the big concept\n"
        "- activity slides: explain how to launch the task, what success looks like, and what the teacher should circulate for\n"
        "- reflection slides: guide discussion, retrieval, or checking for understanding\n"
        "- teacher_notes slides: summarise the biggest teaching cautions, support moves, or extension opportunities\n\n"
        "Quality rules:\n"
        "- Do not simply repeat the slide text\n"
        "- Add value beyond what is already visible on the slide\n"
        "- Use concrete classroom language the teacher could realistically say\n"
        "- Include one useful question for students where appropriate, but not every slide must have a question\n"
        "- Include likely student confusion where relevant\n"
        "- Use natural Australian classroom-friendly language\n"
        "- Avoid robotic phrasing and generic filler\n"
        "- Each note should feel specific to that slide, not reusable on any slide\n\n"
        "Length rules:\n"
        "- Most slides: 70 to 130 words\n"
        "- Section slides can be shorter: 35 to 70 words\n"
        "- Activity slides can be slightly longer if needed\n\n"
        "Style rules:\n"
        "- Plain text only inside each note\n"
        "- No markdown headings\n"
        "- No bullet lists unless absolutely necessary\n"
        "- No numbering inside the note text\n"
        "- No JSON code fences\n"
        "- No labels like 'Question:' or 'Misconception:' unless they read naturally\n\n"
        "IMPORTANT: respond ONLY with valid JSON using this schema:\n"
        "{\n"
        '  "slide_notes": [\n'
        "    {\n"
        '      "slide_number": 1,\n'
        '      "notes": "Presenter notes text"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Here are the slides:\n\n"
        f"{slide_block}\n"
    )


def _call_openai_for_presenter_notes(
    cfg: LessonConfig,
    lesson_title: str,
    essential_question: str,
    slides: List[Dict[str, str]],
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    client = ensure_openai_client()
    prompt = _build_presenter_notes_prompt(
        cfg=cfg,
        lesson_title=lesson_title,
        essential_question=essential_question,
        slides=slides,
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Year 7 Digital Technologies teacher. "
                    "You write premium presenter notes for commercial classroom resources. "
                    "Your notes must sound like a real teacher preparing to teach the slide, not a generic AI assistant. "
                    "They must be specific, practical, varied by slide type, and immediately usable in class. "
                    "Avoid repetitive phrasing across slides. "
                    "Respond ONLY with strict JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.6,
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

    return data


def enhance_slide_presenter_notes(
    cfg: LessonConfig,
    lesson_title: str,
    essential_question: str,
    slides: List[Dict[str, str]],
    model: str = "gpt-4.1-mini",
) -> List[Dict[str, str]]:
    """
    Replace basic speaker_notes with higher-quality AI generated presenter notes.
    Uses one model call for the whole lesson.
    """
    if not slides:
        return slides

    notes_payload = _call_openai_for_presenter_notes(
        cfg=cfg,
        lesson_title=lesson_title,
        essential_question=essential_question,
        slides=slides,
        model=model,
    )

    slide_notes = notes_payload.get("slide_notes", [])
    notes_by_number: Dict[int, str] = {}

    for item in slide_notes:
        if not isinstance(item, dict):
            continue
        slide_number = item.get("slide_number")
        notes = item.get("notes")
        if isinstance(slide_number, int) and isinstance(notes, str) and notes.strip():
            notes_by_number[slide_number] = notes.strip()

    enhanced_slides: List[Dict[str, str]] = []

    for idx, slide in enumerate(slides, start=1):
        new_slide = dict(slide)
        if idx in notes_by_number:
            new_slide["speaker_notes"] = notes_by_number[idx]
        enhanced_slides.append(new_slide)

    return enhanced_slides

def _prepend_if_missing(text: str, prefix: str) -> str:
    text = (text or "").strip()
    prefix = prefix.strip()

    if not text:
        return prefix

    text_lower = text.lower()
    prefix_lower = prefix.lower()

    if text_lower.startswith(prefix_lower):
        return text

    return f"{prefix} {text}"


def _polish_presenter_note(slide_type: str, title: str, note: str) -> str:
    """
    Apply a lightweight local polish layer so notes feel more intentional
    and more varied by slide type, without making another AI call.
    """
    slide_type = (slide_type or "").strip().lower()
    title = (title or "").strip()
    note = (note or "").strip()

    if not note:
        return note

    if slide_type == "section":
        return _prepend_if_missing(
            note,
            "Use this slide to briefly frame the next phase of the lesson and signal the shift in focus."
        )

    if slide_type == "hook":
        return _prepend_if_missing(
            note,
            "Open with curiosity here and get students predicting before you explain anything."
        )

    if slide_type == "video":
        return _prepend_if_missing(
            note,
            "Before playing the video, tell students exactly what key idea or pattern they should listen for."
        )

    if slide_type == "content":
        return _prepend_if_missing(
            note,
            "Keep the explanation tight here, then check understanding with a quick example or comparison."
        )

    if slide_type == "real_world":
        return _prepend_if_missing(
            note,
            "Use this example to connect the concept to a real system students might already know."
        )

    if slide_type == "activity":
        return _prepend_if_missing(
            note,
            "Launch the task clearly, then circulate to check reasoning rather than just completion."
        )

    if slide_type == "reflection":
        return _prepend_if_missing(
            note,
            "Use this moment to check what students actually understand, not just what they remember."
        )

    if slide_type == "teacher_notes":
        return _prepend_if_missing(
            note,
            "Treat this slide as a quick teaching reminder before or during delivery."
        )

    return note


def polish_slide_presenter_notes(
    slides: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """
    Local post-processing pass to improve presenter notes without extra API cost.
    """
    polished: List[Dict[str, str]] = []

    for slide in slides:
        new_slide = dict(slide)
        slide_type = new_slide.get("type", "")
        title = new_slide.get("title", "")
        speaker_notes = new_slide.get("speaker_notes", "")

        new_slide["speaker_notes"] = _polish_presenter_note(
            slide_type=slide_type,
            title=title,
            note=speaker_notes,
        )
        polished.append(new_slide)

    return polished

# --------------------------------------------------------------------
# Slide building
# --------------------------------------------------------------------
def _build_visual_comparison_slide(cfg: LessonConfig) -> Optional[Dict[str, Any]]:
    """
    Create a comparison slide for common contrast-based lesson topics.
    """
    topic = f"{cfg.topic_title} {cfg.micro_unit_name}".lower()

    if "structured" in topic and "unstructured" in topic:
        return {
            "type": "visual_comparison",
            "title": "Structured vs Unstructured Data",
            "left_title": "Structured Data",
            "left_points": [
                "Organised into rows, columns, or clear fields",
                "Easy to sort, search, and analyse",
                "Usually stored in tables or spreadsheets",
            ],
            "left_example": "Student marks in a spreadsheet",
            "right_title": "Unstructured Data",
            "right_points": [
                "No fixed format or table structure",
                "Includes text, images, audio, and video",
                "Usually needs more advanced AI methods to analyse",
            ],
            "right_example": "Photos, chat messages, or videos",
            "speaker_notes": (
                "Use this slide to make the difference visible straight away. "
                "Point out that structured data is organised in a predictable way, "
                "while unstructured data is not. A simple comparison you can use is "
                "'spreadsheet versus Instagram post'. Ask students which one would be "
                "easier for a computer to sort quickly and why. Clarify that unstructured "
                "does not mean bad or useless. It just means the data is harder to organise "
                "and interpret."
            ),
        }

    if "personal data" in topic:
        return {
            "type": "visual_comparison",
            "title": "Personal Data vs Non-Personal Data",
            "left_title": "Personal Data",
            "left_points": [
                "Can identify a person directly or indirectly",
                "Includes obvious and less obvious details",
                "Needs to be handled carefully and protected",
            ],
            "left_example": "full name, birthday, device ID, photo",
            "right_title": "Non-Personal Data",
            "right_points": [
                "Does not identify a specific person",
                "Often used in grouped or general ways",
                "Still needs context to judge risk properly",
            ],
            "right_example": "Photos, chat messages, or videos",
            "speaker_notes": (
                "Use this slide to help students compare identifiable and non-identifiable information. "
                "Remind them that some data feels harmless at first but can still identify someone when "
                "combined with other details. Ask students whether a username, location, or photo could "
                "count as personal data and why. Emphasise that context matters. The key idea is that "
                "personal data is not just names and addresses."
            ),
        }

    if "bias" in topic and "fair" in topic:
        return {
            "type": "visual_comparison",
            "title": "Biased Data vs Fair Data",
            "left_title": "Biased Data",
            "left_points": [
                "Over-represents some groups and misses others",
                "Can lead to unfair or inaccurate AI decisions",
                "Usually reflects gaps or imbalance in collection",
            ],
            "left_example": "Example: training data with mostly one type of user",
            "right_title": "Fair Data",
            "right_points": [
                "Represents people or cases more evenly",
                "Supports more accurate and fair AI decisions",
                "Collected carefully to reduce imbalance",
            ],
            "right_example": "Training data that includes diverse users",
            "speaker_notes": (
                "Use this comparison to show that fairness starts with the data, not just the algorithm. "
                "Ask students what could happen if an AI system mostly learns from one group of people. "
                "Highlight that biased data does not always happen on purpose. It can come from poor sampling "
                "or missing voices. The key message is that fairer data gives AI a better chance of making "
                "fairer decisions."
            ),
        }

    if "data quality" in topic or "missing values" in topic or "noise" in topic:
        return {
            "type": "visual_comparison",
            "title": "High-Quality Data vs Poor-Quality Data",
            "left_title": "High-Quality Data",
            "left_points": [
                "Accurate, complete, and relevant",
                "Supports better decisions and analysis",
                "Has fewer errors, gaps, or misleading values",
            ],
            "left_example": "A complete and correct class survey",
            "right_title": "Poor-Quality Data",
            "right_points": [
                "Contains errors, missing values, or noise",
                "Can mislead people and AI systems",
                "Makes results less reliable",
            ],
            "right_example": "A survey with blank answers and typos",
            "speaker_notes": (
                "Use this slide to show that not all data is equally useful. "
                "Ask students which side would lead to better decisions and why. "
                "Make the point that more data is not always better if the quality is poor. "
                "Students often assume computers will fix bad data automatically, so clarify "
                "that poor-quality data usually produces poor-quality results."
            ),
        }

    return None

def build_slide_deck(
    cfg: LessonConfig,
    schema: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Build a commercially structured slide deck.
    """

    hook_text = (schema.get("hook_scenario") or "").strip()
    core_sections = schema.get("core_sections") or []
    activity = schema.get("activity") or {}
    reflection_questions = schema.get("reflection_questions") or []
    teacher_notes = schema.get("teacher_notes") or {}

    slides: List[Dict[str, str]] = []

    # -----------------------------
    # EXPLORE PHASE
    # -----------------------------
    slides.append(
        {
            "type": "section",
            "title": "🔎 Explore",
            "body": "Let's investigate the problem.",
            "speaker_notes": (
                "Introduce the lesson focus briefly. Explain what students will explore "
                "and connect it to the essential question."
            ),
        }
    )

    slides.append(
        {
            "type": "hook",
            "title": "Hook Scenario",
            "body": hook_text,
            "speaker_notes": (
                "Read the scenario aloud. Ask students what data, patterns, or decisions "
                "might be involved before moving to the explanation."
            ),
        }
    )

    if cfg.video_url:
        video_body = (
            f"Video link: {cfg.video_url}\n\n"
            "- What is one key idea from this video?\n"
            "- How does it connect to today's topic?"
        )
    else:
        video_body = (
            "Teacher: show a short, relevant video introducing today's topic.\n\n"
            "- What is one key idea?\n"
            "- How does it connect to today's topic?"
        )

    slides.append(
        {
            "type": "video",
            "title": "Watch & Think",
            "body": video_body,
            "speaker_notes": (
                "Play the video. Ask students to identify one key idea and how it connects "
                "to today's topic before continuing."
            ),
        }
    )

    # -----------------------------
    # LEARN PHASE
    # -----------------------------
    slides.append(
        {
            "type": "section",
            "title": "🧠 Learn",
            "body": "Key ideas and concepts.",
            "speaker_notes": (
                "Transition into the explanation phase. Introduce the key concepts "
                "students need to understand before applying them."
            ),
        }
    )

    for section in core_sections:
        heading = section.get("heading", "").strip()
        content = section.get("content", "").strip()

        if not heading and not content:
            continue

        if heading:
            heading = heading[0].upper() + heading[1:]
            heading = re.sub(r"\bai\b", "AI", heading, flags=re.IGNORECASE)

        lines = [l.strip() for l in content.split("\n") if l.strip()]
        trimmed = "\n".join(lines[:3])

        slides.append(
            {
                "type": "content",
                "title": heading or "Key idea",
                "body": trimmed,
                "speaker_notes": (
                    f"Explain the concept: {heading or 'Key idea'}. "
                    "Give a simple real-world example and check for understanding before moving on."
                ),
            }
        )
    # -----------------------------
    # VISUAL COMPARISON SLIDE
    # -----------------------------
    comparison_slide = _build_visual_comparison_slide(cfg)
    if comparison_slide:
        slides.append(comparison_slide)

    # -----------------------------
    # REAL WORLD EXAMPLE
    # -----------------------------
    rwe = schema.get("real_world_example") or {}
    rwe_heading = rwe.get("heading", "").strip() or "Real World Example"
    rwe_context = (rwe.get("context") or "").strip()
    rwe_takeaways = [t.strip() for t in rwe.get("takeaways", []) if t.strip()]

    rwe_body_lines: List[str] = []
    if rwe_context:
        rwe_body_lines.append(rwe_context)
        rwe_body_lines.append("")

    for t in rwe_takeaways:
        rwe_body_lines.append(f"- {t}")

    rwe_body = "\n".join(rwe_body_lines).strip() or (
        "Example from the real world.\n\n"
        "- What data is being used?\n"
        "- Why does quality or bias matter here?"
    )

    slides.append(
        {
            "type": "real_world",
            "title": f"🌍 {rwe_heading}",
            "body": rwe_body,
            "speaker_notes": (
                "Discuss this real-world example and ask students what data is being used "
                "and why quality or bias matters in this case."
            ),
        }
    )

    # -----------------------------
    # APPLY PHASE
    # -----------------------------
    slides.append(
        {
            "type": "section",
            "title": "🛠 Apply",
            "body": "Put your learning into action.",
            "speaker_notes": (
                "Explain the task students will complete. Clarify expectations and "
                "the type of output they should produce."
            ),
        }
    )

    activity_title = activity.get("title", "Your Task")
    activity_desc = activity.get("description", "").strip()
    output_desc = (activity.get("output_description") or "").strip()
    success_criteria = [
        s.strip() for s in activity.get("success_criteria", [])
        if isinstance(s, str) and s.strip()
    ]

    activity_body_parts: List[str] = []
    if activity_desc:
        activity_body_parts.append(activity_desc)
        activity_body_parts.append("")

    if output_desc:
        activity_body_parts.append("Output:")
        activity_body_parts.append(f"- {output_desc}")
        activity_body_parts.append("")

    if success_criteria:
        activity_body_parts.append("You must:")
        for sc in success_criteria:
            activity_body_parts.append(f"- {sc}")

    activity_body = "\n".join(activity_body_parts).strip()

    slides.append(
        {
            "type": "activity",
            "title": f"{activity_title} (15 minutes)",
            "body": activity_body,
            "speaker_notes": (
                "Review the task instructions and success criteria. Circulate while "
                "students work and prompt them to explain their reasoning."
            ),
        }
    )

    # -----------------------------
    # REFLECT PHASE
    # -----------------------------
    slides.append(
        {
            "type": "section",
            "title": "💬 Reflect",
            "body": "Review and consolidate your understanding.",
            "speaker_notes": (
                "Lead a short discussion to help students consolidate their understanding "
                "of the key ideas from the lesson."
            ),
        }
    )

    if reflection_questions:
        reflection_body = "\n".join(f"- {q}" for q in reflection_questions[:3])
    else:
        reflection_body = (
            "- What is one idea you learned today?\n"
            "- Why does this matter in real life?\n"
            "- What questions do you still have?"
        )

    slides.append(
        {
            "type": "reflection",
            "title": "Reflection Questions",
            "body": reflection_body,
            "speaker_notes": (
                "Invite students to answer one or two questions verbally or in writing. "
                "Encourage them to explain their reasoning."
            ),
        }
    )

    # -----------------------------
    # TEACHER NOTES
    # -----------------------------
    misconceptions = [
        m.strip() for m in teacher_notes.get("misconceptions", [])
        if isinstance(m, str) and m.strip()
    ]
    differentiation = [
        d.strip() for d in teacher_notes.get("differentiation", [])
        if isinstance(d, str) and d.strip()
    ]
    extension = [
        e.strip() for e in teacher_notes.get("extension", [])
        if isinstance(e, str) and e.strip()
    ]

    tn_lines: List[str] = []
    if misconceptions:
        tn_lines.append("Key misconceptions to watch for:")
        for m in misconceptions:
            tn_lines.append(f"- {m}")
        tn_lines.append("")

    if differentiation:
        tn_lines.append("Differentiation ideas:")
        for d in differentiation:
            tn_lines.append(f"- {d}")
        tn_lines.append("")

    if extension:
        tn_lines.append("Extension ideas:")
        for e in extension:
            tn_lines.append(f"- {e}")

    tn_body = "\n".join(tn_lines).strip() or (
        "Key misconceptions to watch for:\n"
        "- Students confusing examples with definitions\n\n"
        "Differentiation idea:\n"
        "- Provide sentence starters or worked examples\n\n"
        "Extension idea:\n"
        "- Ask students to find a real-world case study"
    )

    slides.append(
        {
            "type": "teacher_notes",
            "title": "Teacher Notes",
            "body": tn_body,
            "speaker_notes": (
                "These notes highlight common misconceptions, differentiation options, "
                "and possible extension activities."
            ),
        }
    )

    return slides


# --------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------


def generate_lesson_schema(
    micro_unit_name: str,
    year_level: str,
    topic_title: str,
    lesson_number: int,
    video_url: Optional[str] = None,
    model: str = "gpt-4.1-mini",
) -> Dict[str, Any]:
    """
    Generate a full lesson JSON, including slides, from OpenAI.
    """
    cfg = LessonConfig(
        micro_unit_name=micro_unit_name,
        year_level=year_level,
        topic_title=topic_title,
        lesson_number=lesson_number,
        video_url=video_url,
    )

    raw_schema = _call_openai_for_lesson(cfg, model=model)

    lesson: Dict[str, Any] = {}
    lesson["unit_name"] = micro_unit_name
    lesson["year_level"] = year_level
    lesson["lesson_number"] = lesson_number
    lesson["lesson_title"] = raw_schema.get("lesson_title") or topic_title
    lesson["topic_title"] = topic_title
    lesson["essential_question"] = raw_schema.get("essential_question", "")

    # Objectives: keep max 3, cleaned
    raw_objectives = raw_schema.get("objectives", []) or []
    cleaned_objectives: List[str] = []
    for obj in raw_objectives[:3]:
        if not isinstance(obj, str):
            continue
        text = obj.strip()
        if not text:
            continue
        cleaned_objectives.append(text)
    lesson["objectives"] = cleaned_objectives

    # Video + real-world example from schema
    lesson["video_url"] = video_url
    lesson["real_world_example"] = raw_schema.get("real_world_example", {}) or {}

    # Build slides first with simple draft notes
    draft_slides = build_slide_deck(cfg, raw_schema)

    # Upgrade all presenter notes in one AI call
    enhanced_slides = enhance_slide_presenter_notes(
        cfg=cfg,
        lesson_title=lesson["lesson_title"],
        essential_question=lesson["essential_question"],
        slides=draft_slides,
        model=model,
    )

    polished_slides = polish_slide_presenter_notes(enhanced_slides)

    lesson["slides"] = polished_slides

    return lesson


def save_lesson(lesson: Dict[str, Any]) -> Path:
    """
    Save the lesson JSON under BASE_OUTPUT_DIR/<unit_slug>/<lesson_slug>/lesson.json
    """
    unit_slug = slugify(lesson["unit_name"])
    lesson_slug = slugify(lesson["topic_title"])

    out_dir = BASE_OUTPUT_DIR / unit_slug / lesson_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "lesson.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)

    return out_path


def generate_and_save_lesson(
    micro_unit_name: str,
    year_level: str,
    topic_title: str,
    lesson_number: int,
    video_url: Optional[str] = None,
    model: str = "gpt-4.1-mini",
) -> Path:
    """
    High-level entry point used by batch_generate.run_batch.
    """
    lesson = generate_lesson_schema(
        micro_unit_name=micro_unit_name,
        year_level=year_level,
        topic_title=topic_title,
        lesson_number=lesson_number,
        video_url=video_url,
        model=model,
    )
    path = save_lesson(lesson)
    print(f"Generated lesson for topic '{topic_title}' at: {path}")
    return path


if __name__ == "__main__":
    # NOTE: MICRO_UNIT_NAME and YEAR_LEVEL would need to be defined here
    # if you actually want to run this file directly. The pipeline doesn't
    # call this block, so it's safe to ignore or adjust as needed.
    pass