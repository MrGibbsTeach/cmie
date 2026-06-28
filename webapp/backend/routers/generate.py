from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from webapp.backend.services import pipeline_service

router = APIRouter(prefix="/api/generate", tags=["generate"])


# ------------------------------------------------------------------
# Request models
# ------------------------------------------------------------------

class TopicIn(BaseModel):
    title: str
    video_url: Optional[str] = None


class UnitRequest(BaseModel):
    unit_id: str
    title: str
    year_level: str
    subject: str
    version: str = "v001"
    topics: List[TopicIn]


class LessonRequest(BaseModel):
    unit_title: str
    year_level: str
    topic_title: str
    lesson_number: int = 1
    video_url: Optional[str] = None


class AssessmentRequest(BaseModel):
    unit_id: str
    title: str
    year_level: str
    subject: str


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@router.post("/unit")
def generate_unit(req: UnitRequest):
    config = req.model_dump()
    job = pipeline_service.create_job(
        type_="unit",
        title=req.title,
        config=config,
    )
    pipeline_service.launch_unit(job)
    return {"job_id": job.id, "status": job.status}


@router.post("/lesson")
def generate_lesson(req: LessonRequest):
    config = req.model_dump()
    job = pipeline_service.create_job(
        type_="lesson",
        title=f"{req.unit_title} — {req.topic_title}",
        config=config,
    )
    pipeline_service.launch_lesson(job)
    return {"job_id": job.id, "status": job.status}


@router.post("/assessment")
def generate_assessment(req: AssessmentRequest):
    config = req.model_dump()
    job = pipeline_service.create_job(
        type_="assessment",
        title=req.title,
        config=config,
    )
    pipeline_service.launch_assessment(job)
    return {"job_id": job.id, "status": job.status}
