"""Cheap keyword filtering, applied before the (expensive) LLM scoring stage."""

from __future__ import annotations

from .config import KeywordsConfig
from .fetchers.base import matches_any
from .models import JobListing


def passes_filter(job: JobListing, keywords: KeywordsConfig) -> bool:
    """Reject non-technical, low-value, or off-target postings early.

    `keywords` comes from a single profile (profiles/<name>.yaml) — each
    profile keeps its own target/exclude/tech lists.
    """
    haystack = job.haystack

    if not matches_any(haystack, keywords.tech):
        return False
    if matches_any(haystack, keywords.exclude):
        return False
    if not (
        matches_any(haystack, keywords.seniority) or matches_any(haystack, keywords.ai)
    ):
        return False
    return matches_any(haystack, keywords.target)
