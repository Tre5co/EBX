"""PROPOSAL: mission-centric ORM rewrite (v2). NOT wired into the app.

Nothing imports this file, so it cannot affect the running API or Alembic until
you promote it. Spine = `Mission`; everything else hangs off it.

Naming: short forms ben / tiv / org are used for attributes, columns, FKs and
relationships (all length 3). Class names stay descriptive (Initiative,
BenefactorAccount, Organization) so e.g. `tiv_id = ForeignKey("initiatives.id")`.

v2 changes vs models.py
-----------------------
* Mission is the SPINE (one cause+cycle slot, holds phase + winner pointers).
* Voting split into VoteP1 (tiv election) and VoteP2 (org election).
* Contribution merged onto VoteP1 (ebx_committed = live value).
* Transaction is the single append-only ledger (replaces VoteEvent): it records
  both vote mutations and EBX bucket movements (pool/org/earthbux/...), keeping
  the vote/mission/ben classes lean.
* `valence` (helpful|neutral|harmful) added to VoteP1/VoteP2 as the hook for the
  upcoming voting redesign (negative/against votes, org blocking). The WEIGHT
  math lives in crud, not here.
* organization_causes dropped — an org's causes derive through its candidacies
  -> missions -> cause.
* MissionCandidacy = an org's bid to run a mission (grants build access).
* Earthbux employees via BenefactorAccount.role; Query = staff-only data tool.
* PostVote values helpful|neutral|harmful. Initiative.rating_* is the aggregated
  average of its VoteP1 valence (recomputed in crud).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ===========================================================================
# Cause — the 7 permanent rotation slots.
# (No more organization_causes link table: an org's causes are derived through
#  its mission candidacies, so the m2m `secondary` table is gone.)
# ===========================================================================
class Cause(Base):
    __tablename__ = "causes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    index: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  # rotation order 0..6
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    emoji: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    missions: Mapped[list["Mission"]] = relationship(back_populates="cause")


# ===========================================================================
# Mission — THE SPINE. One (cause, cycle_num) slot, created at cycle start.
# Holds phase state + the singular WINNER pointers; candidates are on the
# back-ref collections (tivs, candidacies).
# ===========================================================================
class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = (
        UniqueConstraint("cause_id", "cycle_num", name="uq_mission_cause_cycle"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    cause_id: Mapped[str] = mapped_column(ForeignKey("causes.id"), nullable=False)
    cycle_num: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # 'pre' | 'initiative' | 'budget' | 'credit' | 'resolution'
    current_phase: Mapped[str] = mapped_column(String, default="pre", nullable=False)

    winning_tiv_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("initiatives.id"), nullable=True
    )
    winning_org_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )

    budget: Mapped[int] = mapped_column(Integer, default=0)
    spent: Mapped[int] = mapped_column(Integer, default=0)
    credit_value: Mapped[float] = mapped_column(Float, default=1.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    cause: Mapped["Cause"] = relationship(back_populates="missions")
    winning_tiv: Mapped[Optional["Initiative"]] = relationship(
        foreign_keys="Mission.winning_tiv_id"
    )
    winning_org: Mapped[Optional["Organization"]] = relationship(
        foreign_keys="Mission.winning_org_id"
    )
    tivs: Mapped[list["Initiative"]] = relationship(
        back_populates="mission", foreign_keys="Initiative.mission_id"
    )
    candidacies: Mapped[list["MissionCandidacy"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )
    votes_p1: Mapped[list["VoteP1"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )
    votes_p2: Mapped[list["VoteP2"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )
    pool: Mapped[Optional["Pool"]] = relationship(
        back_populates="mission", uselist=False, cascade="all, delete-orphan"
    )
    credit_coins: Mapped[list["CreditCoin"]] = relationship(
        back_populates="mission", cascade="all, delete-orphan"
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="mission", foreign_keys="Post.mission_id"
    )


# ===========================================================================
# Initiative ("tiv") — a candidate idea. Proposed under a cause; once it enters
# a cycle it points at that Mission. Winner named by Mission.winning_tiv_id.
# ===========================================================================
class Initiative(Base):
    __tablename__ = "initiatives"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emoji: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    cause_id: Mapped[str] = mapped_column(ForeignKey("causes.id"), nullable=False)
    mission_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("missions.id"), nullable=True  # NULL while merely 'suggested'
    )

    proposer_ben_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    proposer_org_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )
    proposed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # aggregated average of this tiv's VoteP1 valence (recomputed in crud).
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String, default="suggested", nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # staff-set

    cause: Mapped["Cause"] = relationship()
    mission: Mapped[Optional["Mission"]] = relationship(
        back_populates="tivs", foreign_keys="Initiative.mission_id"
    )
    proposer_ben: Mapped[Optional["BenefactorAccount"]] = relationship(
        foreign_keys="Initiative.proposer_ben_id"
    )
    proposer_org: Mapped[Optional["Organization"]] = relationship(
        foreign_keys="Initiative.proposer_org_id"
    )
    votes_p1: Mapped[list["VoteP1"]] = relationship(back_populates="tiv")


# ===========================================================================
# Organization — a vetted org. Logs in via Memberships (people), not directly.
# Its causes are derived: org -> candidacies -> missions -> cause.
# ===========================================================================
class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    founding_member_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="org", cascade="all, delete-orphan"
    )
    candidacies: Mapped[list["MissionCandidacy"]] = relationship(back_populates="org")
    posts: Mapped[list["Post"]] = relationship(
        back_populates="org_author", foreign_keys="Post.org_author_id"
    )


# ===========================================================================
# BenefactorAccount ("ben") — the personal login. Three user categories via
# `role`. Org access is through Membership; employees are bens with elevated role.
# ===========================================================================
class BenefactorAccount(Base):
    __tablename__ = "benefactor_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    handle: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    pass_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # 'benefactor' (default) | 'employee' | 'admin'. Only employee/admin may
    # approve tivs & orgs, post editorial/headline, and use the Query console.
    role: Mapped[str] = mapped_column(String, default="benefactor", nullable=False)

    vvv: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # set after first p2 vote
    watched_tiv_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list

    credit_coins: Mapped[list["CreditCoin"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="ben", cascade="all, delete-orphan"
    )
    votes_p1: Mapped[list["VoteP1"]] = relationship(
        back_populates="ben", cascade="all, delete-orphan"
    )
    votes_p2: Mapped[list["VoteP2"]] = relationship(
        back_populates="ben", cascade="all, delete-orphan"
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="ben_author", foreign_keys="Post.ben_author_id"
    )

    @property
    def is_staff(self) -> bool:
        return self.role in ("employee", "admin")


# ===========================================================================
# Membership — person <-> org link with a role (association object).
# ===========================================================================
class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("ben_id", "org_id", name="uq_member_org"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ben_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))
    role: Mapped[str] = mapped_column(String, default="community")  # community|rep|executive|beneficiary
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ben: Mapped["BenefactorAccount"] = relationship(back_populates="memberships")
    org: Mapped["Organization"] = relationship(back_populates="memberships")


# ===========================================================================
# MissionCandidacy — an org's BID to run a specific mission. Grants build access
# on approval; the winner sets Mission.winning_org_id. (Replaces OrgRegistration.)
# ===========================================================================
class MissionCandidacy(Base):
    __tablename__ = "mission_candidacies"
    __table_args__ = (
        UniqueConstraint("mission_id", "org_id", name="uq_candidacy_mission_org"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), nullable=False)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    mission_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)  # pending|approved|withdrawn|won|lost
    submitted_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    approved_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True  # the employee who approved
    )
    p2_vote_tally: Mapped[int] = mapped_column(Integer, default=0)  # denormalised
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    mission: Mapped["Mission"] = relationship(back_populates="candidacies")
    org: Mapped["Organization"] = relationship(back_populates="candidacies")


# ===========================================================================
# VoteP1 — TIV election. Split-vote economy: a ben can spread share across
# several tivs (>=0.1 each, sum <=1.0); one row per (ben, tiv). Committed EBX
# lives here. `valence` is the hook for the voting redesign:
#   helpful = vote FOR  |  neutral = abstain/soft  |  harmful = vote AGAINST.
# Weighting & negative-detraction math is computed in crud, not stored here.
# ===========================================================================
class VoteP1(Base):
    __tablename__ = "votes_p1"
    __table_args__ = (
        UniqueConstraint("ben_id", "tiv_id", name="uq_votep1_ben_tiv"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ben_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"))
    tiv_id: Mapped[str] = mapped_column(ForeignKey("initiatives.id"))

    share: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # >=0.1
    ebx_committed: Mapped[float] = mapped_column(Float, default=0, nullable=False)  # holdings x share (continuous, no rounding)
    valence: Mapped[str] = mapped_column(String, default="helpful", nullable=False)  # helpful|neutral|harmful
    committed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ben: Mapped["BenefactorAccount"] = relationship(back_populates="votes_p1")
    mission: Mapped["Mission"] = relationship(back_populates="votes_p1")
    tiv: Mapped["Initiative"] = relationship(back_populates="votes_p1")


# ===========================================================================
# VoteP2 — ORG election. "1 vote, 1 org; extra votes bought at rising prices."
# One row per (ben, mission). `valence` harmful = BLOCK the org (same cost as
# support, per the redesign).
# ===========================================================================
class VoteP2(Base):
    __tablename__ = "votes_p2"
    __table_args__ = (
        UniqueConstraint("ben_id", "mission_id", name="uq_votep2_ben_mission"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ben_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"))
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"))

    votes: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 + bought
    ebx_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valence: Mapped[str] = mapped_column(String, default="helpful", nullable=False)  # helpful|neutral|harmful(=block)
    committed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ben: Mapped["BenefactorAccount"] = relationship(back_populates="votes_p2")
    mission: Mapped["Mission"] = relationship(back_populates="votes_p2")
    # One-directional on purpose: an org doesn't carry a back-collection of the
    # votes for/against it (kept symmetric with how bens relate to missions).
    org: Mapped["Organization"] = relationship()


# ===========================================================================
# Pool — per-mission money aggregate (DERIVED cache; recompute on commit/rollover).
# ===========================================================================
class Pool(Base):
    __tablename__ = "pools"

    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), primary_key=True)
    phase1_total_ebx: Mapped[int] = mapped_column(Integer, default=0)
    phase2_total_ebx: Mapped[int] = mapped_column(Integer, default=0)
    pool_from_winners: Mapped[int] = mapped_column(Integer, default=0)  # 20% / 100% kept
    pool_from_losers: Mapped[int] = mapped_column(Integer, default=0)   # 10% / 20% kept
    total_locked: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    mission: Mapped["Mission"] = relationship(back_populates="pool")


# ===========================================================================
# CreditCoin — the EBX token issued to a ben on a mission. Owning one = community
# membership in that mission (STRUCTURE: "credits=membership").
# ===========================================================================
class CreditCoin(Base):
    __tablename__ = "credit_coins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"))
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"))
    amount_ebx: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[float] = mapped_column(Float, default=1.0)  # drifts post-mint
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    redeemed: Mapped[bool] = mapped_column(Boolean, default=False)

    owner: Mapped["BenefactorAccount"] = relationship(back_populates="credit_coins")
    mission: Mapped["Mission"] = relationship(back_populates="credit_coins")


# ===========================================================================
# Post — discussion/editorial content.
# ===========================================================================
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    category: Mapped[str] = mapped_column(String, default="editorial", nullable=False)  # case|context|analysis|evaluation|org_update|editorial|headline
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    author_type: Mapped[str] = mapped_column(String, default="earthbux", nullable=False)  # ben|org|earthbux
    ben_author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    org_author_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )

    mission_id: Mapped[Optional[str]] = mapped_column(ForeignKey("missions.id"), nullable=True)
    tiv_id: Mapped[Optional[str]] = mapped_column(ForeignKey("initiatives.id"), nullable=True)
    cause_id: Mapped[Optional[str]] = mapped_column(ForeignKey("causes.id"), nullable=True)

    helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    neutral_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    harmful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ben_author: Mapped[Optional["BenefactorAccount"]] = relationship(
        back_populates="posts", foreign_keys="Post.ben_author_id"
    )
    org_author: Mapped[Optional["Organization"]] = relationship(
        back_populates="posts", foreign_keys="Post.org_author_id"
    )
    mission: Mapped[Optional["Mission"]] = relationship(
        back_populates="posts", foreign_keys="Post.mission_id"
    )
    votes: Mapped[list["PostVote"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )


# ===========================================================================
# PostVote — per-ben reaction. helpful | neutral | harmful.
# ===========================================================================
class PostVote(Base):
    __tablename__ = "post_votes"
    __table_args__ = (
        UniqueConstraint("post_id", "ben_id", name="uq_post_vote_ben"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"), nullable=False)
    ben_id: Mapped[int] = mapped_column(ForeignKey("benefactor_accounts.id"), nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)  # helpful|neutral|harmful
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    post: Mapped["Post"] = relationship(back_populates="votes")
    ben: Mapped["BenefactorAccount"] = relationship()


# ===========================================================================
# Query — EMPLOYEE-ONLY saved data-access tool (the "navigate the database"
# staff permission). Tooling, not domain spine. Gated to role in (employee,admin).
# ===========================================================================
class Query(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entity: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # 'missions' | 'votes_p1' ...
    filters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON
    sort: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sql: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # optional raw read-only

    created_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_by: Mapped[Optional["BenefactorAccount"]] = relationship()


# ===========================================================================
# Transaction — the single append-only EBX ledger. Replaces VoteEvent: one log
# for everything that moves EBX or changes a vote in a mission. Two kinds:
#   type='vote'     -> a vote mutation (audit). Uses action (CAST|UPDATE|REMOVE),
#                      phase, target (tiv_id/org_id), old_value/new_value.
#   type='transfer' -> EBX moving into a bucket. Uses bucket and, when paid to an
#                      org, counterparty_org_id.
# Live state still lives on VoteP1/VoteP2 (committed amounts) and Pool (derived
# cache). This table is the history + the per-bucket money breakdown, so the
# vote / mission / ben classes don't have to carry audit or split columns.
#   bucket: pool | org | earthbux | evaluation | credit | refund
# ===========================================================================
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # vote | transfer
    ben_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("benefactor_accounts.id"), nullable=True
    )
    mission_id: Mapped[Optional[str]] = mapped_column(ForeignKey("missions.id"), nullable=True)
    phase: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # p1 | p2

    # --- type='vote' fields ---
    action: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # CAST | UPDATE | REMOVE
    target: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # tiv_id or org_id
    old_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # --- type='transfer' fields ---
    bucket: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # pool|org|earthbux|evaluation|credit|refund
    counterparty_org_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id"), nullable=True
    )

    amount_ebx: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # used by both kinds
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
