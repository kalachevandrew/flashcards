from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flashcards.app import create_app
from flashcards.config import Settings, reset_settings_for_tests
from flashcards.db import apply_schema, connect


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def db(db_path: Path) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    apply_schema(conn)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def settings(db_path: Path) -> Iterator[Settings]:
    s = Settings(db_path=db_path, admin_token="test-token", seed_on_start=False)
    reset_settings_for_tests(s)
    try:
        yield s
    finally:
        reset_settings_for_tests(Settings())


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as c:
        yield c
