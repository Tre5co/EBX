"""CRUD helpers for Earthbucks. Keeps DB queries out of the routers."""
from __future__ import annotations

import json
from typing import Optional, Sequence

from sqlalchemy import select, func as sqlfunc
from sqlalchemy.orm import Session, selectinload

from . import models, schemas
from .auth import hash_password


# ---------------------------------------------------------------------------
# Causes
# ---------------------------------------------------------------------------
def list_causes(db: Session) -> Sequence[models.Cause]:
    return db.scalars(select(models.Cause).order_by(models.Cause.index)).all()


def get_cause(db: Session, cause_id: str) -> Optional[models.Cause]:
    return db.get(models.Cause, cause_id)


def create_cause(db: Session, data: schemas.CauseCreate) -> models.Cause:
    cause = models.Cause(**data.model_dump())
    db.add(cause)
    db.commit()
    db.refresh(cause)
    return cause


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------
def list_organizations(db: Session, cause_id: Optional[str] = None) -> Sequence[models.Organization]:
    stmt = select(models.Organization).options(selectinload(models.Organization.causes))
    if cause_id:
        stmt = stmt.join(models.Organization.causes).where(models.Cause.id == cause_id)
    return db.scalars(stmt).unique().all()


def get_organization(db: Session, org_id: str) -> Optional[models.Organization]:
    return db.scalar(
        select(models.Organization)
        .options(selectinload(models.Organization.causes))
        .where(models.Organization.id == org_id)
    )


def create_organization(db: Session, data: schemas.OrganizationCreate) -> models.Organization:
    payload = data.model_dump(exclude={"cause_ids"})
    org = models.Organization(**payload)
    if data.cause_ids:
        org.causes = [c for c in db.scalars(
            select(models.Cause).where(models.Cause.id.in_(data.cause_ids))
        )]
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


