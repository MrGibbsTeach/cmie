from __future__ import annotations

import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from docx import Document

from cmie.core.unit_config import UnitConfig
from cmie.generator.batch_generate import run_batch
from cmie.generator import assessment_generator
from cmie.generator.assessment_markdown import render_assessment_markdown
from cmie.generator.workbook_generator import generate_student_workbook
from cmie.generator.roadmap_generator import generate_unit_roadmap
from cmie.validation.unit_validation import validate_unit
from cmie.marketing.marketing_generator import generate_marketing_assets

# Optional – listings generator may not exist yet
try:
    from cmie.generator.listing_generator import generate_listings_for_unit  # type: ignore
except Exception:  # pragma: no cover
    generate_listings_for_unit = None  # type: ignore


# --------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("full_product_pipeline")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def markdown_to_docx(md_path: Path, docx_path: Path, logger: logging.Logger) -> None:
    """
    Very simple markdown-to-docx: treat each line as a paragraph.

    This is intentionally minimal; the main goal is to get editable
    Word docs automatically. You can improve formatting later if needed.
    """
    logger.info(f"  Converting {md_path.name} -> {docx_path.name}")
    text = md_path.read_text(encoding="utf-8")

    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)

    docx_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(docx_path)


# --------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------


def stage_lessons(
    cfg: UnitConfig,
    unit_root: Path,
    logger: logging.Logger,
) -> Tuple[Path, Path, List[Path]]:
    """
    Generate lessons and copy JSON + PPTX into the unit release folder.
    """
    logger.info("Stage: lessons")

    lessons_dir = unit_root / "lessons"
    slides_dir = unit_root / "slides"
    lessons_dir.mkdir(parents=True, exist_ok=True)
    slides_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing content (only within these folders)
    for p in lessons_dir.glob("*.json"):
        p.unlink()
    for p in slides_dir.glob("*.pptx"):
        p.unlink()

    # Run the batch lesson generator using the unit config
    results = run_batch(cfg)

    copied_lessons: List[Path] = []
    for lesson_json, pptx in results:
        # Use the topic slug (parent folder name) as the JSON filename
        topic_slug = lesson_json.parent.name  # e.g. "data-shapes-the-ai-world"
        dest_json = lessons_dir / f"{topic_slug}.json"

        dest_pptx = slides_dir / pptx.name

        shutil.copy2(lesson_json, dest_json)
        shutil.copy2(pptx, dest_pptx)
        copied_lessons.append(dest_json)

    logger.info(f"  {len(copied_lessons)} lessons copied.")
    return lessons_dir, slides_dir, copied_lessons


def stage_assessment(
    cfg: UnitConfig,
    unit_root: Path,
    logger: logging.Logger,
) -> Path:
    """
    Generate assessment JSON + markdown directly into unit_root/assessment.
    """
    logger.info("Stage: assessment")

    dest_dir = unit_root / "assessment"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Use pipeline-friendly API that writes JSON into dest_dir
    assessment_generator.generate_summative_assessment(
        unit_id=cfg.unit_id,
        title=cfg.title,
        year_level=cfg.year_level,
        subject=cfg.subject,
        output_dir=dest_dir,
    )

    # Render markdown in dest_dir (using the JSON we just wrote)
    render_assessment_markdown(dest_dir)

    logger.info("  Assessment generated.")
    return dest_dir


def stage_workbook(
    cfg: UnitConfig,
    unit_root: Path,
    lessons_dir: Path,
    assessment_dir: Optional[Path],
    logger: logging.Logger,
) -> Path:
    logger.info("Stage: workbook")
    unit_config_dict = {
        "unit_id": cfg.unit_id,
        "title": cfg.title,
        "year_level": cfg.year_level,
        "subject": cfg.subject,
        "version": cfg.version,
    }
    workbook_path = generate_student_workbook(unit_root, unit_config_dict, lessons_dir, assessment_dir)
    logger.info(f"  Workbook file: {workbook_path}")
    return workbook_path


