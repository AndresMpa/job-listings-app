"""RemoteOK public API."""

from __future__ import annotations

import requests

from ..config import AppConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, is_ai_related, is_senior, report

NAME = "RemoteOK"
API_URL = "https://remoteok.com/api"


def fetch(cfg: AppConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    try:
        resp = requests.get(
            API_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT
        )
        resp.raise_for_status()
        for item in resp.json():
            if not isinstance(item, dict) or "id" not in item:
                continue
            title = item.get("position", "")
            if not (is_senior(title, cfg) or is_ai_related(title, cfg)):
                continue
            jobs.append(
                JobListing(
                    source=NAME,
                    title=title,
                    company=item.get("company", ""),
                    url=item.get("url", ""),
                    description=item.get("description", "") or "",
                    tags=item.get("tags", []) or [],
                    salary=item.get("salary") or None,
                    location=item.get("location", "Remote"),
                )
            )
    except requests.RequestException as exc:
        print(f"{NAME}: error - {exc}")
    report(NAME, jobs)
    return jobs
