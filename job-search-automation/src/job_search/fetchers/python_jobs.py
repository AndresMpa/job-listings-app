"""Python.org Jobs RSS feed."""

from __future__ import annotations

import requests

from ..config import AppConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, fetch_rss_items, is_senior, report, rss_text

NAME = "PythonJobs"
FEED_URL = "https://www.python.org/jobs/feed/rss/"


def fetch(cfg: AppConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    try:
        for item in fetch_rss_items(FEED_URL, DEFAULT_TIMEOUT):
            title = rss_text(item, "title")
            if not title or not is_senior(title, cfg):
                continue
            jobs.append(
                JobListing(
                    source=NAME,
                    title=title,
                    company="",  # python.org rarely includes the company in the feed
                    url=rss_text(item, "link"),
                    description=rss_text(item, "description"),
                    tags=["Python"],
                    location="Remote",
                )
            )
    except (requests.RequestException, SyntaxError) as exc:
        print(f"{NAME}: error - {exc}")
    report(NAME, jobs)
    return jobs
