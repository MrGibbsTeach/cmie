from __future__ import annotations

import argparse
from pathlib import Path

from cmie.marketing.channel_renderer import generate_channel_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate channel-specific listings.")
    parser.add_argument(
        "--bundle-root",
        required=True,
        help="Path to bundle folder (e.g. releases/bundles/ai_data_foundations_bundle)",
    )

    args = parser.parse_args()

    bundle_root = Path(args.bundle_root)
    generate_channel_files(bundle_root)

    print(f"Channel listings generated in {bundle_root}")


if __name__ == "__main__":
    main()