import csv
import json
from pathlib import Path
from typing import Dict, List


CSV_HEADERS = [
    "title_title",
    "title_subtitle",

    "intention_title",
    "intention_subtitle",
    "intention_point1",
    "intention_point2",
    "intention_point3",

    "hook_title",
    "hook_subtitle",
    "hook_point1",
    "hook_point2",
    "hook_point3",

    "prior_title",
    "prior_subtitle",
    "prior_point1",
    "prior_point2",
    "prior_point3",

    "concept1_title",
    "concept1_subtitle",
    "concept1_point1",
    "concept1_point2",
    "concept1_point3",

    "concept2_title",
    "concept2_subtitle",
    "concept2_point1",
    "concept2_point2",
    "concept2_point3",

    "concept3_title",
    "concept3_subtitle",
    "concept3_point1",
    "concept3_point2",
    "concept3_point3",

    "example1_title",
    "example1_subtitle",
    "example1_point1",
    "example1_point2",
    "example1_point3",

    "example2_title",
    "example2_subtitle",
    "example2_point1",
    "example2_point2",
    "example2_point3",

    "check_title",
    "check_subtitle",
    "check_point1",
    "check_point2",
    "check_point3",

    "activity_title",
    "activity_subtitle",
    "activity_point1",
    "activity_point2",
    "activity_point3",

    "extended_title",
    "extended_subtitle",
    "extended_point1",
    "extended_point2",
    "extended_point3",

    "reflection_title",
    "reflection_subtitle",
    "reflection_point1",
    "reflection_point2",
    "reflection_point3",

    "exit_title",
    "exit_subtitle",
    "exit_point1",
    "exit_point2",
    "exit_point3",

    "summary_title",
    "summary_subtitle",
    "summary_point1",
    "summary_point2",
    "summary_point3",
]


def _cap_title(text: str, max_len: int = 23) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text[:max_len].rstrip()


def _shorten(text: str, max_len: int = 120) -> str:
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text[:max_len].rstrip()


def _make_subtitle(text: str, max_len: int = 55) -> str:
    if not text:
        return ""

    text = " ".join(str(text).split())
    first = text.split(". ")[0]

    # FORCE SIMPLIFICATION
    replacements = [
        ("An AI model is a program that", "AI models"),
        ("AI models get better by", "AI improves by"),
        ("For example,", ""),
        ("This means that", ""),
    ]

    for old, new in replacements:
        first = first.replace(old, new)

    first = first.strip()

    if len(first) > max_len:
        first = first[:max_len].rstrip()

    return first


def _split_points(text: str, max_points: int = 3, max_len: int = 70) -> List[str]:
    if not text:
        return [""] * max_points

    parts = []
    for chunk in str(text).replace("\n", " ").split(". "):
        chunk = chunk.strip(" -•\n\t")
        chunk = " ".join(chunk.split())

        if not chunk:
            continue

        if len(chunk) > max_len:
            chunk = chunk[:max_len].rstrip()

        parts.append(chunk)

        if len(parts) >= max_points:
            break

    while len(parts) < max_points:
        parts.append("")

    return parts[:max_points]


def _list_points(items, max_points: int = 3) -> List[str]:
    if not items:
        return [""] * max_points
    points = [_shorten(x, 100) for x in items[:max_points]]
    while len(points) < max_points:
        points.append("")
    return points


