from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List


SERIES_BASE: Dict[str, Any] = {
    "year_level": "Lower Secondary",
    "subject": "Digital Technologies",
    "version": "v001",
    "series_title": "AI & Data Literacy Series",
}

UNIT_DEFINITIONS: Dict[int, Dict[str, Any]] = {
    1: {
        "subtitle": "Data Foundations",
        "topics": [
            "Data Shapes the AI World",
            "What Counts as Personal Data?",
            "Structured vs Unstructured Data (Text, Images, Clicks)",
            "Data Quality: Noise, Errors, and Missing Values",
            "Bias in Training Data and AI Fairness",
            "How Recommendation Systems Use Your Data",
            "Designing Fair Data Collection in the Classroom",
        ],
    },
    2: {
        "subtitle": "Data + AI Models",
        "topics": [
            "What Is an AI Model?",
            "How AI Learns from Data",
            "Training Data vs Testing Data",
            "Finding Patterns and Making Predictions",
            "Classification Models: Sorting Data into Groups",
            "How AI Models Power Recommendations",
            "Designing a Simple AI Model",
        ],
    },
    3: {
        "subtitle": "AI Ethics + Bias",
        "topics": [
            "What Is AI Bias?",
            "Where Bias Comes From in Data",
            "Real-World Examples of Biased AI",
            "Fair vs Unfair AI Decisions",
            "Who Is Responsible for AI Decisions?",
            "Designing Fair AI Systems",
            "Evaluating AI for Bias",
        ],
    },
    4: {
        "subtitle": "AI Systems + Applications",
        "topics": [
            "What Is an AI System?",
            "AI in Everyday Life",
            "How AI Systems Make Decisions",
            "Inputs, Processes, and Outputs",
            "Limits of AI Systems",
            "Humans Working with AI",
            "Designing an AI System for a Real Need",
        ],
    },
    5: {
        "subtitle": "AI in Education",
        "topics": [
            "What Is AI in Education?",
            "AI Tools for Learning",
            "Benefits of AI for Students",
            "Risks and Limitations in Schools",
            "AI and Academic Integrity",
            "Teacher vs AI Roles",
            "Designing an AI Learning Tool",
        ],
    },
    6: {
        "subtitle": "AI in Business",
        "topics": [
            "AI in Modern Business",
            "Automation and Efficiency",
            "AI in Customer Experience",
            "Data-Driven Decisions",
            "Risks of AI in Business",
            "Jobs and the Future of Work",
            "Designing an AI Business Solution",
        ],
    },
    7: {
        "subtitle": "AI in Healthcare",
        "topics": [
            "AI in Healthcare Overview",
            "Diagnosing with AI",
            "AI in Treatment Planning",
            "Benefits for Patients",
            "Risks and Ethics in Healthcare AI",
            "Human vs AI Decisions",
            "Designing an AI Health Tool",
        ],
    },
    8: {
        "subtitle": "AI in Society",
        "topics": [
            "AI in Everyday Society",
            "AI and Privacy",
            "AI and Surveillance",
            "Bias and Inequality in Society",
            "Regulation of AI",
            "Public Perception of AI",
            "Designing Responsible AI Systems",
        ],
    },
}


def build_unit_config(series_prefix: str, unit_number: int) -> Dict[str, Any]:
    if unit_number not in UNIT_DEFINITIONS:
        raise ValueError(f"No definition found for unit {unit_number}")

    unit_info = UNIT_DEFINITIONS[unit_number]
    unit_id = f"{series_prefix}_unit{unit_number}"
    title = f"{SERIES_BASE['series_title']} – Unit {unit_number}: {unit_info['subtitle']}"

    return {
        "unit_id": unit_id,
        "title": title,
        "year_level": SERIES_BASE["year_level"],
        "subject": SERIES_BASE["subject"],
        "version": SERIES_BASE["version"],
        "topics": [{"title": t} for t in unit_info["topics"]],
        "lesson_videos": {},
    }


def save_unit_config(config: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{config['unit_id']}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a unit config JSON.")
    parser.add_argument("--series-prefix", default="year7_ai_data")
    parser.add_argument("--unit-number", type=int, required=True)
    parser.add_argument("--output-dir", default="data/units")
    args = parser.parse_args()

    config = build_unit_config(args.series_prefix, args.unit_number)
    output_path = save_unit_config(config, Path(args.output_dir))
    print(f"Generated unit config: {output_path}")


if __name__ == "__main__":
    main()