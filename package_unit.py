"""
package_unit.py — Build all customer-facing zips for a unit from its
cleaned public release folder. Replaces the manual packaging step
(PROGRESS.md "Next Session" Priority 4, step 5).

Given a unit id, produces (in releases/artifacts/ by default):
    <unit_id>_<version>_PUBLIC.zip        # full bundle (Gumroad/TES upload source)
    <unit_id>_<version>_BUNDLE.zip        # identical content (TPT bundle source)
    <unit_id>_lesson01_<version>.zip ...  # one pptx at zip root, per lesson
    <unit_id>_assessment_<version>.zip    # Assessment_Task + Rubric docx at root

Source of truth: releases/public/<unit_id>_<version>/ with the numbered
folders 01_Lesson_Slides .. 05_Teacher_Guide (built by stage_packaging()).

Packaging hygiene rules (from the 2026-06-26 packaging audit):
customer zips must NEVER contain listings folders (06_Listings), QA
screenshots, raw Canva CSVs, canva prompt files, raw .md/.json pipeline
files, or nested redundant zips. This script enforces that with an
extension allowlist + folder allowlist and logs everything it skips.

Usage:
    python package_unit.py --unit year7_algorithms_unit1
    python package_unit.py --unit year7_algorithms_unit1 --out-dir /tmp/test --force
    python package_unit.py --unit year7_algorithms_unit1 --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
RELEASES_ROOT = PROJECT_ROOT / "releases"

# Only these top-level folders of the public release folder are customer-facing.
CUSTOMER_FOLDERS = [
    "01_Lesson_Slides",
    "02_Assessment",
    "03_Student_Workbook",
    "04_Unit_Roadmap",
    "05_Teacher_Guide",
]

# Only these file types ever ship to a customer.
ALLOWED_EXTENSIONS = {".pptx", ".docx", ".pdf", ".xlsx"}

# Extra name-based denies (belt and braces on top of the allowlist).
DENY_NAME_PATTERNS = [
    re.compile(r"^screenshot", re.IGNORECASE),
    re.compile(r"canva", re.IGNORECASE),
    re.compile(r"\(\d+\)\.\w+$"),  # duplicate-upload names like "Lesson 6 (1).pptx"
]

EXPECTED_LESSON_COUNT = 7


def _is_customer_file(path: Path, skipped: list[str]) -> bool:
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        skipped.append(f"{path.name} (extension {path.suffix or 'none'} not customer-facing)")
        return False
    for pat in DENY_NAME_PATTERNS:
        if pat.search(path.name):
            skipped.append(f"{path.name} (matches deny pattern {pat.pattern!r})")
            return False
    return True


def _collect_customer_files(public_root: Path) -> tuple[dict[str, list[Path]], list[str]]:
    """Return {top_folder: [files]} for customer folders only, plus a skip log."""
    skipped: list[str] = []
    collected: dict[str, list[Path]] = {}

    for entry in sorted(public_root.iterdir()):
        if entry.is_dir():
            if entry.name not in CUSTOMER_FOLDERS:
                skipped.append(f"{entry.name}/ (entire folder — not customer-facing)")
                continue
            files = []
            for f in sorted(entry.rglob("*")):
                if f.is_file() and _is_customer_file(f, skipped):
                    files.append(f)
            collected[entry.name] = files
        else:
            # Loose files at the public root are never customer-facing
            # (historically: stray screenshots).
            skipped.append(f"{entry.name} (loose file at public-folder root)")

    return collected, skipped


def _validate(collected: dict[str, list[Path]]) -> list[str]:
    problems = []
    for folder in CUSTOMER_FOLDERS:
        if folder not in collected:
            problems.append(f"Missing folder: {folder}/")
        elif not collected[folder]:
            problems.append(f"Folder has no shippable files: {folder}/")

    slides = collected.get("01_Lesson_Slides", [])
    pptx = [f for f in slides if f.suffix.lower() == ".pptx"]
    if len(pptx) != EXPECTED_LESSON_COUNT:
        problems.append(
            f"Expected {EXPECTED_LESSON_COUNT} lesson PPTX files, found {len(pptx)}"
        )
    for f in pptx:
        if not re.match(r"^\d{2}-", f.name):
            problems.append(f"Slide file not numbered 'NN-<slug>.pptx': {f.name}")

    assess_names = {f.name for f in collected.get("02_Assessment", [])}
    for required in ("Assessment_Task.docx", "Assessment_Rubric_and_Marking.docx"):
        if required not in assess_names:
            problems.append(f"Missing assessment file: {required}")

    return problems


def _write_zip(zip_path: Path, entries: list[tuple[Path, str]], include_dirs: bool = False) -> None:
    """Write entries [(src_path, arcname)] to zip_path.

    include_dirs adds explicit directory entries (matches the structure of
    the hand-built bundle zips, which were made with shutil.make_archive).
    """
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if include_dirs:
            dirs = sorted({str(Path(arc).parent).replace("\\", "/") for _, arc in entries if "/" in arc.replace("\\", "/")})
            for d in dirs:
                if d and d != ".":
                    zf.writestr(zipfile.ZipInfo(d + "/"), "")
        for src, arc in entries:
            zf.write(src, arc.replace("\\", "/"))


def package_unit(
    unit_id: str,
    version: str = "v001",
    out_dir: Path | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> dict:
    public_root = RELEASES_ROOT / "public" / f"{unit_id}_{version}"
    if not public_root.exists():
        raise FileNotFoundError(
            f"Public release folder not found: {public_root}\n"
            f"Run the full pipeline first: python -m cmie.pipeline.full_product_pipeline "
            f"--unit-config data/units/{unit_id}.json"
        )

    out_dir = out_dir or (RELEASES_ROOT / "artifacts")

    collected, skipped = _collect_customer_files(public_root)
    problems = _validate(collected)

    print(f"Source folder : {public_root}")
    print(f"Output dir    : {out_dir}")
    if skipped:
        print(f"\nExcluded from customer zips ({len(skipped)}):")
        for s in skipped:
            print(f"  - {s}")
    if problems:
        print("\nVALIDATION PROBLEMS:")
        for p in problems:
            print(f"  ! {p}")
        raise RuntimeError(
            "Refusing to package: fix the problems above (or the public folder is incomplete)."
        )

    # ---- plan the four kinds of outputs -------------------------------
    outputs: dict[str, list[tuple[Path, str]]] = {}

    # Bundle content: all customer files, with paths relative to public_root.
    bundle_entries = [
        (f, str(f.relative_to(public_root)))
        for folder in CUSTOMER_FOLDERS
        for f in collected[folder]
    ]
    outputs[f"{unit_id}_{version}_PUBLIC.zip"] = bundle_entries
    outputs[f"{unit_id}_{version}_BUNDLE.zip"] = bundle_entries

    # Per-lesson zips: one NN-<slug>.pptx at the zip root.
    for f in sorted(collected["01_Lesson_Slides"]):
        num = f.name[:2]
        outputs[f"{unit_id}_lesson{num}_{version}.zip"] = [(f, f.name)]

    # Assessment zip: both docx at the zip root.
    outputs[f"{unit_id}_assessment_{version}.zip"] = [
        (f, f.name) for f in sorted(collected["02_Assessment"])
    ]

    # ---- overwrite guard ----------------------------------------------
    existing = [name for name in outputs if (out_dir / name).exists()]
    if existing and not force:
        print("\nThese artifacts already exist (use --force to overwrite, "
              "or --out-dir to write elsewhere):")
        for name in existing:
            print(f"  - {out_dir / name}")
        raise FileExistsError("Refusing to overwrite existing artifacts without --force.")

    # ---- write ----------------------------------------------------------
    print(f"\nBuilding {len(outputs)} zips:")
    results = {}
    for name, entries in outputs.items():
        zip_path = out_dir / name
        is_bundle = name.endswith(("_PUBLIC.zip", "_BUNDLE.zip"))
        if dry_run:
            print(f"  [dry-run] {name}  ({len(entries)} files)")
            for _, arc in entries:
                print(f"      {arc}")
            continue
        _write_zip(zip_path, entries, include_dirs=is_bundle)
        size = zip_path.stat().st_size
        print(f"  {name}  ({len(entries)} files, {size:,} bytes)")
        results[name] = zip_path

    if not dry_run:
        # Verify each zip is readable and matches its planned file list.
        for name, entries in outputs.items():
            with zipfile.ZipFile(out_dir / name) as zf:
                bad = zf.testzip()
                if bad is not None:
                    raise RuntimeError(f"Corrupt entry in {name}: {bad}")
                in_zip = {i.filename for i in zf.infolist() if not i.is_dir()}
                planned = {arc.replace("\\", "/") for _, arc in entries}
                if in_zip != planned:
                    raise RuntimeError(
                        f"Zip contents mismatch in {name}: "
                        f"missing={planned - in_zip}, extra={in_zip - planned}"
                    )
        print("\nAll zips verified: readable, contents match plan.")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Package a unit's customer-facing zips from releases/public/<unit>_<version>/"
    )
    parser.add_argument("--unit", required=True, help="Unit ID, e.g. year7_algorithms_unit1")
    parser.add_argument("--version", default="v001", help="Release version (default v001)")
    parser.add_argument("--out-dir", help="Output directory (default releases/artifacts)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be built, write nothing")
    args = parser.parse_args()

    try:
        package_unit(
            args.unit,
            version=args.version,
            out_dir=Path(args.out_dir) if args.out_dir else None,
            force=args.force,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, FileExistsError, RuntimeError) as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
