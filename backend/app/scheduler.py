"""Scheduled phase advance + weekly mission load — the v2 replacement for
rollover.py.

Holds ONLY the "when": run on a timer (cron / APScheduler / a cloud scheduled
function). Each call (a) loads any newly-opened mission for the week, then
(b) advances every mission whose next vote-day has passed by invoking the crud
operations. The cosmetic "which phase is it" math for the UI lives in the
frontend; this module fires the consequential state changes.

Timeline (anchored on mission.started_at = the day the cause's window opens):
    pre        --(now >= started_at)----------------> phase-1 voting opens
    initiative --(now >= started_at + 7 weeks)-------> finalize_p1 (tiv elected)
    initiative --(now >= started_at + 8 weeks)-------> finalize_p2 (org elected) -> budget
    budget     --(now >= started_at + 33 weeks)------> distribute -> resolution
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import bootstrap, crud, models

WEEK = timedelta(days=7)
P1_ELECTION_OFFSET = 7 * WEEK    # tiv election ~7 weeks after the window opens
P2_ELECTION_OFFSET = 8 * WEEK    # org election the following week
RESOLVE_OFFSET = 33 * WEEK       # resolution: 33 weeks after the window opens


def run_due(db: Session, now: datetime | None = None) -> list[str]:
    """Load this week's new mission, then advance every due phase. Idempotent."""
    now = now or datetime.utcnow()
    log: list[str] = []

    # (a) auto-load any mission whose window has opened.
    try:
        log += bootstrap.ensure_due(db, now)
    except Exception:  # noqa: BLE001
        db.rollback()

    # (b) advance phases.
    for m in db.scalars(select(models.Mission)).all():
        if not m.started_at:
            continue
        # Open phase-1 voting once the window arrives.
        if m.current_phase == "pre" and now >= m.started_at:
            m.current_phase = "initiative"
            db.commit()
            log.append(f"{m.id}: phase-1 open")
        # Phase-1 election (tiv) — only until a winner is chosen.
        if (m.current_phase == "initiative" and not m.winning_tiv_id
                and now >= m.started_at + P1_ELECTION_OFFSET):
            if crud.finalize_p1(db, m.id):
                log.append(f"{m.id}: tiv elected")
        # Phase-2 election (org) — after a tiv winner exists.
        if (m.current_phase == "initiative" and m.winning_tiv_id
                and now >= m.started_at + P2_ELECTION_OFFSET):
            if crud.finalize_p2(db, m.id):
                log.append(f"{m.id}: org elected")
        # Resolution / distribution.
        if m.current_phase == "budget" and now >= m.started_at + RESOLVE_OFFSET:
            crud.distribute_mission(db, m.id)
            log.append(f"{m.id}: distributed")
    return log


_THROTTLE_S = 600  # at most once per 10 min per process
_last_run = 0.0


def maybe_run(db: Session) -> None:
    """Throttled entry point for request paths (e.g. GET /missions)."""
    global _last_run
    if time.time() - _last_run < _THROTTLE_S:
        return
    _last_run = time.time()
    try:
        run_due(db)
    except Exception:  # noqa: BLE001 — never let the clock break a read
        db.rollback()
