"""CRUD + domain logic for the v2 (mission-centric) Earthbucks backend.

Written from scratch on models_v2 / schemas_v2. Parallel to crud.py; nothing
imports it until cutover. At cutover, rename to crud.py and change the two
aliased imports below to ``from . import models, schemas``.

Layout
------
  constants & helpers · causes · missions(spine) · initiatives(tiv) ·
  organizations · benefactors · memberships · mission candidacies ·
  phase-1 voting · phase-2 voting · tallies & finalization · pool ·
  money allocation · posts & reactions · watchlist · credit coins ·
  ledger (transactions) · query console (staff)

Conventions
-----------
  * Domain/validation problems raise ValueError; permission problems raise
    PermissionError. Routers translate these to 4xx.
  * Functions that mutate commit before returning (mirrors crud.py).
  * "ben" = benefactor, "tiv" = initiative, "org" = organization.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional, Sequence

from sqlalchemy import func as sqlfunc, select
from sqlalchemy.orm import Session

from . import models, schemas
from .auth import hash_password


# ===========================================================================
# Constants (STRUCTURE.md)
# ===========================================================================
SHARE_FLOOR = 0.1            # phase-1 vote-split division floor
SHARE_SUM_CAP = 1.0          # a ben's phase-1 shares sum to <= 1.0
BASE_VOTE_EBX = 10           # a vote carries 10 EBX of weight without buying any
EBX_PER_VOTE = 10            # 10 EBX = 1 vote (0.1 vote = 1 EBX)

# Phase send rates — the fraction of a ben's contribution treated as the
# irrevocable (locked-donation) part. NOTE: money is NOT refunded at resolution;
# everything a ben commits stays in the pool until the credit-release phase, when
# the non-guaranteed REMAINDER is released to the org or back to benefactors.
# These rates are the basis for that later return calc, not a resolution refund.
P1_SEND_WIN = 0.20           # your tiv won
P1_SEND_LOSE = 0.10          # your tiv lost
P2_SEND_WIN = 1.00           # your org won
P2_SEND_LOSE = 0.20          # your org lost

# Loser carryover (Jax pass): a losing initiative re-enters its cause's NEXT-cycle
# election automatically, carrying each backer's commitment forward at (1 - skim).
# The skim is booked to a single global "commitment fund" ledger bucket. These are
# placeholder rates — tune later. (The 80% locked behind a winning vote stays in
# the won mission and is untouched by this path.)
COMMITMENT_FUND_SKIM = 0.10          # 10% of a loser's commitment → commitment fund
COMMITMENT_FUND_BUCKET = "commitment_fund"

# Pool allocation, expressed in 32nds of the mission pool. The four top-level
# slices — EN_CUT + ORG_GUARANTEED + ORG_ADVANCE + REMAINDER — sum to 32/32.
POOL_THRESHOLD = 100         # EN takes its cut only when the pool > $100
# EN and the org EACH get a mission-side 1/4 plus a 1/16 advance (= 5/16 each).
EN_MISSION = 8 / 32          # EN guaranteed 1/4 — its mission-side budget
EN_ADVANCE = 2 / 32          # EN 1/16 advance; releases with the case post reward
ORG_MISSION = 8 / 32         # org guaranteed 1/4 — its mission-side budget
ORG_ADVANCE = 2 / 32         # org 1/16 advance; releases with the case post reward
# Three benefactor post-type rewards, 1/32 each (released with the case reward).
REWARD_BEST_CASE = 1 / 32
REWARD_CONTEXT_OR_ANALYSIS = 1 / 32
REWARD_COMMENTS = 1 / 32
# The remaining 9/32 is flexible — released in the credit phase to the org or
# back to benefactors. (8+2 EN) + (8+2 org) + (3 rewards) + (9 flexible) = 32/32.
FLEXIBLE = 9 / 32
ORG_GUARANTEED = ORG_MISSION + ORG_ADVANCE   # 10/32 — the concrete budget floor

FOUNDING_BONUS_EBX = 49      # first 100 signups
FOUNDING_BONUS_MISSION = "founding-bonus"

VALENCE_SIGN = {"helpful": 1.0, "neutral": 0.0, "harmful": -1.0}


# ===========================================================================
# Helpers
# ===========================================================================
def require_staff(account: models.BenefactorAccount) -> None:
    """Gate employee-only actions (approvals, editorial posts, query console)."""
    if not getattr(account, "is_staff", False):
        raise PermissionError("This action requires an Earthbux employee account")


def _valence_ok(value: str) -> str:
    if value not in VALENCE_SIGN:
        raise ValueError(f"valence must be one of {sorted(VALENCE_SIGN)}; got {value!r}")
    return value


# ===========================================================================
# Causes
# ===========================================================================
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


# ===========================================================================
# Missions (the spine)
# ===========================================================================
def list_missions(
    db: Session,
    cause_id: Optional[str] = None,
    phase: Optional[str] = None,
) -> Sequence[models.Mission]:
    stmt = select(models.Mission)
    if cause_id:
        stmt = stmt.where(models.Mission.cause_id == cause_id)
    if phase:
        stmt = stmt.where(models.Mission.current_phase == phase)
    return db.scalars(stmt.order_by(models.Mission.cycle_num.desc())).all()


def get_mission(db: Session, mission_id: str) -> Optional[models.Mission]:
    return db.get(models.Mission, mission_id)


def get_mission_by_cycle(db: Session, cause_id: str, cycle_num: int) -> Optional[models.Mission]:
    return db.scalar(
        select(models.Mission).where(
            models.Mission.cause_id == cause_id,
            models.Mission.cycle_num == cycle_num,
        )
    )


def create_mission(db: Session, data: schemas.MissionCreate) -> models.Mission:
    mission = models.Mission(**data.model_dump())
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


def get_or_create_mission(
    db: Session,
    cause_id: str,
    cycle_num: int,
    started_at: Optional[datetime] = None,
) -> models.Mission:
    """Ensure the (cause, cycle) spine slot exists (created at cycle start,
    before any election). Idempotent."""
    existing = get_mission_by_cycle(db, cause_id, cycle_num)
    if existing:
        return existing
    mission = models.Mission(
        id=f"{cause_id}-{cycle_num}",
        cause_id=cause_id,
        cycle_num=cycle_num,
        current_phase="pre",
        started_at=started_at,
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


# ===========================================================================
# Initiatives (tiv)
# ===========================================================================
def list_tivs(
    db: Session,
    cause_id: Optional[str] = None,
    mission_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    approved_only: bool = False,
) -> Sequence[models.Initiative]:
    stmt = select(models.Initiative)
    if cause_id:
        stmt = stmt.where(models.Initiative.cause_id == cause_id)
    if mission_id:
        stmt = stmt.where(models.Initiative.mission_id == mission_id)
    if status_filter:
        stmt = stmt.where(models.Initiative.status == status_filter)
    if approved_only:
        stmt = stmt.where(models.Initiative.approved.is_(True))
    return db.scalars(stmt.order_by(models.Initiative.rating_avg.desc())).all()


def get_tiv(db: Session, tiv_id: str) -> Optional[models.Initiative]:
    return db.get(models.Initiative, tiv_id)


def p1_ebx_by_tiv(db: Session, tiv_ids: Optional[list[str]] = None) -> dict[str, float]:
    """Total committed EBX per initiative, summed across all phase-1 vote rows.

    This is the public pool aggregate the homepage cards + cause-page leaderboards
    rank by (10 EBX = 1 vote). Pass tiv_ids to scope the sum."""
    q = select(models.VoteP1.tiv_id, sqlfunc.sum(models.VoteP1.ebx_committed))
    if tiv_ids:
        q = q.where(models.VoteP1.tiv_id.in_(tiv_ids))
    q = q.group_by(models.VoteP1.tiv_id)
    return {tid: float(total or 0) for tid, total in db.execute(q).all()}


def create_tiv(db: Session, data: schemas.InitiativeCreate) -> models.Initiative:
    tiv = models.Initiative(**data.model_dump())
    db.add(tiv)
    db.commit()
    db.refresh(tiv)
    return tiv


def approve_tiv(db: Session, tiv_id: str, staff: models.BenefactorAccount) -> models.Initiative:
    """Staff-only: clear a tiv to enter elections."""
    require_staff(staff)
    tiv = db.get(models.Initiative, tiv_id)
    if tiv is None:
        raise ValueError("Initiative not found")
    tiv.approved = True
    db.commit()
    db.refresh(tiv)
    return tiv


def recompute_tiv_rating(db: Session, tiv_id: str) -> models.Initiative:
    """Rating = aggregated average of this tiv's VoteP1 valence (helpful=+1,
    neutral=0, harmful=-1), scaled to 0..1. rating_count = number of voters."""
    tiv = db.get(models.Initiative, tiv_id)
    if tiv is None:
        raise ValueError("Initiative not found")
    valences = db.scalars(
        select(models.VoteP1.valence).where(models.VoteP1.tiv_id == tiv_id)
    ).all()
    if valences:
        avg_sign = sum(VALENCE_SIGN[v] for v in valences) / len(valences)
        tiv.rating_avg = round((avg_sign + 1) / 2, 4)  # map [-1,1] -> [0,1]
        tiv.rating_count = len(valences)
    else:
        tiv.rating_avg = 0.0
        tiv.rating_count = 0
    db.commit()
    db.refresh(tiv)
    return tiv


# ===========================================================================
# Organizations
# ===========================================================================
def list_orgs(db: Session, cause_id: Optional[str] = None) -> Sequence[models.Organization]:
    stmt = select(models.Organization)
    if cause_id:
        # org's causes are derived: org -> candidacies -> missions -> cause
        stmt = (
            stmt.join(models.MissionCandidacy, models.MissionCandidacy.org_id == models.Organization.id)
            .join(models.Mission, models.Mission.id == models.MissionCandidacy.mission_id)
            .where(models.Mission.cause_id == cause_id)
            .distinct()
        )
    return db.scalars(stmt).all()


def get_org(db: Session, org_id: str) -> Optional[models.Organization]:
    return db.get(models.Organization, org_id)


def create_org(db: Session, data: schemas.OrganizationCreate) -> models.Organization:
    org = models.Organization(**data.model_dump())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def org_cause_ids(db: Session, org_id: str) -> list[str]:
    """Derived causes for an org (through its mission candidacies)."""
    rows = db.scalars(
        select(models.Mission.cause_id)
        .join(models.MissionCandidacy, models.MissionCandidacy.mission_id == models.Mission.id)
        .where(models.MissionCandidacy.org_id == org_id)
        .distinct()
    ).all()
    return list(rows)


# ── Org self-registration / nomination (public application) — Phase 2 (A) ──
def _norm_org_name(name: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", (name or "").lower()).strip()


def fuzzy_org_matches(db: Session, name: str, threshold: float = 0.82) -> list[dict]:
    """Fuzzy name matching against existing orgs — the 'did you mean an existing
    org?' guard. An org is a single entity and is never duplicated."""
    target = _norm_org_name(name)
    if not target:
        return []
    out: list[dict] = []
    for org in db.scalars(select(models.Organization)).all():
        cand = _norm_org_name(org.name)
        score = SequenceMatcher(None, target, cand).ratio()
        # containment counts too ("Rainforest Trust" vs "The Rainforest Trust Fund")
        if target and cand and (target in cand or cand in target):
            score = max(score, 0.9)
        if score >= threshold:
            out.append({"org_id": org.id, "name": org.name, "score": round(score, 3)})
    out.sort(key=lambda m: -m["score"])
    return out[:5]


