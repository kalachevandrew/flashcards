from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .db import connect
from .repo import get_deck_by_slug, list_cards, list_decks, list_tags

router = APIRouter(tags=["views"])
templates: Jinja2Templates | None = None


def set_templates(t: Jinja2Templates) -> None:
    global templates
    templates = t


def _conn():
    return connect(get_settings().db_path)


@router.get("/")
def home(request: Request):
    assert templates is not None
    with _conn() as conn:
        decks = list_decks(conn)
        cards = list_cards(conn, limit=200)
        tags = list_tags(conn)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"decks": decks, "cards": cards, "tags": tags},
    )


@router.get("/decks/{slug}")
def deck_page(request: Request, slug: str):
    assert templates is not None
    with _conn() as conn:
        deck = get_deck_by_slug(conn, slug)
        if deck is None:
            raise HTTPException(status_code=404, detail="deck not found")
        cards = list_cards(conn, deck=slug)
        tags = list_tags(conn)
    return templates.TemplateResponse(
        request,
        "deck.html",
        {"deck": deck, "cards": cards, "tags": tags},
    )


@router.get("/admin")
def admin_page(request: Request):
    assert templates is not None
    with _conn() as conn:
        decks = list_decks(conn)
    return templates.TemplateResponse(
        request,
        "admin.html",
        {"decks": decks, "admin_enabled": bool(get_settings().admin_token)},
    )