def stage_roadmap(
    cfg: UnitConfig,
    unit_root: Path,
    lessons_dir: Path,
    assessment_dir: Optional[Path],
    logger: logging.Logger,
) -> Path:
    logger.info("Stage: roadmap")
    unit_config_dict = {
        "unit_id": cfg.unit_id,
        "title": cfg.title,
        "year_level": cfg.year_level,
        "subject": cfg.subject,
        "version": cfg.version,
    }
    meta = generate_unit_roadmap(unit_root, unit_config_dict, lessons_dir, assessment_dir)
    roadmap_path = Path(meta["file"])
    logger.info(f"  Roadmap file: {roadmap_path}")
    return roadmap_path

def stage_marketing(
    cfg: UnitConfig,
    unit_root: Path,
    lessons_dir: Path,
    logger: logging.Logger,
) -> Path:
    """
    Generate marketplace-ready marketing copy for this unit.
    """
    logger.info("Stage: marketing")

    dest_dir = unit_root / "marketing"
    dest_dir.mkdir(parents=True, exist_ok=True)

    unit_meta = {
        "unit_id": cfg.unit_id,
        "title": cfg.title,
        "year_level": cfg.year_level,
        "subject": cfg.subject,
        "version": cfg.version,
    }

    assets = generate_marketing_assets(unit_meta, lessons_dir)

    out_path = dest_dir / "marketing_assets.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    logger.info(f"  Marketing assets generated: {out_path}")
    return out_path


def stage_listings(
    cfg: UnitConfig,
    unit_root: Path,
    logger: logging.Logger,
) -> None:
    logger.info("Stage: listings")
    if generate_listings_for_unit is None:
        logger.info("  Listings generator not available; skipping.")
        return

    unit_config_dict = {
        "unit_id": cfg.unit_id,
        "title": cfg.title,
        "year_level": cfg.year_level,
        "subject": cfg.subject,
        "version": cfg.version,
    }
    try:
        generate_listings_for_unit(unit_root, unit_config_dict)  # type: ignore
        logger.info("  Listings generated.")
    except Exception as e:  # pragma: no cover
        logger.warning(f"  Listings generation failed: {e}")


def stage_packaging(
    cfg: UnitConfig,
    unit_root: Path,
    releases_root: Path,
    lessons_dir: Path,
    slides_dir: Path,
    assessment_dir: Path,
    workbook_path: Path,
    roadmap_path: Path,
    logger: logging.Logger,
) -> None:
    """
    Create:
    - Internal zip of the full unit_root
    - Public editable folder with PPTX and DOCX (no zip for public)
    """
    logger.info("Stage: packaging")

    # -----------------------------
    # Internal zip (for your own archive / internal use)
    # -----------------------------
    artifacts_root = releases_root / "artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    zip_name = f"{cfg.unit_id}_{cfg.version}"
    zip_base = artifacts_root / zip_name
    shutil.make_archive(str(zip_base), "zip", root_dir=unit_root)
    logger.info("  Internal zip created.")

    # -----------------------------
    # Public editable folder
    # -----------------------------
    public_root = releases_root / "public" / f"{cfg.unit_id}_{cfg.version}"

    if public_root.exists():
        try:
            shutil.rmtree(public_root)
        except PermissionError as e:
            logger.warning(
                "Public folder is in use (likely a DOCX open in Word). "
                "Skipping public packaging this run.\nDetails: %s",
                e,
            )
            return

    public_root.mkdir(parents=True, exist_ok=True)

    # 01 – Lesson Slides
    public_slides = public_root / "01_Lesson_Slides"
    public_slides.mkdir(parents=True, exist_ok=True)
    for pptx in slides_dir.glob("*.pptx"):
        shutil.copy2(pptx, public_slides / pptx.name)

    # 02 – Assessment (DOCX from markdown)
    public_assessment = public_root / "02_Assessment"
    public_assessment.mkdir(parents=True, exist_ok=True)

    task_md = assessment_dir / "assessment_task.md"
    rubric_md = assessment_dir / "assessment_rubric_marking.md"

    if task_md.exists():
        markdown_to_docx(task_md, public_assessment / "Assessment_Task.docx", logger)

    if rubric_md.exists():
        markdown_to_docx(
            rubric_md,
            public_assessment / "Assessment_Rubric_and_Marking.docx",
            logger,
        )

    # 03 – Student Workbook (DOCX)
    public_workbook = public_root / "03_Student_Workbook"
    public_workbook.mkdir(parents=True, exist_ok=True)

    workbook_md = workbook_path
    if workbook_md.exists():
        markdown_to_docx(
            workbook_md,
            public_workbook / "Student_Workbook.docx",
            logger,
        )

    # 04 – Unit Roadmap (DOCX)
    public_roadmap = public_root / "04_Unit_Roadmap"
    public_roadmap.mkdir(parents=True, exist_ok=True)

    roadmap_md = roadmap_path
    if roadmap_md.exists():
        markdown_to_docx(
            roadmap_md,
            public_roadmap / "Unit_Roadmap.docx",
            logger,
        )

    # 05 – Listings (optional, if present)
    listings_dir = unit_root / "listings"
    if listings_dir.exists():
        public_listings = public_root / "05_Listings"
        public_listings.mkdir(parents=True, exist_ok=True)
        for f in listings_dir.glob("*.*"):
            shutil.copy2(f, public_listings / f.name)

    logger.info(f"  Public editable folder created: {public_root}")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------


