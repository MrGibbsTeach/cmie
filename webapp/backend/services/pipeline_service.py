from __future__ import annotations

import json
import logging
import re
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict

from webapp.backend.models import Job

PROJECT_ROOT  = Path(__file__).resolve().parents[3]
RELEASES_ROOT = PROJECT_ROOT / "releases"
JOBS_TMP      = RELEASES_ROOT / "jobs_tmp"
JOB_STORE     = RELEASES_ROOT / "jobs"

_jobs: Dict[str, Job] = {}
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _persist(job: Job) -> None:
    JOB_STORE.mkdir(parents=True, exist_ok=True)
    path = JOB_STORE / f"{job.id}.json"
    path.write_text(json.dumps(job.to_dict(), ensure_ascii=False), encoding="utf-8")


def _load_all() -> None:
    if not JOB_STORE.exists():
        return
    for p in sorted(JOB_STORE.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            job  = Job.from_dict(data)
            _jobs[job.id] = job
        except Exception:
            pass


# Load persisted jobs at module import time
_load_all()


# ---------------------------------------------------------------------------
# Store helpers
# ---------------------------------------------------------------------------

def create_job(type_: str, title: str, config: dict) -> Job:
    job = Job(type=type_, title=title, config=config)
    with _lock:
        _jobs[job.id] = job
    _persist(job)
    return job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def list_jobs() -> list[Job]:
    with _lock:
        return sorted(_jobs.values(), key=lambda j: j.created_at, reverse=True)


# ---------------------------------------------------------------------------
# Log capture handler
# ---------------------------------------------------------------------------

class _ListHandler(logging.Handler):
    def __init__(self, job: Job):
        super().__init__()
        self.job = job
        self.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    def emit(self, record: logging.LogRecord) -> None:
        self.job.logs.append(self.format(record))
        _persist(self.job)


# ---------------------------------------------------------------------------
# YouTube search
# ---------------------------------------------------------------------------

def _find_youtube_url(query: str) -> str | None:
    try:
        import yt_dlp  # type: ignore
        opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info and info.get("entries"):
                vid_id = info["entries"][0].get("id")
                if vid_id:
                    return f"https://www.youtube.com/watch?v={vid_id}"
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Slug helper
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---------------------------------------------------------------------------
# Zip helper
# ---------------------------------------------------------------------------

def _zip_dir(source_dir: Path, name: str) -> str:
    zip_base = RELEASES_ROOT / "artifacts" / name
    zip_base.parent.mkdir(parents=True, exist_ok=True)
    shutil.make_archive(str(zip_base), "zip", root_dir=source_dir)
    return str(zip_base) + ".zip"


# ---------------------------------------------------------------------------
# Unit pipeline runner
# ---------------------------------------------------------------------------

def _run_unit(job: Job) -> None:
    import os
    os.chdir(PROJECT_ROOT)

    from cmie.pipeline.full_product_pipeline import run_pipeline

    handler = _ListHandler(job)
    pipeline_logger = logging.getLogger("full_product_pipeline")
    pipeline_logger.addHandler(handler)

    JOBS_TMP.mkdir(parents=True, exist_ok=True)
    config_path = JOBS_TMP / f"{job.id}_config.json"
    config_path.write_text(json.dumps(job.config), encoding="utf-8")

    try:
        job.status = "running"
        job.logs.append("[INFO] Starting unit pipeline...")
        _persist(job)

        run_pipeline(config_path, RELEASES_ROOT)

        unit_id  = job.config["unit_id"]
        version  = job.config.get("version", "v001")
        public_dir = RELEASES_ROOT / "public" / f"{unit_id}_{version}"
        zip_path   = RELEASES_ROOT / "artifacts" / f"{unit_id}_{version}.zip"

        job.output_path = str(public_dir)
        if zip_path.exists():
            job.download_zip = str(zip_path)
        else:
            out_zip_base = RELEASES_ROOT / "artifacts" / f"{unit_id}_{version}_public"
            shutil.make_archive(str(out_zip_base), "zip", root_dir=public_dir)
            job.download_zip = str(out_zip_base) + ".zip"

        job.status       = "completed"
        job.completed_at = datetime.utcnow()
        job.logs.append("[INFO] Pipeline complete.")

    except Exception as exc:
        job.status       = "failed"
        job.error        = str(exc)
        job.completed_at = datetime.utcnow()
        job.logs.append(f"[ERROR] {exc}")
    finally:
        pipeline_logger.removeHandler(handler)
        _persist(job)
        if config_path.exists():
            config_path.unlink()


# ---------------------------------------------------------------------------
# Lesson runner
# ---------------------------------------------------------------------------

def _run_lesson(job: Job) -> None:
    import os
    os.chdir(PROJECT_ROOT)

    from cmie.generator.ai_lesson_engine import generate_and_save_lesson
    from cmie.generator.pptx_generator import lesson_json_to_pptx

    try:
        job.status = "running"
        job.logs.append("[INFO] Generating lesson content...")
        _persist(job)

        cfg = job.config
        lesson_path = generate_and_save_lesson(
            micro_unit_name=cfg["unit_title"],
            year_level=cfg["year_level"],
            topic_title=cfg["topic_title"],
            lesson_number=cfg.get("lesson_number", 1),
            video_url=cfg.get("video_url"),
        )
        job.logs.append("[INFO] Lesson content done.")
        _persist(job)

        if not cfg.get("video_url"):
            topic = cfg.get("topic_title", "")
            year  = cfg.get("year_level", "")
            search_query = f"{topic} {year} explained for students"
            job.logs.append(f"[INFO] Searching YouTube: {search_query}")
            found_url = _find_youtube_url(search_query)
            if found_url:
                job.logs.append(f"[INFO] Video found: {found_url}")
                with lesson_path.open("r", encoding="utf-8") as f:
                    lesson_data = json.load(f)
                lesson_data["video_url"] = found_url
                lesson_path.write_text(
                    json.dumps(lesson_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            else:
                job.logs.append("[INFO] No YouTube video found, continuing without.")
            _persist(job)

        job.logs.append("[INFO] Building PPTX slides...")
        pptx_path = lesson_json_to_pptx(lesson_path, output_dir=lesson_path.parent)
        job.logs.append(f"[INFO] PPTX created: {pptx_path.name}")

        job.output_path = str(lesson_path.parent)

        topic_slug = _slugify(cfg.get("topic_title", "lesson"))
        unit_slug  = _slugify(cfg.get("unit_title", ""))
        zip_name   = f"{unit_slug}_{topic_slug}" if unit_slug else topic_slug
        job.download_zip = _zip_dir(lesson_path.parent, zip_name)

        job.status       = "completed"
        job.completed_at = datetime.utcnow()
        job.logs.append("[INFO] Done. Download your lesson package from the zip.")

    except Exception as exc:
        job.status       = "failed"
        job.error        = str(exc)
        job.completed_at = datetime.utcnow()
        job.logs.append(f"[ERROR] {exc}")
    finally:
        _persist(job)


# ---------------------------------------------------------------------------
# Assessment runner
# ---------------------------------------------------------------------------

def _run_assessment(job: Job) -> None:
    import os
    os.chdir(PROJECT_ROOT)

    from cmie.generator import assessment_generator
    from cmie.generator.assessment_markdown import render_assessment_markdown

    try:
        job.status = "running"
        job.logs.append("[INFO] Generating assessment...")
        _persist(job)

        cfg     = job.config
        out_dir = RELEASES_ROOT / "assessments" / job.id
        out_dir.mkdir(parents=True, exist_ok=True)

        assessment_generator.generate_summative_assessment(
            unit_id=cfg["unit_id"],
            title=cfg["title"],
            year_level=cfg["year_level"],
            subject=cfg["subject"],
            output_dir=out_dir,
        )
        render_assessment_markdown(out_dir)

        job.output_path  = str(out_dir)
        job.download_zip = _zip_dir(out_dir, f"job_{job.id}")
        job.status       = "completed"
        job.completed_at = datetime.utcnow()
        job.logs.append("[INFO] Assessment complete.")

    except Exception as exc:
        job.status       = "failed"
        job.error        = str(exc)
        job.completed_at = datetime.utcnow()
        job.logs.append(f"[ERROR] {exc}")
    finally:
        _persist(job)


# ---------------------------------------------------------------------------
# TPT publish runner
# ---------------------------------------------------------------------------

def _run_tpt_publish(job: Job) -> None:
    import os
    os.chdir(PROJECT_ROOT)

    from cmie.publishing.thumbnail import generate_thumbnail
    from cmie.publishing.tpt import upload_unit

    try:
        job.publish_status = "running"
        job.logs.append("[INFO] Starting TPT publish...")
        _persist(job)

        unit_id = job.config.get("unit_id", "")
        version = job.config.get("version", "v001")

        # Locate the unit folder — prefer the public release folder, fall back to working folder
        public_folder  = RELEASES_ROOT / "public"  / f"{unit_id}_{version}"
        working_folder = RELEASES_ROOT / unit_id
        unit_folder    = public_folder if public_folder.exists() else working_folder

        if not unit_folder.exists():
            raise FileNotFoundError(f"Unit folder not found: {unit_folder}")

        zip_path = Path(job.download_zip)
        if not zip_path.exists():
            raise FileNotFoundError(f"Zip not found: {zip_path}")

        job.logs.append("[INFO] Generating thumbnail...")
        _persist(job)

        thumbnail_path = generate_thumbnail(
            title=job.title,
            config=job.config,
            output_dir=RELEASES_ROOT / "thumbnails",
        )
        job.thumbnail_path = str(thumbnail_path)
        job.logs.append(f"[INFO] Thumbnail: {thumbnail_path.name}")
        _persist(job)

        job.logs.append("[INFO] Opening browser to upload to TPT...")
        _persist(job)

        upload_unit(unit_folder, zip_path, thumbnail_path=thumbnail_path, auto_publish=False)

        job.publish_status = "completed"
        job.logs.append("[INFO] TPT publish complete.")

    except Exception as exc:
        job.publish_status = "failed"
        job.publish_error  = str(exc)
        job.logs.append(f"[ERROR] TPT publish failed: {exc}")

    finally:
        _persist(job)


# ---------------------------------------------------------------------------
# Public launchers
# ---------------------------------------------------------------------------

def launch_unit(job: Job) -> None:
    threading.Thread(target=_run_unit, args=(job,), daemon=True).start()


def launch_lesson(job: Job) -> None:
    threading.Thread(target=_run_lesson, args=(job,), daemon=True).start()


def launch_assessment(job: Job) -> None:
    threading.Thread(target=_run_assessment, args=(job,), daemon=True).start()


def launch_tpt_publish(job: Job) -> None:
    threading.Thread(target=_run_tpt_publish, args=(job,), daemon=True).start()
