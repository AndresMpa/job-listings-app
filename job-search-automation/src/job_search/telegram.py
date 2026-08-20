"""Telegram delivery for each profile's job digest.

Talks to the Telegram Bot API directly over HTTPS — no extra dependency,
`requests` is already required by the rest of the package.

Design mirrors the rest of the config: one bot token shared by the whole
deployment (TELEGRAM_BOT_TOKEN env var — same pattern as OLLAMA_URL/
DATABASE_URL), one chat_id per profile (profiles/<n>.yaml ->
telegram.chat_id) so each person's digest lands in their own chat. A bot
token is a deployment secret, not per-candidate data, so it does not live
in profiles/*.yaml.

Create a bot via @BotFather to get a token, then message your bot once and
hit https://api.telegram.org/bot<token>/getUpdates to read back your
chat_id.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests

from .config import ProfileConfig
from .models import JobListing

TELEGRAM_API_BASE = "https://api.telegram.org"
MAX_MESSAGE_LEN = 4096  # Telegram's hard limit per sendMessage call
SUMMARY_JOB_LIMIT = 10  # how many jobs to list inline before pointing at the file


def _bot_token() -> str | None:
    return os.environ.get("TELEGRAM_BOT_TOKEN") or None


def _build_summary(profile: ProfileConfig, jobs: list[JobListing]) -> str:
    """Short plain-text digest for the chat message; the full report goes
    along as an attached file, so this only needs to be a teaser."""
    plural = "" if len(jobs) == 1 else "es"
    lines = [f"\U0001f4b0 {profile.name}: {len(jobs)} new match{plural}", ""]
    for j in jobs[:SUMMARY_JOB_LIMIT]:
        lines.append(f"[{j.score}/10] {j.title} @ {j.company}\n{j.url}")
    if len(jobs) > SUMMARY_JOB_LIMIT:
        lines.append(f"\n…and {len(jobs) - SUMMARY_JOB_LIMIT} more in the attached report.")
    return "\n\n".join(lines)[:MAX_MESSAGE_LEN]


def send_profile_digest(profile: ProfileConfig, jobs: list[JobListing], md_path: Path) -> bool:
    """Sends `profile`'s digest to its configured Telegram chat, if wired up.

    Returns True only if a message was actually sent. Every "not configured"
    case (disabled, no chat_id, no bot token, nothing to send) is a silent
    no-op — this must never be why a run fails. Network/API errors are
    caught and logged the same way, so a Telegram outage can't take down a
    scan that otherwise completed fine.
    """
    if not profile.telegram.enabled:
        return False
    if not profile.telegram.chat_id:
        print(f"[{profile.name}] Telegram enabled but no chat_id set — skipping")
        return False
    if not jobs:
        return False
    token = _bot_token()
    if not token:
        print(f"[{profile.name}] Telegram enabled but TELEGRAM_BOT_TOKEN is not set — skipping")
        return False

    chat_id = profile.telegram.chat_id
    base = f"{TELEGRAM_API_BASE}/bot{token}"

    try:
        resp = requests.post(
            f"{base}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": _build_summary(profile, jobs),
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        resp.raise_for_status()

        if md_path.exists():
            with md_path.open("rb") as f:
                resp = requests.post(
                    f"{base}/sendDocument",
                    data={"chat_id": chat_id, "caption": f"{profile.name} — full digest"},
                    files={"document": (md_path.name, f, "text/markdown")},
                    timeout=60,
                )
                resp.raise_for_status()

        print(f"[{profile.name}] Telegram digest sent to chat {chat_id}")
        return True
    except requests.RequestException as exc:
        print(f"[{profile.name}] Telegram send failed: {exc}")
        return False
