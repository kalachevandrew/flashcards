from __future__ import annotations

from contextlib import asynccontextmanager
from importlib import resources
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import api as api_module
from . import views as views_module
from .api import health_router
from .api import router as api_router
from .config import get_settings
from .db import apply_schema, connect
from .seed import run as run_seed
from .views import router as views_router


@asynccontextmanager
async def _lifespan(_: FastAPI):
    settings = get_settings()
    with connect(settings.db_path) as conn:
        apply_schema(conn)
        if settings.seed_on_start:
            run_seed(conn)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="flashcards",
        description="AI-native flashcards — browse, search, flip.",
        version="0.1.0",
        lifespan=_lifespan,
    )

    pkg_dir = Path(str(resources.files("flashcards")))
    templates = Jinja2Templates(directory=str(pkg_dir / "templates"))
    api_module.set_templates(templates)
    views_module.set_templates(templates)

    app.mount("/static", StaticFiles(directory=str(pkg_dir / "static")), name="static")
    app.include_router(api_router)
    app.include_router(health_router)
    app.include_router(views_router)
    return app


app = create_app()
