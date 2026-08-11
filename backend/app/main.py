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


@app.on_event("startup")
def _migrate_to_head() -> None:
    """Bring the database up to the latest Alembic revision on boot.

    §5 (2026-08-06) added columns to `causes`, so the ORM can no longer read an
    un-migrated database *at all* — every cause query fails, which means every
    page fails. A forgotten `alembic upgrade head` shouldn't look like the app
    is broken, so it runs itself. Idempotent: if the database is already at
    head this is a no-op. The file is backed up first, because a migration that
    goes wrong on a pilot database should be recoverable by copying a file.
    """
    import shutil
    from pathlib import Path
    from alembic import command
    from alembic.config import Config

    backend_dir = Path(__file__).resolve().parents[1]
    ini = backend_dir / "alembic.ini"
    if not ini.exists():
        return
    try:
        url = settings.database_url
        if url.startswith("sqlite:///"):
            db_path = (backend_dir / url.replace("sqlite:///", "").lstrip("./")).resolve()
            if db_path.exists():
                bak = db_path.with_suffix(db_path.suffix + ".bak_premigrate")
                if not bak.exists() or bak.stat().st_mtime < db_path.stat().st_mtime:
                    shutil.copy2(db_path, bak)
        cfg = Config(str(ini))
        cfg.set_main_option("script_location", str(backend_dir / "alembic"))
        command.upgrade(cfg, "head")
    except Exception as e:   # never block boot on a migration
        print(f"[startup] auto-migration skipped: {e}\n"
              f"[startup] run `alembic upgrade head` from backend/ if pages look broken.")


@app.on_event("startup")
def _adopt_orphan_initiatives() -> None:
    """§0a (2026-08-05): self-heal initiatives that were proposed without a
    mission. They were invisible to every mission-scoped query and could crash
    the phase-1 vote path (UNIQUE(ben_id, tiv_id)); `create_tiv` no longer makes
    them, and this adopts the ones already in the db. Idempotent + cheap."""
    from .database import SessionLocal
    from . import crud as _crud
    db = SessionLocal()
    try:
        adopted = _crud.adopt_orphan_tivs(db)
        if adopted:
            print(f"[startup] adopted {len(adopted)} orphaned initiative(s): {', '.join(adopted)}")
    except Exception as e:  # never block boot on a repair
        print(f"[startup] orphan-initiative repair skipped: {e}")
    finally:
        db.close()


@app.on_event("startup")
def _resync_derived_tallies() -> None:
    """§0 (2026-08-08): rebuild the two caches derived from the vote rows —
    `MissionCandidacy.p2_vote_tally` and `Pool` — so a race can never keep
    reporting votes and EBX that no longer exist. The live database was already
    carrying one such ghost (atm0: 150 phase-2 EBX and a 5-vote tally left by a
    removed pilot account). Account removal now does this itself; this catches
    what happened before it did. Idempotent and cheap."""
    from .database import SessionLocal
    from . import crud as _crud, models as _models
    from sqlalchemy import select as _select
    db = SessionLocal()
    try:
        changed = _crud.resync_p2_tallies(db)
        fixed = []
        for mid in db.scalars(_select(_models.Mission.id)).all():
            pool = db.get(_models.Pool, mid)
            if pool is None:
                continue
            before = (pool.phase1_total_ebx, pool.phase2_total_ebx, pool.total_locked)
            after = _crud.recompute_pool(db, mid)
            if before != (after.phase1_total_ebx, after.phase2_total_ebx, after.total_locked):
                fixed.append(mid)
        if changed or fixed:
            print(f"[startup] resynced {len(changed)} candidacy tall(ies) "
                  f"{sorted(changed)} and {len(fixed)} pool(s) {fixed}")
    except Exception as e:   # never block boot on a cache rebuild
        print(f"[startup] derived-tally resync skipped: {e}")
    finally:
        db.close()


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
