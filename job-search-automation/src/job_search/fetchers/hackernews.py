"""Hacker News "Who is hiring" jobstories, via the Firebase API."""

from __future__ import annotations

import requests

from ..config import AppConfig, KeywordsConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, is_senior, report, split_title_and_company

NAME = "HackerNews"
JOB_STORIES_URL = "https://hacker-news.firebaseio.com/v0/jobstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
MAX_ITEMS = 30


def fetch(cfg: AppConfig, prefilter: KeywordsConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    try:
        resp = requests.get(JOB_STORIES_URL, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        job_ids = resp.json()[:MAX_ITEMS]
    except requests.RequestException as exc:
        print(f"{NAME}: error - {exc}")
        return jobs

    for job_id in job_ids:
        try:
            resp = requests.get(ITEM_URL.format(item_id=job_id), timeout=10)
            resp.raise_for_status()
            item = resp.json()
        except requests.RequestException:
            continue

        if not item or not item.get("title") or item.get("dead"):
            continue
        raw_title = item["title"]
        if not is_senior(raw_title, prefilter):
            continue

        title, company = split_title_and_company(raw_title)
        jobs.append(
            JobListing(
                source=NAME,
                title=title,
                company=company,
                url=item.get("url", f"https://news.ycombinator.com/item?id={job_id}"),
                description=item.get("text", "") or "",
                tags=["YC", "Startup"],
                location="Remote (US Timezone)",
            )
        )
    report(NAME, jobs)
    return jobs
