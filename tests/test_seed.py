from __future__ import annotations

import sqlite3

from flashcards.repo import count_cards
from flashcards.seed import run as run_seed


def test_seed_populates(db: sqlite3.Connection) -> None:
    added = run_seed(db)
    assert added > 0
    assert count_cards(db) == added


def test_seed_is_idempotent(db: sqlite3.Connection) -> None:
    first = run_seed(db)
    second = run_seed(db)
    assert first > 0
    assert second == 0
    assert count_cards(db) == first


def test_seed_force_skips_existing_terms(db: sqlite3.Connection) -> None:
    first = run_seed(db)
    forced = run_seed(db, force=True)
    assert first > 0
    assert forced == 0  # all terms already exist; per-row check prevents duplicates
    assert count_cards(db) == first
