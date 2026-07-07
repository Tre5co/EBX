"""PROPOSAL: Pydantic v2 request/response schemas for the v2 (mission-centric)
API. Parallel to schemas.py; nothing imports it until cutover.

Naming mirrors models_v2: ben / tiv / org. `*Create` = request bodies,
`*Read` = responses (ConfigDict(from_attributes=True) so they read straight off
ORM objects). Valence and post-vote values are helpful | neutral | harmful.
"""
from __future__ import annotations

import json as _json
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Valence = Literal["helpful", "neutral", "harmful"]


# ---------------------------------------------------------------------------
# Cause
# ---------------------------------------------------------------------------
class CauseBase(BaseModel):
    name: str
    color: str
    emoji: Optional[str] = None
    description: Optional[str] = None


class CauseCreate(CauseBase):
    id: str
    index: int


class CauseRead(CauseBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    index: int


# ---------------------------------------------------------------------------
# Mission (the spine)
# ---------------------------------------------------------------------------
class MissionBase(BaseModel):
    cause_id: str
    cycle_num: int
    current_phase: str = "pre"  # pre | initiative | budget | credit | resolution


class MissionCreate(MissionBase):
    id: str


class MissionRead(MissionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    started_at: Optional[datetime] = None
    winning_tiv_id: Optional[str] = None
    winning_org_id: Optional[str] = None
    budget: int = 0
    spent: int = 0
    credit_value: float = 1.0
    guaranteed_pool_rate: Optional[float] = None  # NULL = unclaimed default
    updated_at: datetime


# ---------------------------------------------------------------------------
# Initiative (tiv)
# ---------------------------------------------------------------------------
class InitiativeBase(BaseModel):
    title: str
    description: Optional[str] = None
    emoji: Optional[str] = None
    cause_id: str
    status: str = "suggested"  # suggested | active | resolved (elected tiv -> active; -> resolved at distribution)


class InitiativeCreate(InitiativeBase):
    id: str
    mission_id: Optional[str] = None
    proposer_ben_id: Optional[int] = None
    proposer_org_id: Optional[str] = None


class InitiativeRead(InitiativeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    mission_id: Optional[str] = None
    proposer_ben_id: Optional[int] = None
    proposer_org_id: Optional[str] = None
    proposed_at: datetime
    rating_avg: float = 0.0
    rating_count: int = 0
    logo_url: Optional[str] = None
    approved: bool = False
    ebx_committed: float = 0   # aggregate committed EBX across all phase-1 votes


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------
class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    website_link: Optional[str] = None
    founded_year: Optional[int] = None
    verified: bool = False


class OrganizationCreate(OrganizationBase):
    id: str
    founding_member_id: Optional[int] = None


class OrganizationRead(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    founding_member_id: Optional[int] = None
    joined_at: Optional[datetime] = None
    score: float = 0.0
    logo_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Benefactor account & auth (role = the employee category)
# ---------------------------------------------------------------------------
class BenefactorCreate(BaseModel):
    email: EmailStr
    handle: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8, max_length=72)


class BenefactorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    handle: str
    is_active: bool
    role: str = "benefactor"  # benefactor | employee | admin
    vvv: bool = False
    created_at: datetime
    watched_tiv_ids: list[str] = Field(default_factory=list)

    @field_validator("watched_tiv_ids", mode="before")
    @classmethod
    def _parse_watched(cls, v: object) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        try:
            parsed = _json.loads(v)  # type: ignore[arg-type]
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except (TypeError, ValueError):
            pass
        return []


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None  # ben id as string
    exp: Optional[int] = None


# ---------------------------------------------------------------------------
# Membership
# ---------------------------------------------------------------------------
OrgRole = Literal["community", "rep", "executive", "beneficiary"]


class MembershipCreate(BaseModel):
    """Invite/add a member to an org. Identify the ben by id OR handle/email."""
    ben_id: Optional[int] = None
    handle: Optional[str] = None
    email: Optional[str] = None
    role: OrgRole = "community"


class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ben_id: int
    org_id: str
    role: str  # community | rep | executive | beneficiary
    joined_at: datetime


class MembershipDetail(MembershipRead):
    """Membership row enriched with the member's handle (org members list)."""
    handle: Optional[str] = None


# ---------------------------------------------------------------------------
# Mission candidacy (org's bid to run a mission)
# ---------------------------------------------------------------------------
class MissionCandidacyCreate(BaseModel):
    mission_id: str
    org_id: str
    mission_statement: Optional[str] = None


class MissionCandidacyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mission_id: str
    org_id: str
    mission_statement: Optional[str] = None
    status: str = "pending"  # pending | approved | withdrawn | won | lost
    submitted_by_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    p2_vote_tally: int = 0
    created_at: datetime


# ---------------------------------------------------------------------------
# Org self-registration / nomination (public application) — Build Phase 2 (A)
# ---------------------------------------------------------------------------
class OrganizationRegister(BaseModel):
    """Public org application. kind='registration' = a real member registers
    (founding executive membership); kind='nomination' = a benefactor puts an
    org forward (no membership created). Pass org_id to use an existing org
    (picked from a duplicate match) instead of creating a new one; pass
    force=True to create despite fuzzy matches."""
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = None
    website_link: Optional[str] = None
    founded_year: Optional[int] = None
    logo_url: Optional[str] = None
    kind: Literal["registration", "nomination"] = "registration"
    org_id: Optional[str] = None          # use existing org instead of creating
    mission_id: Optional[str] = None      # also enter this mission's org race
    mission_statement: Optional[str] = None
    member_name: Optional[str] = None     # registration attestation details
    member_position: Optional[str] = None
    force: bool = False


class OrgMatch(BaseModel):
    org_id: str
    name: str
    score: float                          # 0..1 fuzzy similarity


class OrgRegisterResult(BaseModel):
    created: bool                         # False = duplicates found, nothing written
    org: Optional[OrganizationRead] = None
    membership: Optional[MembershipRead] = None
    candidacy: Optional[MissionCandidacyRead] = None
    matches: list[OrgMatch] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Org claim (THE gate) — click-through legal acceptance — Build Phase 2 (D)
# ---------------------------------------------------------------------------
class OrgClaimCreate(BaseModel):
    org_id: str
    kind: Literal["claim", "register"] = "claim"
    attestation_version: Optional[str] = None   # defaults to settings.attestation_version
    member_name: Optional[str] = None
    member_position: Optional[str] = None


class OrgClaimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mission_id: str
    org_id: str
    ben_id: int
    kind: str
    attestation_version: str
    member_name: Optional[str] = None
    member_position: Optional[str] = None
    accepted_at: datetime


# ---------------------------------------------------------------------------
# VoteP1 (tiv election — split shares; carries committed EBX)
# ---------------------------------------------------------------------------
class VoteP1Create(BaseModel):
    tiv_id: str
    share: float = Field(default=1.0, ge=0.1, le=1.0)
    ebx_committed: int = Field(default=0, ge=0)
    valence: Valence = "helpful"


class VoteP1Shares(BaseModel):
    """Full shares map a ben PUTs for a mission's phase-1 election.

    initiative shares must each be >= 0.1 and sum to <= 1.0 (validated server-side).
    """
    mission_id: str
    shares: dict[str, float]
    ebx: int = 0   # total EBX committed, split across the slate by share (replace)


class VoteP1Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ben_id: int
    mission_id: str
    tiv_id: str
    share: float = 1.0
    ebx_committed: float = 0   # holdings x share (continuous — not rounded)
    valence: Valence = "helpful"
    committed: bool = False
    created_at: datetime


# ---------------------------------------------------------------------------
# VoteP2 (org election — 1 org, buy extra votes; harmful = block)
# ---------------------------------------------------------------------------
class VoteP2Create(BaseModel):
    org_id: str
    votes: int = Field(default=1, ge=1)
    ebx_spent: int = Field(default=0, ge=0)
    valence: Valence = "helpful"


class VoteP2Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ben_id: int
    mission_id: str
    org_id: str
    votes: int = 1
    ebx_spent: int = 0
    valence: Valence = "helpful"
    committed: bool = False
    created_at: datetime


# ---------------------------------------------------------------------------
# Pool (derived money rollup)
# ---------------------------------------------------------------------------
class PoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    mission_id: str
    phase1_total_ebx: int = 0
    phase2_total_ebx: int = 0
    pool_from_winners: int = 0
    pool_from_losers: int = 0
    total_locked: int = 0
    updated_at: datetime


# ---------------------------------------------------------------------------
# CreditCoin
# ---------------------------------------------------------------------------
class CreditCoinRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    mission_id: str
    amount_ebx: int
    value: float = 1.0
    issued_at: datetime
    redeemed: bool = False


# ---------------------------------------------------------------------------
# Posts & post votes
# ---------------------------------------------------------------------------
class PostBase(BaseModel):
    category: str = "editorial"  # case|context|analysis|evaluation|org_update|editorial|headline
    title: Optional[str] = None
    body: str
    author_type: str = "earthbux"  # ben | org | earthbux
    mission_id: Optional[str] = None
    tiv_id: Optional[str] = None
    cause_id: Optional[str] = None
    org_id: Optional[str] = None     # target org (evaluation / org-scoped posts)
    stance: Optional[str] = None     # case: for|against · evaluation: positive|negative
    parent_id: Optional[str] = None  # set for a comment (reply to another post)
    image_url: Optional[str] = None  # attached image (data URL or path)


class PostCreate(PostBase):
    id: str
    ben_author_id: Optional[int] = None
    org_author_id: Optional[str] = None


class PostRead(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    ben_author_id: Optional[int] = None
    org_author_id: Optional[str] = None
    helpful_count: int = 0
    neutral_count: int = 0
    harmful_count: int = 0
    created_at: datetime


class PostVoteCreate(BaseModel):
    value: Valence


class PostVoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: str
    ben_id: int
    value: Valence
    created_at: datetime


# ---------------------------------------------------------------------------
# Query (employee-only data tool)
# ---------------------------------------------------------------------------
class QueryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    entity: Optional[str] = None
    filters: Optional[str] = None  # JSON string
    sort: Optional[str] = None
    sql: Optional[str] = None
    shared: bool = False


class QueryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    entity: Optional[str] = None
    filters: Optional[str] = None
    sort: Optional[str] = None
    sql: Optional[str] = None
    created_by_id: Optional[int] = None
    shared: bool = False
    created_at: datetime
    last_run_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Transaction (the ledger — read-only out of the API)
# ---------------------------------------------------------------------------
class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str  # vote | transfer
    ben_id: Optional[int] = None
    mission_id: Optional[str] = None
    phase: Optional[str] = None
    action: Optional[str] = None
    target: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    bucket: Optional[str] = None  # pool|org|earthbux|evaluation|credit|refund
    counterparty_org_id: Optional[str] = None
    amount_ebx: int = 0
    note: Optional[str] = None
    created_at: datetime
