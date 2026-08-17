# job-search-automation

Fetches remote job listings from several public sources, filters them down
to senior/AI-relevant postings with cheap keyword rules, scores the survivors
with a local LLM via [Ollama](https://ollama.com), and writes a CSV +
Markdown digest of the best matches.

Originally a single ~660-line script; split into a small package so each
concern (fetching, filtering, scoring, reporting) lives in its own module and
every tunable lives in `config.yaml` instead of source code.

## Project layout

```
job-search-automation/
├── main.py                      # entrypoint: python main.py
├── config.yaml.example          # documented config template — copy to config.yaml
├── requirements.txt
├── Dockerfile
└── src/job_search/
    ├── config.py                 # loads + validates config.yaml
    ├── models.py                 # JobListing dataclass
    ├── filters.py                # keyword pre-filtering (passes_filter)
    ├── scoring.py                # OllamaClient: score_job / draft_outreach
    ├── reports.py                # CSV + Markdown writers
    ├── cli.py                    # pipeline orchestration (fetch → dedupe → filter → score → report)
    └── fetchers/
        ├── base.py               # shared helpers (RSS parsing, keyword matching)
        ├── remoteok.py
        ├── remotive.py
        ├── weworkremotely.py
        ├── python_jobs.py
        ├── vuejobs.py
        ├── hackernews.py
        └── arbeitnow.py
```

Each fetcher module exposes one function — `fetch(cfg) -> list[JobListing]`
— and is registered in `fetchers/__init__.py`. Adding a new source means
adding one module + one registry line; no existing fetcher needs to change.

Two more modules turn this from a script into a service:

- `db.py` — SQLAlchemy model + upsert/read helpers for Postgres.
- `api.py` — a small FastAPI app (`/jobs`, `/config`, `/run`) that the
  [job-listings-app](../job-listings-app) frontend talks to. See "HTTP API"
  below.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.yaml.example config.yaml
```

Edit `config.yaml` (see field reference below), then:

```bash
python main.py                 # uses ./config.yaml
python main.py -c other.yaml   # or a different path
```

You need a running Ollama instance with the configured model pulled, e.g.
`ollama pull qwen2.5:14b`.

## Docker

The simplest path is `docker-compose.yml`, which brings up Postgres and the
API together:

```bash
cp config.yaml.example config.yaml   # edit as needed
docker compose up -d          # starts db + api (http://localhost:8000)
docker compose run --rm api python main.py   # one-off scan, persists to Postgres
```

If Ollama runs in another container on a shared Docker network instead of
on the host, put the `api` service on that network too and set `ollama.url`
in `config.yaml` (or `OLLAMA_URL` in `docker-compose.yml`) to
`http://<ollama-service-name>:11434/api/generate` — no code change needed.

Manual `docker run` (no compose) still works for one-off scans:

```bash
docker build -t job-search-automation .
docker run --rm \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -v "$(pwd)/output:/app/output" \
  --add-host=host.docker.internal:host-gateway \
  job-search-automation
```

## HTTP API

Served by `job_search.api:app` (`docker compose up`, or locally with
`uvicorn job_search.api:app --reload`):

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check. |
| `GET` | `/jobs?min_score=&limit=&offset=` | Scored listings from Postgres, best `score` first. Requires `database.url`. |
| `GET` | `/config` | Current `config.yaml`, as JSON. |
| `PUT` | `/config` | Replaces `config.yaml`. Body is validated (round-tripped through `AppConfig`) before writing. |
| `POST` | `/run` | Runs the pipeline in the background (fetch → filter → score → persist). 409 if a run is already in progress. |

This is what `job-listings-app`'s `/settings` page and job list read from —
see that project's README for the frontend side of the integration.

## Configuration reference

All settings live in `config.yaml` (see `config.yaml.example` for the fully
commented version with defaults). Sections, top to bottom:

| Section | Key | Purpose |
|---|---|---|
| `ollama` | `url` | Ollama `/api/generate` endpoint. `null` = auto-detect (Docker host vs `localhost`). Overridable with the `OLLAMA_URL` env var. |
| | `model` | Model name to use for scoring/outreach (`OLLAMA_MODEL` env override). |
| | `timeout` | Request timeout in seconds (`OLLAMA_TIMEOUT` env override). |
| `profile` | — | Free-text candidate profile injected into every LLM prompt. |
| `keywords` | `target` | A listing must match at least one to be considered at all. |
| | `exclude` | A listing matching any of these is dropped outright. |
| | `seniority` | Terms used to detect senior-level titles (per-provider pre-filter). |
| | `ai` | Terms used to detect AI-related titles (per-provider pre-filter). |
| | `tech` | A listing must match at least one to count as "technical". |
| `providers` | `remoteok`, `remotive`, `weworkremotely`, `python_jobs`, `vuejobs`, `hackernews`, `arbeitnow` | Toggle each source on/off. |
| `weworkremotely` | `categories` | RSS category slugs to query on WeWorkRemotely. |
| `scoring` | `min_score_to_keep` | Minimum weighted score (0-10) for a listing to make the final report. |
| | `fit_weight` / `income_weight` | Weights combined into the final score (`fit*fit_weight + income*income_weight`). |
| `output` | `dir`, `csv_filename`, `md_filename` | Where reports are written. |

`config.yaml` is gitignored — it's meant to hold your personal profile and
keyword tuning, not to be committed.

## Pipeline

1. **Fetch** — each enabled provider in `fetchers/` hits its public API/RSS
   feed and does a cheap title-only pre-filter (senior or AI-related).
2. **Dedupe** — by URL.
3. **Filter** — `filters.passes_filter` applies the full keyword rules from
   `config.yaml`.
4. **Score** — `scoring.OllamaClient` asks the local model for a fit/income
   score per listing and drafts outreach for anything above
   `scoring.min_score_to_keep`.
5. **Report** — `reports.write_csv_report` / `write_markdown_report`.
