"""CRUD helpers for Earthbucks. Keeps DB queries out of the routers."""
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
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
    from sqlalchemy import func as sqlfunc
    rows = db.execute(
        select(models.Vote.org_id, sqlfunc.count(models.Vote.id).label("cnt"))
        .where(models.Vote.initiative_id == initiative_id)
        .group_by(models.Vote.org_id)
    ).all()
    return {row.org_id: row.cnt for row in rows}


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
    return user
