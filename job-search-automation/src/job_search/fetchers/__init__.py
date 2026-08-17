"""Fetcher registry.

To add a new provider: write a module exposing `fetch(cfg) -> list[JobListing]`
(see base.py for shared helpers), add a matching boolean field to
ProvidersConfig in config.py, and register it in REGISTRY below. Nothing
else needs to change (open/closed principle).
"""

from __future__ import annotations

from ..config import AppConfig
from ..models import JobListing
from . import arbeitnow, hackernews, python_jobs, remoteok, remotive, vuejobs, weworkremotely

# provider config field name -> fetch function
REGISTRY = {
    "remoteok": remoteok.fetch,
    "remotive": remotive.fetch,
    "weworkremotely": weworkremotely.fetch,
    "python_jobs": python_jobs.fetch,
    "vuejobs": vuejobs.fetch,
    "hackernews": hackernews.fetch,
    "arbeitnow": arbeitnow.fetch,
}


def fetch_all(cfg: AppConfig) -> list[JobListing]:
    """Run every provider enabled in config.yaml and return the combined list."""
    jobs: list[JobListing] = []
    for field_name, fetch_fn in REGISTRY.items():
        if getattr(cfg.providers, field_name):
            jobs.extend(fetch_fn(cfg))
    return jobs
