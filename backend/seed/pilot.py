"""Pilot seed — STRUCTURE.md build-seq 1.

Creates the synthetic dataset Jax wants for the cofounder pilot:

    * GameMaster benefactor (id assigned by autoincrement, handle ``GameMaster``)
    * 21 dummy initiatives — three per cause, ids Atm-1001..1003 ... Hpr-1001..1003,
      with backdated election dates so phase-2+ tivs already have a winning org.
    * 21 dummy organizations (org-1 .. org-21), each assigned to one of the
      phase-2+ initiatives.
    * GameMaster as the sole voter on each of the 21 initiatives (Contribution
      row + Vote row, share=1.0, committed=True).
    * Every pre-existing sample initiative without committed EBX has its
      status normalised to ``suggested`` per STRUCTURE.md build-seq 1.

Run from ``backend/``::

    python -m seed.pilot

Idempotent — re-running is a no-op (every row is keyed by a stable id and
guarded by ``db.get`` / ``select`` lookups).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import select

from app import models
from app.auth import hash_password
from app.database import Base, SessionLocal, engine


CAUSE_CODES: dict[str, str] = {
    "atmosphere":     "Atm",
    "oceans":         "Oce",
    "land":           "Lnd",
    "forests":        "Frs",
    "wildlife":       "Wld",
    "human-rights":   "Rts",
    "human-progress": "Hpr",
}

# Phase mapping for the three per-cause cycles. 1001 is the oldest (already
# resolved); 1003 is the youngest (just elected, org-vote phase).
#
# Pass 36 (INSTRUCTIONS build-seq 3): every pilot mission gets a UNIQUE
# election date that sits on its own cause's real vote-day grid. A cause's
# vote days are CYCLE_START + 7d*(cause_index + 7k) — the first day of each
# of its active windows (matches EBX.Cycle.nextDecisionDate in the frontend;
# e.g. Oceans Jun 4 2026, Land Jun 11 2026). The third column is the number
# of 49-day ROTATIONS back from the cause's most recent strictly-past vote day:
#   1003 → org_vote (phase 2)  — rotation 0 (just elected; org vote upcoming)
#   1002 → active   (phase 3+) — 2 rotations (14 weeks) ago
#   1001 → resolved (phase 5)  — 5 rotations (35 weeks) ago
PILOT_PHASES: list[tuple[int, str, int]] = [
    (1001, "resolved", 5),
    (1002, "active",   2),
    (1003, "org_vote", 0),
]

# Mirrors frontend EBX config: cycleStart 2026-01-01, 7-day decision interval,
# 49-day cause windows.
CYCLE_START = datetime(2026, 1, 1)
WEEK = timedelta(days=7)
ROTATION = 7 * WEEK


def cause_vote_day(cause_index, rotations_ago, now=None):
    """The cause's most recent vote day STRICTLY before today, minus
    ``rotations_ago`` full 49-day rotations. Strictly-before matters: on a
    cause's own vote day the live election is the community's to win — the
    pilot mission elected 'most recently' must come from the previous
    rotation, not collide with today's tally."""
    now = now or datetime.utcnow()
    today = datetime(now.year, now.month, now.day)
    first = CYCLE_START + WEEK * cause_index
    if today <= first:
        d = first
    else:
        k = int((today - first) / ROTATION)
        d = first + k * ROTATION
        while d >= today:
            d -= ROTATION
    return d - rotations_ago * ROTATION

GAMEMASTER_HANDLE = "GameMaster"
GAMEMASTER_EMAIL = "gamemaster@earthbucks.test"
# Stable, throwaway password — pilot account, not exposed to the public.
GAMEMASTER_PASSWORD = "pilot-game-master"  # noqa: S105 (test fixture)
GAMEMASTER_VOTE_EBX = 49  # one founding-bonus-sized commitment per cycle