def _gen_org_id(db: Session, name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "org").lower()).strip("-")[:28] or "org"
    oid = slug
    while db.get(models.Organization, oid) is not None:
        oid = f"{slug}-{uuid.uuid4().hex[:5]}"
    return oid


def register_org(
    db: Session,
    data: schemas.OrganizationRegister,
    actor: models.BenefactorAccount,
    dup_threshold: float = 0.82,
) -> dict:
    """Public org application/registration (no staff gate — 'organizations can
    self-register at any time'). Returns an OrgRegisterResult-shaped dict.

    kind='registration': the actor is a real member — they become
      founding_member_id (when creating) and get an executive Membership.
    kind='nomination': a benefactor puts the org forward — no membership.
    Duplicate guard: unless force or an explicit org_id is given, fuzzy name
    matches are returned instead of creating anything.
    """
    org: Optional[models.Organization] = None
    created = False
    if data.org_id:
        org = db.get(models.Organization, data.org_id)
        if org is None:
            raise ValueError("Organization not found")
    else:
        matches = fuzzy_org_matches(db, data.name, threshold=dup_threshold)
        if matches and not data.force:
            return {"created": False, "org": None, "membership": None,
                    "candidacy": None, "matches": matches}
        org = models.Organization(
            id=_gen_org_id(db, data.name),
            name=data.name.strip(),
            description=data.description,
            website_link=data.website_link,
            founded_year=data.founded_year,
            logo_url=data.logo_url,
            founding_member_id=actor.id if data.kind == "registration" else None,
            joined_at=datetime.utcnow(),
        )
        db.add(org)
        db.flush()
        created = True

    membership = None
    if data.kind == "registration":
        # The registering member operates the org: executive when founding,
        # rep when joining an existing org via registration.
        role = "executive" if created else "rep"
        existing = db.scalar(
            select(models.Membership).where(
                models.Membership.ben_id == actor.id,
                models.Membership.org_id == org.id,
            )
        )
        if existing:
            # never demote an existing executive
            if existing.role not in ("executive",):
                existing.role = role
            membership = existing
        else:
            membership = models.Membership(ben_id=actor.id, org_id=org.id, role=role)
            db.add(membership)

    candidacy = None
    if data.mission_id:
        if db.get(models.Mission, data.mission_id) is None:
            raise ValueError("Mission not found")
        candidacy = db.scalar(
            select(models.MissionCandidacy).where(
                models.MissionCandidacy.mission_id == data.mission_id,
                models.MissionCandidacy.org_id == org.id,
            )
        )
        if candidacy is None:
            candidacy = models.MissionCandidacy(
                mission_id=data.mission_id,
                org_id=org.id,
                mission_statement=data.mission_statement,
                submitted_by_id=actor.id,
                status="pending",
            )
            db.add(candidacy)
        elif data.mission_statement and not candidacy.mission_statement:
            candidacy.mission_statement = data.mission_statement

    db.commit()
    db.refresh(org)
    if membership is not None:
        db.refresh(membership)
    if candidacy is not None:
        db.refresh(candidacy)
    return {"created": created, "org": org, "membership": membership,
            "candidacy": candidacy, "matches": []}


# ===========================================================================
# Benefactor accounts (ben) — role carries the employee category
# ===========================================================================
def get_ben_by_email(db: Session, email: str) -> Optional[models.BenefactorAccount]:
    return db.scalar(select(models.BenefactorAccount).where(models.BenefactorAccount.email == email))


