"""Earthbucks FastAPI entrypoint — v2 (mission-centric).

Parallel to main.py; becomes main.py at cutover. Wires the routers package
against the v2 models/schemas/crud. Run from backend/:
    uvicorn app.main:app --reload --port 8000
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import (
    admin,
    auth,
    benefactors,
    candidacies,
    causes,
    initiatives,
    missions,
    organizations,
    posts,
    transactions,
    votes,
)

settings = get_settings()

# Project root (one directory above backend/).
ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(
    title="Earthbucks API",
    version="0.2.0",
    description="Mission-centric backend + static host for the Earthbucks platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api", tags=["health"])
def api_root() -> JSONResponse:
    return JSONResponse({"name": "Earthbucks API", "version": "0.2.0", "status": "ok"})


@app.get("/health", tags=["health"])
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/coin-value", tags=["health"])
def coin_value() -> JSONResponse:
    """Global credit-coin value — moved by commits/withdrawals platform-wide.
    Per-mission values ride on mission.credit_value (moved by resolutions)."""
    from .database import SessionLocal
    from . import crud as _crud
    db = SessionLocal()
    try:
        return JSONResponse(_crud.global_coin_value(db, scale=settings.coin_value_scale))
    finally:
        db.close()


# JSON API routers
app.include_router(auth.router)
app.include_router(causes.router)
app.include_router(organizations.router)
app.include_router(initiatives.router)
app.include_router(missions.router)
app.include_router(candidacies.router)
app.include_router(votes.router)
app.include_router(posts.router)
app.include_router(benefactors.router)
app.include_router(transactions.router)
app.include_router(admin.router)


# Static hosting from the project root.
app.mount("/resources", StaticFiles(directory=ROOT / "resources"), name="resources")
data_dir = ROOT / "data"
if data_dir.exists():
    app.mount("/data", StaticFiles(directory=data_dir), name="data")


def _html(name: str) -> FileResponse:
    return FileResponse(ROOT / f"{name}.html", media_type="text/html")


@app.get("/", include_in_schema=False)
def root_page() -> FileResponse:
    return _html("index")

# index.html = public landing page (served at "/"); main.html = the home/missions app page.
# Orgs have NO page of their own (restructure 2026-07-10): their public face is
# the org panel on mission.html (?org=), their admin lives behind admin.html.
_HTML_PAGES = ("index", "main", "cause", "mission", "profile", "admin")


def _make_handler(page: str):
    def handler() -> FileResponse:
        return _html(page)
    return handler


for _page in _HTML_PAGES:
    app.add_api_route(f"/{_page}", _make_handler(_page), include_in_schema=False)
    app.add_api_route(f"/{_page}.html", _make_handler(_page), include_in_schema=False)
