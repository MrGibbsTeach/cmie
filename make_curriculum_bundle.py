"""
make_curriculum_bundle.py -- combine ALL (or many) units' persisted zips into
one flagship, whole-curriculum product, with curriculum-level front matter
(overview, standards alignment, vocabulary glossary) added at the top of the
zip. This is the "separate curriculum-bundle initiative" make_bundle.py's
own docstring defers to for anything bigger than 2-3 units (standing flag
agreed 2026-08-27, built 2026-09-19).

Usage:
    python make_curriculum_bundle.py --bundle-id complete_digital_technologies_curriculum \\
        --title "The Complete Digital Technologies Curriculum" \\
        --units year7_orientation_unit1 year7_digital_systems_unit1 ... \\
        --front-matter-dir <dir with 00_*.docx, 01_*.docx, 02_*.docx> \\
        --price-usd 249 --price-aud 299 --price-gbp 149

Output (mirrors make_bundle.py's convention):
    releases/artifacts/<bundle-id>_v001_PUBLIC.zip
    releases/artifacts/<bundle-id>_v001_BUNDLE.zip
        00_Curriculum_Overview/*.docx  (front matter, un-namespaced)
        <unit_id>/...                  (one subfolder per unit, namespaced
                                         so lesson numbering never collides)
    releases/<bundle-id>/listings/unit/{tpt,gumroad,tes}_listing.md
    data/units/marketing/<bundle-id>_listing.md
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
PACKAGED_ROOT = PROJECT_ROOT / "data" / "units" / "packaged"
UNITS_ROOT = PROJECT_ROOT / "data" / "units"
MARKETING_ROOT = UNITS_ROOT / "marketing"
ARTIFACTS_ROOT = PROJECT_ROOT / "releases" / "artifacts"


def _packaged_zip(unit_id: str, version: str) -> Path:
    return PACKAGED_ROOT / f"{unit_id}_{version}_PUBLIC.zip"


def _load_unit_config(unit_id: str) -> dict:
    path = UNITS_ROOT / f"{unit_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No unit config at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_bundle_zip(bundle_id: str, unit_ids: list[str], front_matter_dir: Path | None,
                      version: str = "v001") -> Path:
    missing = [u for u in unit_ids if not _packaged_zip(u, version).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing persisted content for: " + ", ".join(missing) + "\n"
            f"Expected at {PACKAGED_ROOT}/<unit_id>_{version}_PUBLIC.zip for each."
        )

    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    public_path = ARTIFACTS_ROOT / f"{bundle_id}_{version}_PUBLIC.zip"
    bundle_path = ARTIFACTS_ROOT / f"{bundle_id}_{version}_BUNDLE.zip"

    with zipfile.ZipFile(public_path, "w", zipfile.ZIP_DEFLATED) as out_zf:
        if front_matter_dir and front_matter_dir.exists():
            for f in sorted(front_matter_dir.glob("*.docx")):
                out_zf.write(f, f"00_Curriculum_Overview/{f.name}")
        for unit_id in unit_ids:
            src = _packaged_zip(unit_id, version)
            with zipfile.ZipFile(src) as in_zf:
                for info in in_zf.infolist():
                    if info.is_dir():
                        continue
                    data = in_zf.read(info.filename)
                    out_zf.writestr(f"{unit_id}/{info.filename}", data)

    with zipfile.ZipFile(public_path) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise RuntimeError(f"Corrupt entry in {public_path.name}: {bad}")

    bundle_path.write_bytes(public_path.read_bytes())
    return public_path


def build_listing(bundle_id: str, title: str, unit_ids: list[str],
                   price_usd: str | None, price_aud: str | None, price_gbp: str | None,
                   platform_copy: dict[str, str]) -> dict[str, Path]:
    configs = [_load_unit_config(u) for u in unit_ids]
    n_units = len(unit_ids)
    n_lessons = sum(len(cfg.get("topics", [])) for cfg in configs)

    RELEASES_ROOT = ARTIFACTS_ROOT.parent
    from cmie.publishing.thumbnail import generate_thumbnail
    thumbnail_path = generate_thumbnail(
        title,
        {**configs[0], "unit_id": bundle_id, "title": title},
        RELEASES_ROOT / "thumbnails",
        includes=[
            f"{n_lessons} fully planned lessons across {n_units} units",
            f"{n_units} assessment packs + rubrics",
            f"{n_units} student workbooks + teacher guides",
            "Full curriculum overview, standards alignment & glossary",
        ],
    )

    bundle_unit_root = RELEASES_ROOT / bundle_id / "listings" / "unit"
    bundle_unit_root.mkdir(parents=True, exist_ok=True)
    written = {}
    for platform, text in platform_copy.items():
        p = bundle_unit_root / f"{platform}_listing.md"
        p.write_text(text, encoding="utf-8")
        written[f"{platform}_listing.md"] = p

    price_line = " / ".join(
        s for s in [
            f"USD ${price_usd}" if price_usd else "",
            f"AUD ${price_aud}" if price_aud else "",
            f"GBP £{price_gbp}" if price_gbp else "",
        ] if s
    )
    ref_lines = [
        f"# Bundle listing — {title}",
        "",
        f"Bundle ID: `{bundle_id}`",
        f"Price: {price_line or '[SET PRICE]'}",
        f"Zip: releases/artifacts/{bundle_id}_v001_BUNDLE.zip",
        f"Thumbnail: {thumbnail_path}",
        "",
        "## Per-platform listing copy is in the same folder as this file",
        "(tpt_listing.md / gumroad_listing.md / tes_listing.md — optimised per platform, not identical copy).",
    ]
    MARKETING_ROOT.mkdir(parents=True, exist_ok=True)
    ref_path = MARKETING_ROOT / f"{bundle_id}_listing.md"
    ref_path.write_text("\n".join(ref_lines), encoding="utf-8")
    written["reference"] = ref_path
    written["thumbnail"] = thumbnail_path
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine many units into one flagship curriculum bundle.")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--units", nargs="+", required=True)
    parser.add_argument("--front-matter-dir", default=None)
    parser.add_argument("--version", default="v001")
    parser.add_argument("--price-usd", default=None)
    parser.add_argument("--price-aud", default=None)
    parser.add_argument("--price-gbp", default=None)
    args = parser.parse_args()

    front_matter_dir = Path(args.front_matter_dir) if args.front_matter_dir else None

    try:
        zip_path = build_bundle_zip(args.bundle_id, args.units, front_matter_dir, args.version)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    print(f"Bundle zip built: {zip_path} ({zip_path.stat().st_size:,} bytes)")
    print("Now write per-platform listing copy manually and call build_listing() "
          "via a follow-up script, or import this module directly.")


if __name__ == "__main__":
    main()
