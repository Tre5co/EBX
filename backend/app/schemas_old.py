"""Pydantic v2 request/response schemas for the Earthbucks API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import json as _json

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
# Organization
# ---------------------------------------------------------------------------
class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    mission_statement: Optional[str] = None
    website_link: Optional[str] = None
    verified: bool = False
    founded_year: Optional[int] = None


class OrganizationCreate(OrganizationBase):
    id: str
    cause_ids: list[str] = Field(default_factory=list)


class OrganizationRead(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    score: float = 0.0
    logo_url: Optional[str] = None
    date_approved: Optional[datetime] = None
    causes: list[CauseRead] = []


# ---------------------------------------------------------------------------
# Initiative
# ---------------------------------------------------------------------------
class InitiativeBase(BaseModel):
    title: str
    description: Optional[str] = None
    emoji: Optional[str] = None
    proposed_by: str = "benefactor"  # benefactor | org
    cycle_num: int = 0
    status: str = "suggested"


class InitiativeCreate(InitiativeBase):
    id: str
    cause_id: str
    proposer_benefactor_id: Optional[int] = None
    proposer_org_id: Optional[str] = None


class InitiativeRead(InitiativeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    index: Optional[int] = None
    cause_id: str
    rating: float = 0.0
    # build-seq 4 — denormalised rating rollup served to the table.
    rating_avg: float = 0.0
    rating_count: int = 0
    logo_url: Optional[str] = None
    ebx_committed: int = 0
    pool_value: int = 0
    election_open: Optional[datetime] = None
    election_close: Optional[datetime] = None
    winning_org_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Mission
# ---------------------------------------------------------------------------
class MissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    community_members: int = 0
    credit_value: float = 1.0
    budget: int = 0
    spent: int = 0
    status: str = "active"


class MissionCreate(MissionBase):
    id: str
    initiative_id: str
    org_id: str


class MissionRead(MissionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    initiative_id: str
    org_id: str
    started_at: Optional[datetime] = None
    updated_at: datetime


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------
class PostBase(BaseModel):
    type: str = "editorial"
    title: Optional[str] = None
    body: str
    author_type: str = "earthbux"
    author_label: Optional[str] = None
    cause_id: Optional[str] = None
    initiative_id: Optional[str] = None
    mission_id: Optional[str] = None
    opinion_type: Optional[str] = None


class PostCreate(PostBase):
    id: str


class PostRead(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    likes: int = 0
    created_at: datetime


# ---------------------------------------------------------------------------
# Votes (org election — one per benefactor per initiative)
# ---------------------------------------------------------------------------
class VoteCreate(BaseModel):
    # org_id is only set during the org-election phase; omit for initiative-only (soft) votes.
    org_id: Optional[str] = None
    # Fractional vote share across multiple initiatives. Minimum 0.1.
    share: float = Field(default=1.0, ge=0.1, le=1.0)


class VoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    benefactor_id: int
    initiative_id: str
    org_id: Optional[str] = None
    share: float = 1.0
    created_at: datetime


# build-seq 2 note: the ORM has a single dual-purpose ``Vote`` model. The
# CauseVote* schemas below describe the phase-1 (initiative) election; the
# VoteCreate/VoteRead pair above IS the phase-2 (org) election schema. These
# explicit aliases give the org election a name symmetric with CauseVote* so
# the asymmetry Jax flagged ("a causevote but no orgvote") is resolved without
# a risky model rename.
OrgVoteCreate = VoteCreate
OrgVoteRead = VoteRead


# ---------------------------------------------------------------------------
# Benefactor account & auth
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
    vvv: bool = False
    created_at: datetime
    # build-seq 4 — surface the watchlist so the profile page can render
    # without a second round-trip. JSON-encoded string at rest; we serialise
    # to a list on the way out (see crud.serialize_watchlist).
    watched_initiative_ids: list[str] = Field(default_factory=list)

    @field_validator("watched_initiative_ids", mode="before")
    @classmethod
    def _parse_watched(cls, v: object) -> list[str]:
        """Coerce DB Text (None or JSON string) → list[str]."""
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        try:
            parsed = _json.loads(v)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except (TypeError, ValueError):
            pass
        return []


# ---------------------------------------------------------------------------
# Cause-scoped votes (build-seq 3)
# ---------------------------------------------------------------------------
class CauseVoteShares(BaseModel):
    """Full shares map a benefactor PUTs for a cause.

    Map of initiative_id -> share (>= 0.1). Sum must be <= 1.0. The server
    deletes any prior soft-vote rows not represented in the map; committed
    rows (vote.committed=True) are immutable and rejected here.
    """
    cause_id: str
    shares: dict[str, float]


class CauseVoteTallyEntry(BaseModel):
    initiative_id: str
    raw_share: float        # sum of share values across all benefactors
    weighted_share: float   # vote-weight formula applied server-side
    voter_count: int


class CauseVoteTally(BaseModel):
    cause_id: str
    size_factor: float
    pool_total_ebx: int
    entries: list[CauseVoteTallyEntry] = Field(default_factory=list)


class CauseVoteCommit(BaseModel):
    cause_id: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None  # benefactor id as string
    exp: Optional[int] = None


# ---------------------------------------------------------------------------
# Contributions
# ---------------------------------------------------------------------------
class ContributionCreate(BaseModel):
    initiative_id: str
    amount_ebx: int = Field(gt=0)


class ContributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    benefactor_id: int
    initiative_id: str
    amount_ebx: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Memberships
# ---------------------------------------------------------------------------
class MembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    benefactor_id: int
    organization_id: str
    role: str
    joined_at: datetime


# ---------------------------------------------------------------------------
# OrgRegistration (pass 34, build-seq 2)
# ---------------------------------------------------------------------------
class OrgRegistrationBase(BaseModel):
    kind: str = "nomination"  # nomination | registration
    org_name: str
    website: str
    justification: str
    member_name: Optional[str] = None
    member_position: Optional[str] = None
    # At least one initiative the org is believed fit to accomplish.
    initiative_ids: list[str] = Field(min_length=1)

    @field_validator("kind")
    @classmethod
    def _kind_known(cls, v: str) -> str:
        if v not in ("nomination", "registration"):
            raise ValueError("kind must be 'nomination' or 'registration'")
        return v


class OrgRegistrationCreate(OrgRegistrationBase):
    pass


class OrgRegistrationRead(OrgRegistrationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str = "pending"
    submitted_by_id: Optional[int] = None
    organization_id: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("initiative_ids", mode="before")
    @classmethod
    def _coerce_initiative_ids(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                return _json.loads(v)
            except Exception:
                return []
        return v


# ---------------------------------------------------------------------------
# Vote audit log + admin console (build-seq 1)
# ---------------------------------------------------------------------------
class VoteEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: Optional[int] = None
    election_id: Optional[str] = None
    cause_id: Optional[str] = None
    target: Optional[str] = None
    kind: str = "initiative"
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime


class AdminVoteRow(BaseModel):
    """A live vote row enriched with display names for the admin table."""
    id: int
    benefactor_id: Optional[int] = None
    handle: Optional[str] = None
    initiative_id: str
    initiative_title: Optional[str] = None
    cause_id: Optional[str] = None
    org_id: Optional[str] = None
    org_name: Optional[str] = None
    share: float = 1.0
    committed: bool = False
    kind: str = "initiative"
    created_at: Optional[datetime] = None


class AdminSummaryEntry(BaseModel):
    key: Optional[str] = None
    label: Optional[str] = None
    vote_count: int = 0
    event_count: int = 0


class AdminChecks(BaseModel):
    duplicate_votes: list[dict] = Field(default_factory=list)
    votes_without_users: list[dict] = Field(default_factory=list)
    invalid_elections: list[dict] = Field(default_factory=list)
