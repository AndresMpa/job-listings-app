"""HTTP API for job-search-automation.

Responsibilities:

- GET /jobs                  -> reads scored listings from Postgres, optionally per profile
- GET/PUT /config             -> reads/writes config.yaml, the *system* settings
- GET /profiles                -> lists candidate profiles (profiles/*.yaml)
- GET/PUT/DELETE /profiles/{name} -> reads/writes/removes a single profile
- POST /run                    -> triggers a pipeline run in the background,
                                    for one profile or every profile

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
from .cli import write_reports
from .config import (
    DEFAULT_PROFILES_DIR,
    config_from_dict,
    list_profile_paths,
    load_config,
    load_profile,
    load_profiles,
    profile_from_dict,
    save_config,
    save_profile,
)

CONFIG_PATH = Path("config.yaml")
PROFILES_DIR = DEFAULT_PROFILES_DIR

app = FastAPI(title="job-search-automation API", version="2.0.0")

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
    profile: str
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
def list_jobs(profile: str | None = None, min_score: int | None = None, limit: int = 200, offset: int = 0):
    cfg = load_config(CONFIG_PATH)
    if not cfg.database.url:
        raise HTTPException(500, "database.url is not configured")
    records = db.fetch_jobs(cfg.database, profile=profile, min_score=min_score, limit=limit, offset=offset)
    return records


# ---------------------------------------------------------------------------
# Settings (config.yaml) — system-wide, not tied to any profile
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
# Profiles (profiles/<name>.yaml) — one entry per person/role being searched for
# ---------------------------------------------------------------------------

@app.get("/profiles")
def list_profiles() -> list[dict[str, Any]]:
    profiles = []
    for path in list_profile_paths(PROFILES_DIR):
        try:
            profiles.append(load_profile(path).to_dict())
        except (OSError, ValueError) as exc:
            raise HTTPException(500, f"Could not read profile {path.name}: {exc}") from exc
    return profiles


@app.get("/profiles/{name}")
def get_profile(name: str) -> dict[str, Any]:
    path = PROFILES_DIR / f"{name}.yaml"
    if not path.exists():
        raise HTTPException(404, f"Profile '{name}' not found")
    return load_profile(path).to_dict()


@app.put("/profiles/{name}")
def update_profile(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Create or replace profiles/<name>.yaml. Validated via ProfileConfig."""
    payload = {**payload, "name": name}
    try:
        profile = profile_from_dict(name, payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(400, f"Invalid profile: {exc}") from exc
    save_profile(profile, PROFILES_DIR)
    return profile.to_dict()


@app.delete("/profiles/{name}")
def delete_profile(name: str) -> dict[str, str]:
    path = PROFILES_DIR / f"{name}.yaml"
    if not path.exists():
        raise HTTPException(404, f"Profile '{name}' not found")
    path.unlink()
    return {"status": "deleted", "name": name}


# ---------------------------------------------------------------------------
# Manual trigger
# ---------------------------------------------------------------------------

_run_lock = asyncio.Lock()


def _run_and_persist(profile_names: list[str] | None) -> None:
    cfg = load_config(CONFIG_PATH)
    if profile_names:
        profiles = [load_profile(PROFILES_DIR / f"{name}.yaml") for name in profile_names]
    else:
        profiles = load_profiles(PROFILES_DIR)

    results = run_pipeline(cfg, profiles)
    for profile in profiles:
        kept = results.get(profile.name, [])
        if not kept:
            continue
        write_reports(cfg, profile, kept)
        if cfg.database.url:
            db.save_jobs(kept, cfg.database, profile.name)


@app.post("/run")
async def trigger_run(background_tasks: BackgroundTasks, profile: str | None = None) -> dict[str, str]:
    """Runs the pipeline for a single profile (?profile=name) or every profile."""
    if _run_lock.locked():
        raise HTTPException(409, "A run is already in progress")

    profile_names = [profile] if profile else None

    async def _guarded_run() -> None:
        async with _run_lock:
            await asyncio.to_thread(_run_and_persist, profile_names)

    background_tasks.add_task(_guarded_run)
    return {"status": "started", "profiles": profile_names or "all"}
