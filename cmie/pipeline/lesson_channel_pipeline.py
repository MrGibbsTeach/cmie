from __future__ import annotations

import argparse
from pathlib import Path

from cmie.marketing.lesson_channel_renderer import generate_lesson_channel_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate lesson listings.")
    parser.add_argument(
        "--unit-root",
        required=True,
        help="Path to unit release folder (e.g. releases/year7_ai_data_unit1)",
    )

    args = parser.parse_args()

    unit_root = Path(args.unit_root)
    generate_lesson_channel_files(unit_root)

    print(f"Lesson listings generated in {unit_root / 'lesson_listings'}")


if __name__ == "__main__":
    main()