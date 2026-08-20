"""Data models shared across the package."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class JobListing:
    """A single job posting, enriched in-place as it moves through the pipeline."""

    source: str
    title: str
    company: str
    url: str
    description: str
    tags: list[str] = field(default_factory=list)
    salary: str | None = None
    location: str = ""
    posted_date: str = ""

    # Populated by the scoring stage
    fit_score: int | None = None
    income_score: int | None = None
    score: int | None = None
    reasoning: str | None = None
    outreach_draft: str | None = None

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
