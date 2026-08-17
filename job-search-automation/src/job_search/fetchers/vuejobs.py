"""VueJobs RSS feed."""

from __future__ import annotations

import requests

from ..config import AppConfig
from ..models import JobListing
from .base import DEFAULT_TIMEOUT, fetch_rss_items, is_senior, report, rss_text

NAME = "VueJobs"
FEED_URL = "https://vuejobs.com/posts"


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
                    company="",
                    url=rss_text(item, "link"),
                    description=rss_text(item, "description"),
                    tags=["Vue.js"],
                    location="Remote",
                )
            )
    except (requests.RequestException, SyntaxError) as exc:
        print(f"{NAME}: error - {exc}")
    report(NAME, jobs)
    return jobs