def lesson_json_to_canva_row(lesson: Dict) -> Dict[str, str]:
    row = {h: "" for h in CSV_HEADERS}

    lesson_title = lesson.get("lesson_title", "")
    lesson_number = lesson.get("lesson_number", "")
    objectives = lesson.get("objectives", []) or lesson.get("success_criteria", [])
    reflection_questions = lesson.get("reflection_questions", []) or []

    slides = lesson.get("slides", [])
    content_slides = [s for s in slides if s.get("type") == "content"]
    real_world_slides = [s for s in slides if s.get("type") == "real_world"]
    activity_slides = [s for s in slides if s.get("type") == "activity"]
    hook_slide = next((s for s in slides if s.get("type") == "hook"), {})

    # Title
    row["title_title"] = _cap_title(f"Lesson {lesson_number}")
    row["title_subtitle"] = _shorten(lesson_title, 80)

    # Learning goal
    row["intention_title"] = _cap_title("Learning Goal")
    row["intention_subtitle"] = "What you will learn"
    intent_points = _list_points(objectives, 3)
    row["intention_point1"], row["intention_point2"], row["intention_point3"] = intent_points

    # Hook
    row["hook_title"] = _cap_title("Hook")
    row["hook_subtitle"] = _shorten(hook_slide.get("body", ""), 80)
    row["hook_point1"] = "Think about the scenario"
    row["hook_point2"] = "Discuss what you notice"
    row["hook_point3"] = "Be ready to share"

    # Prior knowledge
    row["prior_title"] = _cap_title("Quick Starter")
    row["prior_subtitle"] = "Think and discuss"
    row["prior_point1"] = "List 3 examples of data"
    row["prior_point2"] = "Where is AI used?"
    row["prior_point3"] = "Share one idea"

    # Concepts 1-3
    for idx in range(3):
        key = f"concept{idx+1}"
        if idx < len(content_slides):
            slide = content_slides[idx]
            body = slide.get("body", "")
            body = body.replace(" - ", ". ")

            row[f"{key}_title"] = _cap_title(slide.get("title", f"Concept {idx+1}"))
            row[f"{key}_subtitle"] = _make_subtitle(body, 60)

            p1, p2, p3 = _split_points(body, max_points=3, max_len=50)
            row[f"{key}_point1"] = p1
            row[f"{key}_point2"] = p2
            row[f"{key}_point3"] = p3
        else:
            row[f"{key}_title"] = ""
            row[f"{key}_subtitle"] = ""
            row[f"{key}_point1"] = ""
            row[f"{key}_point2"] = ""
            row[f"{key}_point3"] = ""

    # Examples 1-2
    for idx in range(2):
        key = f"example{idx+1}"

        if idx < len(real_world_slides):
            slide = real_world_slides[idx]
            body = slide.get("body", "")
            body = body.replace(" - ", ". ")

            row[f"{key}_title"] = _cap_title("Real Example" if idx == 0 else "More Examples")
            row[f"{key}_subtitle"] = _make_subtitle(body, 60)

            p1, p2, p3 = _split_points(body, max_points=3, max_len=70)

            if not p3:
                p3 = "How does this use AI data?"

            row[f"{key}_point1"] = p1
            row[f"{key}_point2"] = p2
            row[f"{key}_point3"] = p3

        else:
            row[f"{key}_title"] = ""
            row[f"{key}_subtitle"] = ""
            row[f"{key}_point1"] = ""
            row[f"{key}_point2"] = ""
            row[f"{key}_point3"] = ""


    # Check
    row["check_title"] = _cap_title("Check Learning")
    row["check_subtitle"] = "Show what you know"
    row["check_point1"] = "What is the key idea?"
    row["check_point2"] = "What example explains it?"
    row["check_point3"] = "What could go wrong?"

    # Main task
    row["activity_title"] = _cap_title("Main Task")
    row["activity_subtitle"] = "Complete the task"
    if activity_slides:
        p1, p2, p3 = _split_points(activity_slides[0].get("body", ""))
        row["activity_point1"] = p1
        row["activity_point2"] = p2
        row["activity_point3"] = p3
    else:
        row["activity_point1"] = "Choose a simple problem"
        row["activity_point2"] = "List data + model output"
        row["activity_point3"] = "Create a short explanation"

    # Challenge task
    row["extended_title"] = _cap_title("Challenge Task")
    row["extended_subtitle"] = "Test the model"
    row["extended_point1"] = "Change one part of the data"
    row["extended_point2"] = "Predict how results change"
    row["extended_point3"] = "Explain why this happens"

    # Reflection
    row["reflection_title"] = _cap_title("Reflection")
    row["reflection_subtitle"] = "Think about learning"
    if reflection_questions:
        row["reflection_point1"] = _shorten(reflection_questions[0], 70) if len(reflection_questions) > 0 else ""
        row["reflection_point2"] = _shorten(reflection_questions[1], 70) if len(reflection_questions) > 1 else ""
        row["reflection_point3"] = _shorten(reflection_questions[2], 70) if len(reflection_questions) > 2 else ""
    else:
        row["reflection_point1"] = "What did you learn today?"
        row["reflection_point2"] = "What was most challenging?"
        row["reflection_point3"] = "What still confuses you?"

    # Exit ticket
    row["exit_title"] = _cap_title("Exit Ticket")
    row["exit_subtitle"] = "Show your learning"
    row["exit_point1"] = "Write one thing you now understand"
    row["exit_point2"] = "Write one example from today"
    row["exit_point3"] = "Write one question you still have"

    # Summary
    row["summary_title"] = _cap_title("Summary")
    row["summary_subtitle"] = "Key takeaways"
    row["summary_point1"] = intent_points[0]
    row["summary_point2"] = intent_points[1]
    row["summary_point3"] = intent_points[2]

    return row


def export_unit_canva_csv(unit_title: str, lesson_json_paths: List[Path], output_csv: Path) -> Path:
    rows = []
    for path in lesson_json_paths:
        with path.open("r", encoding="utf-8") as f:
            lesson = json.load(f)
        rows.append(lesson_json_to_canva_row(lesson))

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    return output_csv