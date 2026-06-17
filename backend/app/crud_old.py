"""CRUD helpers for Earthbucks. Keeps DB queries out of the routers."""
from __future__ import annotations

import json
from datetime import datetime
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
    stmt = select(models.Mission)
    if status_filter:
        stmt = stmt.where(models.Mission.status == status_filter)
    stmt = stmt.order_by(models.Mission.updated_at.desc())
    return db.scalars(stmt).all()


def get_mission(db: Session, mission_id: str) -> Optional[models.Mission]:
    return db.get(models.Mission, mission_id)


def create_mission(db: Session, data: schemas.MissionCreate) -> models.Mission:
    mission = models.Mission(**data.model_dump())
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
# Vote audit log (build-seq 1) — append-only history of vote mutations.
# ---------------------------------------------------------------------------
def log_vote_event(
    db: Session,
    *,
    user_id: Optional[int],
    election_id: Optional[str],
    action: str,
    cause_id: Optional[str] = None,
    target: Optional[str] = None,
    kind: str = "initiative",
    old_value=None,
    new_value=None,
) -> None:
    """Append one CAST/UPDATE/REMOVE row. Caller commits with the mutation."""
    db.add(models.VoteEvent(
        user_id=user_id,
        election_id=election_id,
        cause_id=cause_id,
        target=target,
        kind=kind,
        action=action,
        old_value=None if old_value is None else str(old_value),
        new_value=None if new_value is None else str(new_value),
    ))


# ---------------------------------------------------------------------------
# Votes (org election)
# ---------------------------------------------------------------------------
def cast_vote(
    db: Session,
    initiative_id: str,
    benefactor_id: int,
    org_id: str,
) -> models.Vote:
    """Upsert a benefactor's org vote for an initiative (one per benefactor per
    initiative). Logs a CAST or UPDATE event instead of silently overwriting."""
    init = db.get(models.Initiative, initiative_id)
    cause_id = init.cause_id if init else None
    existing = db.scalar(
        select(models.Vote)
        .where(models.Vote.benefactor_id == benefactor_id)
        .where(models.Vote.initiative_id == initiative_id)
    )
    if existing:
        old_org = existing.org_id
        existing.org_id = org_id
        existing.cause_id = existing.cause_id or cause_id
        log_vote_event(
            db, user_id=benefactor_id, election_id=initiative_id,
            cause_id=existing.cause_id, target=org_id, kind="org",
            action="UPDATE", old_value=old_org, new_value=org_id,
        )
        db.commit()
        db.refresh(existing)
        return existing
    vote = models.Vote(
        benefactor_id=benefactor_id,
        initiative_id=initiative_id,
        cause_id=cause_id,
        org_id=org_id,
    )
    db.add(vote)
    log_vote_event(
        db, user_id=benefactor_id, election_id=initiative_id,
        cause_id=cause_id, target=org_id, kind="org",
        action="CAST", old_value=None, new_value=org_id,
    )
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
            log_vote_event(
                db, user_id=benefactor_id, election_id=init_id,
                cause_id=cause_id, target=init_id, kind="initiative",
                action="CAST", old_value=None, new_value=share,
            )
        else:
            if abs(float(row.share or 0) - float(share)) > 1e-9:
                log_vote_event(
                    db, user_id=benefactor_id, election_id=init_id,
                    cause_id=cause_id, target=init_id, kind="initiative",
                    action="UPDATE", old_value=row.share, new_value=share,
                )
            row.share = share
            row.cause_id = cause_id  # backfill if a pre-migration row lacked it

    # Drop rows that are no longer represented (and aren't committed).
    for init_id, row in by_init.items():
        if init_id not in cleaned and not row.committed:
            log_vote_event(
                db, user_id=benefactor_id, election_id=init_id,
                cause_id=cause_id, target=init_id, kind="initiative",
                action="REMOVE", old_value=row.share, new_value=None,
            )
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
        log_vote_event(
            db, user_id=benefactor_id, election_id=row.initiative_id,
            cause_id=cause_id, target=row.org_id or row.initiative_id,
            kind="org" if row.org_id else "initiative",
            action="UPDATE", old_value="soft", new_value="committed",
        )
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


# ---------------------------------------------------------------------------
# Admin votes console (build-seq 1)
# ---------------------------------------------------------------------------
def _enrich_votes(db: Session) -> list[dict]:
    handles = {b.id: b.handle for b in db.scalars(select(models.BenefactorAccount)).all()}
    valid_users = set(handles.keys())
    titles = {i.id: i.title for i in db.scalars(select(models.Initiative)).all()}
    causes = {i.id: i.cause_id for i in db.scalars(select(models.Initiative)).all()}
    orgnames = {o.id: o.name for o in db.scalars(select(models.Organization)).all()}
    rows = []
    for v in db.scalars(select(models.Vote)).all():
        kind = "org" if v.org_id else "initiative"
        rows.append({
            "id": v.id,
            "benefactor_id": v.benefactor_id,
            "handle": handles.get(v.benefactor_id),
            "initiative_id": v.initiative_id,
            "initiative_title": titles.get(v.initiative_id),
            "cause_id": v.cause_id or causes.get(v.initiative_id),
            "org_id": v.org_id,
            "org_name": orgnames.get(v.org_id) if v.org_id else None,
            "share": float(v.share or 0),
            "committed": bool(v.committed),
            "kind": kind,
            "created_at": v.created_at,
            "_user_valid": v.benefactor_id in valid_users,
            "_election_valid": v.initiative_id in titles,
            "_org_valid": (v.org_id is None) or (v.org_id in orgnames),
        })
    return rows