def get_ben_by_handle(db: Session, handle: str) -> Optional[models.BenefactorAccount]:
    return db.scalar(select(models.BenefactorAccount).where(models.BenefactorAccount.handle == handle))


def create_ben(db: Session, data: schemas.BenefactorCreate) -> models.BenefactorAccount:
    ben = models.BenefactorAccount(
        email=data.email,
        handle=data.handle,
        pass_hash=hash_password(data.password),
    )
    db.add(ben)
    db.commit()
    db.refresh(ben)

    # Founding bonus: first 100 signups get one 49-EBX credit coin, if the
    # founding-bonus mission slot exists (seeded). Silent no-op otherwise.
    if ben.id <= 100 and db.get(models.Mission, FOUNDING_BONUS_MISSION) is not None:
        db.add(models.CreditCoin(
            owner_id=ben.id,
            mission_id=FOUNDING_BONUS_MISSION,
            amount_ebx=FOUNDING_BONUS_EBX,
            value=1.0,
        ))
        db.commit()
        db.refresh(ben)
    return ben


def set_role(
    db: Session,
    ben_id: int,
    role: str,
    staff: models.BenefactorAccount,
) -> models.BenefactorAccount:
    """Staff-only: promote/demote an account (benefactor | employee | admin)."""
    require_staff(staff)
    if role not in ("benefactor", "employee", "admin"):
        raise ValueError("role must be benefactor | employee | admin")
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Account not found")
    ben.role = role
    db.commit()
    db.refresh(ben)
    return ben


# ===========================================================================
# Memberships (ben <-> org, with role)
# ===========================================================================
def add_membership(
    db: Session,
    ben_id: int,
    org_id: str,
    role: str = "community",
) -> models.Membership:
    existing = db.scalar(
        select(models.Membership).where(
            models.Membership.ben_id == ben_id,
            models.Membership.org_id == org_id,
        )
    )
    if existing:
        existing.role = role
        db.commit()
        db.refresh(existing)
        return existing
    m = models.Membership(ben_id=ben_id, org_id=org_id, role=role)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def list_memberships(
    db: Session,
    ben_id: Optional[int] = None,
    org_id: Optional[str] = None,
) -> Sequence[models.Membership]:
    stmt = select(models.Membership)
    if ben_id is not None:
        stmt = stmt.where(models.Membership.ben_id == ben_id)
    if org_id is not None:
        stmt = stmt.where(models.Membership.org_id == org_id)
    return db.scalars(stmt).all()


ORG_ROLES = ("community", "rep", "executive", "beneficiary")
# Roles that carry org authority (may edit the mission page/budget, add members).
ORG_OPERATOR_ROLES = ("rep", "executive")


def get_membership(db: Session, ben_id: int, org_id: str) -> Optional[models.Membership]:
    return db.scalar(
        select(models.Membership).where(
            models.Membership.ben_id == ben_id,
            models.Membership.org_id == org_id,
        )
    )


def _require_org_operator(db: Session, actor: models.BenefactorAccount, org_id: str) -> None:
    """Org authority flows through Membership roles, not the account role.
    Staff pass for administration."""
    if getattr(actor, "is_staff", False):
        return
    m = get_membership(db, actor.id, org_id)
    if m is None or m.role not in ORG_OPERATOR_ROLES:
        raise PermissionError("Requires a rep/executive membership of this organization")


def create_membership(
    db: Session,
    org_id: str,
    data: schemas.MembershipCreate,
    actor: models.BenefactorAccount,
) -> models.Membership:
    """Invite/add a member (or change a member's role). Permission model:
      * anyone may join an org as 'community' (self-service follow);
      * rep/executive members (or staff) may add anyone at any role.
    The target ben is identified by ben_id, handle, or email."""
    if db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")
    if data.role not in ORG_ROLES:
        raise ValueError(f"role must be one of {ORG_ROLES}")

    target: Optional[models.BenefactorAccount] = None
    if data.ben_id is not None:
        target = db.get(models.BenefactorAccount, data.ben_id)
    elif data.handle:
        target = get_ben_by_handle(db, data.handle)
    elif data.email:
        target = get_ben_by_email(db, data.email)
    else:
        target = actor  # no target given = self
    if target is None:
        raise ValueError("Benefactor not found")

    self_community = target.id == actor.id and data.role == "community"
    if not self_community:
        _require_org_operator(db, actor, org_id)
    return add_membership(db, target.id, org_id, role=data.role)


def list_org_members(db: Session, org_id: str) -> list[dict]:
    """Org members list enriched with handles (MembershipDetail shape)."""
    rows = db.execute(
        select(models.Membership, models.BenefactorAccount.handle)
        .join(models.BenefactorAccount, models.BenefactorAccount.id == models.Membership.ben_id)
        .where(models.Membership.org_id == org_id)
        .order_by(models.Membership.joined_at.asc())
    ).all()
    return [
        {"id": m.id, "ben_id": m.ben_id, "org_id": m.org_id, "role": m.role,
         "joined_at": m.joined_at, "handle": handle}
        for m, handle in rows
    ]


# ===========================================================================
# Org claims — THE gate (click-through legal agreement) — Phase 2 (D)
# ===========================================================================
# A nominated (not self-registered) org has until the start of Phase 4
# (credit release) to claim. Phases before that keep the window open.
_CLAIMABLE_PHASES = ("pre", "initiative", "budget")


def get_claim(db: Session, mission_id: str, org_id: str) -> Optional[models.OrgClaim]:
    return db.scalar(
        select(models.OrgClaim).where(
            models.OrgClaim.mission_id == mission_id,
            models.OrgClaim.org_id == org_id,
        )
    )


def list_claims(
    db: Session,
    mission_id: Optional[str] = None,
    org_id: Optional[str] = None,
) -> Sequence[models.OrgClaim]:
    stmt = select(models.OrgClaim)
    if mission_id:
        stmt = stmt.where(models.OrgClaim.mission_id == mission_id)
    if org_id:
        stmt = stmt.where(models.OrgClaim.org_id == org_id)
    return db.scalars(stmt.order_by(models.OrgClaim.accepted_at.desc())).all()


