"""Workday-hosted company career boards (public internal JSON API, no auth).

Companies are configured in config.yaml under `workday.companies`. Unlike
Greenhouse, Workday has no predictable board-token-from-company-name
convention - tenant/site/wd_server must be read off a real job link the
company publishes, e.g.:

    https://cisco.wd1.myworkdayjobs.com/en-US/External/job/...
            ^tenant  ^wd_server        ^site

This module is registered and ready, but ships with an empty company list
and `providers.workday: false` by default (see config.yaml) until real
tenant/site values are confirmed for the companies you want - don't guess
them, a wrong value here fails differently than a wrong Greenhouse token
(Workday can return valid-looking empty JSON for some bad inputs too).

Workday sits behind Akamai bot management on many tenants - keep this
provider's company list short and avoid re-running it in a tight loop.
"""

from __future__ import annotations

import requests

from ..config import AppConfig, KeywordsConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, is_ai_related, is_senior, report

NAME = "Workday"
PAGE_SIZE = 20
MAX_PAGES = 10  # safety cap: 200 postings/company is plenty for this use case


def fetch(cfg: AppConfig, prefilter: KeywordsConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    for company in cfg.workday.companies:
        jobs.extend(_fetch_company(company, prefilter))
    report(NAME, jobs)
    return jobs


def _fetch_company(company, prefilter: KeywordsConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    base = f"https://{company.tenant}.{company.wd_server}.myworkdayjobs.com"
    url = f"{base}/wday/cxs/{company.tenant}/{company.site}/jobs"

    offset = 0
    for _ in range(MAX_PAGES):
        try:
            resp = requests.post(
                url,
                json={"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": ""},
                headers={"Accept": "application/json"},
                timeout=DEFAULT_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as exc:
            print(f"{NAME}:{company.name} - error - {exc}")
            break

        postings = data.get("jobPostings", [])
        if not postings:
            break

        for item in postings:
            title = item.get("title", "")
            if not (is_senior(title, prefilter) or is_ai_related(title, prefilter)):
                continue
            path = item.get("externalPath", "")
            jobs.append(
                JobListing(
                    source=f"{NAME}:{company.name}",
                    title=title,
                    company=company.name,
                    url=f"{base}/en-US/{company.site}{path}" if path else base,
                    description="",  # list endpoint doesn't include full description
                    location=item.get("locationsText", ""),
                    posted_date=item.get("postedOn", ""),
                )
            )

        offset += PAGE_SIZE
        if offset >= data.get("total", 0):
            break

    return jobs
