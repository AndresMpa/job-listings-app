"""LLM-backed scoring and outreach drafting, via a local Ollama instance."""

from __future__ import annotations

import json
import re

import requests

from .config import AppConfig
from .models import JobListing

SCORE_PROMPT = """Evaluate this job posting for a Senior AI Engineer.

Respond ONLY with JSON:
{{"fit": <1-10>, "income": <1-10>, "reason": "<short explanation>"}}

CANDIDATE PROFILE:
{profile}

POSTING:
Title: {title}
Company: {company}
Location: {location}
Salary: {salary}
Description: {description}

INCOME CRITERIA (1-10):
- 9-10: USA, 250k+ USD
- 7-8: USA/UK, 150-250k
- 5-6: Europe, 100-150k
- <5: low or unspecified
"""

OUTREACH_PROMPT = """Write a short outreach message in English (max 100 words).

CANDIDATE PROFILE:
{profile}

POSTING:
{title} @ {company}

Mention:
- The candidate's flagship open-source project (see profile)
- Their technical stack
- Genuine interest in the company
- A [Name] placeholder for the signature
"""


class OllamaClient:
    """Thin wrapper around the Ollama /api/generate endpoint."""

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg

    def check_connection(self) -> bool:
        base_url = self.cfg.ollama.url.replace("/api/generate", "")
        try:
            resp = requests.get(f"{base_url}/api/tags", timeout=5)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"Could not reach Ollama at {base_url}: {exc}")
            return False

        model_names = [m.get("name") for m in resp.json().get("models", [])]
        if not any(self.cfg.ollama.model in name for name in model_names):
            print(f"Model '{self.cfg.ollama.model}' not found. Available: {', '.join(model_names)}")
            return False

        print(f"Connected to Ollama, model '{self.cfg.ollama.model}' is available.")
        return True

    def _generate(self, prompt: str) -> str:
        try:
            resp = requests.post(
                self.cfg.ollama.url,
                json={"model": self.cfg.ollama.model, "prompt": prompt, "stream": False},
                timeout=self.cfg.ollama.timeout,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            print(f"  Ollama timed out after {self.cfg.ollama.timeout}s - skipping.")
            return ""
        except requests.RequestException as exc:
            print(f"  Ollama error: {exc}")
            return ""

    def score_job(self, job: JobListing) -> None:
        prompt = SCORE_PROMPT.format(
            profile=self.cfg.profile,
            title=job.title,
            company=job.company,
            location=job.location,
            salary=job.salary or "unspecified",
            description=job.description[:1000],
        )
        raw = self._generate(prompt)
        if not raw:
            job.fit_score = job.income_score = job.score = 0
            job.reasoning = "Timeout"
            return

        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            parsed = json.loads(match.group(0)) if match else {}
            job.fit_score = int(parsed.get("fit", 0))
            job.income_score = int(parsed.get("income", 0))
            job.score = int(
                job.fit_score * self.cfg.scoring.fit_weight
                + job.income_score * self.cfg.scoring.income_weight
            )
            job.reasoning = parsed.get("reason", "")
        except (ValueError, AttributeError) as exc:
            print(f"  Could not parse score response: {exc}")
            job.fit_score = job.income_score = job.score = 0
            job.reasoning = "Error"

    def draft_outreach(self, job: JobListing) -> None:
        prompt = OUTREACH_PROMPT.format(profile=self.cfg.profile, title=job.title, company=job.company)
        job.outreach_draft = self._generate(prompt)
