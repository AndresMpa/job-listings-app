"""Remotive public API."""

from __future__ import annotations

import requests

from ..config import AppConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, is_ai_related, is_senior, report

NAME = "Remotive"
API_URL = "https://remotive.com/api/remote-jobs"


def fetch(cfg: AppConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    try:
        resp = requests.get(
            API_URL,
            params={"category": "software-dev", "limit": 100},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        for item in resp.json().get("jobs", []):
            title = item.get("title", "")
            if not (is_senior(title, cfg) or is_ai_related(title, cfg)):
                continue
            jobs.append(
                JobListing(
                    source=NAME,
                    title=title,
                    company=item.get("company_name", ""),
                    url=item.get("url", ""),
                    description=item.get("description", "") or "",
                    tags=item.get("tags", []) or [],
                    salary=item.get("salary", ""),
                    location=item.get("candidate_required_location", "Remote"),
                )
            )
    except requests.RequestException as exc:
        print(f"{NAME}: error - {exc}")
    report(NAME, jobs)
    return jobs