def admin_list_votes(
    db: Session,
    user: Optional[str] = None,
    election: Optional[str] = None,
    organization: Optional[str] = None,
    sort: str = "timestamp_desc",
) -> list[dict]:
    """Full live-vote table across all elections + accounts, with filters.

    user         - substring match on handle, or exact benefactor id
    election     - exact initiative (election) id
    organization - exact org id
    sort         - timestamp_desc (default) | timestamp_asc
    """
    rows = _enrich_votes(db)
    if user:
        u = str(user).strip().lower()
        rows = [r for r in rows if (r["handle"] and u in r["handle"].lower())
                or (r["benefactor_id"] is not None and str(r["benefactor_id"]) == u)]
    if election:
        rows = [r for r in rows if r["initiative_id"] == election]
    if organization:
        rows = [r for r in rows if r["org_id"] == organization]
    reverse = sort != "timestamp_asc"
    rows.sort(key=lambda r: r["created_at"] or datetime.min, reverse=reverse)
    return rows


def admin_vote_summary(db: Session, by: str = "user") -> list[dict]:
    """Summary counts grouped by 'user', 'election', or 'target'."""
    rows = _enrich_votes(db)
    events = db.scalars(select(models.VoteEvent)).all()
    agg: dict = {}

    def bucket(key, label):
        e = agg.setdefault(key, {"key": key, "label": label, "vote_count": 0, "event_count": 0})
        if label and not e["label"]:
            e["label"] = label
        return e

    if by == "election":
        for r in rows:
            bucket(r["initiative_id"], r["initiative_title"])["vote_count"] += 1
        for ev in events:
            if ev.election_id:
                bucket(ev.election_id, None)["event_count"] += 1
    elif by == "target":
        for r in rows:
            key = r["org_id"] or r["initiative_id"]
            label = r["org_name"] or r["initiative_title"]
            bucket(key, label)["vote_count"] += 1
        for ev in events:
            if ev.target:
                bucket(ev.target, None)["event_count"] += 1
    else:  # user
        for r in rows:
            key = str(r["benefactor_id"]) if r["benefactor_id"] is not None else "(none)"
            bucket(key, r["handle"])["vote_count"] += 1
        for ev in events:
            key = str(ev.user_id) if ev.user_id is not None else "(none)"
            bucket(key, None)["event_count"] += 1

    out = list(agg.values())
    out.sort(key=lambda e: (-e["vote_count"], -e["event_count"]))
    return out


def admin_vote_checks(db: Session) -> dict:
    """Flag duplicate votes, votes without users, and invalid elections."""
    rows = _enrich_votes(db)

    # Duplicate votes: same (benefactor, initiative) appearing more than once.
    seen: dict = {}
    for r in rows:
        k = (r["benefactor_id"], r["initiative_id"])
        seen.setdefault(k, []).append(r["id"])
    duplicates = [
        {"benefactor_id": k[0], "initiative_id": k[1], "vote_ids": ids}
        for k, ids in seen.items() if len(ids) > 1
    ]

    # Votes without (valid) users.
    no_user = [
        {"vote_id": r["id"], "benefactor_id": r["benefactor_id"],
         "initiative_id": r["initiative_id"]}
        for r in rows if r["benefactor_id"] is None or not r["_user_valid"]
    ]

    # Invalid elections: initiative missing, or org set but missing.
    invalid = [
        {"vote_id": r["id"], "initiative_id": r["initiative_id"],
         "org_id": r["org_id"],
         "reason": ("unknown initiative" if not r["_election_valid"] else "unknown organization")}
        for r in rows if not r["_election_valid"] or not r["_org_valid"]
    ]

    return {
        "duplicate_votes": duplicates,
        "votes_without_users": no_user,
        "invalid_elections": invalid,
    }


def admin_list_vote_events(
    db: Session,
    user: Optional[str] = None,
    election: Optional[str] = None,
    sort: str = "timestamp_desc",
) -> list[models.VoteEvent]:
    rows = db.scalars(select(models.VoteEvent)).all()
    if user:
        u = str(user).strip()
        rows = [e for e in rows if e.user_id is not None and str(e.user_id) == u]
    if election:
        rows = [e for e in rows if e.election_id == election]
    reverse = sort != "timestamp_asc"
    rows.sort(key=lambda e: e.created_at or datetime.min, reverse=reverse)
    return rows