def claim_mission(
    db: Session,
    mission_id: str,
    ben: models.BenefactorAccount,
    data: schemas.OrgClaimCreate,
    attestation_version: str = "draft",
    claimed_rate: float = 0.35,
) -> models.OrgClaim:
    """Record the click-through acceptance and grant the org authority over the
    mission's budget/sequence. Claiming:
      * verifies the actor is a rep/executive member of the org — or creates
        that ('rep') membership as part of claiming;
      * ensures a candidacy row exists (a claim implies a bid);
      * records the acceptance (attestation version + timestamp + ben);
      * bumps the mission's guaranteed-to-pool rate to the claimed rate.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    org = db.get(models.Organization, data.org_id)
    if org is None:
        raise ValueError("Organization not found")
    if mission.current_phase not in _CLAIMABLE_PHASES:
        raise ValueError(
            "The claim window for this mission has closed (claims are open until the start of Phase 4)"
        )
    if get_claim(db, mission_id, data.org_id) is not None:
        raise ValueError("This mission has already been claimed for this organization")

    # Membership: verify rep/executive, or create the rep membership now.
    m = get_membership(db, ben.id, data.org_id)
    if m is None:
        m = models.Membership(ben_id=ben.id, org_id=data.org_id, role="rep")
        db.add(m)
    elif m.role not in ORG_OPERATOR_ROLES:
        m.role = "rep"

    # A claim implies a candidacy (the org is bidding to run the mission).
    cand = db.scalar(
        select(models.MissionCandidacy).where(
            models.MissionCandidacy.mission_id == mission_id,
            models.MissionCandidacy.org_id == data.org_id,
        )
    )
    if cand is None:
        db.add(models.MissionCandidacy(
            mission_id=mission_id, org_id=data.org_id,
            submitted_by_id=ben.id, status="pending",
        ))

    claim = models.OrgClaim(
        mission_id=mission_id,
        org_id=data.org_id,
        ben_id=ben.id,
        kind=data.kind,
        attestation_version=data.attestation_version or attestation_version,
        member_name=data.member_name,
        member_position=data.member_position,
    )
    db.add(claim)
    # Guaranteed-to-pool rate bumps when a real representative shows up.
    mission.guaranteed_pool_rate = claimed_rate
    db.commit()
    db.refresh(claim)
    return claim


def org_state(
    db: Session,
    mission_id: str,
    org_id: str,
    unclaimed_rate: float = 0.20,
) -> dict:
    """The mission page's three booleans for one (mission, org):
    nominate → (register / claim) → elect. Plus supporting detail."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")
    cand = db.scalar(
        select(models.MissionCandidacy).where(
            models.MissionCandidacy.mission_id == mission_id,
            models.MissionCandidacy.org_id == org_id,
        )
    )
    claim = get_claim(db, mission_id, org_id)
    operators = [
        m for m in list_memberships(db, org_id=org_id) if m.role in ORG_OPERATOR_ROLES
    ]
    return {
        "mission_id": mission_id,
        "org_id": org_id,
        # the three booleans
        "nominated": cand is not None,
        "claimed": claim is not None,
        "elected": mission.winning_org_id == org_id,
        # supporting detail
        "registered": bool(operators),   # a real person operates this org
        "has_mission_statement": bool(cand and (cand.mission_statement or "").strip()),
        "candidacy_status": cand.status if cand else None,
        "approved": bool(cand and cand.status in ("approved", "won")),
        "claim_window_open": mission.current_phase in _CLAIMABLE_PHASES,
        "guaranteed_pool_rate": (
            mission.guaranteed_pool_rate
            if mission.guaranteed_pool_rate is not None else unclaimed_rate
        ),
    }


# ===========================================================================
# Mission candidacies (an org's bid to run a mission) — replaces OrgRegistration
# ===========================================================================
def create_candidacy(
    db: Session,
    data: schemas.MissionCandidacyCreate,
    submitted_by_id: Optional[int] = None,
) -> models.MissionCandidacy:
    if db.get(models.Mission, data.mission_id) is None:
        raise ValueError("Mission not found")
    if db.get(models.Organization, data.org_id) is None:
        raise ValueError("Organization not found")
    existing = db.scalar(
        select(models.MissionCandidacy).where(
            models.MissionCandidacy.mission_id == data.mission_id,
            models.MissionCandidacy.org_id == data.org_id,
        )
    )
    if existing:
        raise ValueError("Organization has already bid on this mission")
    cand = models.MissionCandidacy(
        mission_id=data.mission_id,
        org_id=data.org_id,
        mission_statement=data.mission_statement,
        submitted_by_id=submitted_by_id,
        status="pending",
    )
    db.add(cand)
    db.commit()
    db.refresh(cand)
    return cand


def list_candidacies(
    db: Session,
    mission_id: Optional[str] = None,
    org_id: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> Sequence[models.MissionCandidacy]:
    stmt = select(models.MissionCandidacy)
    if mission_id:
        stmt = stmt.where(models.MissionCandidacy.mission_id == mission_id)
    if org_id:
        stmt = stmt.where(models.MissionCandidacy.org_id == org_id)
    if status_filter:
        stmt = stmt.where(models.MissionCandidacy.status == status_filter)
    return db.scalars(stmt.order_by(models.MissionCandidacy.created_at.desc())).all()


def approve_candidacy(
    db: Session,
    candidacy_id: int,
    staff: models.BenefactorAccount,
) -> models.MissionCandidacy:
    """Staff-only: clear an org to build the mission page."""
    require_staff(staff)
    cand = db.get(models.MissionCandidacy, candidacy_id)
    if cand is None:
        raise ValueError("Candidacy not found")
    cand.status = "approved"
    cand.approved_by_id = staff.id
    db.commit()
    db.refresh(cand)
    return cand


# ===========================================================================
# Phase-1 voting (tiv election) — split shares, committed EBX, valence
# ===========================================================================
def get_p1_votes(db: Session, ben_id: int, mission_id: str) -> Sequence[models.VoteP1]:
    return db.scalars(
        select(models.VoteP1).where(
            models.VoteP1.ben_id == ben_id,
            models.VoteP1.mission_id == mission_id,
        )
    ).all()


def get_all_p1_votes(db: Session, ben_id: int) -> Sequence[models.VoteP1]:
    """Every phase-1 vote row this benefactor holds, across all missions.

    Powers the homepage election cards and the profile choices table with a
    single round-trip instead of one /p1/mine call per mission."""
    return db.scalars(
        select(models.VoteP1).where(models.VoteP1.ben_id == ben_id)
    ).all()


def replace_p1_shares(
    db: Session,
    ben_id: int,
    mission_id: str,
    shares: dict[str, float],
    ebx_total: int = 0,
    valences: Optional[dict[str, str]] = None,
) -> Sequence[models.VoteP1]:
    """Replace a ben's soft (uncommitted) phase-1 vote shares for a mission.

    `shares` maps tiv_id -> share (each >= 0.1, sum <= 1.0). Committed rows are
    immutable and any attempt to overwrite one raises. ebx_committed on each row
    is preserved (set it via commit_p1_ebx). Logs vote Transactions.
    """
    valences = valences or {}
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")

    cleaned: dict[str, float] = {}
    total = 0.0
    for tiv_id, raw in shares.items():
        try:
            v = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"Share for {tiv_id} is not numeric")
        if v <= 0:
            continue
        cleaned[tiv_id] = v   # continuous sliders — no 0.1 floor, no rounding
        total += v
    if total > SHARE_SUM_CAP + 1e-6:
        raise ValueError(f"Total share {total:.2f} exceeds {SHARE_SUM_CAP}")

    # Every tiv must belong to this mission.
    if cleaned:
        bad = db.scalars(
            select(models.Initiative.id).where(
                models.Initiative.id.in_(list(cleaned.keys())),
                models.Initiative.mission_id != mission_id,
            )
        ).all()
        if bad:
            raise ValueError(f"Initiatives {list(bad)} are not in mission {mission_id}")

    existing = {row.tiv_id: row for row in get_p1_votes(db, ben_id, mission_id)}
    # Pilot: a benefactor may change their slate at will, even after committing.
    # A vote carries weight without buying EBX: a no-EBX vote holds the base.
    if cleaned and ebx_total < BASE_VOTE_EBX:
        ebx_total = BASE_VOTE_EBX

    # Upsert.
    for tiv_id, share in cleaned.items():
        row = existing.get(tiv_id)
        valence = _valence_ok(valences.get(tiv_id, row.valence if row else "helpful"))
        ebx = ebx_total * share   # holdings split by share — float, no rounding
        if row is None:
            row = models.VoteP1(
                ben_id=ben_id, mission_id=mission_id, tiv_id=tiv_id,
                share=share, ebx_committed=ebx, valence=valence, committed=False,
            )
            db.add(row)
            _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p1",
                      action="CAST", target=tiv_id, old_value=None, new_value=share)
        else:
            if abs(float(row.share or 0) - share) > 1e-9:
                _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p1",
                          action="UPDATE", target=tiv_id, old_value=row.share, new_value=share)
            row.share = share
            row.ebx_committed = ebx
            row.valence = valence

    # Remove dropped rows — full replace, so withdrawing a vote drops its EBX too.
    for tiv_id, row in existing.items():
        if tiv_id not in cleaned:
            _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p1",
                      action="REMOVE", target=tiv_id, old_value=row.share, new_value=None)
            db.delete(row)

    db.commit()
    return get_p1_votes(db, ben_id, mission_id)


