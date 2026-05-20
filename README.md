# flashcards

AI-native flashcards. A tiny web app that helps you (and your team) learn the vocabulary of working with LLMs — **CLI**, **MCP**, **token**, **context window**, **RAG**, **agent**, **embedding**, **fine-tuning**, and ~20 more. Click a card to flip it; search to filter live.

**Stack:** FastAPI + HTMX + SQLite. One Python process. No build step. No JavaScript framework. Ships with a seed deck so it's useful the moment you start it.

## Quick start

```bash
# clone, then:
uv sync
uv run python scripts/init_db.py   # creates ./data/flashcards.db + seeds ~25 AI terms
uv run python -m flashcards        # serves http://localhost:8000
```

Open <http://localhost:8000>, pick a deck, click a card. The search box uses HTMX to filter the grid live.

## Tests

```bash
uv run pytest -ra            # unit + API + view tests
uv run ruff check .          # lint
uv run ruff format --check . # format check
uv run mypy src              # type-check
```

## Docker

```bash
docker compose up --build
```

The SQLite file persists at `./data/flashcards.db` via a mounted volume; the container restarts cleanly without losing cards.

## Adding cards

Two ways:

**CLI** (no auth, local only):

```bash
uv run python scripts/add_card.py \
  --deck ai-native \
  --term "Prompt injection" \
  --definition "An attack where untrusted input rewrites a model's instructions." \
  --tag patterns --tag safety
```

**HTTP** (requires the `X-Admin-Token` header, matched against the `ADMIN_TOKEN` env var):

```bash
export ADMIN_TOKEN=changeme
curl -X POST http://localhost:8000/api/cards \
  -H "X-Admin-Token: $ADMIN_TOKEN" \
  -H "content-type: application/json" \
  -d '{
        "term": "Prompt injection",
        "definition": "An attack where untrusted input rewrites a model'\''s instructions.",
        "deck": "ai-native",
        "tags": ["patterns", "safety"]
      }'
```

Without the token, the endpoint returns `401`.

## Configuration

All settings read from environment variables (prefix `FLASHCARDS_`):

| Variable                 | Default                      | Meaning                                    |
| ------------------------ | ---------------------------- | ------------------------------------------ |
| `FLASHCARDS_DB_PATH`     | `./data/flashcards.db`       | SQLite file path                           |
| `FLASHCARDS_ADMIN_TOKEN` | *(unset → admin disabled)*   | Token required on `POST /api/cards`        |
| `FLASHCARDS_HOST`        | `0.0.0.0`                    | uvicorn bind host                          |
| `FLASHCARDS_PORT`        | `8000`                       | uvicorn bind port                          |
| `FLASHCARDS_SEED_ON_START` | `true`                     | Seed the DB on startup if it's empty       |

## Deploy

- **Fly.io:** `fly launch --no-deploy && fly deploy` — the included Dockerfile is fly-compatible.
- **Railway / Render:** point at the repo; both auto-detect the Dockerfile.

## API

| Method | Path                  | Description                                      |
| -----: | --------------------- | ------------------------------------------------ |
|    GET | `/`                   | Deck list + global search                        |
|    GET | `/decks/{slug}`       | Card grid for one deck                           |
|    GET | `/api/decks`          | JSON list of decks                               |
|    GET | `/api/cards`          | JSON list; `?q=`, `?tag=`, `?deck=`, `?format=html` |
|    GET | `/api/cards/{id}`     | JSON single card                                 |
|   POST | `/api/cards`          | Create card (requires `X-Admin-Token`)           |
|    GET | `/healthz`            | Health check                                     |

## License

MIT — see [LICENSE](LICENSE).
