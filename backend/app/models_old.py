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
VoteEvent              - append-only audit log of every vote mutation (CAST/UPDATE/REMOVE)
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
    news: Mapped[list["Post"]] = relationship(
        back_populates="mission",
        foreign_keys="Post.mission_id",
    )
    credit_coins: Mapped[list["CreditCoin"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )


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
# OrgRegistration (pass 34, build-seq 2) — an organization nominated by a
# benefactor ('nomination') or registered by one of its own members
# ('registration'). Replaces the cause-membership proxy once approved rows
# are promoted to Organization + linked initiatives.
# ---------------------------------------------------------------------------
class OrgRegistration(Base):
    __tablename__ = "org_registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String, nullable=False, default="nomination")  # nomination | registration
    org_name: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[str] = mapped_column(String, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    # registration-only fields
    member_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    member_position: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # JSON-encoded list of initiative ids the org is believed fit to accomplish (>=1)
    initiative_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    submitted_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True)
    # set when an admin approves and promotes/links to a real Organization row
    organization_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # pending | approved | rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    submitted_by: Mapped[Optional["BenefactorAccount"]] = relationship()
    organization: Mapped[Optional["Organization"]] = relationship()


# ---------------------------------------------------------------------------
# VoteEvent (build-seq 1) — append-only audit log of vote mutations.
# Instead of silently overwriting Vote rows, every CAST/UPDATE/REMOVE is
# recorded here so the /admin/votes console has a full, ordered history.
#   election_id -> the initiative the vote belongs to (phase-1 or org election)
#   target      -> org_id for org-election votes; the initiative_id for phase-1
#   kind        -> 'initiative' (phase-1 soft share) | 'org' (phase-2 org vote)
#   old_value / new_value -> JSON-ish string snapshots (share or org_id)
# ---------------------------------------------------------------------------
class VoteEvent(Base):
    __tablename__ = "vote_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    election_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("initiatives.id"), nullable=True
    )
    cause_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("causes.id"), nullable=True
    )
    target: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String, default="initiative", nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)  # CAST | UPDATE | REMOVE
    old_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
