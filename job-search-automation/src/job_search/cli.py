"""Pipeline orchestration: fetch -> dedupe -> filter -> score -> report."""

from __future__ import annotations

import argparse
import sys
import time

from .config import AppConfig, load_config
from .fetchers import fetch_all
from .filters import passes_filter
from .models import JobListing
from .reports import write_csv_report, write_markdown_report
from .scoring import OllamaClient


def deduplicate(jobs: list[JobListing]) -> list[JobListing]:
    seen: set[str] = set()
    unique: list[JobListing] = []
    for job in jobs:
        if job.url:
            if job.url in seen:
                continue
            seen.add(job.url)
        unique.append(job)
    return unique


def run(cfg: AppConfig) -> list[JobListing]:
    client = OllamaClient(cfg)
    print("Checking Ollama connection...")
    if not client.check_connection():
        sys.exit(1)

    print("\nFetching job listings...")
    all_jobs = fetch_all(cfg)
    unique = deduplicate(all_jobs)
    print(f"\n{len(all_jobs)} listings fetched, {len(unique)} unique")

    filtered = [j for j in unique if passes_filter(j, cfg)]
    print(f"{len(filtered)} passed keyword filtering")
    if not filtered:
        print("No relevant listings found.")
        return []

    print(f"\nScoring with {cfg.ollama.model} (timeout {cfg.ollama.timeout}s)...")
    for i, job in enumerate(filtered, 1):
        print(f"[{i}/{len(filtered)}] {job.title[:40]} @ {job.company[:20]}")
        client.score_job(job)
        if (job.score or 0) >= cfg.scoring.min_score_to_keep:
            client.draft_outreach(job)
        time.sleep(0.5)

    kept = [j for j in filtered if (j.score or 0) >= cfg.scoring.min_score_to_keep]
    kept.sort(key=lambda j: (j.income_score or 0), reverse=True)
    return kept


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch, score and report high-value remote job listings.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to config.yaml (default: ./config.yaml)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    kept = run(cfg)
    if not kept:
        return

    write_csv_report(kept, cfg.output.csv_path)
    write_markdown_report(kept, cfg.output.md_path)
    print(f"\n{len(kept)} listings saved to:\n  - {cfg.output.csv_path}\n  - {cfg.output.md_path}")

    if cfg.database.url:
        from . import db

        saved = db.save_jobs(kept, cfg.database)
        print(f"  - {saved} rows upserted into Postgres")


if __name__ == "__main__":
    main()
