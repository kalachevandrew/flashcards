from __future__ import annotations

from flashcards.config import get_settings
from flashcards.db import apply_schema, connect
from flashcards.seed import run as run_seed


def main() -> None:
    settings = get_settings()
    print(f"Using DB: {settings.db_path}")
    with connect(settings.db_path) as conn:
        apply_schema(conn)
        added = run_seed(conn)
        print(f"Seeded {added} new cards.")


if __name__ == "__main__":
    main()
