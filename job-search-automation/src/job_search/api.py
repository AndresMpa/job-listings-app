"""HTTP API for job-search-automation.

Two responsibilities, deliberately kept in one small file since neither is
big enough to justify its own module:

- GET /jobs            -> reads scored listings from Postgres (for the frontend)
- GET/PUT /config      -> reads/writes config.yaml (for the /settings panel)
- POST /run            -> triggers a pipeline run in the background

Run with: uvicorn job_search.api:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import db
from .cli import run as run_pipeline
from .config import config_from_dict, load_config, save_config
from .reports import write_csv_report, write_markdown_report

CONFIG_PATH = Path("config.yaml")

app = FastAPI(title="job-search-automation API", version="1.0.0")

# The Nuxt app calls this from its own server routes (not the browser), but
# CORS is opened up for convenience when calling the API directly too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class JobOut(BaseModel):
    id: int
    source: str
    title: str
    company: str
    url: str
    description: str
    tags: list[str]
    salary: str | None
    location: str
    posted_date: str
    fit_score: int | None
    income_score: int | None
    score: int | None
    reasoning: str | None
    outreach_draft: str | None

    model_config = {"from_attributes": True}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/jobs", response_model=list[JobOut])
def list_jobs(min_score: int | None = None, limit: int = 200, offset: int = 0):
    cfg = load_config(CONFIG_PATH)
    if not cfg.database.url:
        raise HTTPException(500, "database.url is not configured")
    records = db.fetch_jobs(cfg.database, min_score=min_score, limit=limit, offset=offset)
    return records


# ---------------------------------------------------------------------------
# Settings (config.yaml)
# ---------------------------------------------------------------------------

@app.get("/config")
def get_config() -> dict[str, Any]:
    return load_config(CONFIG_PATH).to_dict()


@app.put("/config")
def update_config(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the payload by round-tripping it through AppConfig, then save."""
    try:
        cfg = config_from_dict(payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(400, f"Invalid configuration: {exc}") from exc
    save_config(cfg, CONFIG_PATH)
    return cfg.to_dict()


# ---------------------------------------------------------------------------
# Manual trigger
# ---------------------------------------------------------------------------

_run_lock = asyncio.Lock()


def _run_and_persist() -> None:
    cfg = load_config(CONFIG_PATH)
    kept = run_pipeline(cfg)
    if not kept:
        return
    write_csv_report(kept, cfg.output.csv_path)
    write_markdown_report(kept, cfg.output.md_path)
    if cfg.database.url:
        db.save_jobs(kept, cfg.database)


@app.post("/run")
async def trigger_run(background_tasks: BackgroundTasks) -> dict[str, str]:
    if _run_lock.locked():
        raise HTTPException(409, "A run is already in progress")

    async def _guarded_run() -> None:
        async with _run_lock:
            await asyncio.to_thread(_run_and_persist)

    background_tasks.add_task(_guarded_run)
    return {"status": "started"}
