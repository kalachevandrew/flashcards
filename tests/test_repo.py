from __future__ import annotations

import sqlite3

from flashcards.models import CardCreate
from flashcards.repo import (
    count_cards,
    create_card,
    create_deck,
    get_card,
    get_deck_by_slug,
    list_cards,
    list_decks,
    list_tags,
)


def _seed_two(conn: sqlite3.Connection) -> None:
    create_deck(conn, slug="ai-native", name="AI-Native")
    create_deck(conn, slug="other", name="Other")
    create_card(
        conn,
        CardCreate(
            term="RAG",
            definition="Retrieval-augmented generation pattern.",
            deck="ai-native",
            tags=["patterns"],
        ),
    )
    create_card(
        conn,
        CardCreate(
            term="Embedding",
            definition="Vector representation of text.",
            deck="ai-native",
            tags=["models", "patterns"],
        ),
    )


def test_count_starts_at_zero(db: sqlite3.Connection) -> None:
    assert count_cards(db) == 0


def test_create_and_get_card(db: sqlite3.Connection) -> None:
    _seed_two(db)
    cards = list_cards(db)
    assert len(cards) == 2
    rag = next(c for c in cards if c.term == "RAG")
    fetched = get_card(db, rag.id)
    assert fetched is not None
    assert fetched.term == "RAG"
    assert "patterns" in fetched.tags


def test_search_by_term(db: sqlite3.Connection) -> None:
    _seed_two(db)
    hits = list_cards(db, q="rag")
    assert [c.term for c in hits] == ["RAG"]


def test_search_by_definition(db: sqlite3.Connection) -> None:
    _seed_two(db)
    hits = list_cards(db, q="vector")
    assert [c.term for c in hits] == ["Embedding"]


def test_search_no_hits(db: sqlite3.Connection) -> None:
    _seed_two(db)
    assert list_cards(db, q="nonexistent") == []


def test_filter_by_tag(db: sqlite3.Connection) -> None:
    _seed_two(db)
    hits = list_cards(db, tag="models")
    assert [c.term for c in hits] == ["Embedding"]


def test_filter_by_deck(db: sqlite3.Connection) -> None:
    _seed_two(db)
    hits = list_cards(db, deck="ai-native")
    assert len(hits) == 2


def test_get_deck_by_slug(db: sqlite3.Connection) -> None:
    _seed_two(db)
    deck = get_deck_by_slug(db, "ai-native")
    assert deck is not None
    assert deck.card_count == 2


def test_list_decks_includes_counts(db: sqlite3.Connection) -> None:
    _seed_two(db)
    decks = {d.slug: d for d in list_decks(db)}
    assert decks["ai-native"].card_count == 2
    assert decks["other"].card_count == 0


def test_list_tags(db: sqlite3.Connection) -> None:
    _seed_two(db)
    assert list_tags(db) == ["models", "patterns"]


def test_get_card_missing(db: sqlite3.Connection) -> None:
    assert get_card(db, 999) is None