def commit_p1_ebx(
    db: Session,
    ben_id: int,
    mission_id: str,
    tiv_id: str,
    amount: int,
) -> models.VoteP1:
    """Commit EBX to a specific tiv in a mission's phase-1 election. Creates the
    vote row if absent. Only allowed while the mission is still pre/initiative."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if mission.current_phase not in ("pre", "initiative"):
        raise ValueError("Phase-1 commitments are closed for this mission")
    row = db.scalar(
        select(models.VoteP1).where(
            models.VoteP1.ben_id == ben_id,
            models.VoteP1.tiv_id == tiv_id,
        )
    )
    if row is None:
        row = models.VoteP1(
            ben_id=ben_id, mission_id=mission_id, tiv_id=tiv_id,
            share=SHARE_FLOOR, ebx_committed=amount, valence="helpful",
        )
        db.add(row)
    else:
        row.ebx_committed = amount   # SET, not add — caller controls the full amount
    _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p1",
              action="UPDATE", target=tiv_id, old_value=None, new_value=amount, amount_ebx=amount)
    db.commit()
    db.refresh(row)
    return row


def withdraw_p1(db: Session, ben_id: int, mission_id: str) -> dict:
    """Phase-2 withdrawal: a benefactor pulls back their phase-1 commitment in a
    mission, **minus the send** (the irrevocable donation slice). The send is
    20% if they backed the winning tiv, 10% otherwise; the rest is refunded.

    Allowed only during phase 2 — i.e. an initiative has been elected
    (`winning_tiv_id`) but the org race is still open (no `winning_org_id`, phase
    not yet `budget`). Once budgeting begins the pool locks. Returns the total
    refunded and the EBX left as the send.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if not mission.winning_tiv_id or mission.winning_org_id or mission.current_phase != "initiative":
        raise ValueError("Withdrawal is only open during phase 2 (after the initiative is elected, before budgeting)")

    refunded = 0.0
    kept = 0.0
    for row in get_p1_votes(db, ben_id, mission_id):
        committed = float(row.ebx_committed or 0)
        if committed <= 0:
            continue
        send_rate = P1_SEND_WIN if row.tiv_id == mission.winning_tiv_id else P1_SEND_LOSE
        keep = committed * send_rate          # the send stays in the pool
        give_back = committed - keep
        row.ebx_committed = keep
        refunded += give_back
        kept += keep
        if give_back > 0:
            db.add(models.Transaction(
                type="transfer", bucket="refund", ben_id=ben_id, mission_id=mission_id,
                phase="p2", target=row.tiv_id, amount_ebx=int(round(give_back)),
                note=f"phase-2 withdrawal — kept {send_rate:.0%} send",
            ))
    db.commit()
    recompute_pool(db, mission_id)
    return {"mission_id": mission_id, "refunded_ebx": round(refunded, 2), "send_kept_ebx": round(kept, 2)}


def commit_p1(db: Session, ben_id: int, mission_id: str) -> int:
    """Lock the ben's phase-1 slate for a mission. Returns rows committed."""
    rows = db.scalars(
        select(models.VoteP1).where(
            models.VoteP1.ben_id == ben_id,
            models.VoteP1.mission_id == mission_id,
            models.VoteP1.committed.is_(False),
        )
    ).all()
    for row in rows:
        row.committed = True
        _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p1",
                  action="UPDATE", target=row.tiv_id, old_value="soft", new_value="committed")
    db.commit()
    return len(rows)


# ===========================================================================
# Phase-2 voting (org election) — 1 org per ben, buy extra votes, harmful=block
# ===========================================================================
def cast_p2(
    db: Session,
    ben_id: int,
    mission_id: str,
    org_id: str,
    votes: int = 1,
    ebx_spent: int = 0,
    valence: str = "helpful",
    unapproved_ebx_cap: int = 10,
) -> models.VoteP2:
    """Upsert a ben's single org vote for a mission. votes>1 = bought extra
    votes; valence='harmful' = block the org. Sets vvv on first p2 vote.

    Election rules (Phase 2 polish):
      * the org must be a CANDIDATE for this mission (nominated/registered);
      * a candidacy must carry a mission statement to receive votes;
      * an UNAPPROVED (pending) org is capped at 1 vote / `unapproved_ebx_cap`
        EBX per ben — if the org is later rejected, that money is returned.
    """
    _valence_ok(valence)
    if votes < 1:
        raise ValueError("votes must be >= 1")
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")
    cand = db.scalar(
        select(models.MissionCandidacy).where(
            models.MissionCandidacy.mission_id == mission_id,
            models.MissionCandidacy.org_id == org_id,
        )
    )
    if cand is None:
        raise ValueError("This organization is not a candidate for this mission — nominate or register it first")
    if not (cand.mission_statement or "").strip():
        raise ValueError("This organization must submit a mission statement before it can receive votes")
    if cand.status == "pending" and (votes > 1 or ebx_spent > unapproved_ebx_cap):
        raise ValueError(
            f"This organization isn't approved yet — it's capped at 1 vote ({unapproved_ebx_cap} EBX) until approval"
        )

    row = db.scalar(
        select(models.VoteP2).where(
            models.VoteP2.ben_id == ben_id,
            models.VoteP2.mission_id == mission_id,
        )
    )
    action = "UPDATE" if row else "CAST"
    old = row.org_id if row else None
    if row is None:
        row = models.VoteP2(ben_id=ben_id, mission_id=mission_id, org_id=org_id)
        db.add(row)
    row.org_id = org_id
    row.votes = votes
    row.ebx_spent = ebx_spent
    row.valence = valence

    # Unlock the cause-color perk after the first org vote.
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is not None and not ben.vvv:
        ben.vvv = True

    _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p2",
              action=action, target=org_id, old_value=old, new_value=org_id, amount_ebx=ebx_spent)
    db.commit()
    db.refresh(row)
    return row


def commit_p2(db: Session, ben_id: int, mission_id: str) -> int:
    rows = db.scalars(
        select(models.VoteP2).where(
            models.VoteP2.ben_id == ben_id,
            models.VoteP2.mission_id == mission_id,
            models.VoteP2.committed.is_(False),
        )
    ).all()
    for row in rows:
        row.committed = True
        _log_vote(db, ben_id=ben_id, mission_id=mission_id, phase="p2",
                  action="UPDATE", target=row.org_id, old_value="soft", new_value="committed")
    db.commit()
    return len(rows)


