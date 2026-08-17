"""Shared helpers for provider fetchers.

Each provider module (remoteok.py, remotive.py, ...) exposes a single
function: `fetch(cfg: AppConfig) -> list[JobListing]`. That's the whole
contract — adding a new provider means adding a new module and registering
it in fetchers/__init__.py, without touching any existing provider.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import requests

from ..config import AppConfig
from ..models import JobListing

DEFAULT_TIMEOUT = 15


def matches_any(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)


def is_senior(title: str, cfg: AppConfig) -> bool:
    return matches_any(title.lower(), cfg.keywords.seniority)


def is_ai_related(title: str, cfg: AppConfig) -> bool:
    return matches_any(title.lower(), cfg.keywords.ai)


def split_title_and_company(raw_title: str) -> tuple[str, str]:
    """RSS feeds often format titles as 'Role at Company'."""
    if " at " in raw_title:
        title, _, company = raw_title.partition(" at ")
        return title, company
    return raw_title, ""


def report(name: str, jobs: list[JobListing]) -> None:
    print(f"{name}: {len(jobs)} listings")


def fetch_rss_items(url: str, timeout: int = DEFAULT_TIMEOUT) -> list[ET.Element]:
    """Fetch an RSS feed and return its <item> elements. Raises on HTTP errors."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    return root.findall(".//item")


def rss_text(item: ET.Element, tag: str) -> str:
    elem = item.find(tag)
    return (elem.text or "") if elem is not None else ""
