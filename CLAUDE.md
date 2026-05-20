# CLAUDE.md

## Project

**flashcards** — a small FastAPI + HTMX + SQLite web app for browsing AI-native definitions (CLI, MCP, token, RAG, agent, etc.). One Python process serves both the API and server-rendered HTML; HTMX handles interactivity without a JS build step. SQLite ships in the repo for zero infra.

Read this file before editing — it documents non-obvious conventions.

## Stack

- **Python ≥3.11** — runs on 3.11/3.12/3.13
- **FastAPI** (async-capable, sync handlers used throughout — the DB is local SQLite)
- **Jinja2** — server-rendered templates with HTMX partials
- **HTMX 2.x** via CDN — no JS toolchain
- **Tailwind Play CDN** — no CSS build step
- **stdlib `sqlite3`** — no SQLAlchemy. `isolation_level=None`, explicit BEGIN/COMMIT, WAL journal, FTS5 for search
- **Pydantic v2** — request/response models
- **pydantic-settings** — env-driven config
- **uv** for env + lock; **hatchling** as build backend
- **ruff + mypy + pytest** — same shape as the workspace's other Python projects

## Conventions

**Database access:**
- Every DB connection goes through `db.connect()`. It sets `foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout=5000`. Don't call `sqlite3.connect()` directly.
- The schema lives in `src/flashcards/schema.sql`. The FTS5 virtual table `cards_fts` is kept in sync by triggers — don't write to `cards_fts` directly.
- Tests get a fresh DB per test via the `db` fixture in `tests/conftest.py`. No shared state, no mocking.

**HTMX content negotiation:**
- `GET /api/cards` returns JSON by default, an HTML grid partial when `?format=html` is set or when `HX-Request: true` is present. The function returns one shape; FastAPI's `Response` is the right boundary.

**Admin auth:**
- `POST /api/cards` is gated by a `X-Admin-Token` header compared against `settings.admin_token`. If `admin_token` is unset, the endpoint always returns 401 — opt-in, never accidentally open.

**Seed data:**
- `assets/seed_cards.json` is the canonical source for the starter deck. `seed.run()` is idempotent — runs on startup if `FLASHCARDS_SEED_ON_START=true` and the DB has zero cards.

**Comments:**
- Default to no comments. Only add a `# why:` line when the reasoning isn't obvious from the names.

## Architecture

```
src/flashcards/
├── __main__.py     # uvicorn launcher
├── app.py          # FastAPI factory + route registration + lifespan (schema apply + seed)
├── config.py       # pydantic-settings Settings(env_prefix="FLASHCARDS_")
├── db.py           # sqlite3 connection factory, schema-apply helper
├── schema.sql      # decks, cards, tags, card_tags, cards_fts + triggers
├── models.py       # Pydantic models: Deck, Card, CardCreate, Tag
├── repo.py         # CRUD over sqlite — pure functions, take a Connection
├── api.py          # APIRouter for /api/*
├── views.py        # APIRouter for HTML routes
├── seed.py         # idempotent loader for assets/seed_cards.json
├── templates/      # base, index, deck, _card_grid, _card, admin
└── static/         # style.css, flip.js
```

**Layer rules:**
- `models` has zero project deps.
- `db` imports nothing project (only stdlib + `config`).
- `repo` imports `db` + `models`.
- `api`, `views` import `repo` + `models` + `config`.
- `seed` imports `repo`.
- `app` is the composition root.

## Run / test commands

```bash
uv sync
uv run python scripts/init_db.py
uv run python -m flashcards
uv run pytest -ra
uv run ruff check . && uv run ruff format --check .
uv run mypy src
```