def ensure_gamemaster(db) -> models.BenefactorAccount:
    """Get-or-create the GameMaster benefactor account.

    Implemented as a real ``BenefactorAccount`` (not a magic id) so the
    founding-49-EBX path and the auth flow exercise the same code paths a
    cofounder will. Tagged via the handle; a future ``is_test`` column will
    make this filterable in admin views.
    """
    existing = db.scalar(
        select(models.BenefactorAccount).where(
            models.BenefactorAccount.handle == GAMEMASTER_HANDLE
        )
    )
    if existing is not None:
        return existing
    acct = models.BenefactorAccount(
        email=GAMEMASTER_EMAIL,
        handle=GAMEMASTER_HANDLE,
        pass_hash=hash_password(GAMEMASTER_PASSWORD),
        is_active=True,
        vvv=True,  # treat as a participant who has voted before
    )
    db.add(acct)
    db.flush()
    return acct


def ensure_orgs(db, causes: list[models.Cause]) -> list[models.Organization]:
    """Create org-1 .. org-21 if missing. Each org's primary cause cycles
    through the 7 causes (org-1 → atmosphere, org-2 → oceans, …)."""
    orgs: list[models.Organization] = []
    for n in range(1, 22):
        oid = f"org-{n}"
        org = db.get(models.Organization, oid)
        if org is None:
            primary_cause = causes[(n - 1) % len(causes)]
            org = models.Organization(
                id=oid,
                name=f"Pilot Org {n:02d}",
                description=(
                    f"Synthetic pilot organization #{n} — generated by "
                    "seed.pilot. Replace with real candidates before the "
                    "cofounder demo."
                ),
                verified=True,
            )
            org.causes = [primary_cause]
            db.add(org)
        orgs.append(org)
    db.flush()
    return orgs


def ensure_pilot_initiatives(
    db,
    causes: list[models.Cause],
    orgs: list[models.Organization],
) -> list[models.Initiative]:
    """21 initiatives: 3 per cause × 7 causes. Phase per the PILOT_PHASES
    table; backdated election_open/close so the cycle math reads them as
    historical decisions."""
    out: list[models.Initiative] = []
    now = datetime.utcnow()
    org_idx = 0
    for cause in causes:
        code = CAUSE_CODES.get(cause.id, cause.id[:3].title())
        for cycle, status, rotations_ago in PILOT_PHASES:
            init_id = f"{code}-{cycle}"
            init = db.get(models.Initiative, init_id)
            assigned_org = orgs[org_idx % len(orgs)]
            org_idx += 1
            # Pass 36 (build-seq 3): unique per-cause election dates on the
            # real vote-day grid. The election close IS the mission start
            # date (the day the initiative was elected).
            close = cause_vote_day(cause.index, rotations_ago, now)
            opened = close - timedelta(days=7)
            # build-seq 6 (pass 35): pilot initiatives PAST phase 2 are each
            # linked to a pilot organization. Phase-1/2 tivs must not carry a
            # winner yet (org_vote means the org race is still open).
            past_phase2 = status in {"active", "resolved"}
            if init is not None:
                # Backfill rows seeded before winning_org_id existed, and
                # clear presumptive winners from not-yet-decided tivs.
                if past_phase2 and not init.winning_org_id:
                    init.winning_org_id = assigned_org.id
                elif not past_phase2 and init.winning_org_id:
                    init.winning_org_id = None
                # Pass 36: re-sync election dates onto the vote-day grid
                # (older seeds stamped every cause with the same now-based
                # offsets, so all missions claimed the same start date).
                init.election_open = opened
                init.election_close = close
            if init is None:
                init = models.Initiative(
                    id=init_id,
                    cause_id=cause.id,
                    cycle_num=cycle,
                    title=f"{cause.name} Pilot {cycle}",
                    description=(
                        f"Synthetic pilot initiative for {cause.name} "
                        f"cycle {cycle}. Phase: {status}."
                    ),
                    emoji=cause.emoji,
                    proposed_by="benefactor",
                    ebx_committed=GAMEMASTER_VOTE_EBX,
                    election_open=opened,
                    election_close=close,
                    status=status,
                    winning_org_id=assigned_org.id if past_phase2 else None,
                )
                db.add(init)
            out.append(init)
    db.flush()
    return out