# ===========================================================================
# Tallies & finalization
# ===========================================================================
def p1_tally(db: Session, mission_id: str, size_factor: float = 1.0) -> dict:
    """Per-tiv raw + vote-weighted shares for a mission's phase-1 election.

    weight(b) = 1 + b_contribution / (pool_excluding_b * n_votes * size_factor)
    Each vote contributes share * weight * sign(valence) (harmful subtracts).
    """
    rows = db.scalars(select(models.VoteP1).where(models.VoteP1.mission_id == mission_id)).all()
    per_tiv: dict[str, dict] = {}
    for v in rows:
        e = per_tiv.setdefault(v.tiv_id, {"votes": 0.0, "voters": 0})
        # 0.1 vote = 1 EBX: a ben's weight on a tiv is max(share, ebx/10), so a
        # plain split counts its share and 10 committed EBX = 1 vote. harmful
        # subtracts; neutral is 0.
        # Winner is decided by EBX held (base + bought + converted), split by
        # share — not the raw split. 10 EBX = 1 vote.
        e["votes"] += (float(v.ebx_committed or 0) / EBX_PER_VOTE) * VALENCE_SIGN[v.valence]
        e["voters"] += 1

    total = sum(max(0.0, s["votes"]) for s in per_tiv.values()) or 1.0
    entries = [
        {"tiv_id": tid,
         "votes": round(s["votes"], 1),
         "weighted_share": round(max(0.0, s["votes"]) / total, 4),
         "voter_count": s["voters"]}
        for tid, s in sorted(per_tiv.items(), key=lambda kv: -kv[1]["votes"])
    ]
    return {
        "mission_id": mission_id,
        "size_factor": size_factor,
        "pool_total_ebx": int(sum(float(v.ebx_committed or 0) for v in rows)),
        "entries": entries,
    }


def p2_tally(db: Session, mission_id: str) -> dict:
    """Per-org net vote count for a mission's phase-2 election. Blocks (harmful)
    subtract; support (helpful) adds; neutral is 0."""
    votes = db.scalars(select(models.VoteP2).where(models.VoteP2.mission_id == mission_id)).all()
    per_org: dict[str, dict] = {}
    for v in votes:
        e = per_org.setdefault(v.org_id, {"net_votes": 0, "voters": 0})
        e["net_votes"] += int(v.votes) * int(VALENCE_SIGN[v.valence])
        e["voters"] += 1
    entries = [
        {"org_id": oid, "net_votes": s["net_votes"], "voter_count": s["voters"]}
        for oid, s in sorted(per_org.items(), key=lambda kv: -kv[1]["net_votes"])
    ]
    return {"mission_id": mission_id, "entries": entries}


def _carry_losers_forward(db: Session, mission: models.Mission, losers: list[models.Initiative]) -> None:
    """Roll losing initiatives into their cause's NEXT-cycle election.

    Each loser is re-listed (status 'suggested') under the cause's cycle+1 mission
    (created if it doesn't exist yet). Every backer's phase-1 commitment moves with
    it at (1 - COMMITMENT_FUND_SKIM); the skim is booked to the global commitment
    fund as a `transfer` to bucket 'commitment_fund'. Idempotent per finalize call.
    """
    from . import bootstrap  # local import avoids a module-load cycle

    next_cycle = (mission.cycle_num or 0) + 1
    next_mid = bootstrap.mission_id(mission.cause_id, next_cycle)
    if db.get(models.Mission, next_mid) is None:
        bootstrap.ensure_mission(db, mission.cause_id, next_cycle)

    for tiv in losers:
        tiv.mission_id = next_mid
        tiv.status = "suggested"   # re-listed as a fresh candidate next cycle
        for v in db.scalars(select(models.VoteP1).where(models.VoteP1.tiv_id == tiv.id)).all():
            committed = float(v.ebx_committed or 0)
            skim = committed * COMMITMENT_FUND_SKIM
            v.ebx_committed = committed - skim          # 90% carries to next cycle
            v.mission_id = next_mid
            v.committed = False                          # carried, but adjustable next cycle
            if skim > 0:
                db.add(models.Transaction(
                    type="transfer", bucket=COMMITMENT_FUND_BUCKET,
                    ben_id=v.ben_id, mission_id=mission.id, phase="p1",
                    target=tiv.id, amount_ebx=int(round(skim)),
                    note=f"loser carryover skim {COMMITMENT_FUND_SKIM:.0%} {mission.id}->{next_mid}",
                ))


def finalize_p1(db: Session, mission_id: str) -> Optional[str]:
    """Elect the leading phase-1 tiv. Sets mission.winning_tiv_id, marks the
    winner 'active', and rolls every losing initiative (with 90% of its committed
    EBX) into the cause's next-cycle election — skimming 10% to the commitment
    fund. Returns the winning tiv id, or None if there's no vote signal yet."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    tally = p1_tally(db, mission_id)
    if not tally["entries"] or tally["entries"][0]["weighted_share"] <= 0:
        return None
    winner_id = tally["entries"][0]["tiv_id"]
    mission.winning_tiv_id = winner_id
    mission.current_phase = "initiative"
    # Status vocabulary is just suggested | active | resolved. The elected tiv
    # becomes 'active' (its mission is now in flight through phases 2-4); losing
    # tivs stay 'suggested' and roll into the next cycle (below).
    # IMPORTANT: attach the winner to this mission explicitly. A vote references a
    # tiv_id, but that tiv's own mission_id can be unset/drifted; without this the
    # winner would never be marked active and phase-2 would appear "skipped".
    winner = db.get(models.Initiative, winner_id)
    if winner is not None:
        winner.mission_id = mission_id
        winner.status = "active"
    losers = [
        t for t in db.scalars(
            select(models.Initiative).where(models.Initiative.mission_id == mission_id)
        ).all()
        if t.id != winner_id
    ]
    if losers:
        _carry_losers_forward(db, mission, losers)
    db.commit()
    return winner_id


def finalize_p2(db: Session, mission_id: str) -> Optional[str]:
    """Elect the winning org. Sets mission.winning_org_id, flips the winning
    candidacy to 'won' (others 'lost'), advances to the budget phase."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    tally = p2_tally(db, mission_id)
    if not tally["entries"] or tally["entries"][0]["net_votes"] <= 0:
        return None
    winner_org = tally["entries"][0]["org_id"]
    mission.winning_org_id = winner_org
    mission.current_phase = "budget"
    for cand in db.scalars(select(models.MissionCandidacy).where(models.MissionCandidacy.mission_id == mission_id)).all():
        cand.status = "won" if cand.org_id == winner_org else "lost"
        if cand.org_id == winner_org:
            cand.p2_vote_tally = tally["entries"][0]["net_votes"]
    db.commit()
    return winner_org


# ===========================================================================
# Pool (derived money rollup — recompute on commit / distribution)
# ===========================================================================
def _pool_total(db: Session, mission_id: str) -> int:
    """Total EBX in the pool = everything committed (p1) + spent (p2). No money
    is refunded, so the pool is the full committed amount."""
    p1 = db.scalar(
        select(sqlfunc.coalesce(sqlfunc.sum(models.VoteP1.ebx_committed), 0))
        .where(models.VoteP1.mission_id == mission_id)
    ) or 0
    p2 = db.scalar(
        select(sqlfunc.coalesce(sqlfunc.sum(models.VoteP2.ebx_spent), 0))
        .where(models.VoteP2.mission_id == mission_id)
    ) or 0
    return int(p1) + int(p2)


