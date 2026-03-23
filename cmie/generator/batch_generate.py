from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from cmie.core.unit_config import UnitConfig

from .ai_lesson_engine import generate_and_save_lesson
from .slide_generator import (
    lesson_json_to_pptx,
    lesson_json_to_public_pptx,
)
from .canva_prompts import lesson_json_to_canva_prompt


def run_batch(unit_cfg: UnitConfig) -> List[Tuple[Path, Path]]:
    """
    Generate all lessons for a unit and return list of
    (lesson_json_path, public_pptx_path).

    Full deck is still generated for internal use.
    Public deck is what gets returned for release packaging.
    Canva prompt files are also generated beside each lesson JSON.
    """

    print(f"Running batch for unit: {unit_cfg.title}")
    print(f"Audience: {unit_cfg.year_level}")
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

        # Full teacher/internal deck
        full_pptx_path: Path = lesson_json_to_pptx(lesson_json_path)

        # Public Canva-friendly deck
        public_pptx_path: Path = lesson_json_to_public_pptx(lesson_json_path)

        # Canva prompt text file
        canva_prompt_path: Path = lesson_json_to_canva_prompt(lesson_json_path)

        print(f"Saved full deck to: {full_pptx_path}")
        print(f"Saved public deck to: {public_pptx_path}")
        print(f"Saved Canva prompt to: {canva_prompt_path}")

        # IMPORTANT: public deck returned for packaging
        results.append((lesson_json_path, public_pptx_path))

    print("\nBatch generation complete.")
    for json_path, public_pptx_path in results:
        print(f"- JSON: {json_path}")
        print(f"  PUBLIC PPTX: {public_pptx_path}")

    return results