def ensure_pilot_missions(
    db, initiatives: Iterable[models.Initiative]
) -> None:
    """Materialize a Mission row for every active/resolved pilot initiative
    so the cause-page right cards (phase 3 / phase 4 recap) have something
    to point at."""
    for init in initiatives:
        if init.status not in {"active", "resolved"}:
            continue
        mission_id = f"mission-{init.id}"
        existing = db.get(models.Mission, mission_id)
        if existing is not None:
            # Pass 36: keep the mission start date in lockstep with the
            # (re-synced) election date.
            existing.started_at = init.election_close
            continue
        if not init.winning_org_id:
            continue
        db.add(models.Mission(
            id=mission_id,
            initiative_id=init.id,
            org_id=init.winning_org_id,
            title=init.title,
            description=init.description,
            credit_value=1.0,
            budget=GAMEMASTER_VOTE_EBX,
            spent=GAMEMASTER_VOTE_EBX if init.status == "resolved" else 0,
            started_at=init.election_close,
            status="resolved" if init.status == "resolved" else "active",
        ))
    db.flush()


def ensure_gamemaster_votes(
    db,
    gm: models.BenefactorAccount,
    initiatives: Iterable[models.Initiative],
) -> None:
    """One Contribution + one Vote per pilot initiative, share=1.0,
    committed=True. GameMaster is the sole voter, which is why every
    pilot initiative already has a winner."""
    for init in initiatives:
        existing_contrib = db.scalar(
            select(models.Contribution).where(
                models.Contribution.benefactor_id == gm.id,
                models.Contribution.initiative_id == init.id,
            )
        )
        if existing_contrib is None:
            db.add(models.Contribution(
                benefactor_id=gm.id,
                initiative_id=init.id,
                amount_ebx=GAMEMASTER_VOTE_EBX,
            ))
        existing_vote = db.scalar(
            select(models.Vote).where(
                models.Vote.benefactor_id == gm.id,
                models.Vote.initiative_id == init.id,
            )
        )
        if existing_vote is None:
            db.add(models.Vote(
                benefactor_id=gm.id,
                initiative_id=init.id,
                cause_id=init.cause_id,
                org_id=init.winning_org_id,
                share=1.0,
                committed=True,
            ))
        else:
            # Pass 36 (build-seq 5): keep the GM org vote consistent with the
            # mission's phase — org_vote tivs have NO org wired in yet (the
            # org election hasn't happened), so the standing GM vote must not
            # carry one either.
            existing_vote.org_id = init.winning_org_id
    db.flush()


def normalise_sample_initiatives_to_suggested(
    db, pilot_ids: set[str]
) -> int:
    """STRUCTURE.md build-seq 1: every NON-pilot initiative without
    committed EBX should read ``status='suggested'``. Returns the number of
    rows touched so the CLI can report progress."""
    rows = db.execute(select(models.Initiative)).scalars().all()
    touched = 0
    for r in rows:
        if r.id in pilot_ids:
            continue
        if (r.ebx_committed or 0) > 0:
            continue
        if r.status != "suggested":
            r.status = "suggested"
            touched += 1
    db.flush()
    return touched


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        causes = db.execute(
            select(models.Cause).order_by(models.Cause.index)
        ).scalars().all()
        if len(causes) != 7:
            raise SystemExit(
                f"Expected 7 causes; found {len(causes)}. "
                "Run `python -m seed.seed` first to load the cause registry."
            )

        gm = ensure_gamemaster(db)
        orgs = ensure_orgs(db, causes)
        inits = ensure_pilot_initiatives(db, causes, orgs)
        ensure_pilot_missions(db, inits)
        ensure_gamemaster_votes(db, gm, inits)
        normalised = normalise_sample_initiatives_to_suggested(
            db, {i.id for i in inits}
        )

        db.commit()
        # Access the primary key while the instance is still bound
        gm_id = gm.id

    print(
        f"Pilot seed complete: GameMaster id={gm_id}, "
        f"{len(inits)} initiatives, {len(orgs)} orgs, "
        f"{normalised} sample initiatives reset to 'suggested'."
    )


if __name__ == "__main__":
    main()
