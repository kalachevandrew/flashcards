from __future__ import annotations

from typing import Annotated

import typer

from flashcards.config import get_settings
from flashcards.db import apply_schema, connect
from flashcards.models import CardCreate
from flashcards.repo import create_card

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def add(
    term: Annotated[str, typer.Option(help="Term / front of card")],
    definition: Annotated[str, typer.Option(help="Definition / back of card")],
    deck: Annotated[str, typer.Option(help="Deck slug")] = "ai-native",
    source_url: Annotated[str | None, typer.Option(help="Optional source URL")] = None,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Tag (repeatable)")] = None,
) -> None:
    settings = get_settings()
    with connect(settings.db_path) as conn:
        apply_schema(conn)
        card = create_card(
            conn,
            CardCreate(
                term=term,
                definition=definition,
                deck=deck,
                source_url=source_url,
                tags=tag or [],
            ),
        )
    typer.echo(f"added card #{card.id} ({card.term}) to deck '{card.deck_slug}'")


if __name__ == "__main__":
    app()
