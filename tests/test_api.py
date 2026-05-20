from __future__ import annotations

from fastapi.testclient import TestClient


def _add(client: TestClient, **kw) -> dict:
    body = {
        "term": kw.get("term", "RAG"),
        "definition": kw.get("definition", "Retrieval-augmented generation."),
        "deck": kw.get("deck", "ai-native"),
        "tags": kw.get("tags", ["patterns"]),
    }
    r = client.post(
        "/api/cards",
        json=body,
        headers={"X-Admin-Token": "test-token"},
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_healthz(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_list_cards_empty(client: TestClient) -> None:
    r = client.get("/api/cards")
    assert r.status_code == 200
    assert r.json() == []


def test_create_requires_token(client: TestClient) -> None:
    r = client.post(
        "/api/cards",
        json={"term": "x", "definition": "y", "deck": "z"},
    )
    assert r.status_code == 401


def test_create_rejects_wrong_token(client: TestClient) -> None:
    r = client.post(
        "/api/cards",
        json={"term": "x", "definition": "y", "deck": "z"},
        headers={"X-Admin-Token": "nope"},
    )
    assert r.status_code == 401


def test_create_and_fetch(client: TestClient) -> None:
    card = _add(client, term="Token", definition="Atomic unit of model input.", tags=["models"])
    assert card["term"] == "Token"
    assert card["deck_slug"] == "ai-native"
    assert "models" in card["tags"]

    r = client.get(f"/api/cards/{card['id']}")
    assert r.status_code == 200
    assert r.json()["term"] == "Token"


def test_get_card_404(client: TestClient) -> None:
    r = client.get("/api/cards/999999")
    assert r.status_code == 404


def test_list_with_search(client: TestClient) -> None:
    _add(client, term="RAG", definition="Retrieval pattern.")
    _add(client, term="Embedding", definition="Vector representation.")
    r = client.get("/api/cards", params={"q": "vector"})
    assert r.status_code == 200
    assert [c["term"] for c in r.json()] == ["Embedding"]


def test_list_filter_by_tag(client: TestClient) -> None:
    _add(client, term="RAG", tags=["patterns"])
    _add(client, term="LLM", tags=["models"])
    r = client.get("/api/cards", params={"tag": "models"})
    assert [c["term"] for c in r.json()] == ["LLM"]


def test_list_filter_by_deck(client: TestClient) -> None:
    _add(client, term="RAG", deck="ai-native")
    _add(client, term="Misc", deck="other")
    r = client.get("/api/cards", params={"deck": "other"})
    assert [c["term"] for c in r.json()] == ["Misc"]


def test_list_html_format(client: TestClient) -> None:
    _add(client, term="RAG")
    r = client.get("/api/cards", params={"format": "html"})
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "RAG" in r.text


def test_list_hx_request_returns_html(client: TestClient) -> None:
    _add(client, term="RAG")
    r = client.get("/api/cards", headers={"HX-Request": "true"})
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_list_decks(client: TestClient) -> None:
    _add(client, term="RAG", deck="ai-native")
    r = client.get("/api/decks")
    assert r.status_code == 200
    slugs = [d["slug"] for d in r.json()]
    assert "ai-native" in slugs
