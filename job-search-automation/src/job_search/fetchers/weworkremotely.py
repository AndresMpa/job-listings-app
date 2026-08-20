"""We Work Remotely RSS feeds. Categories are configurable in config.yaml."""

from __future__ import annotations

import requests

from ..config import AppConfig, KeywordsConfig
from ..models import JobListing
from .base import (
    DEFAULT_TIMEOUT,
    fetch_rss_items,
    is_senior,
    report,
    rss_text,
    split_title_and_company,
)

NAME = "WeWorkRemotely"
FEED_URL = "https://weworkremotely.com/categories/{category}.rss"


def fetch(cfg: AppConfig, prefilter: KeywordsConfig) -> list[JobListing]:
    jobs: list[JobListing] = []
    for category in cfg.weworkremotely.categories:
        try:
            items = fetch_rss_items(FEED_URL.format(category=category), DEFAULT_TIMEOUT)
        except (requests.RequestException, SyntaxError):
            continue  # a single broken category feed shouldn't kill the run

        for item in items:
            raw_title = rss_text(item, "title")
            if not raw_title or not is_senior(raw_title, prefilter):
                continue
            title, company = split_title_and_company(raw_title)
            jobs.append(
                JobListing(
                    source=NAME,
                    title=title,
                    company=company,
                    url=rss_text(item, "link"),
                    description=rss_text(item, "description"),
                    location="Remote",
                )
            )
    report(NAME, jobs)
    return jobs
