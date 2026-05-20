from __future__ import annotations

import sqlite3

from .db import transaction
from .models import Card, CardCreate, Deck


def _row_to_card(row: sqlite3.Row, tags: list[str]) -> Card:
    return Card(
        id=row["id"],
        deck_id=row["deck_id"],
        deck_slug=row["deck_slug"],
        term=row["term"],
        definition=row["definition"],
        source_url=row["source_url"],
        tags=tags,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _tags_for(conn: sqlite3.Connection, card_ids: list[int]) -> dict[int, list[str]]:
    if not card_ids:
        return {}
    placeholders = ",".join("?" * len(card_ids))
    rows = conn.execute(
        f"""
        SELECT ct.card_id, t.name
        FROM card_tags ct
        JOIN tags t ON t.id = ct.tag_id
        WHERE ct.card_id IN ({placeholders})
        ORDER BY t.name
        """,
        card_ids,
    ).fetchall()
    out: dict[int, list[str]] = {cid: [] for cid in card_ids}
    for r in rows:
        out[r["card_id"]].append(r["name"])
    return out


def list_decks(conn: sqlite3.Connection) -> list[Deck]:
    rows = conn.execute(
        """
        SELECT d.id, d.slug, d.name, d.description,
               (SELECT COUNT(*) FROM cards c WHERE c.deck_id = d.id) AS card_count
        FROM decks d
        ORDER BY d.name
        """
    ).fetchall()
    return [
        Deck(
            id=r["id"],
            slug=r["slug"],
            name=r["name"],
            description=r["description"],
            card_count=r["card_count"],
        )
        for r in rows
    ]


def get_deck_by_slug(conn: sqlite3.Connection, slug: str) -> Deck | None:
    r = conn.execute(
        """
        SELECT d.id, d.slug, d.name, d.description,
               (SELECT COUNT(*) FROM cards c WHERE c.deck_id = d.id) AS card_count
        FROM decks d WHERE d.slug = ?
        """,
        (slug,),
    ).fetchone()
    if r is None:
        return None
    return Deck(
        id=r["id"],
        slug=r["slug"],
        name=r["name"],
        description=r["description"],
        card_count=r["card_count"],
    )


def get_card(conn: sqlite3.Connection, card_id: int) -> Card | None:
    r = conn.execute(
        """
        SELECT c.id, c.deck_id, d.slug AS deck_slug, c.term, c.definition,
               c.source_url, c.created_at, c.updated_at
        FROM cards c JOIN decks d ON d.id = c.deck_id
        WHERE c.id = ?
        """,
        (card_id,),
    ).fetchone()
    if r is None:
        return None
    tags = _tags_for(conn, [card_id]).get(card_id, [])
    return _row_to_card(r, tags)


def list_cards(
    conn: sqlite3.Connection,
    *,
    q: str | None = None,
    tag: str | None = None,
    deck: str | None = None,
    limit: int = 200,
) -> list[Card]:
    clauses: list[str] = []
    params: list[object] = []

    base = """
        SELECT c.id, c.deck_id, d.slug AS deck_slug, c.term, c.definition,
               c.source_url, c.created_at, c.updated_at
        FROM cards c
        JOIN decks d ON d.id = c.deck_id
    """

    if q:
        base += " JOIN cards_fts f ON f.rowid = c.id"
        clauses.append("cards_fts MATCH ?")
        params.append(_fts_query(q))

    if tag:
        base += """
            JOIN card_tags ct ON ct.card_id = c.id
            JOIN tags t ON t.id = ct.tag_id
        """
        clauses.append("t.name = ?")
        params.append(tag)

    if deck:
        clauses.append("d.slug = ?")
        params.append(deck)

    sql = base
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " GROUP BY c.id ORDER BY c.term ASC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    tag_map = _tags_for(conn, [r["id"] for r in rows])
    return [_row_to_card(r, tag_map.get(r["id"], [])) for r in rows]


def _fts_query(q: str) -> str:
    # why: FTS5 treats raw user input as MATCH syntax; wrap each token as a prefix-match.
    tokens = [t for t in q.replace('"', " ").split() if t]
    if not tokens:
        return '""'
    return " ".join(f'"{t}"*' for t in tokens)


def create_deck(
    conn: sqlite3.Connection, *, slug: str, name: str, description: str | None = None
) -> int:
    cur = conn.execute(
        "INSERT INTO decks(slug, name, description) VALUES (?, ?, ?)",
        (slug, name, description),
    )
    assert cur.lastrowid is not None
    return cur.lastrowid


def get_or_create_deck(conn: sqlite3.Connection, *, slug: str, name: str | None = None) -> int:
    r = conn.execute("SELECT id FROM decks WHERE slug = ?", (slug,)).fetchone()
    if r is not None:
        return int(r["id"])
    return create_deck(conn, slug=slug, name=name or slug.replace("-", " ").title())


def _get_or_create_tag(conn: sqlite3.Connection, name: str) -> int:
    r = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
    if r is not None:
        return int(r["id"])
    cur = conn.execute("INSERT INTO tags(name) VALUES (?)", (name,))
    assert cur.lastrowid is not None
    return cur.lastrowid


def create_card(conn: sqlite3.Connection, payload: CardCreate) -> Card:
    with transaction(conn):
        deck_id = get_or_create_deck(conn, slug=payload.deck)
        cur = conn.execute(
            """
            INSERT INTO cards(deck_id, term, definition, source_url)
            VALUES (?, ?, ?, ?)
            """,
            (deck_id, payload.term, payload.definition, payload.source_url),
        )
        assert cur.lastrowid is not None
        card_id: int = cur.lastrowid
        for tag in payload.tags:
            tag_norm = tag.strip().lower()
            if not tag_norm:
                continue
            tag_id = _get_or_create_tag(conn, tag_norm)
            conn.execute(
                "INSERT OR IGNORE INTO card_tags(card_id, tag_id) VALUES (?, ?)",
                (card_id, tag_id),
            )
    card = get_card(conn, card_id)
    assert card is not None
    return card


def count_cards(conn: sqlite3.Connection) -> int:
    r = conn.execute("SELECT COUNT(*) AS n FROM cards").fetchone()
    return int(r["n"])


def list_tags(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM tags ORDER BY name").fetchall()
    return [r["name"] for r in rows]
