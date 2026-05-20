from __future__ import annotations

import contextlib
import json
import sqlite3
from importlib import resources
from pathlib import Path
from typing import Any

from .models import CardCreate
from .repo import count_cards, create_card, get_or_create_deck


def _load_seed_json() -> dict[str, Any]:
    # why: in a built wheel the file is packaged under flashcards/_data/; in a checkout
    # it lives at the repo's assets/. Try the package path first, fall back to the repo path.
    text: str | None = None
    with contextlib.suppress(FileNotFoundError, ModuleNotFoundError):
        text = resources.files("flashcards").joinpath("_data/seed_cards.json").read_text("utf-8")
    if text is None:
        repo_path = Path(__file__).resolve().parents[2] / "assets" / "seed_cards.json"
        text = repo_path.read_text("utf-8")
    data: dict[str, Any] = json.loads(text)
    return data


def run(conn: sqlite3.Connection, *, force: bool = False) -> int:
    if not force and count_cards(conn) > 0:
        return 0
    data = _load_seed_json()
    added = 0
    for deck in data["decks"]:
        get_or_create_deck(conn, slug=deck["slug"], name=deck["name"])
    for raw in data["cards"]:
        existing = conn.execute(
            "SELECT id FROM cards WHERE term = ? AND deck_id = (SELECT id FROM decks WHERE slug = ?)",
            (raw["term"], raw["deck"]),
        ).fetchone()
        if existing is not None:
            continue
        create_card(conn, CardCreate(**raw))
        added += 1
    return added
