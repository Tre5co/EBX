"""Election rollover — pass 36 (INSTRUCTIONS build-seq 4 / error 0a).

Jax (Jun 11): "It's June 11 and the land vote day arrived, but nothing
shifted." Until now NOTHING advanced initiative phases — statuses were
static seed data. This module is the missing clock:

  * Phase 1 → 2: on a cause's vote day (the first day of its active
    window), the leading phase-1 initiative is elected — status
    ``org_vote``, election_open/close stamped onto the vote-day grid.
  * Phase 2 → 3: on the mission's ORG vote day (election_close + 8 weeks —
    the last day of the cause's NEXT active window), the org-election
    tally picks a winning organization — ``active``, Mission row created.
  * Phase 3 → resolved: 33 weeks after election (STRUCTURE: Resolution
    weeks 33+).

``run_rollover(db)`` is idempotent and cheap; ``maybe_rollover(db)`` is the
throttled entry point wired into GET /initiatives so a long-running server
shifts phases without a restart.

Answer to Jax's "is this because of the 1-day counting period?" — no. The
tally is instantaneous on the vote day; there was simply no code doing it.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models

# Mirrors frontend EBX config (ebx_shared.ts): cycleStart 2026-01-01,
# 7-day decision interval, 49-day cause windows.
CYCLE_START = datetime(2026, 1, 1)
WEEK = timedelta(days=7)
ROTATION = 7 * WEEK
ORG_VOTE_OFFSET = 8 * WEEK     # org vote = election + 8 weeks
RESOLVE_OFFSET = 33 * WEEK     # resolution = election + 33 weeks

_ELECTABLE = ("suggested", "debate")


def most_recent_vote_day(cause_index: int, now: datetime | None = None) -> datetime:
    """Most recent vote day (start of active window) <= now for a cause.
    Vote days sit on the grid CYCLE_START + 7d*(cause_index + 7k)."""
    now = now or datetime.utcnow()
    first = CYCLE_START + WEEK * cause_index
    if now < first:
        return first - ROTATION  # before the first-ever vote day
    k = int((now - first) / ROTATION)
    d = first + k * ROTATION
    if d > now:
        d -= ROTATION
    return d


def _phase1_weight(db: Session, init: models.Initiative, cutoff: datetime) -> float:
    """Tally weight for a phase-1 candidate: committed EBX + each
    benefactor's vote share weighted by their contribution (1:1 EBX→weight,
    floor = the bare share). Mirrors the frontend voteWeight model. Only
    votes cast on/before the cutoff (the vote day) count."""
    weight = float(init.ebx_committed or 0)
    votes = db.scalars(
        select(models.Vote).where(models.Vote.initiative_id == init.id)
    ).all()
    for v in votes:
        if v.created_at and v.created_at > cutoff:
            continue  # cast after the vote day → belongs to the next election
        contrib = db.scalar(
            select(models.Contribution).where(
                models.Contribution.benefactor_id == v.benefactor_id,
                models.Contribution.initiative_id == init.id,
            )
        )
        ebx = float(contrib.amount_ebx) if contrib else 0.0
        share = float(v.share or 0)
        weight += max(share, ebx * share)
    return weight


def _finalize_phase1(db: Session, now: datetime) -> list[str]:
    """Elect the leading phase-1 initiative of every cause whose vote day
    has arrived AND that has at least one real signal (a Vote row or
    committed EBX cast for the still-open election)."""
    out: list[str] = []
    causes = db.scalars(select(models.Cause)).all()
    for cause in causes:
        d = most_recent_vote_day(cause.index, now)
        candidates = db.scalars(
            select(models.Initiative).where(
                models.Initiative.cause_id == cause.id,
                models.Initiative.status.in_(_ELECTABLE),
            )
        ).all()
        if not candidates:
            continue
        # Idempotence: if some initiative of this cause was already elected
        # on (or after) this vote day, this election is done.
        already = db.scalar(
            select(models.Initiative).where(
                models.Initiative.cause_id == cause.id,
                models.Initiative.status.in_(("org_vote", "active", "resolved")),
                models.Initiative.election_close >= d,
            )
        )
        if already is not None:
            continue
        # An election only tallies if at least one REAL ballot (a Vote row)
        # was cast on a candidate on/before the vote day. Seed EBX sitting on
        # sample proposals is not a ballot — without this guard the first
        # rollover would mass-elect sample initiatives in every cause.
        ballots = [
            v for c in candidates
            for v in db.scalars(
                select(models.Vote).where(models.Vote.initiative_id == c.id)
            ).all()
            if not v.created_at or v.created_at <= d
        ]
        if not ballots:
            continue
        weighted = [(c, _phase1_weight(db, c, d)) for c in candidates]
        winner = max(weighted, key=lambda t: t[1])[0]
        winner.status = "org_vote"
        winner.election_close = d
        winner.election_open = d - WEEK
        winner.winning_org_id = None  # org race opens now
        out.append(f"phase1 {cause.id}: elected {winner.id} on {d:%Y-%m-%d}")
    return out


def _finalize_phase2(db: Session, now: datetime) -> list[str]:
    """Promote org_vote → active when the mission's org vote day has
    passed and an org-election tally exists."""
    out: list[str] = []
    rows = db.scalars(
        select(models.Initiative).where(models.Initiative.status == "org_vote")
    ).all()
    for init in rows:
        if not init.election_close:
            continue
        org_vote_day = init.election_close + ORG_VOTE_OFFSET
        if org_vote_day > now:
            continue
        tally: dict[str, int] = {}
        for v in db.scalars(
            select(models.Vote).where(
                models.Vote.initiative_id == init.id,
                models.Vote.org_id.isnot(None),
            )
        ).all():
            tally[v.org_id] = tally.get(v.org_id, 0) + 1
        if not tally:
            # No org votes — leave the race open and let EN handle it.
            continue
        winner_org = max(tally.items(), key=lambda t: t[1])[0]
        init.winning_org_id = winner_org
        init.status = "active"
        mission_id = f"mission-{init.id}"
        if db.get(models.Mission, mission_id) is None:
            db.add(models.Mission(
                id=mission_id,
                initiative_id=init.id,
                org_id=winner_org,
                title=init.title,
                description=init.description,
                credit_value=1.0,
                budget=init.ebx_committed or 0,
                spent=0,
                started_at=init.election_close,
                status="active",
            ))
        out.append(f"phase2 {init.id}: org {winner_org} elected ({org_vote_day:%Y-%m-%d})")
    return out


def _finalize_phase3(db: Session, now: datetime) -> list[str]:
    out: list[str] = []
    rows = db.scalars(
        select(models.Initiative).where(models.Initiative.status == "active")
    ).all()
    for init in rows:
        if not init.election_close:
            continue
        if init.election_close + RESOLVE_OFFSET > now:
            continue
        init.status = "resolved"
        mission = db.get(models.Mission, f"mission-{init.id}")
        if mission is not None:
            mission.status = "resolved"
        out.append(f"phase3 {init.id}: resolved")
    return out


def run_rollover(db: Session, now: datetime | None = None) -> list[str]:
    """Run all phase transitions that are due. Returns a change log."""
    now = now or datetime.utcnow()
    changes = []
    changes += _finalize_phase1(db, now)
    changes += _finalize_phase2(db, now)
    changes += _finalize_phase3(db, now)
    if changes:
        db.commit()
    return changes


_THROTTLE_S = 600  # at most once per 10 minutes per process
_last_run = 0.0


def maybe_rollover(db: Session) -> None:
    """Throttled rollover for request paths (GET /initiatives)."""
    global _last_run
    if time.time() - _last_run < _THROTTLE_S:
        return
    _last_run = time.time()
    try:
        run_rollover(db)
    except Exception:  # noqa: BLE001 — never let the clock break a read
        db.rollback()
