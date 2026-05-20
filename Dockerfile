FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY assets ./assets
COPY scripts ./scripts
COPY README.md ./

RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

ENV PATH="/opt/venv/bin:$PATH" \
    FLASHCARDS_DB_PATH=/data/flashcards.db \
    FLASHCARDS_HOST=0.0.0.0 \
    FLASHCARDS_PORT=8000

RUN mkdir -p /data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

CMD ["python", "-m", "flashcards"]
