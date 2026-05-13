"""Pydantic v2 request/response schemas for the Earthbucks API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    date_approved: Optional[datetime] = None


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
    ebx_committed: int = 0
    pool_value: int = 0
    election_open: Optional[datetime] = None
    election_close: Optional[datetime] = None
    winning_org_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Mission
# ---------------------------------------------------------------------------
class MissionMetricBase(BaseModel):
    name: str
    target_value: float = 0.0
    current_value: float = 0.0
    unit: Optional[str] = None


class MissionMetricCreate(MissionMetricBase):
    pass


class MissionMetricRead(MissionMetricBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mission_id: str


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
    metrics: list[MissionMetricCreate] = Field(default_factory=list)


class MissionRead(MissionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    initiative_id: str
    org_id: str
    started_at: Optional[datetime] = None
    updated_at: datetime
    metrics: list[MissionMetricRead] = Field(default_factory=list)


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
# Reviews
# ---------------------------------------------------------------------------
class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    body: Optional[str] = None


class ReviewCreate(ReviewBase):
    organization_id: str


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: str
    benefactor_id: Optional[int] = None
    created_at: datetime


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
    created_at: datetime


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
