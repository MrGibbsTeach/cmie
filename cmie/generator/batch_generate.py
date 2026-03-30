from __future__ import annotations

from pathlib import Path
from typing import List

from cmie.core.unit_config import UnitConfig

from .ai_lesson_engine import generate_and_save_lesson


def run_batch(unit_cfg: UnitConfig) -> List[Path]:
    """
    Generate all lessons for a unit and return a list of lesson JSON paths.

    Legacy PPTX generation and lesson Canva prompt generation have been removed
    from the active workflow. Slides are now produced via unit-level CSV export
    for Canva Sheets.
    """

    print(f"Running batch for unit: {unit_cfg.title}")
    print(f"Audience: {unit_cfg.year_level}")
    print(f"Total topics: {len(unit_cfg.topics)}\n")

    results: List[Path] = []

    for idx, topic in enumerate(unit_cfg.topics, start=1):
        print(f"=== [{idx}/{len(unit_cfg.topics)}] Generating lesson: {topic.title} ===")

        lesson_json_path: Path = generate_and_save_lesson(
            micro_unit_name=unit_cfg.title,
            year_level=unit_cfg.year_level,
            topic_title=topic.title,
            lesson_number=idx,
            video_url=topic.video_url,
        )

        results.append(lesson_json_path)

    print("\nBatch generation complete.")
    for json_path in results:
        print(f"- JSON: {json_path}")

    return results