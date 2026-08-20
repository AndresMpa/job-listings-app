"""Report writers: CSV for spreadsheets, Markdown for a readable digest."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from .models import JobListing

CSV_HEADER = ["Score", "Fit", "Income", "Title", "Company", "Salary", "URL"]


def write_csv_report(jobs: list[JobListing], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for j in jobs:
            writer.writerow(
                [
                    j.score,
                    j.fit_score,
                    j.income_score,
                    j.title,
                    j.company,
                    j.salary or "",
                    j.url,
                ]
            )


def _emoji_for(job: JobListing) -> str:
    income = job.income_score or 0
    if income >= 8:
        return "🟢🟢🟢"
    if income >= 6:
        return "🟢🟢"
    return "🟢"


def write_markdown_report(jobs: list[JobListing], path: Path) -> None:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 💰 High-Value Job Matches — {now}",
        "",
        f"Total: **{len(jobs)}** matches",
        "",
        "---",
        "",
    ]

    for j in jobs:
        lines += [
            f"## {_emoji_for(j)} [{j.score}/10] {j.title}",
            "",
            f"- **Company:** {j.company}",
            f"- **Fit:** {j.fit_score}/10 | **Income:** {j.income_score}/10",
            f"- **Salary:** {j.salary or 'unspecified'}",
            f"- **Link:** [{j.url}]({j.url})",
            "",
            f"**Analysis:** {j.reasoning}",
            "",
        ]
        if j.outreach_draft:
            lines += [
                "**Outreach:**",
                "> " + j.outreach_draft.replace("\n", "\n> "),
                "",
            ]
        lines += ["---", ""]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