def recompute_pool(db: Session, mission_id: str) -> models.Pool:
    """Rebuild the Pool cache from the committed votes. total_locked is the whole
    pool (nothing is refunded); from_winners/from_losers split it by whether the
    contributor backed the winning tiv/org (NULL winners count as losers)."""
    mission = db.get(models.Mission, mission_id)
    win_tiv = mission.winning_tiv_id if mission else None
    win_org = mission.winning_org_id if mission else None

    p1_total = from_winners = from_losers = 0
    for v in db.scalars(select(models.VoteP1).where(models.VoteP1.mission_id == mission_id)).all():
        amt = int(v.ebx_committed or 0)
        p1_total += amt
        if win_tiv and v.tiv_id == win_tiv:
            from_winners += amt
        else:
            from_losers += amt
    p2_total = 0
    for v in db.scalars(select(models.VoteP2).where(models.VoteP2.mission_id == mission_id)).all():
        amt = int(v.ebx_spent or 0)
        p2_total += amt
        if win_org and v.org_id == win_org:
            from_winners += amt
        else:
            from_losers += amt

    pool = db.get(models.Pool, mission_id)
    if pool is None:
        pool = models.Pool(mission_id=mission_id)
        db.add(pool)
    pool.phase1_total_ebx = p1_total
    pool.phase2_total_ebx = p2_total
    pool.pool_from_winners = from_winners
    pool.pool_from_losers = from_losers
    pool.total_locked = p1_total + p2_total
    db.commit()
    db.refresh(pool)
    return pool


# ===========================================================================
# Money allocation — budgeting range + resolution-time distribution
# ===========================================================================
def mission_budget_range(db: Session, mission_id: str) -> dict:
    """Read-only helper for the BUDGETING phase. The org budgets between a
    concrete floor and an OPEN ceiling:
        min (concrete) = guaranteed 1/4 + 1/16 advance = 10/32 of the pool now.
        max (flexible) = min + the 9/32 flexible remainder — but NOT capped: the
                         pool can still grow as new donations arrive, so both
                         figures rise. The frontend should recompute from the
                         fractions as the pool changes rather than treat max as
                         a hard ceiling.
    """
    pool = _pool_total(db, mission_id)
    org_min = round(pool * ORG_GUARANTEED)          # concrete floor on today's pool
    flexible = round(pool * FLEXIBLE)
    return {
        "mission_id": mission_id,
        "pool_ebx": pool,
        "org_min_budget": org_min,                  # concrete guaranteed minimum
        "org_max_budget": org_min + flexible,       # current max; see max_is_capped
        "max_is_capped": False,                     # pool may still grow -> max is open
        "guaranteed_fraction": ORG_GUARANTEED,      # 10/32
        "flexible_fraction": FLEXIBLE,              # 9/32
        "flexible_ebx": flexible,
        "en_cut": round(pool * (EN_MISSION + EN_ADVANCE)),
    }


def distribute_mission(db: Session, mission_id: str) -> dict:
    """Lock the pool at resolution and write the guaranteed allocation ledger.

    NOTHING is refunded — every committed EBX stays in the pool. Only the
    guaranteed slices move now; the flexible remainder is held for the credit-
    release phase (org or back to benefactors). 32nds table is in the constants.

    Buckets (written only when pool > POOL_THRESHOLD):
      earthbux    EN mission-side (1/4) + EN advance (1/16)        = 5/16
      org         org mission-side (1/4) + org advance (1/16)      = 5/16
      reward      best-case + context/analysis + comments (1/32 each)
      pool        the 9/32 flexible remainder, held for credit release
    Idempotent: refuses if the mission is already resolved.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if mission.current_phase == "resolution":
        raise ValueError("Mission already distributed")
    if not mission.winning_tiv_id or not mission.winning_org_id:
        raise ValueError("Mission must have both a winning tiv and org before distribution")

    pool = _pool_total(db, mission_id)

    def _T(bucket: str, frac: float, note: str, org: Optional[str] = None) -> int:
        amount = round(pool * frac)
        if amount > 0:
            db.add(models.Transaction(
                type="transfer", mission_id=mission_id, bucket=bucket,
                counterparty_org_id=org, amount_ebx=amount, note=note,
            ))
        return amount

    alloc: dict[str, int] = {}
    if pool > POOL_THRESHOLD:
        win_org = mission.winning_org_id
        # Earthbux News: mission-side 1/4 + 1/16 advance (= 5/16).
        alloc["en_mission"] = _T("earthbux", EN_MISSION, "EN mission-side budget (1/4)")
        alloc["en_advance"] = _T("earthbux", EN_ADVANCE, "EN advance 1/16 (releases with case reward)")
        # Organization: mission-side 1/4 + 1/16 advance (= 5/16).
        alloc["org_mission"] = _T("org", ORG_MISSION, "org mission-side budget (1/4)", org=win_org)
        alloc["org_advance"] = _T("org", ORG_ADVANCE, "org advance 1/16 (releases with case reward)", org=win_org)
        # Three benefactor post-type rewards (1/32 each).
        alloc["reward_best_case"] = _T("reward", REWARD_BEST_CASE, "best-case post reward")
        alloc["reward_context_or_analysis"] = _T("reward", REWARD_CONTEXT_OR_ANALYSIS, "context/analysis post reward")
        alloc["reward_comments"] = _T("reward", REWARD_COMMENTS, "comments post reward")
        # Whatever is left is the 9/32 flexible remainder, held in the pool.
        flexible = pool - sum(alloc.values())
        if flexible > 0:
            db.add(models.Transaction(type="transfer", mission_id=mission_id, bucket="pool",
                                      amount_ebx=flexible, note="flexible remainder (credit release: org or benefactors)"))
        alloc["flexible_remainder"] = flexible
        threshold_cleared = True
    else:
        # Below threshold: EN takes nothing; the whole pool is held for the
        # org / benefactors at credit release.
        db.add(models.Transaction(type="transfer", mission_id=mission_id, bucket="pool",
                                  amount_ebx=pool, note="below threshold — whole pool held for org/benefactors"))
        alloc["flexible_remainder"] = pool
        threshold_cleared = False

    mission.current_phase = "resolution"
    mission.budget = alloc.get("org_mission", 0) + alloc.get("org_advance", 0)
    # The winning initiative reaches its terminal status. (suggested|active|resolved)
    win_tiv = db.get(models.Initiative, mission.winning_tiv_id)
    if win_tiv is not None:
        win_tiv.status = "resolved"
    db.commit()
    recompute_pool(db, mission_id)
    return {
        "mission_id": mission_id,
        "pool_ebx": pool,
        "threshold_cleared": threshold_cleared,
        "allocation": alloc,
    }


# ===========================================================================
# Posts & reactions (helpful | neutral | harmful)
# ===========================================================================
def list_posts(
    db: Session,
    mission_id: Optional[str] = None,
    tiv_id: Optional[str] = None,
    cause_id: Optional[str] = None,
    category: Optional[str] = None,
    parent_id: Optional[str] = None,
    roots_only: bool = False,
    limit: int = 50,
) -> Sequence[models.Post]:
    stmt = select(models.Post)
    if mission_id:
        stmt = stmt.where(models.Post.mission_id == mission_id)
    if tiv_id:
        stmt = stmt.where(models.Post.tiv_id == tiv_id)
    if cause_id:
        stmt = stmt.where(models.Post.cause_id == cause_id)
    if category:
        stmt = stmt.where(models.Post.category == category)
    # parent_id set → that post's comments (oldest first, thread order).
    if parent_id:
        stmt = stmt.where(models.Post.parent_id == parent_id)
        return db.scalars(stmt.order_by(models.Post.created_at.asc()).limit(limit)).all()
    # roots_only → exclude comments from a feed so threads don't double-list.
    if roots_only:
        stmt = stmt.where(models.Post.parent_id.is_(None))
    return db.scalars(stmt.order_by(models.Post.created_at.desc()).limit(limit)).all()


def list_org_posts(db: Session, org_id: str, limit: int = 50) -> Sequence[models.Post]:
    """Posts AUTHORED by an org (org_update etc.) — the org page feed."""
    return db.scalars(
        select(models.Post)
        .where(models.Post.org_author_id == org_id)
        .order_by(models.Post.created_at.desc())
        .limit(limit)
    ).all()


# Categories only staff may author.
_STAFF_ONLY_CATEGORIES = {"editorial", "headline"}


def create_post(
    db: Session,
    data: schemas.PostCreate,
    author: Optional[models.BenefactorAccount] = None,
) -> models.Post:
    if data.category in _STAFF_ONLY_CATEGORIES:
        if author is None:
            raise PermissionError("editorial/headline posts require an employee account")
        require_staff(author)
    post = models.Post(**data.model_dump())
    # Attribute ben-authored posts to the signed-in account so the profile
    # "my posts" history + helpful-post rewards can find them.
    if author is not None and post.author_type == "ben" and post.ben_author_id is None:
        post.ben_author_id = author.id
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def react_to_post(db: Session, post_id: str, ben_id: int, value: str) -> models.Post:
    """Upsert a ben's reaction and keep the denormalised counts in sync."""
    _valence_ok(value)
    post = db.get(models.Post, post_id)
    if post is None:
        raise ValueError("Post not found")
    existing = db.scalar(
        select(models.PostVote).where(
            models.PostVote.post_id == post_id,
            models.PostVote.ben_id == ben_id,
        )
    )
    if existing:
        if existing.value == value:
            return post
        _bump_post_count(post, existing.value, -1)
        existing.value = value
    else:
        db.add(models.PostVote(post_id=post_id, ben_id=ben_id, value=value))
    _bump_post_count(post, value, +1)
    db.commit()
    db.refresh(post)
    return post


