# job-search-automation

Fetches remote job listings from several public sources, filters them down
to senior/AI-relevant postings with cheap keyword rules, scores the survivors
with a local LLM via [Ollama](https://ollama.com), and writes a CSV +
Markdown digest of the best matches — **for one or several candidate
profiles at once**.

Originally a single ~660-line script; split into a small package so each
concern (fetching, filtering, scoring, reporting) lives in its own module.
System-wide tunables live in `config.yaml`; who you're searching jobs *for*
lives in `profiles/`, one YAML file per person or role.

## Profiles: searching for more than one person

`config.yaml` and `profiles/*.yaml` are deliberately separate:

- **`config.yaml`** — settings that apply to every run regardless of who's
  searching: the Ollama connection, which providers are enabled, scoring
  weights, the Postgres URL. See `config.yaml.example`.
- **`profiles/<name>.yaml`** — one file per candidate: the free-text profile
  fed to the LLM and that person's own keyword lists (`target`, `exclude`,
  `seniority`, `ai`, `tech`). See `profiles/profile.yaml.example`.

A run fetches every source **once** (network calls are expensive/rate
limited, so they're shared) and then filters + scores that same set of
listings independently for each profile. Each profile gets its own report
under `profiles/output/<name>/job_matches.{csv,md}` — nothing overwrites
anyone else's results, and each person's report is self-contained (handy
for a future step that, say, sends `profiles/output/andres/job_matches.md`
to Andres' Telegram chat and `profiles/output/maria/job_matches.md` to
Maria's — see `telegram:` in the profile schema, reserved but not wired up
yet).

```
profiles/
├── profile.yaml.example   # template — copy to profiles/<name>.yaml
├── andres.yaml            # gitignored — your own profiles
├── maria.yaml
└── output/
    ├── andres/
    │   ├── job_matches.csv
    │   └── job_matches.md
    └── maria/
        ├── job_matches.csv
        └── job_matches.md
```

## Project layout

```
job-search-automation/
├── main.py                      # entrypoint: python main.py
├── config.yaml.example          # documented SYSTEM config template — copy to config.yaml
├── profiles/
│   ├── profile.yaml.example     # documented PROFILE template — copy to profiles/<name>.yaml
│   └── output/                  # per-profile reports (gitignored, created at runtime)
├── requirements.txt
├── Dockerfile
└── src/job_search/
    ├── config.py                 # loads + validates config.yaml AND profiles/*.yaml
    ├── models.py                 # JobListing dataclass
    ├── filters.py                # keyword pre-filtering (passes_filter), per profile
    ├── scoring.py                # OllamaClient: score_job / draft_outreach, per profile
    ├── reports.py                # CSV + Markdown writers
    ├── cli.py                    # orchestration: fetch once → dedupe → (filter → score → report) per profile
    ├── db.py                     # Postgres persistence, rows keyed by (profile, url)
    ├── api.py                    # FastAPI app: /jobs, /config, /profiles, /run
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

Each fetcher module exposes one function —
`fetch(cfg, prefilter) -> list[JobListing]` — and is registered in
`fetchers/__init__.py`. `prefilter` is the union of every loaded profile's
`seniority`/`ai` keywords, used only for the cheap title-only pre-filter
inside each fetcher; the full per-profile filter runs afterward. Adding a
new source means adding one module + one registry line; no existing fetcher
needs to change.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.yaml.example config.yaml
cp profiles/profile.yaml.example profiles/andres.yaml   # one per person you're searching for
```

Edit `config.yaml` and each `profiles/<name>.yaml` (see field references
below), then:

```bash
python main.py                     # runs every profile in profiles/
python main.py -p andres           # runs just profiles/andres.yaml
python main.py -p andres -p maria  # runs a specific subset
python main.py -c other.yaml       # a different system config path
```

You need a running Ollama instance with the configured model pulled, e.g.
`ollama pull qwen2.5:14b`.

## Docker

The simplest path is `docker-compose.yml`, which brings up Postgres and the
API together:

```bash
cp config.yaml.example config.yaml            # edit as needed
cp profiles/profile.yaml.example profiles/andres.yaml
docker compose up -d                          # starts db + api (http://localhost:8000)
docker compose run --rm api python main.py    # one-off scan, all profiles, persists to Postgres
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
  -v "$(pwd)/profiles:/app/profiles" \
  --add-host=host.docker.internal:host-gateway \
  job-search-automation
```

## HTTP API

Served by `job_search.api:app` (`docker compose up`, or locally with
`uvicorn job_search.api:app --reload`):

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check. |
| `GET` | `/jobs?profile=&min_score=&limit=&offset=` | Scored listings from Postgres, best `score` first. Omit `profile` to see every profile's matches. Requires `database.url`. |
| `GET` | `/config` | Current system `config.yaml`, as JSON. |
| `PUT` | `/config` | Replaces `config.yaml`. Body is validated (round-tripped through `AppConfig`) before writing. |
| `GET` | `/profiles` | Every profile in `profiles/`, as JSON. |
| `GET` | `/profiles/{name}` | A single profile. 404 if it doesn't exist. |
| `PUT` | `/profiles/{name}` | Creates or replaces `profiles/{name}.yaml`. Body is validated before writing. |
| `DELETE` | `/profiles/{name}` | Removes `profiles/{name}.yaml`. |
| `POST` | `/run?profile=` | Runs the pipeline in the background for one profile, or every profile if omitted. 409 if a run is already in progress. |

This is what `job-listings-app`'s job list reads from — see that project's
README for the frontend side of the integration. The frontend's `/settings`
page currently only covers system settings (`/config`); a profiles-picker
UI on top of `/profiles` is a natural next step but isn't built yet.

## Configuration reference

### System (`config.yaml`, see `config.yaml.example`)

| Section | Key | Purpose |
|---|---|---|
| `ollama` | `url` | Ollama `/api/generate` endpoint. `null` = auto-detect (Docker host vs `localhost`). Overridable with the `OLLAMA_URL` env var. |
| | `model` | Model name to use for scoring/outreach (`OLLAMA_MODEL` env override). |
| | `timeout` | Request timeout in seconds (`OLLAMA_TIMEOUT` env override). |
| `providers` | `remoteok`, `remotive`, `weworkremotely`, `python_jobs`, `vuejobs`, `hackernews`, `arbeitnow` | Toggle each source on/off, for every profile. |
| `weworkremotely` | `categories` | RSS category slugs to query on WeWorkRemotely. |
| `scoring` | `min_score_to_keep` | Minimum weighted score (0-10) for a listing to make the final report. |
| | `fit_weight` / `income_weight` | Weights combined into the final score (`fit*fit_weight + income*income_weight`). |
| `output_base_dir` | — | Base directory for per-profile reports; each profile writes to `<output_base_dir>/<name>/`. Defaults to `profiles/output`. |
| `database` | `url` | Postgres URL. Empty disables persistence (CSV/Markdown only). |

`config.yaml` is gitignored.

### Per profile (`profiles/<name>.yaml`, see `profiles/profile.yaml.example`)

| Key | Purpose |
|---|---|
| `name` | Report folder name (`profiles/output/<name>/`); defaults to the filename if omitted. |
| `profile` | Free-text candidate profile injected into every LLM prompt. |
| `keywords.target` | A listing must match at least one to be considered at all. |
| `keywords.exclude` | A listing matching any of these is dropped outright. |
| `keywords.seniority` | Terms used to detect senior-level titles (per-provider pre-filter). |
| `keywords.ai` | Terms used to detect AI-related titles (per-provider pre-filter). |
| `keywords.tech` | A listing must match at least one to count as "technical". |
| `output.csv_filename` / `output.md_filename` | Report filenames within this profile's output folder. |
| `telegram.enabled` / `telegram.chat_id` | Reserved for a future step that pushes each profile's digest to Telegram. Not implemented yet. |

`profiles/*.yaml` are gitignored (only `profile.yaml.example` is tracked) —
they hold personal data (CV summary, keyword tuning).

## Pipeline

1. **Load** — `config.yaml` (system) plus every `profiles/*.yaml` (or just
   the ones passed with `-p`).
2. **Fetch** — once per run: each enabled provider in `fetchers/` hits its
   public API/RSS feed and does a cheap title-only pre-filter using the
   *union* of every loaded profile's senior/AI keywords.
3. **Dedupe** — by URL, once, across the whole fetched set.
4. For **each profile**, on that same shared set of listings:
   - **Filter** — `filters.passes_filter` applies that profile's own
     `target`/`exclude`/`tech` keyword rules.
   - **Score** — `scoring.OllamaClient` asks the local model for a
     fit/income score per listing (using that profile's text) and drafts
     outreach for anything above `scoring.min_score_to_keep`.
   - **Report** — `reports.write_csv_report` / `write_markdown_report` to
     `profiles/output/<name>/`.
   - **Persist** — if `database.url` is set, rows are upserted keyed by
     `(profile, url)`, so the same posting can carry a different score per
     profile without collisions.
