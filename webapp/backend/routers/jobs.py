from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from webapp.backend.services import pipeline_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def list_jobs():
    return [j.to_dict() for j in pipeline_service.list_jobs()]


@router.get("/{job_id}")
def get_job(job_id: str):
    job = pipeline_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@router.get("/{job_id}/stream")
async def stream_logs(job_id: str):
    job = pipeline_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    async def generate():
        last_idx = 0
        while True:
            logs = job.logs
            new = logs[last_idx:]
            for line in new:
                payload = json.dumps({"log": line})
                yield f"data: {payload}\n\n"
            last_idx = len(logs)

            if job.status in ("completed", "failed"):
                payload = json.dumps({"status": job.status, "done": True, "error": job.error})
                yield f"data: {payload}\n\n"
                break

            await asyncio.sleep(0.4)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{job_id}/download")
def download_job(job_id: str):
    job = pipeline_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    if not job.download_zip:
        raise HTTPException(status_code=404, detail="No output zip available")

    zip_path = Path(job.download_zip)
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Zip file missing")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_path.name,
    )
