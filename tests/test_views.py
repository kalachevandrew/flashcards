from __future__ import annotations

from fastapi.testclient import TestClient


def _seed(client: TestClient) -> None:
    client.post(
        "/api/cards",
        json={
            "term": "RAG",
            "definition": "Retrieval-augmented generation.",
            "deck": "ai-native",
            "tags": ["patterns"],
        },
        headers={"X-Admin-Token": "test-token"},
    )


def test_home_200(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "flashcards" in r.text.lower()


def test_home_shows_cards(client: TestClient) -> None:
    _seed(client)
    r = client.get("/")
    assert "RAG" in r.text


def test_deck_page(client: TestClient) -> None:
    _seed(client)
    r = client.get("/decks/ai-native")
    assert r.status_code == 200
    assert "RAG" in r.text


def test_deck_404(client: TestClient) -> None:
    r = client.get("/decks/does-not-exist")
    assert r.status_code == 404


def test_admin_page(client: TestClient) -> None:
    r = client.get("/admin")
    assert r.status_code == 200
    assert "X-Admin-Token" in r.text or "Admin token" in r.text