def run_pipeline(config_path: Path, releases_root: Path) -> None:
    logger = setup_logger()

    with config_path.open(encoding="utf-8") as f:
        raw_config = json.load(f)

    cfg = UnitConfig.from_dict(raw_config)

    unit_root = releases_root / cfg.unit_id
    unit_root.mkdir(parents=True, exist_ok=True)

    # Stages
    lessons_dir, slides_dir, _ = stage_lessons(cfg, unit_root, logger)
    assessment_dir = stage_assessment(cfg, unit_root, logger)
    workbook_path = stage_workbook(cfg, unit_root, lessons_dir, assessment_dir, logger)
    roadmap_path = stage_roadmap(cfg, unit_root, lessons_dir, assessment_dir, logger)
    marketing_path = stage_marketing(cfg, unit_root, lessons_dir, logger)

    # Listings are optional – skip cleanly if the generator isn't available
    try:
        stage_listings(cfg, unit_root, logger)
    except ImportError:
        logger.info("Listings generator not available; skipping.")

    stage_packaging(
        cfg,
        unit_root,
        releases_root,
        lessons_dir,
        slides_dir,
        assessment_dir,
        workbook_path,
        roadmap_path,
        logger,
    )

        # Validation summary
    errors = validate_unit(unit_root)

    report_path = unit_root / "validation_report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(f"# Validation report for {cfg.unit_id} ({cfg.version})\n\n")

        if errors:
            f.write("## Status\n\n")
            f.write("⚠️ Validation completed **with issues**.\n\n")
            f.write("## Issues\n\n")
            for e in errors:
                f.write(f"- {e}\n")
        else:
            f.write("## Status\n\n")
            f.write("✅ Validation completed: no structural issues detected.\n")

    if errors:
        logger.info("Validation completed with issues:")
        for e in errors:
            logger.info(f"  - {e}")
        logger.info(f"Full validation report written to {report_path}")
    else:
        logger.info("Validation completed: no structural issues detected.")
        logger.info(f"Validation report written to {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Full product pipeline for a micro-unit.")
    parser.add_argument(
        "--unit-config",
        required=True,
        help="Path to the unit config JSON (e.g. data/units/year7_ai_data_unit1.json)",
    )
    parser.add_argument(
        "--releases-root",
        default="releases",
        help="Root folder for releases (default: releases)",
    )
    args = parser.parse_args()

    config_path = Path(args.unit_config)
    releases_root = Path(args.releases_root)

    run_pipeline(config_path, releases_root)


if __name__ == "__main__":
    main()