"""SQLAlchemy ORM models for Earthbucks.

Entity overview
---------------
Cause                  - one of the 7 permanent causes (Atmosphere, Oceans, ...)
Organization           - a vetted org that can be elected to run a mission
Initiative             - a proposed action under a cause for a given cycle
Mission                - what an elected org is actually executing
BenefactorAccount      - a personal user account (email + hashed password + wallet)
Membership             - links a BenefactorAccount to an Organization with a role
Contribution           - EBX a benefactor has committed to an initiative
CreditCoin             - a credit token issued to a benefactor on a specific mission
Post                   - benefactor/org/EBX content; type values:
                           Benefactor election commentary (phase 1 & 2):
                             'context'    — shared: background on initiative or org (both elections)
                             'analysis'   — shared: data-driven / expert take (both elections)
                             'case'       — tiv-vote only: "why I voted for this initiative"
                             'evaluation' — org-vote only: "why I voted for this organization"
                           Org & EBX operational posts:
                             'org_update' — mission progress from an org
                             'editorial'  — EBX-authored news / status
                             'headline'   — short EBX headline
PostVote               - per-benefactor helpful/neutral/wrong vote on a post
Review                 - rating left on an organization (star-based; backlog: deprecate)
MissionMetric          - a single tracked metric for a mission (name, target, current, unit)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ---------------------------------------------------------------------------
# Many-to-many: Organization ↔ Cause (an org can serve multiple causes)
# ---------------------------------------------------------------------------
organization_causes = Table(
    "organization_causes",
    Base.metadata,
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
    Column("cause_id", ForeignKey("causes.id"), primary_key=True),
)


# ---------------------------------------------------------------------------
# Cause
# ---------------------------------------------------------------------------
class Cause(Base):
    __tablename__ = "causes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    index: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    emoji: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    initiatives: Mapped[list["Initiative"]] = relationship(back_populates="cause")
    organizations: Mapped[list["Organization"]] = relationship(
        secondary=organization_causes,
        back_populates="causes",
    )


# ---------------------------------------------------------------------------
# Organization (also serves as the "OrgAccount" — orgs log in via memberships)
# ---------------------------------------------------------------------------
class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mission_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date_approved: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    causes: Mapped[list["Cause"]] = relationship(
        secondary=organization_causes,
        back_populates="organizations",
    )
    initiatives_pursued: Mapped[list["Initiative"]] = relationship(
        back_populates="winning_org",
        foreign_keys="Initiative.winning_org_id",
    )
    missions: Mapped[list["Mission"]] = relationship(back_populates="org")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    posts: Mapped[list["Post"]] = relationship(back_populates="org_author")


# ---------------------------------------------------------------------------
# BenefactorAccount (personal user account)
# ---------------------------------------------------------------------------
class BenefactorAccount(Base):
    __tablename__ = "benefactor_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    handle: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    pass_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    # vvv: True after first org vote cast. Unlocks cause-color perk on profile logo.
    vvv: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Watchlist — JSON-encoded list of initiative ids. Nullable until the user
    # rates or explicitly watches an initiative. Set by Pass 16 (build-seq 4).
    watched_initiative_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    credit_coins: Mapped[list["CreditCoin"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    contributions: Mapped[list["Contribution"]] = relationship(
        back_populates="benefactor",
        cascade="all, delete-orphan",
    )
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="benefactor",
        cascade="all, delete-orphan",
    )
    posts: Mapped[list["Post"]] = relationship(back_populates="benefactor_author")
    reviews: Mapped[list["Review"]] = relationship(back_populates="benefactor")


# ---------------------------------------------------------------------------
# Membership (BenefactorAccount ↔ Organization, with role)
# ---------------------------------------------------------------------------
class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("benefactor_id", "organization_id", name="uq_member_org"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    benefactor_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    role: Mapped[str] = mapped_column(String, default="community")  # community | rep | admin
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    benefactor: Mapped["BenefactorAccount"] = relationship(back_populates="memberships")
    organization: Mapped["Organization"] = relationship(back_populates="memberships")


# ---------------------------------------------------------------------------
# Initiative
# ---------------------------------------------------------------------------
class Initiative(Base):
    __tablename__ = "initiatives"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cause_id: Mapped[str] = mapped_column(ForeignKey("causes.id"), nullable=False)
    cycle_num: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emoji: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    proposed_by: Mapped[str] = mapped_column(String, default="benefactor")  # benefactor | org
    proposer_benefactor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    proposer_org_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )

    rating: Mapped[float] = mapped_column(Float, default=0.0)
    # build-seq 4 — denormalised rating rollup (server-side single source of
    # truth so list_initiatives doesn't recompute per call).
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ebx_committed: Mapped[int] = mapped_column(Integer, default=0)
    pool_value: Mapped[int] = mapped_column(Integer, default=0)

    election_open: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    election_close: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 'suggested' | 'debate' | 'org_vote' | 'active' | 'resolved'
    status: Mapped[str] = mapped_column(String, default="suggested")
    winning_org_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )

    cause: Mapped["Cause"] = relationship(back_populates="initiatives")
    winning_org: Mapped[Optional["Organization"]] = relationship(
        back_populates="initiatives_pursued",
        foreign_keys="Initiative.winning_org_id",
    )
    proposer_org: Mapped[Optional["Organization"]] = relationship(
        foreign_keys="Initiative.proposer_org_id",
    )
    proposer_benefactor: Mapped[Optional["BenefactorAccount"]] = relationship(
        foreign_keys="Initiative.proposer_benefactor_id",
    )
    missions: Mapped[list["Mission"]] = relationship(back_populates="initiative")
    contributions: Mapped[list["Contribution"]] = relationship(
        back_populates="initiative",
        cascade="all, delete-orphan",
    )

    @property
    def is_mission(self) -> bool:
        return self.status in ("active", "resolved")


# ---------------------------------------------------------------------------
# Contribution (a benefactor commits EBX to an initiative)
# ---------------------------------------------------------------------------
class Contribution(Base):
    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    benefactor_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    initiative_id: Mapped[str] = mapped_column(ForeignKey("initiatives.id"))
    amount_ebx: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    benefactor: Mapped["BenefactorAccount"] = relationship(back_populates="contributions")
    initiative: Mapped["Initiative"] = relationship(back_populates="contributions")


# ---------------------------------------------------------------------------
# Mission (what the elected org is actually doing)
# ---------------------------------------------------------------------------
class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    initiative_id: Mapped[str] = mapped_column(ForeignKey("initiatives.id"))
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    community_members: Mapped[int] = mapped_column(Integer, default=0)
    credit_value: Mapped[float] = mapped_column(Float, default=1.0)
    budget: Mapped[int] = mapped_column(Integer, default=0)
    spent: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    status: Mapped[str] = mapped_column(String, default="active")

    initiative: Mapped["Initiative"] = relationship(back_populates="missions")
    org: Mapped["Organization"] = relationship(back_populates="missions")
    metrics: Mapped[list["MissionMetric"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )
    news: Mapped[list["Post"]] = relationship(
        back_populates="mission",
        foreign_keys="Post.mission_id",
    )
    credit_coins: Mapped[list["CreditCoin"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# MissionMetric (one row per tracked metric)
# ---------------------------------------------------------------------------
class MissionMetric(Base):
    __tablename__ = "mission_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, default=0.0)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    mission: Mapped["Mission"] = relationship(back_populates="metrics")


# ---------------------------------------------------------------------------
# CreditCoin (the EBX token issued to a benefactor on a mission)
# ---------------------------------------------------------------------------
class CreditCoin(Base):
    __tablename__ = "credit_coins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"))
    amount_ebx: Mapped[int] = mapped_column(Integer, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    redeemed: Mapped[bool] = mapped_column(Boolean, default=False)

    owner: Mapped["BenefactorAccount"] = relationship(back_populates="credit_coins")
    mission: Mapped["Mission"] = relationship(back_populates="credit_coins")


# ---------------------------------------------------------------------------
# Post (feed content — editorial, opinion, org_update, headline)
# ---------------------------------------------------------------------------
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    # See module docstring for valid type values.
    type: Mapped[str] = mapped_column(String, default="editorial")

    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # Denormalised vote tallies — kept in sync by the PostVote upsert endpoint.
    helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    neutral_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author_type: Mapped[str] = mapped_column(String, default="earthbux")
    author_label: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    benefactor_author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    org_author_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )

    cause_id: Mapped[Optional[str]] = mapped_column(ForeignKey("causes.id"), nullable=True)
    initiative_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("initiatives.id"), nullable=True
    )
    mission_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("missions.id"), nullable=True
    )

    opinion_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    cause: Mapped[Optional["Cause"]] = relationship(
        foreign_keys="Post.cause_id", viewonly=True,
    )
    benefactor_author: Mapped[Optional["BenefactorAccount"]] = relationship(
        back_populates="posts",
        foreign_keys="Post.benefactor_author_id",
    )
    org_author: Mapped[Optional["Organization"]] = relationship(
        back_populates="posts",
        foreign_keys="Post.org_author_id",
    )
    mission: Mapped[Optional["Mission"]] = relationship(
        back_populates="news",
        foreign_keys="Post.mission_id",
    )
    votes: Mapped[list["PostVote"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# PostVote (per-benefactor helpful/neutral/wrong vote on a post)
# ---------------------------------------------------------------------------
class PostVote(Base):
    __tablename__ = "post_votes"
    __table_args__ = (
        UniqueConstraint("post_id", "benefactor_id", name="uq_post_vote_benefactor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"), nullable=False)
    benefactor_id: Mapped[int] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=False
    )
    # 'helpful' | 'neutral' | 'wrong'
    value: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    post: Mapped["Post"] = relationship(back_populates="votes")
    benefactor: Mapped["BenefactorAccount"] = relationship()


# ---------------------------------------------------------------------------
# Review (rating left on an organization by a benefactor)
# ---------------------------------------------------------------------------
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    benefactor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    organization: Mapped["Organization"] = relationship(back_populates="reviews")
    benefactor: Mapped[Optional["BenefactorAccount"]] = relationship(back_populates="reviews")


# ---------------------------------------------------------------------------
# Vote (one benefactor vote per initiative cycle — org election)
# ---------------------------------------------------------------------------
class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("benefactor_id", "initiative_id", name="uq_vote_benefactor_initiative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    benefactor_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"), nullable=False)
    initiative_id: Mapped[str] = mapped_column(ForeignKey("initiatives.id"), nullable=False)
    # without joining through initiatives. Backfilled by the migration.
    cause_id: Mapped[Optional[str]] = mapped_column(ForeignKey("causes.id"), nullable=True)
    # org_id is NULL for initiative-only (soft) votes; set during the org-election phase.
    org_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    # Fractional vote share. Min 0.1. Defaults to 1.0 (full vote on one initiative).
    share: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    # build-seq 3 — locked-in commitment flag. False = pre-commit soft share;
    # True = the benefactor pressed Commit and the vote weights are sealed for
    # this cycle. POST /votes/commit flips it; the share allocator UI on
    # cause.html can still rewrite shares while False.
    committed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    benefactor: Mapped["BenefactorAccount"] = relationship()
    initiative: Mapped["Initiative"] = relationship()
    cause: Mapped[Optional["Cause"]] = relationship(foreign_keys="Vote.cause_id")
    org: Mapped[Optional["Organization"]] = relationship(foreign_keys="Vote.org_id")


# ---------------------------------------------------------------------------
# InitiativeRating (per-benefactor stars on an initiative; build-seq 4)
# ---------------------------------------------------------------------------
class InitiativeRating(Base):
    __tablename__ = "initiative_ratings"
    __table_args__ = (
        UniqueConstraint("benefactor_id", "initiative_id", name="uq_initiative_rating_benefactor"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    benefactor_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"), nullable=False)
    initiative_id: Mapped[str] = mapped_column(ForeignKey("initiatives.id"), nullable=False)
    # 0..5 stars. 0 means "rated but withdrawn"; UI surfaces stars >= 1.
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    benefactor: Mapped["BenefactorAccount"] = relationship()
    initiative: Mapped["Initiative"] = relationship()
