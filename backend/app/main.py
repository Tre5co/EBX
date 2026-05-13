"""Earthbucks FastAPI entrypoint.

Run locally from the backend/ directory:
    uvicorn app.main:app --reload --port 8000

This server does double duty:
  - Routes under /causes, /initiatives, /organizations, /missions, /posts,
    /auth -> JSON API.
  - /, /index.html, /cause.html, etc. and /resources/* and /data/* are served
    as static files from the project root.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import auth, causes, initiatives, missions, organizations, posts

settings = get_settings()

# Project root (one directory above backend/).
ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(
    title="Earthbucks API",
    version="0.1.0",
    description="Backend + static host for the Earthbucks platform.",
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
    return JSONResponse({"name": "Earthbucks API", "version": "0.1.0", "status": "ok"})


@app.get("/health", tags=["health"])
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


# JSON API routers
app.include_router(auth.router)
app.include_router(causes.router)
app.include_router(organizations.router)
app.include_router(initiatives.router)
app.include_router(missions.router)
app.include_router(posts.router)


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


_HTML_PAGES = ("index", "cause", "initiative", "mission", "profile", "feed", "about")

def _make_handler(page: str):
    def handler() -> FileResponse:
        return _html(page)
    return handler

for _page in _HTML_PAGES:
    app.add_api_route(f"/{_page}", _make_handler(_page), include_in_schema=False)
    app.add_api_route(f"/{_page}.html", _make_handler(_page), include_in_schema=False)