# ---------------------------------------------------------------------------
# Initiatives
# ---------------------------------------------------------------------------
def list_initiatives(
    db: Session,
    cause_id: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> Sequence[models.Initiative]:
    stmt = select(models.Initiative)
    if cause_id:
        stmt = stmt.where(models.Initiative.cause_id == cause_id)
    if status_filter:
        stmt = stmt.where(models.Initiative.status == status_filter)
    stmt = stmt.order_by(models.Initiative.ebx_committed.desc())
    return db.scalars(stmt).all()


def get_initiative(db: Session, initiative_id: str) -> Optional[models.Initiative]:
    return db.get(models.Initiative, initiative_id)


def create_initiative(db: Session, data: schemas.InitiativeCreate) -> models.Initiative:
    init = models.Initiative(**data.model_dump())
    db.add(init)
    db.commit()
    db.refresh(init)
    return init


def commit_ebx(
    db: Session,
    initiative_id: str,
    benefactor_id: int,
    amount: int,
) -> models.Contribution:
    init = db.get(models.Initiative, initiative_id)
    if init is None:
        raise ValueError("Initiative not found")
    # NOW #1 (pass 40): phase-1 commitments are only valid while the
    # initiative election is open. Once a tiv is elected (org_vote) or its
    # mission is live/resolved, new EBX must NOT swell that mission's phase-1
    # carry-over pool (the phase-2/org card reads it straight off
    # ebx_committed) — it belongs to the NEXT cycle's phase-1 election.
    if (init.status or "suggested") not in ("suggested", "debate"):
        raise ValueError(
            "Initiative election has closed; phase-1 commitments are no longer accepted"
        )
    contrib = models.Contribution(
        benefactor_id=benefactor_id,
        initiative_id=initiative_id,
        amount_ebx=amount,
    )
    init.ebx_committed = (init.ebx_committed or 0) + amount
    db.add(contrib)
    db.commit()
    db.refresh(contrib)
    return contrib


# ---------------------------------------------------------------------------
# Missions
# ---------------------------------------------------------------------------
def list_missions(db: Session, status_filter: Optional[str] = None) -> Sequence[models.Mission]:
    stmt = select(models.Mission).options(selectinload(models.Mission.metrics))
    if status_filter:
        stmt = stmt.where(models.Mission.status == status_filter)
    stmt = stmt.order_by(models.Mission.updated_at.desc())
    return db.scalars(stmt).all()


def get_mission(db: Session, mission_id: str) -> Optional[models.Mission]:
    return db.get(models.Mission, mission_id)


def create_mission(db: Session, data: schemas.MissionCreate) -> models.Mission:
    payload = data.model_dump(exclude={"metrics"})
    mission = models.Mission(**payload)
    for m in data.metrics:
        mission.metrics.append(models.MissionMetric(**m.model_dump()))
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


# ---------------------------------------------------------------------------
# Posts (feed)
# ---------------------------------------------------------------------------
def list_posts(
    db: Session,
    cause_id: Optional[str] = None,
    initiative_id: Optional[str] = None,
    limit: int = 50,
) -> Sequence[models.Post]:
    stmt = select(models.Post)
    if cause_id:
        stmt = stmt.where(models.Post.cause_id == cause_id)
    if initiative_id:
        stmt = stmt.where(models.Post.initiative_id == initiative_id)
    stmt = stmt.order_by(models.Post.created_at.desc()).limit(limit)
    return db.scalars(stmt).all()


def create_post(db: Session, data: schemas.PostCreate) -> models.Post:
    post = models.Post(**data.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------
def create_review(
    db: Session,
    data: schemas.ReviewCreate,
    benefactor_id: Optional[int] = None,
) -> models.Review:
    review = models.Review(
        organization_id=data.organization_id,
        benefactor_id=benefactor_id,
        rating=data.rating,
        body=data.body,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def list_reviews(db: Session, organization_id: str) -> Sequence[models.Review]:
    return db.scalars(
        select(models.Review)
        .where(models.Review.organization_id == organization_id)
        .order_by(models.Review.created_at.desc())
    ).all()


# ---------------------------------------------------------------------------
# Votes (org election)
# ---------------------------------------------------------------------------
def cast_vote(
    db: Session,
    initiative_id: str,
    benefactor_id: int,
    org_id: str,
) -> models.Vote:
    """Upsert a benefactor's org vote for an initiative (one vote per benefactor per initiative)."""
    existing = db.scalar(
        select(models.Vote)
        .where(models.Vote.benefactor_id == benefactor_id)
        .where(models.Vote.initiative_id == initiative_id)
    )
    if existing:
        existing.org_id = org_id
        db.commit()
        db.refresh(existing)
        return existing
    vote = models.Vote(
        benefactor_id=benefactor_id,
        initiative_id=initiative_id,
        org_id=org_id,
    )
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote


def get_vote_tally(db: Session, initiative_id: str) -> dict[str, int]:
    """Return a dict of org_id -> vote count for an initiative."""
    rows = db.execute(
        select(models.Vote.org_id, sqlfunc.count(models.Vote.id).label("cnt"))
        .where(models.Vote.initiative_id == initiative_id)
        .group_by(models.Vote.org_id)
    ).all()
    return {row.org_id: row.cnt for row in rows}


# ---------------------------------------------------------------------------
# Initiative-election (cause-scoped) votes — build-seq 3
# ---------------------------------------------------------------------------
SHARE_FLOOR = 0.1
SHARE_SUM_CAP = 1.0


def replace_cause_votes(
    db: Session,
    benefactor_id: int,
    cause_id: str,
    shares: dict[str, float],
) -> list[models.Vote]:
    """Replace a benefactor's soft (uncommitted) vote shares for a cause.

    Validates the 0.1 floor and the sum <= 1.0 cap server-side so the client
    can't slip past localStorage tampering. Committed rows are left in place
    and any attempt to overwrite them raises ValueError — clients should call
    POST /votes/commit only when the benefactor is ready to lock the slate.
    """
    # Floor + cap.
    cleaned: dict[str, float] = {}
    total = 0.0
    for init_id, raw in shares.items():
        try:
            v = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"Share for {init_id} is not numeric")
        if v <= 0:
            continue
        if v < SHARE_FLOOR:
            raise ValueError(f"Share for {init_id} is below the 0.1 floor")
        v = round(v, 1)
        cleaned[init_id] = v
        total += v
    if total > SHARE_SUM_CAP + 1e-6:
        raise ValueError(f"Total share {total:.2f} exceeds 1.0")

    # All initiatives must belong to the named cause.
    if cleaned:
        bad = db.execute(
            select(models.Initiative.id).where(
                models.Initiative.id.in_(list(cleaned.keys())),
                models.Initiative.cause_id != cause_id,
            )
        ).scalars().all()
        if bad:
            raise ValueError(f"Initiatives {bad} are not in cause {cause_id}")

    # Existing rows for this benefactor + cause.
    existing = db.scalars(
        select(models.Vote)
        .where(models.Vote.benefactor_id == benefactor_id)
        .where(models.Vote.cause_id == cause_id)
    ).all()

    by_init: dict[str, models.Vote] = {row.initiative_id: row for row in existing}

    # Reject overwrites against committed rows.
    for init_id, row in by_init.items():
        if row.committed:
            raise ValueError(
                f"Vote for {init_id} is already committed; "
                "use a new cycle to change it."
            )

    # Upsert the new shares.
    for init_id, share in cleaned.items():
        row = by_init.get(init_id)
        if row is None:
            row = models.Vote(
                benefactor_id=benefactor_id,
                initiative_id=init_id,
                cause_id=cause_id,
                share=share,
                committed=False,
            )
            db.add(row)
        else:
            row.share = share
            row.cause_id = cause_id  # backfill if a pre-migration row lacked it

    # Drop rows that are no longer represented (and aren't committed).
    for init_id, row in by_init.items():
        if init_id not in cleaned and not row.committed:
            db.delete(row)

    db.commit()
    # Return the live set.
    return list(db.scalars(
        select(models.Vote)
        .where(models.Vote.benefactor_id == benefactor_id)
        .where(models.Vote.cause_id == cause_id)
    ).all())


def get_cause_vote_tally(
    db: Session,
    cause_id: str,
    size_factor: float,
) -> dict:
    """Return per-initiative raw + vote-weighted shares for a cause.

    Vote-weight formula (per STRUCTURE.md):
        weight(b) = 1 + b_contribution / (pool_excluding_b * n_votes * size_factor)

    `pool_excluding_b` is the cause-wide EBX committed by everyone *other*
    than this benefactor. `n_votes` is the count of soft+committed votes for
    the initiative. When pool_excluding_b is 0 (only this benefactor has
    committed) the weight collapses to 1 — no over-counting from /0 guards.
    """
    # Aggregate cause-wide committed EBX per benefactor for the weight formula.
    init_id_subq = (
        select(models.Initiative.id)
        .where(models.Initiative.cause_id == cause_id)
        .scalar_subquery()
    )
    contrib_rows = db.execute(
        select(
            models.Contribution.benefactor_id,
            sqlfunc.coalesce(sqlfunc.sum(models.Contribution.amount_ebx), 0).label("ebx"),
        )
        .where(models.Contribution.initiative_id.in_(init_id_subq))
        .group_by(models.Contribution.benefactor_id)
    ).all()
    contributions: dict[int, float] = {row.benefactor_id: float(row.ebx) for row in contrib_rows}
    pool_total = float(sum(contributions.values()))

    # All soft+committed votes for this cause.
    vote_rows = db.scalars(
        select(models.Vote).where(models.Vote.cause_id == cause_id)
    ).all()

    if not vote_rows:
        return {
            "cause_id": cause_id,
            "size_factor": size_factor,
            "pool_total_ebx": int(pool_total),
            "entries": [],
        }

    # Per-initiative counts (single pass).
    per_init: dict[str, dict] = {}
    for v in vote_rows:
        e = per_init.setdefault(v.initiative_id, {"raw": 0.0, "weighted": 0.0, "voters": 0})
        b_contrib = contributions.get(v.benefactor_id, 0.0)
        pool_excl = max(0.0, pool_total - b_contrib)
        if pool_excl > 0 and size_factor > 0:
            # n_votes for THIS initiative is finalised below; use the running
            # count so the weight reflects current breadth of support.
            n_votes_running = e["voters"] + 1
            weight = 1.0 + (b_contrib / (pool_excl * n_votes_running * size_factor))
        else:
            weight = 1.0
        e["raw"] += float(v.share)
        e["weighted"] += float(v.share) * weight
        e["voters"] += 1

    entries = [
        {
            "initiative_id": init_id,
            "raw_share": round(stats["raw"], 4),
            "weighted_share": round(stats["weighted"], 4),
            "voter_count": stats["voters"],
        }
        for init_id, stats in sorted(per_init.items(), key=lambda kv: -kv[1]["weighted"])
    ]
    return {
        "cause_id": cause_id,
        "size_factor": size_factor,
        "pool_total_ebx": int(pool_total),
        "entries": entries,
    }


def commit_cause_votes(db: Session, benefactor_id: int, cause_id: str) -> int:
    """Lock the benefactor's current shares for this cause. Returns row count."""
    rows = db.scalars(
        select(models.Vote)
        .where(models.Vote.benefactor_id == benefactor_id)
        .where(models.Vote.cause_id == cause_id)
        .where(models.Vote.committed.is_(False))
    ).all()
    for row in rows:
        row.committed = True
    db.commit()
    return len(rows)


# ---------------------------------------------------------------------------
# Initiative ratings + watchlist — build-seq 4
# ---------------------------------------------------------------------------
def _watched_list(account: models.BenefactorAccount) -> list[str]:
    if not account.watched_initiative_ids:
        return []
    try:
        parsed = json.loads(account.watched_initiative_ids)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except (TypeError, ValueError):
        pass
    return []


def _save_watched(account: models.BenefactorAccount, ids: list[str]) -> None:
    # Dedupe + preserve insertion order.
    seen, out = set(), []
    for x in ids:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    account.watched_initiative_ids = json.dumps(out) if out else None


def list_watched(db: Session, account: models.BenefactorAccount) -> list[str]:
    return _watched_list(account)


def add_watch(db: Session, account: models.BenefactorAccount, init_id: str) -> list[str]:
    current = _watched_list(account)
    if init_id not in current:
        current.append(init_id)
        _save_watched(account, current)
        db.commit()
    return current


def remove_watch(db: Session, account: models.BenefactorAccount, init_id: str) -> list[str]:
    current = _watched_list(account)
    if init_id in current:
        current = [x for x in current if x != init_id]
        _save_watched(account, current)
        db.commit()
    return current


def rate_initiative(
    db: Session,
    benefactor_id: int,
    initiative_id: str,
    stars: int,
) -> models.InitiativeRating:
    """Upsert a benefactor's rating; recompute rating_avg/count; auto-watch.

    Per Jax's pass-14 note: rating an initiative auto-adds it to the
    benefactor's watchlist. Removing from the watchlist does NOT nullify the
    rating (see DELETE /benefactors/me/watch/{init_id}).
    """
    if not 0 <= stars <= 5:
        raise ValueError("stars must be in 0..5")

    init = db.get(models.Initiative, initiative_id)
    if init is None:
        raise ValueError("Initiative not found")

    existing = db.scalar(
        select(models.InitiativeRating)
        .where(models.InitiativeRating.benefactor_id == benefactor_id)
        .where(models.InitiativeRating.initiative_id == initiative_id)
    )
    if existing:
        existing.stars = stars
    else:
        existing = models.InitiativeRating(
            benefactor_id=benefactor_id,
            initiative_id=initiative_id,
            stars=stars,
        )
        db.add(existing)

    db.flush()  # so the aggregate sees the upserted row

    # Recompute the rollup from non-zero stars only (0 = withdrawn).
    agg = db.execute(
        select(
            sqlfunc.coalesce(sqlfunc.avg(models.InitiativeRating.stars), 0.0).label("avg"),
            sqlfunc.count(models.InitiativeRating.id).label("cnt"),
        )
        .where(models.InitiativeRating.initiative_id == initiative_id)
        .where(models.InitiativeRating.stars > 0)
    ).one()
    init.rating_avg = float(agg.avg or 0.0)
    init.rating_count = int(agg.cnt or 0)
    init.rating = init.rating_avg  # keep the legacy "rating" column in sync

    # Auto-watch (side-effect from Jax's spec).
    account = db.get(models.BenefactorAccount, benefactor_id)
    if account is not None:
        watched = _watched_list(account)
        if initiative_id not in watched:
            watched.append(initiative_id)
            _save_watched(account, watched)

    db.commit()
    db.refresh(existing)
    return existing


# ---------------------------------------------------------------------------
# Benefactor accounts
# ---------------------------------------------------------------------------
def get_benefactor_by_email(db: Session, email: str) -> Optional[models.BenefactorAccount]:
    return db.scalar(select(models.BenefactorAccount).where(models.BenefactorAccount.email == email))


def get_benefactor_by_handle(db: Session, handle: str) -> Optional[models.BenefactorAccount]:
    return db.scalar(select(models.BenefactorAccount).where(models.BenefactorAccount.handle == handle))


def create_benefactor(db: Session, data: schemas.BenefactorCreate) -> models.BenefactorAccount:
    user = models.BenefactorAccount(
        email=data.email,
        handle=data.handle,
        pass_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Founding bonus: first 100 signups receive 49 EBX automatically.
    # These are credited as unminted (no mission yet) generic credit coins.
    if user.id <= 100:
        from .models import CreditCoin
        # Use a sentinel mission id "founding-bonus" — real missions will use real ids.
        # The frontend will show these as "Founding 49 EBX" in the wallet.
        # Only add if a founding-bonus mission-like entry exists; otherwise skip silently.
        # For now we create 49 individual 1-EBX coins against mission id "founding-bonus"
        # so they show up in the credit portfolio. A seed mission entry is expected.
        founding_mission = db.execute(
            __import__('sqlalchemy').text("SELECT id FROM missions WHERE id = 'founding-bonus' LIMIT 1")
        ).fetchone()
        if founding_mission:
            for _ in range(49):
                coin = CreditCoin(
                    owner_id=user.id,
                    mission_id='founding-bonus',
                    amount_ebx=1,
                )
                db.add(coin)
            db.commit()

    return user


# ---------------------------------------------------------------------------
# Org registrations / nominations (pass 34, build-seq 2)
# ---------------------------------------------------------------------------
def create_org_registration(
    db: Session,
    data: schemas.OrgRegistrationCreate,
    benefactor_id: Optional[int] = None,
) -> models.OrgRegistration:
    reg = models.OrgRegistration(
        kind=data.kind,
        org_name=data.org_name,
        website=data.website,
        justification=data.justification,
        member_name=data.member_name,
        member_position=data.member_position,
        initiative_ids=json.dumps(data.initiative_ids),
        submitted_by_id=benefactor_id,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def list_org_registrations(
    db: Session,
    initiative_id: Optional[str] = None,
    status: Optional[str] = None,
) -> list[models.OrgRegistration]:
    regs = db.scalars(
        select(models.OrgRegistration)
        .order_by(models.OrgRegistration.created_at.desc())
    ).all()
    out = []
    for r in regs:
        if status and r.status != status:
            continue
        if initiative_id:
            try:
                ids = json.loads(r.initiative_ids or "[]")
            except Exception:
                ids = []
            if initiative_id not in ids:
                continue
        out.append(r)
    return out