def _bump_post_count(post: models.Post, value: str, delta: int) -> None:
    if value == "helpful":
        post.helpful_count = max(0, (post.helpful_count or 0) + delta)
    elif value == "neutral":
        post.neutral_count = max(0, (post.neutral_count or 0) + delta)
    elif value == "harmful":
        post.harmful_count = max(0, (post.harmful_count or 0) + delta)


# ===========================================================================
# Watchlist (watched_tiv_ids JSON)
# ===========================================================================
def _watched(account: models.BenefactorAccount) -> list[str]:
    if not account.watched_tiv_ids:
        return []
    try:
        parsed = json.loads(account.watched_tiv_ids)
        return [str(x) for x in parsed] if isinstance(parsed, list) else []
    except (TypeError, ValueError):
        return []


def list_watched(db: Session, account: models.BenefactorAccount) -> list[str]:
    return _watched(account)


def add_watch(db: Session, account: models.BenefactorAccount, tiv_id: str) -> list[str]:
    cur = _watched(account)
    if tiv_id not in cur:
        cur.append(tiv_id)
        account.watched_tiv_ids = json.dumps(cur)
        db.commit()
    return cur


def remove_watch(db: Session, account: models.BenefactorAccount, tiv_id: str) -> list[str]:
    cur = [x for x in _watched(account) if x != tiv_id]
    account.watched_tiv_ids = json.dumps(cur) if cur else None
    db.commit()
    return cur


# ===========================================================================
# Credit coins
# ===========================================================================
def list_credit_coins(db: Session, ben_id: int) -> Sequence[models.CreditCoin]:
    return db.scalars(
        select(models.CreditCoin)
        .where(models.CreditCoin.owner_id == ben_id)
        .order_by(models.CreditCoin.issued_at.desc())
    ).all()


# ===========================================================================
# Ledger (transactions)
# ===========================================================================
def _log_vote(
    db: Session,
    *,
    ben_id: Optional[int],
    mission_id: Optional[str],
    phase: str,
    action: str,
    target: Optional[str] = None,
    old_value=None,
    new_value=None,
    amount_ebx: int = 0,
) -> None:
    """Append one vote-mutation row. Caller commits with the mutation."""
    db.add(models.Transaction(
        type="vote", ben_id=ben_id, mission_id=mission_id, phase=phase,
        action=action, target=target,
        old_value=None if old_value is None else str(old_value),
        new_value=None if new_value is None else str(new_value),
        amount_ebx=amount_ebx,
    ))


def list_transactions(
    db: Session,
    mission_id: Optional[str] = None,
    ben_id: Optional[int] = None,
    type_filter: Optional[str] = None,
    bucket: Optional[str] = None,
    limit: int = 200,
) -> Sequence[models.Transaction]:
    stmt = select(models.Transaction)
    if mission_id:
        stmt = stmt.where(models.Transaction.mission_id == mission_id)
    if ben_id is not None:
        stmt = stmt.where(models.Transaction.ben_id == ben_id)
    if type_filter:
        stmt = stmt.where(models.Transaction.type == type_filter)
    if bucket:
        stmt = stmt.where(models.Transaction.bucket == bucket)
    return db.scalars(stmt.order_by(models.Transaction.created_at.desc()).limit(limit)).all()


# ===========================================================================
# Query console (staff-only data tool)
# ===========================================================================
# Whitelist of entities the console may read, mapped to their model.
_QUERY_ENTITIES = {
    "causes": models.Cause,
    "missions": models.Mission,
    "initiatives": models.Initiative,
    "organizations": models.Organization,
    "benefactor_accounts": models.BenefactorAccount,
    "memberships": models.Membership,
    "mission_candidacies": models.MissionCandidacy,
    "votes_p1": models.VoteP1,
    "votes_p2": models.VoteP2,
    "pools": models.Pool,
    "credit_coins": models.CreditCoin,
    "posts": models.Post,
    "post_votes": models.PostVote,
    "transactions": models.Transaction,
    "queries": models.Query,
}


def query_entities() -> list[str]:
    """The filetree of browsable tables for admin.html."""
    return sorted(_QUERY_ENTITIES)


def create_query(db: Session, data: schemas.QueryCreate, staff: models.BenefactorAccount) -> models.Query:
    require_staff(staff)
    q = models.Query(**data.model_dump(), created_by_id=staff.id)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def list_queries(db: Session, staff: models.BenefactorAccount) -> Sequence[models.Query]:
    require_staff(staff)
    return db.scalars(
        select(models.Query)
        .where((models.Query.shared.is_(True)) | (models.Query.created_by_id == staff.id))
        .order_by(models.Query.created_at.desc())
    ).all()


def run_query(
    db: Session,
    staff: models.BenefactorAccount,
    entity: str,
    filters: Optional[dict] = None,
    limit: int = 100,
) -> list[dict]:
    """Read-only, whitelisted entity reader for the console. Filters are simple
    equality (column == value) against real columns only — no raw SQL path."""
    require_staff(staff)
    model = _QUERY_ENTITIES.get(entity)
    if model is None:
        raise ValueError(f"Unknown entity {entity!r}")
    stmt = select(model)
    cols = {c.name for c in model.__table__.columns}
    for key, val in (filters or {}).items():
        if key not in cols:
            raise ValueError(f"Unknown column {key!r} on {entity}")
        stmt = stmt.where(getattr(model, key) == val)
    rows = db.scalars(stmt.limit(min(limit, 500))).all()
    return [{c.name: getattr(r, c.name) for c in model.__table__.columns} for r in rows]

# end of crud.py (build phase 2)
