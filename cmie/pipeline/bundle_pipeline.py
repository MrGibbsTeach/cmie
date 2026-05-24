from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from cmie.bundles.bundle_generator import generate_bundle_marketing


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate marketing for a bundle of units.")
    parser.add_argument(
        "--bundle-name",
        required=True,
        help="Name of the bundle (e.g. AI Data Foundations Bundle)",
    )
    parser.add_argument(
        "--unit-roots",
        required=True,
        nargs="+",
        help="Paths to unit release folders (e.g. releases/year7_ai_data_unit1)",
    )
    parser.add_argument(
        "--output-root",
        default="releases/bundles",
        help="Where bundle output should go",
    )

    args = parser.parse_args()

    unit_paths: List[Path] = [Path(p) for p in args.unit_roots]
    output_root = Path(args.output_root)

    result = generate_bundle_marketing(
        bundle_name=args.bundle_name,
        unit_roots=unit_paths,
        output_root=output_root,
    )

    print(f"Bundle marketing generated: {result}")


if __name__ == "__main__":
    main()