from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .db import connect
from .models import Card, CardCreate, Deck
from .repo import create_card, get_card, list_cards, list_decks

router = APIRouter(prefix="/api", tags=["api"])
templates: Jinja2Templates | None = None


def set_templates(t: Jinja2Templates) -> None:
    global templates
    templates = t


def _conn():
    return connect(get_settings().db_path)


@router.get("/decks", response_model=list[Deck])
def api_list_decks() -> list[Deck]:
    with _conn() as conn:
        return list_decks(conn)


@router.get("/cards/{card_id}", response_model=Card)
def api_get_card(card_id: int) -> Card:
    with _conn() as conn:
        card = get_card(conn, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="card not found")
    return card


@router.get("/cards")
def api_list_cards(
    request: Request,
    q: str | None = None,
    tag: str | None = None,
    deck: str | None = None,
    format: str | None = None,  # noqa: A002 — query param name, intentional
):
    with _conn() as conn:
        cards = list_cards(conn, q=q, tag=tag, deck=deck)

    wants_html = format == "html" or request.headers.get("hx-request", "").lower() == "true"
    if wants_html:
        assert templates is not None
        return templates.TemplateResponse(
            request,
            "_card_grid.html",
            {"cards": cards, "q": q, "tag": tag, "deck": deck},
        )
    return cards


@router.post("/cards", response_model=Card, status_code=status.HTTP_201_CREATED)
def api_create_card(
    payload: CardCreate,
    x_admin_token: Annotated[str | None, Header(alias="X-Admin-Token")] = None,
) -> Card:
    settings = get_settings()
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise HTTPException(status_code=401, detail="admin token required")
    with _conn() as conn:
        return create_card(conn, payload)


health_router = APIRouter(tags=["meta"])


@health_router.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


__all__ = ["router", "health_router", "set_templates", "HTMLResponse"]
