from __future__ import annotations

from fastapi import APIRouter, HTTPException

from webapp.backend.services import pipeline_service

router = APIRouter(prefix="/api/jobs", tags=["publish"])


@router.post("/{job_id}/publish/tpt")
def publish_to_tpt(job_id: str):
    job = pipeline_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed before publishing")
    if job.type != "unit":
        raise HTTPException(status_code=400, detail="Only unit jobs can be published to TPT")
    if job.publish_status == "running":
        raise HTTPException(status_code=400, detail="Publish already in progress")

    pipeline_service.launch_tpt_publish(job)
    return {"publish_status": "running"}
