"""Mission bootstrap + weekly auto-load (v2).

The annulus model: each cause runs a staggered 7-week cycle. Every week one
cause's window opens and a new mission is created. Mission id = <prefix><cycle>,
so the first rotation is atm0, oce0, lan0, for0, wil0, hmr0, hpr0; the next is
atm1, oce1, … Cycle 0 missions inherit the cause's existing catalog initiatives
as their phase-1 candidates; later cycles collect fresh proposals.

  * bootstrap(db)   — one-off: seed the first rotation (atm0..hpr0) now.
  * ensure_due(db)  — idempotent weekly loader the scheduler calls so a new
                      mission appears as each cause's window opens.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

WEEK = timedelta(days=7)
ROTATION_WEEKS = 7

# PROGRAM week 0 of the mission timeline — atm0 opens here; each later week opens
# the next cause's mission. The initiative election is 7 weeks later (UX week 0).
# Aligned to the seeded data (atm0 started_at = 2026-04-28 12:00); the frontend
# cycleStart matches this exactly.
GENESIS = datetime(2026, 4, 28, 12, 0, 0)

# cause_id -> (rotation index, 3-letter mission-id prefix).
CAUSE_PREFIX: dict[str, tuple[int, str]] = {
    "atmosphere":     (0, "atm"),
    "oceans":         (1, "oce"),
    "land":           (2, "lan"),
    "forests":        (3, "for"),
    "wildlife":       (4, "wil"),
    "human-rights":   (5, "hmr"),
    "human-progress": (6, "hpr"),
}
_BY_INDEX = {idx: cid for cid, (idx, _p) in CAUSE_PREFIX.items()}


def open_date(cause_index: int, cycle: int) -> datetime:
    """When this cause's cycle-`cycle` phase-1 window opens."""
    return GENESIS + (cause_index + ROTATION_WEEKS * cycle) * WEEK


def mission_id(cause_id: str, cycle: int) -> str:
    return f"{CAUSE_PREFIX[cause_id][1]}{cycle}"


def ensure_mission(
    db: Session,
    cause_id: str,
    cycle: int,
    now: Optional[datetime] = None,
    assign_candidates: bool = False,
) -> models.Mission:
    """Create the (cause, cycle) mission if missing. Idempotent.

    Phase starts 'initiative' (phase-1 voting open) once the window has opened,
    else 'pre'. When assign_candidates, the cause's unassigned 'suggested'
    initiatives are attached as this mission's phase-1 candidates.
    """
    now = now or datetime.utcnow()
    mid = mission_id(cause_id, cycle)
    existing = db.get(models.Mission, mid)
    if existing:
        return existing
    idx = CAUSE_PREFIX[cause_id][0]
    started = open_date(idx, cycle)
    m = models.Mission(
        id=mid,
        cause_id=cause_id,
        cycle_num=cycle,
        started_at=started,
        current_phase="initiative" if started <= now else "pre",
    )
    db.add(m)
    if assign_candidates:
        for tiv in db.scalars(
            select(models.Initiative).where(
                models.Initiative.cause_id == cause_id,
                models.Initiative.mission_id.is_(None),
                models.Initiative.status == "suggested",
            )
        ).all():
            tiv.mission_id = mid
    db.commit()
    db.refresh(m)
    return m


def bootstrap(db: Session, rotations: int = 1, now: Optional[datetime] = None) -> list[str]:
    """Seed the first `rotations` rotations of missions (atm0..hpr0 for the
    default of 1), assigning cycle-0 candidate initiatives. Idempotent."""
    now = now or datetime.utcnow()
    log: list[str] = []
    for cycle in range(rotations):
        for cause_id, (idx, _p) in sorted(CAUSE_PREFIX.items(), key=lambda kv: kv[1][0]):
            mid = mission_id(cause_id, cycle)
            if db.get(models.Mission, mid) is not None:
                continue
            m = ensure_mission(db, cause_id, cycle, now=now, assign_candidates=(cycle == 0))
            log.append(f"created {m.id}: opens {m.started_at:%Y-%m-%d}, phase={m.current_phase}")
    return log


def ensure_due(db: Session, now: Optional[datetime] = None) -> list[str]:
    """Weekly auto-load: create the mission for every cause-cycle whose window
    has opened by `now` and doesn't exist yet. Cheap + idempotent; the scheduler
    calls this so a new mission appears as each cause's window opens."""
    now = now or datetime.utcnow()
    if now < GENESIS:
        return []
    weeks = int((now - GENESIS) / WEEK)
    log: list[str] = []
    for w in range(weeks + 1):
        cause_id = _BY_INDEX[w % ROTATION_WEEKS]
        cycle = w // ROTATION_WEEKS
        if db.get(models.Mission, mission_id(cause_id, cycle)) is None:
            m = ensure_mission(db, cause_id, cycle, now=now, assign_candidates=(cycle == 0))
            log.append(f"auto-loaded {m.id}")
    return log


if __name__ == "__main__":
    from .database import SessionLocal
    _db = SessionLocal()
    try:
        for line in bootstrap(_db):
            print(line)
    finally:
        _db.close()
