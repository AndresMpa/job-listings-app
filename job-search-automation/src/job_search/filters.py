"""Cheap keyword filtering, applied before the (expensive) LLM scoring stage."""

from __future__ import annotations

from .config import AppConfig
from .fetchers.base import matches_any
from .models import JobListing


def passes_filter(job: JobListing, cfg: AppConfig) -> bool:
    """Reject non-technical, low-value, or off-target postings early."""
    haystack = job.haystack
    kw = cfg.keywords

    if not matches_any(haystack, kw.tech):
        return False
    if matches_any(haystack, kw.exclude):
        return False
    if not (matches_any(haystack, kw.seniority) or matches_any(haystack, kw.ai)):
        return False
    if not matches_any(haystack, kw.target):
        return False
    return True
