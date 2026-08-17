"""Arbeitnow public API."""

from __future__ import annotations

import requests

from ..config import AppConfig, KeywordsConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, is_senior, report

NAME = "Arbeitnow"
API_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch(cfg: AppConfig, prefilter: KeywordsConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    try:
        resp = requests.get(API_URL, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        for item in resp.json().get("data", []):
            if not item.get("remote"):
                continue
            title = item.get("title", "")
            if not is_senior(title, prefilter):
                continue
            jobs.append(
                JobListing(
                    source=NAME,
                    title=title,
                    company=item.get("company_name", ""),
                    url=item.get("url", ""),
                    description=item.get("description", "") or "",
                    tags=item.get("tags", []) or [],
                    location="Remote",
                )
            )
    except requests.RequestException as exc:
        print(f"{NAME}: error - {exc}")
    report(NAME, jobs)
    return jobs
