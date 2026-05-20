from __future__ import annotations

from pydantic import BaseModel, Field


class Deck(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    card_count: int = 0


class Card(BaseModel):
    id: int
    deck_id: int
    deck_slug: str
    term: str
    definition: str
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


class CardCreate(BaseModel):
    term: str = Field(min_length=1, max_length=200)
    definition: str = Field(min_length=1, max_length=4000)
    deck: str = Field(min_length=1, max_length=80, description="Deck slug")
    source_url: str | None = Field(default=None, max_length=500)
    tags: list[str] = Field(default_factory=list)
