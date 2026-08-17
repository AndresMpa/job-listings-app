"""Data models shared across the package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobListing:
    """A single job posting, enriched in-place as it moves through the pipeline."""

    source: str
    title: str
    company: str
    url: str
    description: str
    tags: list[str] = field(default_factory=list)
    salary: Optional[str] = None
    location: str = ""
    posted_date: str = ""

    # Populated by the scoring stage
    fit_score: Optional[int] = None
    income_score: Optional[int] = None
    score: Optional[int] = None
    reasoning: Optional[str] = None
    outreach_draft: Optional[str] = None

    @property
    def haystack(self) -> str:
        """Lowercase blob used for keyword matching."""
        return " ".join(
            [
                self.title.lower(),
                self.company.lower(),
                self.description.lower(),
                " ".join(self.tags).lower(),
            ]
        )
