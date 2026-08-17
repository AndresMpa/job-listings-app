"""Loads and validates config.yaml into typed, immutable config objects.

Every tunable that used to be a module-level constant in the original
single-file script now lives in config.yaml. See config.yaml.example
for the documented defaults.
"""

from __future__ import annotations

import os
import socket
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path("config.yaml")


def _detect_ollama_url() -> str:
    """Best-effort default when ollama.url is not set in config.yaml."""
    if os.path.exists("/.dockerenv"):
        try:
            socket.gethostbyname("host.docker.internal")
            return "http://host.docker.internal:11434/api/generate"
        except OSError:
            return "http://172.17.0.1:11434/api/generate"
    return "http://localhost:11434/api/generate"


@dataclass(frozen=True)
class OllamaConfig:
    url: str = field(default_factory=_detect_ollama_url)
    model: str = "qwen2.5:14b"
    timeout: int = 300


@dataclass(frozen=True)
class KeywordsConfig:
    target: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    seniority: list[str] = field(default_factory=list)
    ai: list[str] = field(default_factory=list)
    tech: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProvidersConfig:
    remoteok: bool = True
    remotive: bool = True
    weworkremotely: bool = True
    python_jobs: bool = True
    vuejobs: bool = True
    hackernews: bool = True
    arbeitnow: bool = True


@dataclass(frozen=True)
class WeWorkRemotelyConfig:
    categories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScoringConfig:
    min_score_to_keep: int = 6
    fit_weight: float = 0.4
    income_weight: float = 0.6


@dataclass(frozen=True)
class OutputConfig:
    dir: str = "."
    csv_filename: str = "job_matches.csv"
    md_filename: str = "job_matches.md"

    @property
    def csv_path(self) -> Path:
        return Path(self.dir) / self.csv_filename

    @property
    def md_path(self) -> Path:
        return Path(self.dir) / self.md_filename


@dataclass(frozen=True)
class DatabaseConfig:
    # Standard SQLAlchemy URL, e.g. postgresql+psycopg://user:pass@host:5432/jobs
    # Overridable at runtime with the DATABASE_URL env var (handy in Docker
    # Compose where the host differs per environment). Empty = DB disabled;
    # the CLI still writes CSV/Markdown only.
    url: str = ""


@dataclass(frozen=True)
class AppConfig:
    profile: str
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    keywords: KeywordsConfig = field(default_factory=KeywordsConfig)
    providers: ProvidersConfig = field(default_factory=ProvidersConfig)
    weworkremotely: WeWorkRemotelyConfig = field(default_factory=WeWorkRemotelyConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    def to_dict(self) -> dict[str, Any]:
        """JSON/YAML-serializable view, used by the settings API and save_config()."""
        return asdict(self)


def _section(raw: dict[str, Any], key: str, cls):
    return cls(**raw.get(key, {})) if raw.get(key) else cls()


def config_from_dict(raw: dict[str, Any]) -> AppConfig:
    """Build an AppConfig from a plain dict, applying the same env overrides
    that load_config() does. Used directly by the settings API when it
    receives a JSON body instead of reading a file.
    """
    ollama_raw = raw.get("ollama", {}) or {}
    ollama = OllamaConfig(
        url=os.environ.get("OLLAMA_URL") or ollama_raw.get("url") or _detect_ollama_url(),
        model=os.environ.get("OLLAMA_MODEL") or ollama_raw.get("model", "qwen2.5:14b"),
        timeout=int(os.environ.get("OLLAMA_TIMEOUT") or ollama_raw.get("timeout", 300)),
    )
    database_raw = raw.get("database", {}) or {}
    database = DatabaseConfig(url=os.environ.get("DATABASE_URL") or database_raw.get("url", ""))

    return AppConfig(
        profile=raw.get("profile", "").strip(),
        ollama=ollama,
        keywords=_section(raw, "keywords", KeywordsConfig),
        providers=_section(raw, "providers", ProvidersConfig),
        weworkremotely=_section(raw, "weworkremotely", WeWorkRemotelyConfig),
        scoring=_section(raw, "scoring", ScoringConfig),
        output=_section(raw, "output", OutputConfig),
        database=database,
    )


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    """Read config.yaml (falling back to defaults for any missing section)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Copy config.yaml.example to config.yaml and edit it."
        )
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return config_from_dict(raw)


def save_config(cfg: AppConfig, path: str | Path = DEFAULT_CONFIG_PATH) -> None:
    """Persist an AppConfig back to config.yaml (used by the settings API)."""
    path = Path(path)
    path.write_text(yaml.safe_dump(cfg.to_dict(), sort_keys=False, allow_unicode=True), encoding="utf-8")
