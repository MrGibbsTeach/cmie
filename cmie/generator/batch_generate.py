from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .ai_lesson_engine import generate_and_save_lesson
from .slide_generator import lesson_json_to_pptx
from cmie.core.unit_config import UnitConfig


def run_batch(unit_cfg: UnitConfig) -> List[Tuple[Path, Path]]:
    """
    Generate all lessons for a unit and return list of
    (lesson_json_path, pptx_path).
    """

    print(f"Running batch for unit: {unit_cfg.title}")
    print(f"Year level: {unit_cfg.year_level}")
    print(f"Total topics: {len(unit_cfg.topics)}\n")

    results: List[Tuple[Path, Path]] = []

    for idx, topic in enumerate(unit_cfg.topics, start=1):
        print(f"=== [{idx}/{len(unit_cfg.topics)}] Generating lesson: {topic.title} ===")

        lesson_json_path: Path = generate_and_save_lesson(
            micro_unit_name=unit_cfg.title,
            year_level=unit_cfg.year_level,
            topic_title=topic.title,
            lesson_number=idx,
            video_url=topic.video_url,
        )

        pptx_path: Path = lesson_json_to_pptx(lesson_json_path)

        results.append((lesson_json_path, pptx_path))

    print("\nBatch generation complete.")
    for json_path, pptx_path in results:
        print(f"- JSON: {json_path}")
        print(f"  PPTX: {pptx_path}")

    return results