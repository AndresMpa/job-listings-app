"""Greenhouse-hosted company career boards (public JSON API, no auth needed).

Companies are configured in config.yaml under `greenhouse.companies` - add a
new company by adding one entry there, no code changes needed here. Verified
in the POC: Celonis and Databricks both work; Snowflake looked like a
Greenhouse company by naming convention but has actually migrated to a
different platform (its board_token 404s) - don't add companies here without
confirming their board exists at https://boards.greenhouse.io/<token> first.
"""

from __future__ import annotations

import requests

from ..config import AppConfig, KeywordsConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, is_ai_related, is_senior, report

NAME = "Greenhouse"
API_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


def fetch(cfg: AppConfig, prefilter: KeywordsConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    for company in cfg.greenhouse.companies:
        try:
            resp = requests.get(
                API_URL.format(token=company.board_token),
                params={"content": "true"},
                timeout=DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"{NAME}:{company.name} - error - {exc}")
            continue  # a single misconfigured company shouldn't kill the run

        for item in resp.json().get("jobs", []):
            title = item.get("title", "")
            if not (is_senior(title, prefilter) or is_ai_related(title, prefilter)):
                continue
            jobs.append(
                JobListing(
                    source=f"{NAME}:{company.name}",
                    title=title,
                    company=company.name,
                    url=item.get("absolute_url", ""),
                    description=item.get("content", "") or "",
                    location=(item.get("location") or {}).get("name", ""),
                    posted_date=(item.get("updated_at") or "")[:10],
                )
            )
    report(NAME, jobs)
    return jobs
