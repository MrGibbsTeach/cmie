from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so cmie imports work
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.backend.routers import generate, jobs, publish

app = FastAPI(title="CMIE Studio API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(jobs.router)
app.include_router(publish.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
