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
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional, Sequence

from sqlalchemy import func as sqlfunc, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from . import models, schemas
from . import post_config as pcfg
from .auth import hash_password


# ===========================================================================
# Constants (STRUCTURE.md)
# ===========================================================================
SHARE_FLOOR = 0.1            # phase-1 vote-split division floor
SHARE_SUM_CAP = 1.0          # a ben's phase-1 shares sum to <= 1.0
BASE_VOTE_EBX = 10           # a vote carries 10 EBX of weight without buying any
EBX_PER_VOTE = 10            # 10 EBX = 1 vote (0.1 vote = 1 EBX)
P2_EXTRA_VOTE_BASE = 10      # nth EXTRA org vote costs 10 × 2^(n−1) EBX (10, 20, 40, 80 …)


def p2_vote_cost(votes: int) -> int:
    """Total EBX spent to hold `votes` org votes: 1st free, extras on the
    doubling curve — total = 10 × (2^(votes−1) − 1)."""
    return P2_EXTRA_VOTE_BASE * (2 ** (max(1, int(votes)) - 1) - 1)

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
# The three REWARDED post types (mission_support), 1/32 each — context ·
# investigation · analysis (replaces best_case/context_or_analysis/comments).
# Staggered release (context with the advances · investigation at end of P3 ·
# analysis later) awaits the winner-picker; distribution currently books all
# three at settlement (staged in INSTRUCTIONS "Post model v2").
REWARD_CONTEXT = 1 / 32
REWARD_INVESTIGATION = 1 / 32
REWARD_ANALYSIS = 1 / 32
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


def open_p1_mission(db: Session, cause_id: str) -> Optional[models.Mission]:
    """The cause's mission whose phase-1 election is still open — i.e. no winner
    yet and the phase hasn't moved past `initiative`. Newest cycle wins.

    This is the same choice the frontends make (`_p1MissionForCause` on
    main.html / `_v2Mission` on cause.html), lifted server-side so a proposal
    lands in the right election no matter which page submitted it.
    """
    return db.scalars(
        select(models.Mission)
        .where(
            models.Mission.cause_id == cause_id,
            models.Mission.winning_tiv_id.is_(None),
            models.Mission.current_phase.in_(("pre", "initiative")),
        )
        .order_by(models.Mission.cycle_num.desc())
    ).first()


# ===========================================================================
# The cause election — §5 (2026-08-06)
#
# Seven windows rotate; each can be contested. Benefactors propose causes
# (name + colour) and vote, per week, on which cause should hold a given
# upcoming window. A challenger TAKES a week by clearing >50% of that week's
# votes for that window. Take all seven and the challenger replaces the
# incumbent.
#
# Seven weeks, advertised as six: **week 1 is an aggregation of the six weeks
# before the contest opened**, so a challenger that has quietly been winning
# arrives with that head start instead of starting from zero.
# ===========================================================================
CAUSE_STREAK_WEEKS = 7          # columns to win
CAUSE_LOOKBACK_WEEKS = 6        # weeks folded into column 1
CAUSE_MAJORITY = 0.5            # strictly greater than


def _week_start(when: Optional[datetime] = None) -> datetime:
    """Monday 00:00 UTC of the week `when` falls in — the unit a majority is
    measured over."""
    when = when or datetime.utcnow()
    day = datetime(when.year, when.month, when.day)
    return day - timedelta(days=day.weekday())


def active_cause_index(when: Optional[datetime] = None) -> int:
    """Which of the seven causes holds this week's window.

    §2 (2026-08-08). The rotation is a pure function of the calendar — one cause
    per week from `bootstrap.GENESIS` — and the server needs it to answer "which
    window is open to a vote", which cannot be a client claim. Same clock the
    frontend's `EBX.Cycle` runs on, so the two agree by construction.
    """
    from . import bootstrap
    when = when or datetime.utcnow()
    weeks = (when - bootstrap.GENESIS).days // 7
    return int(weeks) % bootstrap.ROTATION_WEEKS


def _slot_is_open(db: Session, slot: int) -> tuple[bool, Optional[str]]:
    """Is this window open to a cause vote this week, and who (if anyone) has
    already been elected into it? See `cause_slate` for the rule."""
    slot = int(slot)
    if slot == CAUSE_STREAK_WEEKS:
        return True, None
    idx = (active_cause_index() + slot) % CAUSE_STREAK_WEEKS
    incumbent = db.scalar(select(models.Cause).where(models.Cause.index == idx,
                                                     models.Cause.status == "active"))
    state = cause_ballot_state(db, slot, incumbent.id if incumbent else None)
    challenger = state.get("challenger_id")
    elected = challenger if (challenger and int(state.get("streak") or 0) >= CAUSE_STREAK_WEEKS) else None
    return bool(elected), elected


def list_causes_all(db: Session, status: Optional[str] = None) -> Sequence[models.Cause]:
    """Causes, optionally filtered by status. Falls back to the plain list on a
    database that predates the b7d4e9a1c206 migration."""
    stmt = select(models.Cause)
    if status:
        stmt = stmt.where(models.Cause.status == status)
    try:
        return db.scalars(stmt.order_by(models.Cause.index.is_(None), models.Cause.index)).all()
    except OperationalError:
        db.rollback()
        return list_causes(db) if status in (None, "active") else []


def suggest_cause(
    db: Session,
    ben_id: int,
    name: str,
    color: str,
    description: Optional[str] = None,
    emoji: Optional[str] = None,
) -> models.Cause:
    """Propose a cause. It holds no window until it wins one, so `index` is
    NULL and `status` is 'suggested'. The colour comes from the client's colour
    wheel — a cause is recognised by its colour everywhere in the UI, so the
    proposer picks it."""
    name = (name or "").strip()
    if not name:
        raise ValueError("A cause needs a name")
    color = (color or "").strip()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Colour must be a hex value like #6baed6")
    cid = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "cause"
    existing = db.get(models.Cause, cid)
    if existing is not None:
        raise ValueError(f"'{existing.name}' already exists")
    # Don't let a suggestion sit on top of an active cause's colour.
    clash = db.scalar(select(models.Cause).where(
        models.Cause.color == color, models.Cause.status == "active"))
    if clash is not None:
        raise ValueError(f"That colour already belongs to {clash.name} — pick another")
    cause = models.Cause(
        id=cid, index=None, name=name, color=color, emoji=emoji,
        description=description, status="suggested", proposed_by_id=ben_id,
    )
    db.add(cause)
    db.commit()
    db.refresh(cause)
    return cause


def cast_cause_vote(db: Session, ben_id: int, slot: int, cause_id: str) -> models.CauseVote:
    """One vote, one benefactor, one window, THIS week. Voting again this week
    replaces the earlier vote rather than stacking."""
    if not (1 <= int(slot) <= 7):
        raise ValueError("slot must be 1..7")
    cause = db.get(models.Cause, cause_id)
    if cause is None:
        raise ValueError("Cause not found")
    if cause.status == "retired":
        raise ValueError("That cause has been retired")
    # §2 (2026-08-08): a window that is not open this week cannot be voted in,
    # and the client is not the authority on which those are. Slot 7 — the
    # active cause's own next appearance, seven weeks out — is always open; any
    # other window is open only if a replacement has already been elected into
    # it. The rule is stated in `cause_slate`.
    open_, _elected = _slot_is_open(db, int(slot))
    if not open_:
        raise ValueError(
            f"That window is settled. This week's cause vote decides the window "
            f"{CAUSE_STREAK_WEEKS} weeks out — the active cause's replacement. A window "
            f"reopens only once a replacement has been elected into it."
        )
    wk = _week_start()
    row = db.scalar(select(models.CauseVote).where(
        models.CauseVote.ben_id == ben_id,
        models.CauseVote.slot == int(slot),
        models.CauseVote.week_start == wk,
    ))
    if row is None:
        row = models.CauseVote(ben_id=ben_id, slot=int(slot), cause_id=cause_id, week_start=wk)
        db.add(row)
    else:
        row.cause_id = cause_id
    db.commit()
    db.refresh(row)
    return row


def _week_winner(db: Session, slot: int, start: datetime, end: datetime) -> tuple[Optional[str], int, dict]:
    """Who cleared >50% of the votes cast for `slot` in [start, end)?
    Returns (winning cause id or None, total votes, per-cause counts).

    Tolerates a database that hasn't run the b7d4e9a1c206 migration yet: an
    empty ballot is a better answer than a 500 on every page load.
    """
    try:
        rows = db.execute(
            select(models.CauseVote.cause_id, sqlfunc.count()).where(
                models.CauseVote.slot == slot,
                models.CauseVote.week_start >= start,
                models.CauseVote.week_start < end,
            ).group_by(models.CauseVote.cause_id)
        ).all()
    except OperationalError:
        db.rollback()
        return None, 0, {}
    counts = {cid: int(n) for cid, n in rows}
    total = sum(counts.values())
    if not total:
        return None, 0, counts
    top_id, top_n = max(counts.items(), key=lambda kv: kv[1])
    return (top_id if top_n / total > CAUSE_MAJORITY else None), total, counts


def cause_ballot_state(db: Session, slot: int, incumbent_id: Optional[str] = None) -> dict:
    """The seven columns for one contested window.

    Ordered as Jax drew them: **leftmost is the ACTIVE week** (1 line),
    rightmost is the oldest (7 lines). The oldest column is the one that makes
    the process "seven weeks advertised as six" — it aggregates the six weeks
    before the contest opened, so a challenger that was already winning arrives
    with that behind it rather than starting from nothing.

    A column is won by whichever cause cleared >50% of the votes cast in it.
    The **streak** fills from the left: this week, then last week, and so on,
    for as long as the SAME challenger keeps winning. Break the run and it
    resets to the incumbent.
    """
    now_week = _week_start()
    columns: list[dict] = []
    # Columns 1..6 — this week, then one week back each, newest on the left.
    for k in range(CAUSE_STREAK_WEEKS - 1):
        s_ = now_week - timedelta(weeks=k)
        e_ = s_ + timedelta(weeks=1)
        win, total, counts = _week_winner(db, slot, s_, e_)
        columns.append({"index": k + 1, "lines": k + 1, "aggregate": False, "weeks": 1,
                        "start": s_.isoformat(), "winner": win, "votes": total, "counts": counts})
    # Column 7 — the aggregate of the six weeks before the contest opened.
    agg_end = now_week - timedelta(weeks=CAUSE_STREAK_WEEKS - 1)
    agg_start = agg_end - timedelta(weeks=CAUSE_LOOKBACK_WEEKS)
    win, total, counts = _week_winner(db, slot, agg_start, agg_end)
    columns.append({"index": CAUSE_STREAK_WEEKS, "lines": CAUSE_STREAK_WEEKS,
                    "aggregate": True, "weeks": CAUSE_LOOKBACK_WEEKS,
                    "start": agg_start.isoformat(), "winner": win, "votes": total, "counts": counts})

    # The streak: consecutive columns from the LEFT (this week backwards), all
    # won by one challenger that isn't the incumbent.
    challenger, streak = None, 0
    for col in columns:
        w = col["winner"]
        if w is None or w == incumbent_id:
            break
        if challenger is None:
            challenger = w
        if w != challenger:
            break
        streak += 1
        col["won"] = True

    # Standings this week, so the card can show each suggestion's share.
    _, this_total, this_counts = _week_winner(db, slot, now_week, now_week + timedelta(weeks=1))
    standings = [
        {"cause_id": cid, "votes": n,
         "share": round(n / this_total * 100) if this_total else 0}
        for cid, n in sorted(this_counts.items(), key=lambda kv: -kv[1])
    ]
    return {
        "slot": slot,
        "incumbent_id": incumbent_id,
        "challenger_id": challenger,
        "streak": streak,
        "weeks_required": CAUSE_STREAK_WEEKS,
        "advertised_weeks": CAUSE_STREAK_WEEKS - 1,
        "columns": columns,
        "standings": standings,
        "this_week_votes": this_total,
        "week_start": now_week.isoformat(),
    }


def cause_slate(db: Session, active_index: Optional[int] = None) -> dict:
    """Every upcoming window at once: who holds it, who is challenging it, and
    whether it is open to a vote this week.

    §2 (2026-08-08) — the cause vote has **dates and display conditions** now
    (structure.md, main.html backlog):

    * **The vote decided this week settles the window seven weeks out.** Seven
      causes rotate one per week, so seven weeks ahead is exactly one full
      rotation — the ACTIVE cause's own next appearance. That window is `slot`
      7 and it is always open.
    * **Every other window is read-only, with one exception**: a window that a
      challenger has already WON (all seven columns) is no longer held by the
      rotation incumbent, so it opens for a vote again. Nothing about the
      rotation guarantees the replacement is still what benefactors want by the
      time it runs, and this is where they say so.
    * A window whose challenger is mid-streak is *contested*, not elected — it
      stays read-only until the streak completes.

    Slot s is the window s weeks out, held by the cause at index
    (active_index + s) % 7 unless a challenger has taken it. `active_index`
    defaults to the server's own rotation clock; a client may pass its cycle
    index instead, and the two agree by construction.
    """
    if active_index is None:
        active_index = active_cause_index()
    try:
        active_index = int(active_index) % 7
    except (TypeError, ValueError):
        raise ValueError("active_index must be an integer")
    by_index = {
        c.index: c for c in db.scalars(
            select(models.Cause).where(models.Cause.status == "active")
        ).all() if c.index is not None
    }
    slots = []
    for slot in range(1, CAUSE_STREAK_WEEKS + 1):
        incumbent = by_index.get((active_index + slot) % 7)
        incumbent_id = incumbent.id if incumbent else None
        state = cause_ballot_state(db, slot, incumbent_id)
        streak = int(state.get("streak") or 0)
        challenger_id = state.get("challenger_id")
        elected_id = challenger_id if (challenger_id and streak >= CAUSE_STREAK_WEEKS) else None
        holder_id = elected_id or incumbent_id
        holder = db.get(models.Cause, holder_id) if holder_id else None
        slots.append({
            "slot": slot,
            "weeks_out": slot,
            "incumbent_id": incumbent_id,
            "challenger_id": challenger_id,
            "streak": streak,
            "weeks_required": CAUSE_STREAK_WEEKS,
            # The cause that will actually run this window as things stand.
            "elected_id": elected_id,
            "holder_id": holder_id,
            "holder_name": holder.name if holder else None,
            "holder_color": holder.color if holder else None,
            # The two conditions above, and which one applies.
            "votable": bool(slot == CAUSE_STREAK_WEEKS or elected_id),
            "votable_reason": (
                "the active cause's replacement — decided seven weeks before it runs"
                if slot == CAUSE_STREAK_WEEKS else
                "a replacement has been elected for this window, so it is open again"
                if elected_id else
                "this window is settled until it comes back around"
            ),
            "swapped": bool(elected_id and elected_id != incumbent_id),
        })
    return {
        "active_index": active_index,
        "weeks_required": CAUSE_STREAK_WEEKS,
        "default_slot": CAUSE_STREAK_WEEKS,
        "slots": slots,
    }


def my_cause_votes(db: Session, ben_id: int) -> dict:
    """This benefactor's live votes, slot → cause_id (this week only)."""
    wk = _week_start()
    rows = db.scalars(select(models.CauseVote).where(
        models.CauseVote.ben_id == ben_id, models.CauseVote.week_start == wk)).all()
    return {str(r.slot): r.cause_id for r in rows}


def create_tiv(db: Session, data: schemas.InitiativeCreate) -> models.Initiative:
    """Create an initiative.

    §0a (2026-08-05): a proposal with no `mission_id` used to be stored ORPHANED
    (mission_id NULL). Neither propose dialog sends one, so every user-proposed
    initiative was invisible to mission-scoped queries — and worse, a NULL
    mission_id slipped past the "is this tiv in this mission?" guard in
    `replace_p1_shares` (SQL `NULL != 'oce1'` is NULL, not TRUE), so the same
    orphan could be voted on under two different missions and blow up the
    UNIQUE(ben_id, tiv_id) index with a 500. Orphans now adopt their cause's
    open phase-1 mission at creation.
    """
    payload = data.model_dump()
    if not payload.get("mission_id") and payload.get("cause_id"):
        m = open_p1_mission(db, payload["cause_id"])
        if m is not None:
            payload["mission_id"] = m.id
    tiv = models.Initiative(**payload)
    db.add(tiv)
    db.commit()
    db.refresh(tiv)
    return tiv


def adopt_orphan_tivs(db: Session) -> list[str]:
    """Idempotent repair: attach every mission-less initiative to its cause's
    open phase-1 mission. Runs at startup (see main.py) so pre-§0a orphans stop
    poisoning the vote path. Returns the ids it adopted."""
    adopted: list[str] = []
    orphans = db.scalars(
        select(models.Initiative).where(models.Initiative.mission_id.is_(None))
    ).all()
    if not orphans:
        return adopted
    for tiv in orphans:
        if not tiv.cause_id:
            continue
        m = open_p1_mission(db, tiv.cause_id)
        if m is None:
            continue
        tiv.mission_id = m.id
        adopted.append(tiv.id)
        # Any phase-1 vote already cast on the orphan belongs to the mission it
        # has just joined — otherwise the row keeps a stale mission_id and the
        # ben's own slate reads short.
        moved = db.scalars(
            select(models.VoteP1).where(models.VoteP1.tiv_id == tiv.id)
        ).all()
        for row in moved:
            row.mission_id = m.id
        # Re-pointing can push a benefactor's slate for the target mission over
        # the 1.0 share cap (their orphan vote joins a slate they already
        # filled). Scale that ben's rows back down proportionally so the tally
        # stays honest until they next edit their slate.
        for ben_id in {r.ben_id for r in moved}:
            rows = db.scalars(
                select(models.VoteP1).where(
                    models.VoteP1.ben_id == ben_id,
                    models.VoteP1.mission_id == m.id,
                )
            ).all()
            total = sum(float(r.share or 0) for r in rows)
            if total > SHARE_SUM_CAP + 1e-6:
                for r in rows:
                    r.share = float(r.share or 0) * SHARE_SUM_CAP / total
                    r.ebx_committed = float(r.ebx_committed or 0) * SHARE_SUM_CAP / total
    if adopted:
        db.commit()
    return adopted


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


def account_footprints(db: Session) -> list[dict]:
    """Every account plus what it has done — the numbers a staffer needs before
    deciding an account is fraudulent or bug-created (2026-08-06)."""
    out: list[dict] = []
    for ben in db.scalars(select(models.BenefactorAccount).order_by(models.BenefactorAccount.id)).all():
        p1 = db.scalars(select(models.VoteP1).where(models.VoteP1.ben_id == ben.id)).all()
        p2 = db.scalars(select(models.VoteP2).where(models.VoteP2.ben_id == ben.id)).all()
        posts = db.scalar(
            select(sqlfunc.count()).select_from(models.Post).where(models.Post.ben_author_id == ben.id)
        ) or 0
        reacts = db.scalar(
            select(sqlfunc.count()).select_from(models.PostVote).where(models.PostVote.ben_id == ben.id)
        ) or 0
        out.append({
            "id": ben.id,
            "email": ben.email,
            "handle": ben.handle,
            "role": ben.role,
            "created_at": ben.created_at.isoformat() if ben.created_at else None,
            "p1_votes": len(p1),
            "p1_ebx": round(sum(float(v.ebx_committed or 0) for v in p1), 2),
            "p2_votes": len(p2),
            "p2_ebx": round(sum(float(v.ebx_spent or 0) for v in p2), 2),
            "posts": posts,
            "reactions": reacts,
            "memberships": db.scalar(
                select(sqlfunc.count()).select_from(models.Membership).where(models.Membership.ben_id == ben.id)
            ) or 0,
            "credit_coins": db.scalar(
                select(sqlfunc.count()).select_from(models.CreditCoin).where(models.CreditCoin.owner_id == ben.id)
            ) or 0,
        })
    return out


def issue_temp_password(db: Session, ben_id: int, staff: models.BenefactorAccount) -> dict:
    """Staff-only: replace an account's password with a one-off temporary one
    and hand it back so it can be sent to the address on the account.

    §0d (2026-08-08) — "I forgot the password to Jackson. How can I recover it?
    The email registered with the account is valid." Earthbux has no mail
    transport, so a real self-serve *forgot password* flow (token email, expiry,
    single-use redemption) is not a trivial change and stays on the backlog.
    A staff-issued temporary password is trivial, and it recovers the account
    today: staff issues it, sends it to the registered address, the owner signs
    in and changes it in profile settings.

    The plaintext is returned EXACTLY ONCE — it is never stored, only its hash.
    """
    require_staff(staff)
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Account not found")
    if not ben.email:
        raise ValueError("That account has no registered email to send a temporary password to")
    import secrets
    from . import auth as _auth
    # Readable but not guessable: three short groups, no ambiguous characters.
    alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
    temp = "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))
    ben.pass_hash = _auth.hash_password(temp)
    db.add(models.Transaction(
        type="admin", bucket="account", ben_id=None, phase=None, target=str(ben_id),
        amount_ebx=0,
        note=f"temporary password issued for account #{ben_id} ({ben.handle}) by staff #{staff.id}",
    ))
    db.commit()
    return {
        "id": ben.id,
        "handle": ben.handle,
        "email": ben.email,
        "temp_password": temp,
        "note": "Send this to the registered address. It replaces the old password "
                "immediately — the owner should change it from profile settings after signing in.",
    }


def remove_account(db: Session, ben_id: int, staff: models.BenefactorAccount) -> dict:
    """Staff-only: delete an account and withdraw everything it voted.

    Fraudulent and bug-created accounts skew every tally they touched, so the
    votes go with the account rather than being left behind as orphan rows.
    What survives: **posts** (orphaned to `ben_author_id = NULL`, because a
    thread other people replied to shouldn't develop holes) and the
    **transaction ledger** (append-only by design — the rows are relabelled,
    not erased, so the history of what happened stays auditable).

    Refuses to delete the last remaining admin, and refuses to delete you.
    """
    require_staff(staff)
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Account not found")
    if ben.id == staff.id:
        raise ValueError("You cannot remove your own account")
    if ben.role == "admin":
        others = db.scalar(
            select(sqlfunc.count()).select_from(models.BenefactorAccount).where(
                models.BenefactorAccount.role == "admin",
                models.BenefactorAccount.id != ben.id,
            )
        ) or 0
        if not others:
            raise ValueError("Refusing to remove the last admin account")

    summary = {"id": ben.id, "handle": ben.handle, "email": ben.email}
    missions_touched: set[str] = set()

    p1 = db.scalars(select(models.VoteP1).where(models.VoteP1.ben_id == ben_id)).all()
    for v in p1:
        missions_touched.add(v.mission_id)
        db.delete(v)
    p2 = db.scalars(select(models.VoteP2).where(models.VoteP2.ben_id == ben_id)).all()
    for v in p2:
        missions_touched.add(v.mission_id)
        db.delete(v)
    reacts = db.scalars(select(models.PostVote).where(models.PostVote.ben_id == ben_id)).all()
    for r in reacts:
        db.delete(r)
    memberships = db.scalars(select(models.Membership).where(models.Membership.ben_id == ben_id)).all()
    for m in memberships:
        db.delete(m)
    coins = db.scalars(select(models.CreditCoin).where(models.CreditCoin.owner_id == ben_id)).all()
    for c in coins:
        db.delete(c)

    posts = db.scalars(select(models.Post).where(models.Post.ben_author_id == ben_id)).all()
    for p in posts:
        p.ben_author_id = None
    txs = db.scalars(select(models.Transaction).where(models.Transaction.ben_id == ben_id)).all()
    for t in txs:
        t.ben_id = None
        t.note = ((t.note + " · ") if t.note else "") + f"account #{ben_id} removed by staff"

    db.delete(ben)
    db.commit()

    # §0 (2026-08-08): deleting the vote rows was only half the job. Two caches
    # are derived from them — `Pool` and `MissionCandidacy.p2_vote_tally` — and
    # neither was rebuilt, so a removed account went on inflating the cards it
    # was removed for. (The id-7 pilot account left atm0 reading 150 EBX of
    # phase-2 pool and org-001 holding a 5-vote candidacy tally after every one
    # of its votes was gone.) Both are rebuilt here, per mission touched.
    for mid in sorted(missions_touched):
        try:
            recompute_pool(db, mid)
            resync_p2_tallies(db, mid)
        except Exception:      # a cache rebuild must never fail the removal
            db.rollback()

    summary.update({
        "p1_votes_deleted": len(p1),
        "p2_votes_deleted": len(p2),
        "reactions_deleted": len(reacts),
        "memberships_deleted": len(memberships),
        "credit_coins_deleted": len(coins),
        "posts_orphaned": len(posts),
        "transactions_relabelled": len(txs),
        "missions_retallied": sorted(missions_touched),
    })
    return summary


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
    # Role separation shipped 2026-07-10/11 (org-experience restructure): only
    # rep/executive memberships carry editing, claiming and org-admin rights.
    # community/beneficiary members keep the mission & profile surfaces.
    if m is None or m.role not in ORG_OPERATOR_ROLES:
        raise PermissionError("Requires a rep or executive membership of this organization")


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
# Mission membership & credit coins (§1 — credits = membership)
# ===========================================================================
def is_mission_member(db: Session, ben_id: int, mission_id: str) -> bool:
    """MISSION membership (held by benefactors; distinct from org memberships).
    Per the settled rule: voting in BOTH elections guarantees membership;
    holding the mission's credit coin is membership. Excluded: those who did
    not vote for any organization, or who voted for an org but committed
    nothing to the initiative and bought nothing."""
    coin = db.scalar(
        select(models.CreditCoin).where(
            models.CreditCoin.owner_id == ben_id,
            models.CreditCoin.mission_id == mission_id,
        )
    )
    if coin is not None:
        return True
    p2 = db.scalar(
        select(models.VoteP2).where(
            models.VoteP2.ben_id == ben_id,
            models.VoteP2.mission_id == mission_id,
        )
    )
    if p2 is None:
        return False              # did not vote for any organization
    p1_committed = db.scalar(
        select(sqlfunc.coalesce(sqlfunc.sum(models.VoteP1.ebx_committed), 0)).where(
            models.VoteP1.ben_id == ben_id,
            models.VoteP1.mission_id == mission_id,
        )
    ) or 0
    # voted p2 AND (has a p1 stake, or bought extra org votes) -> member
    return float(p1_committed) > 0 or int(p2.ebx_spent or 0) > 0


def can_post_mission(db: Session, ben_id: int, mission_id: str) -> bool:
    """Posting gate for benefactor categories (settled 2026-07-19): you must be a
    mission member, OR have *agreed to become one* by committing a phase-1 stake.

    Strict membership is minted at election (finalize_p2); before that no one holds
    a coin, so `is_mission_member` is false through phase 1. The "agreement" that
    lets you post early is a committed phase-1 stake (ebx_committed > 0) — the same
    skin-in-the-game the membership rule ultimately requires. Someone who never
    commits stays ineligible and will not receive membership at the p2 vote."""
    if is_mission_member(db, ben_id, mission_id):
        return True
    p1_committed = db.scalar(
        select(sqlfunc.coalesce(sqlfunc.sum(models.VoteP1.ebx_committed), 0)).where(
            models.VoteP1.ben_id == ben_id,
            models.VoteP1.mission_id == mission_id,
        )
    ) or 0
    return float(p1_committed) > 0


def mint_mission_coins(db: Session, mission_id: str) -> int:
    """Mint the mission's credit coins — every benefactor who voted gets coins
    sized by their remaining stake (p1 committed + p2 spend), possibly tiny
    (e.g. just the 10% send left after a lost commit + withdrawal). Idempotent
    per (ben, mission); does NOT commit (caller's transaction). Returns the
    number of coins minted."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    stakes: dict[int, float] = {}
    for v in db.scalars(select(models.VoteP1).where(models.VoteP1.mission_id == mission_id)).all():
        stakes[v.ben_id] = stakes.get(v.ben_id, 0.0) + float(v.ebx_committed or 0)
    for v in db.scalars(select(models.VoteP2).where(models.VoteP2.mission_id == mission_id)).all():
        stakes[v.ben_id] = stakes.get(v.ben_id, 0.0) + float(v.ebx_spent or 0)
    existing = {
        c.owner_id for c in db.scalars(
            select(models.CreditCoin).where(models.CreditCoin.mission_id == mission_id)
        ).all()
    }
    minted = 0
    for ben_id, stake in stakes.items():
        amount = int(round(stake))
        if amount <= 0 or ben_id in existing:
            continue
        db.add(models.CreditCoin(
            owner_id=ben_id, mission_id=mission_id,
            amount_ebx=amount, value=float(mission.credit_value or 1.0),
        ))
        minted += 1
    return minted


def global_coin_value(db: Session, scale: float = 100000.0) -> dict:
    """The GLOBAL coin value — moved by people committing/withdrawing money
    across the platform (placeholder curve: 1 + net_flow/scale). Per-mission
    values live on mission.credit_value and move with resolutions."""
    committed = float(db.scalar(select(sqlfunc.coalesce(sqlfunc.sum(models.VoteP1.ebx_committed), 0))) or 0)
    spent = float(db.scalar(select(sqlfunc.coalesce(sqlfunc.sum(models.VoteP2.ebx_spent), 0))) or 0)
    refunded = float(db.scalar(
        select(sqlfunc.coalesce(sqlfunc.sum(models.Transaction.amount_ebx), 0)).where(
            models.Transaction.type == "transfer",
            models.Transaction.bucket == "refund",
        )
    ) or 0)
    net = committed + spent - refunded
    return {
        "global_value": round(1.0 + net / scale, 4),
        "net_flow_ebx": int(net),
        "scale": scale,
    }


def _bump_mission_coin_value(db: Session, mission: models.Mission, bump: float) -> None:
    """A RESOLUTION landed: bump the mission's credit value and drift every
    minted coin of the mission to it. Does not commit."""
    mission.credit_value = round(float(mission.credit_value or 1.0) + bump, 4)
    for coin in db.scalars(
        select(models.CreditCoin).where(models.CreditCoin.mission_id == mission.id)
    ).all():
        coin.value = mission.credit_value


# ===========================================================================
# Mission steps (release-phase structure, §1d) + resolutions
# ===========================================================================
def list_steps(db: Session, mission_id: str) -> Sequence[models.MissionStep]:
    return db.scalars(
        select(models.MissionStep)
        .where(models.MissionStep.mission_id == mission_id)
        .order_by(models.MissionStep.order_num.asc(), models.MissionStep.id.asc())
    ).all()


def _require_mission_operator(db: Session, actor: models.BenefactorAccount, mission: models.Mission) -> None:
    """Steps/plan authority: staff, or a rep/executive member of the mission's
    winning/claiming org (role separation, 2026-07-10)."""
    if getattr(actor, "is_staff", False):
        return
    org_ids = set()
    if mission.winning_org_id:
        org_ids.add(mission.winning_org_id)
    for claim in db.scalars(
        select(models.OrgClaim).where(models.OrgClaim.mission_id == mission.id)
    ).all():
        org_ids.add(claim.org_id)
    for org_id in org_ids:
        m = get_membership(db, actor.id, org_id)
        if m is not None and m.role in ORG_OPERATOR_ROLES:
            return
    raise PermissionError("Requires a rep or executive membership in this mission's organization (or staff)")


def create_step(
    db: Session,
    mission_id: str,
    data: schemas.MissionStepCreate,
    actor: models.BenefactorAccount,
) -> models.MissionStep:
    """Add a release-phase STEP. Pools are FINALIZED by the end of the
    budgeting phase — steps can be added/changed until the mission leaves
    'budget'; after that the plan is locked."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    _require_mission_operator(db, actor, mission)
    if mission.current_phase not in ("pre", "initiative", "budget"):
        raise ValueError("The plan is locked — steps are finalized by the end of the budgeting phase")
    step = models.MissionStep(
        mission_id=mission_id,
        title=data.title,
        description=data.description,
        order_num=data.order_num,
        guaranteed_ebx=data.guaranteed_ebx,
        potential_ebx=data.potential_ebx,
        starts_at=data.starts_at,
        due_at=data.due_at,
        created_by_id=actor.id,
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def resolve_step(
    db: Session,
    step_id: int,
    actor: models.BenefactorAccount,
    value_bump: float = 0.02,
) -> models.MissionStep:
    """Resolve a STEP — a RESOLUTION: a small mission-tied outcome we can
    reasonably assume was accomplished. Grants the evaluation point (ledger
    note) and moves the mission's credit-coin value. Resolving AHEAD of the
    due date is recorded (higher cash reward later)."""
    step = db.get(models.MissionStep, step_id)
    if step is None:
        raise ValueError("Step not found")
    if step.status == "resolved":
        raise ValueError("Step already resolved")
    mission = db.get(models.Mission, step.mission_id)
    _require_mission_operator(db, actor, mission)
    step.status = "resolved"
    step.resolved_at = datetime.utcnow()
    early = bool(step.due_at and step.resolved_at < step.due_at)
    _bump_mission_coin_value(db, mission, value_bump)
    db.add(models.Transaction(
        type="transfer", bucket="evaluation", mission_id=mission.id,
        ben_id=actor.id, amount_ebx=0,
        note=f"resolution: step '{step.title}'"
             + (" — resolved EARLY (bonus eligible)" if early else "")
             + f"; credit value -> {mission.credit_value}",
    ))
    db.commit()
    db.refresh(step)
    return step


def set_projected_end(
    db: Session,
    mission_id: str,
    when: datetime,
    actor: models.BenefactorAccount,
) -> models.Mission:
    """Set the projected MISSION LENGTH end date (release-phase structure)."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    _require_mission_operator(db, actor, mission)
    mission.projected_end_at = when
    db.commit()
    db.refresh(mission)
    return mission


def resolve_suggestion(
    db: Session,
    post_id: str,
    actor: models.BenefactorAccount,
    value_bump: float = 0.02,
) -> models.Post:
    """Mark a BUDGETING item (S/S/S — service/supply/support) as achieved — it
    becomes a RESOLUTION. Per the settled model a budgeting item resolves when
    its money is actually paid out; a mission operator records that here, which
    bumps the mission's credit-coin value. (Auto-resolve-on-payout is staged —
    INSTRUCTIONS "Post model v2".)"""
    post = db.get(models.Post, post_id)
    if post is None:
        raise ValueError("Post not found")
    if post.category == "resolution":
        raise ValueError("Already resolved")
    if post.category != "budgeting":
        raise ValueError("Only budgeting items (service/supply/support) can be resolved")
    mission = db.get(models.Mission, post.mission_id) if post.mission_id else None
    if mission is None and post.tiv_id:
        tiv = db.get(models.Initiative, post.tiv_id)
        mission = db.get(models.Mission, tiv.mission_id) if (tiv and tiv.mission_id) else None
    if mission is None:
        raise ValueError("Suggestion is not tied to a mission")
    _require_mission_operator(db, actor, mission)
    post.category = "resolution"
    _bump_mission_coin_value(db, mission, value_bump)
    if mission.winning_org_id:
        org = db.get(models.Organization, mission.winning_org_id)
        if org is not None:
            org.score = round(float(org.score or 0) + 1.0, 2)
    db.add(models.Transaction(
        type="transfer", bucket="evaluation", mission_id=mission.id,
        ben_id=post.ben_author_id, amount_ebx=0,
        note=f"resolution: suggestion '{(post.title or post.body or '')[:60]}'"
             f" ({post.stance or 'sss'}); credit value -> {mission.credit_value}",
    ))
    db.commit()
    db.refresh(post)
    return post


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


def reject_candidacy(
    db: Session,
    candidacy_id: int,
    staff: models.BenefactorAccount,
) -> models.MissionCandidacy:
    """Staff-only: REJECT an org's bid. §1 rule: "If your org was rejected, all
    your money is returned to you" — every backer's p2 spend is booked to the
    refund bucket and the vote rows are removed, freeing each ben to vote for
    another org (one VoteP2 row per ben+mission)."""
    require_staff(staff)
    cand = db.get(models.MissionCandidacy, candidacy_id)
    if cand is None:
        raise ValueError("Candidacy not found")
    if cand.status in ("won", "lost"):
        raise ValueError("This election has already been finalized")
    cand.status = "rejected"
    cand.approved_by_id = staff.id     # the employee who decided
    votes = db.scalars(
        select(models.VoteP2).where(
            models.VoteP2.mission_id == cand.mission_id,
            models.VoteP2.org_id == cand.org_id,
        )
    ).all()
    refunded = 0
    for v in votes:
        spent = int(v.ebx_spent or 0)
        if spent > 0:
            refunded += spent
            db.add(models.Transaction(
                type="transfer", bucket="refund", ben_id=v.ben_id,
                mission_id=cand.mission_id, phase="p2", target=cand.org_id,
                amount_ebx=spent, note="org rejected — full p2 refund",
            ))
        _log_vote(db, ben_id=v.ben_id, mission_id=cand.mission_id, phase="p2",
                  action="REMOVE", target=cand.org_id, old_value=v.org_id, new_value=None)
        db.delete(v)
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


def get_all_p2_votes(db: Session, ben_id: int) -> Sequence[models.VoteP2]:
    """Every phase-2 (organization) vote row this benefactor holds, across all
    missions. §2 (2026-08-05): the twin of get_all_p1_votes — the Context page's
    side + top cards each show "my choice" for an org race, and one round-trip
    beats one /p2/mine call per card."""
    return db.scalars(
        select(models.VoteP2).where(models.VoteP2.ben_id == ben_id)
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
    # §0a (2026-08-05): the old predicate was `mission_id != mission_id`, which
    # in SQL is NULL — never TRUE — for an orphaned initiative. Orphans therefore
    # passed the guard, were inserted under an arbitrary mission, and collided
    # with UNIQUE(ben_id, tiv_id) as an unhandled IntegrityError (the "Exception
    # in ASGI application" Jax hit committing an Oceans vote). Match NULLs
    # explicitly, and treat an unknown id as out-of-mission too.
    if cleaned:
        wanted = list(cleaned.keys())
        in_mission = set(db.scalars(
            select(models.Initiative.id).where(
                models.Initiative.id.in_(wanted),
                models.Initiative.mission_id == mission_id,
            )
        ).all())
        bad = [t for t in wanted if t not in in_mission]
        if bad:
            raise ValueError(f"Initiatives {bad} are not in mission {mission_id}")

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


CARRYOVER_BUCKET = "carryover"


def _rolled_so_far(db: Session, ben_id: int, mission_id: str) -> float:
    """EBX this benefactor has already rolled out of this mission.

    Summed from `new_value` (the exact float) rather than `amount_ebx` (whole
    EBX, for the human-readable ledger) — rounding the roll and then deriving
    the send floor from it would let the floor drift every time the slider
    moves. Cf. the open "skim ledger rounding" item in the backlog.
    """
    return float(db.scalar(
        select(sqlfunc.sum(sqlfunc.coalesce(models.Transaction.new_value,
                                            models.Transaction.amount_ebx))).where(
            models.Transaction.ben_id == ben_id,
            models.Transaction.mission_id == mission_id,
            models.Transaction.bucket == CARRYOVER_BUCKET,
        )
    ) or 0)


def _send_floor(rows, winner_id: Optional[str], original: float, current: float) -> float:
    """The irrevocable slice of the ORIGINAL phase-1 commitment: 20% of what
    backed the winner, 10% of the rest. Scaled off the original total so a
    second pass at the slider can't dip into money already in the pool."""
    if current <= 0:
        return 0.0
    scale = original / current
    return sum(
        float(r.ebx_committed or 0) * scale
        * (P1_SEND_WIN if r.tiv_id == winner_id else P1_SEND_LOSE)
        for r in rows
    )


def p1_carryover_state(db: Session, ben_id: int, mission_id: str) -> dict:
    """What a benefactor's phase-1 commitment looks like once the initiative
    election is over — the numbers behind the OE carryover slider (2026-08-06).

    After `finalize_p1`, the losing initiatives (and the vote rows behind them)
    have already rolled to the cause's next cycle via `_carry_losers_forward`.
    What is still sitting in THIS mission is what backed the winner. Of that, the
    **send** is irrevocable — it went to the pool the moment the election closed
    — and the rest is the benefactor's to keep here or roll forward.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    from . import bootstrap
    rows = get_p1_votes(db, ben_id, mission_id)
    winner_id = mission.winning_tiv_id
    total = sum(float(r.ebx_committed or 0) for r in rows)
    already = float(_rolled_so_far(db, ben_id, mission_id))
    # The send is a slice of the ORIGINAL commitment, not of whatever is left
    # after a previous roll — otherwise moving the slider twice would eat into
    # money that is already irrevocably in the pool.
    original = total + already
    send = _send_floor(rows, winner_id, original, total)
    # What they voted for here, strongest first (their slate as it was cast).
    my_picks = [
        {"tiv_id": r.tiv_id, "ebx": round(float(r.ebx_committed or 0), 2),
         "share": round(float(r.share or 0), 4), "won": r.tiv_id == winner_id}
        for r in sorted(rows, key=lambda r: -(float(r.ebx_committed or 0)))
    ]
    next_mid = bootstrap.mission_id(mission.cause_id, (mission.cycle_num or 0) + 1) \
        if mission.cause_id in bootstrap.CAUSE_PREFIX else None
    return {
        "mission_id": mission_id,
        "cause_id": mission.cause_id,
        "winning_tiv_id": winner_id,
        "backed_winner": any(p["won"] for p in my_picks),
        "my_picks": my_picks,
        "total_ebx": round(total, 2),
        "original_ebx": round(original, 2),
        "sent_to_pool_ebx": round(send, 2),     # irrevocable, already in the pool
        "movable_ebx": round(max(0.0, total - send), 2),
        "kept_here_ebx": round(total, 2),       # everything still here is "kept"
        "already_rolled_ebx": round(float(already), 2),
        "next_mission_id": next_mid,
        "open": bool(winner_id and not mission.winning_org_id and mission.current_phase == "initiative"),
    }


def carryover_p1(db: Session, ben_id: int, mission_id: str, keep_ebx: float) -> dict:
    """Keep `keep_ebx` of this mission's phase-1 commitment here; roll the rest
    into the next iteration of the same cause.

    The **send** can never be rolled — it is the irrevocable slice that made the
    election real (20% behind the winner, 10% behind the rest), so `keep_ebx` is
    clamped to at least that. Rolled EBX lands on the benefactor's carried rows
    in the next-cycle mission when they have any, and is booked to the ledger
    either way so the balance is auditable.

    Open during phase 2 only — the same window as `withdraw_p1`. Once an
    organization is elected the pool locks.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if not mission.winning_tiv_id or mission.winning_org_id or mission.current_phase != "initiative":
        raise ValueError("The carryover choice is open during phase 2 only "
                         "(after the initiative is elected, before budgeting)")
    from . import bootstrap

    rows = [r for r in get_p1_votes(db, ben_id, mission_id) if float(r.ebx_committed or 0) > 0]
    total = sum(float(r.ebx_committed or 0) for r in rows)
    if total <= 0:
        raise ValueError("You have no commitment in this mission")
    already = float(_rolled_so_far(db, ben_id, mission_id))
    send = _send_floor(rows, mission.winning_tiv_id, total + already, total)
    try:
        keep = float(keep_ebx)
    except (TypeError, ValueError):
        raise ValueError("keep_ebx must be a number")
    keep = max(send, min(total, keep))
    rolled = total - keep
    if rolled <= 0:
        return {"mission_id": mission_id, "kept_ebx": round(total, 2), "rolled_ebx": 0.0,
                "next_mission_id": None, "landed_on": []}

    # Take the rolled amount off each row proportionally, never below its share
    # of the send floor.
    for r in rows:
        committed = float(r.ebx_committed or 0)
        floor = send * (committed / total) if total else 0.0
        take = min(rolled * (committed / total), max(0.0, committed - floor))
        r.ebx_committed = committed - take

    next_mid = bootstrap.mission_id(mission.cause_id, (mission.cycle_num or 0) + 1) \
        if mission.cause_id in bootstrap.CAUSE_PREFIX else None
    landed: list[str] = []
    if next_mid is not None:
        if db.get(models.Mission, next_mid) is None:
            bootstrap.ensure_mission(db, mission.cause_id, (mission.cycle_num or 0) + 1)
        # If they already hold carried rows there (losing initiatives that rolled
        # forward), the money lands on them proportionally and becomes votes.
        carried = [r for r in get_p1_votes(db, ben_id, next_mid)]
        base = sum(float(r.ebx_committed or 0) for r in carried)
        if carried and base > 0:
            for r in carried:
                r.ebx_committed = float(r.ebx_committed or 0) + rolled * (float(r.ebx_committed or 0) / base)
                landed.append(r.tiv_id)
        elif carried:
            each = rolled / len(carried)
            for r in carried:
                r.ebx_committed = float(r.ebx_committed or 0) + each
                landed.append(r.tiv_id)
        # No carried rows: the ledger entry below is the whole record — the
        # balance is theirs to allocate when the next election opens.
    db.add(models.Transaction(
        type="transfer", bucket=CARRYOVER_BUCKET, ben_id=ben_id, mission_id=mission_id,
        phase="p2", target=next_mid, amount_ebx=int(round(rolled)),
        new_value=round(rolled, 6),   # exact, so the send floor can't drift
        note=f"carryover {mission_id}->{next_mid or 'unassigned'} "
             f"(kept {round(keep, 2)} of {round(total, 2)} EBX)",
    ))
    db.commit()
    recompute_pool(db, mission_id)
    return {
        "mission_id": mission_id,
        "kept_ebx": round(keep, 2),
        "rolled_ebx": round(rolled, 2),
        "next_mission_id": next_mid,
        "landed_on": landed,
    }


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

    Election rules:
      * orgs can RUN AND RECEIVE VOTES without being registered — a vote for an
        org with no candidacy auto-creates a pending one (vote = implicit
        nomination, submitted_by = the voter);
      * a missing mission statement does NOT block votes — it blocks ELECTION
        (enforced in finalize_p2) and is surfaced as a display flag;
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
        # Vote = implicit nomination. The org enters the race unregistered.
        cand = models.MissionCandidacy(
            mission_id=mission_id, org_id=org_id,
            submitted_by_id=ben_id, status="pending",
        )
        db.add(cand)
        db.flush()
    if cand.status == "rejected":
        raise ValueError("This organization was rejected for this mission — its votes were refunded and it can no longer receive them")
    # PRICING is server-authoritative: additional votes cost 10, 20, 40, 80 …
    # EBX (10 × 2^(n−1) for the nth extra). The client's ebx_spent is ignored.
    ebx_spent = p2_vote_cost(votes)
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


def p2_ebx_by_ben(db: Session, mission_id: str) -> dict[int, float]:
    """The EBX each benefactor carries into a mission's ORGANIZATION election.

    §1 (2026-08-08). Phase 2 is not funded by a second 10-EBX allowance — it is
    funded by what phase 1 left behind. When the initiative election closed each
    backer chose (via the carryover slider) how much of their commitment stays
    in this mission; whatever stayed is the weight that follows their org vote.
    Their remaining `VoteP1.ebx_committed` rows for this mission ARE that
    number, so this is a straight per-benefactor sum.

    structure.md, main.html › Table › Vote dialog › OE: "Votes column needs to
    have the amount of p2 votes, not p1. That is also the count we route the
    votes committed after p1 in and the pool."
    """
    out: dict[int, float] = {}
    for v in db.scalars(select(models.VoteP1).where(models.VoteP1.mission_id == mission_id)).all():
        out[v.ben_id] = out.get(v.ben_id, 0.0) + float(v.ebx_committed or 0)
    return out


def p2_tally(db: Session, mission_id: str) -> dict:
    """Per-org net vote count for a mission's phase-2 election. Blocks (harmful)
    subtract; support (helpful) adds; neutral is 0.

    §2 (2026-08-05): also reports **EBX** per org and the race total. The
    election cards rank on EBX rather than percentages — "that allows one to
    estimate the total pool size" (jax notes 2) — and a percentage can't do
    that. EBX is counted at face value regardless of valence: a block still
    spent its money, it just pushes the net vote count the other way.

    §1 (2026-08-08) — **the race was reading 0 EBX everywhere.** The only money
    it counted was `ebx_spent`, and `p2_vote_cost(1)` is 0 by design (the first
    org vote is free), so a race with real votes and no bought extras totalled
    zero. An org's EBX is now:

        carried_ebx  the phase-1 commitment its voters kept in this mission
        bought_ebx   what those voters spent on EXTRA votes
        ebx          the sum — the money standing behind that organization

    and the race carries an `unassigned_ebx` figure too: EBX kept here by
    benefactors who have not yet picked an organization. `pool_ebx` (assigned +
    unassigned) is the whole phase-2 pool, which is what the cards mean by
    "Race pool". Ranking is by **votes first, EBX second** — the rule the org
    faces already follow (§4, 2026-08-06).
    """
    votes = db.scalars(select(models.VoteP2).where(models.VoteP2.mission_id == mission_id)).all()
    carried = p2_ebx_by_ben(db, mission_id)
    per_org: dict[str, dict] = {}
    for v in votes:
        e = per_org.setdefault(v.org_id, {"net_votes": 0, "voters": 0,
                                          "carried": 0.0, "bought": 0.0})
        e["net_votes"] += int(v.votes) * int(VALENCE_SIGN[v.valence])
        e["voters"] += 1
        e["bought"] += float(v.ebx_spent or 0)
        e["carried"] += float(carried.get(v.ben_id, 0.0))
    entries = [
        {"org_id": oid, "net_votes": s["net_votes"], "voter_count": s["voters"],
         "carried_ebx": round(s["carried"], 2), "bought_ebx": round(s["bought"], 2),
         "ebx": round(s["carried"] + s["bought"], 2)}
        for oid, s in sorted(per_org.items(),
                             key=lambda kv: (-kv[1]["net_votes"],
                                             -(kv[1]["carried"] + kv[1]["bought"])))
    ]
    voted = {v.ben_id for v in votes}
    unassigned = sum(ebx for ben, ebx in carried.items() if ben not in voted)
    assigned = sum(e["ebx"] for e in entries)
    return {
        "mission_id": mission_id,
        "entries": entries,
        "total_ebx": round(assigned, 2),          # money standing behind an org
        "unassigned_ebx": round(unassigned, 2),   # kept here, no org picked yet
        "pool_ebx": round(assigned + unassigned, 2),
        "total_votes": sum(e["net_votes"] for e in entries),
        "voter_count": len(voted),
    }


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
    candidacy to 'won' (others 'lost'), advances to the budget phase.

    Mission-statement rule bites HERE, not at vote time: an org can run and
    receive votes unregistered, but cannot be ELECTED without a mission
    statement — the tally walks down to the best-placed org that has one."""
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    tally = p2_tally(db, mission_id)
    cands = {
        c.org_id: c
        for c in db.scalars(
            select(models.MissionCandidacy).where(models.MissionCandidacy.mission_id == mission_id)
        ).all()
    }
    winner_entry = None
    for entry in tally["entries"]:
        if entry["net_votes"] <= 0:
            break
        c = cands.get(entry["org_id"])
        if c is not None and (c.mission_statement or "").strip():
            winner_entry = entry
            break
    if winner_entry is None:
        return None
    winner_org = winner_entry["org_id"]
    mission.winning_org_id = winner_org
    mission.current_phase = "budget"
    for cand in cands.values():
        cand.status = "won" if cand.org_id == winner_org else "lost"
        if cand.org_id == winner_org:
            cand.p2_vote_tally = winner_entry["net_votes"]
    # §1a: settlement mints the mission's credit coins — every benefactor who
    # voted gets coins sized by their remaining stake.
    mint_mission_coins(db, mission_id)
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


def resync_p2_tallies(db: Session, mission_id: Optional[str] = None) -> dict[str, int]:
    """Rebuild `MissionCandidacy.p2_vote_tally` from the live phase-2 vote rows.

    §0 (2026-08-08). The tally is a display cache written once, by `finalize_p2`,
    for the winner. Nothing rewrote it when the votes underneath changed — so a
    vote withdrawn, retargeted or deleted with its account left the number
    frozen at whatever it was on election day. It is derived data; derive it.

    Pass a `mission_id` to rebuild one race, nothing to rebuild every one.
    Returns {candidacy_key: net_votes} for what actually moved.
    """
    q = select(models.MissionCandidacy)
    if mission_id:
        q = q.where(models.MissionCandidacy.mission_id == mission_id)
    cands = db.scalars(q).all()
    by_mission: dict[str, dict[str, int]] = {}
    changed: dict[str, int] = {}
    for cand in cands:
        counts = by_mission.get(cand.mission_id)
        if counts is None:
            counts = {}
            for v in db.scalars(select(models.VoteP2).where(
                    models.VoteP2.mission_id == cand.mission_id)).all():
                counts[v.org_id] = counts.get(v.org_id, 0) + int(v.votes) * int(VALENCE_SIGN[v.valence])
            by_mission[cand.mission_id] = counts
        net = int(counts.get(cand.org_id, 0))
        if int(cand.p2_vote_tally or 0) != net:
            cand.p2_vote_tally = net
            changed[f"{cand.mission_id}:{cand.org_id}"] = net
    if changed:
        db.commit()
    return changed


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
        # The three rewarded mission-support post types (1/32 each).
        alloc["reward_context"] = _T("reward", REWARD_CONTEXT, "context post reward")
        alloc["reward_investigation"] = _T("reward", REWARD_INVESTIGATION, "investigation post reward")
        alloc["reward_analysis"] = _T("reward", REWARD_ANALYSIS, "analysis post reward")
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
# Context suggestions carry the S/S/S taxonomy in `stance` (§1b):
#   Service — something we can send people to DO (orgs)
#   Supply  — WHAT those people need to do it (bens)
#   Support — assurance the issue is being resolved honestly (ebx)
SSS_VALUES = ("service", "supply", "support")


def _post_mission_id(db: Session, data: schemas.PostCreate) -> Optional[str]:
    """Resolve the mission a post targets (directly or through its tiv)."""
    if data.mission_id:
        return data.mission_id
    if data.tiv_id:
        tiv = db.get(models.Initiative, data.tiv_id)
        if tiv is not None and tiv.mission_id:
            return tiv.mission_id
    return None


def create_post(
    db: Session,
    data: schemas.PostCreate,
    author: Optional[models.BenefactorAccount] = None,
) -> models.Post:
    """Post creation rules (settled 2026-07-19; taxonomy in `post_config`).

    Benefactor categories (budgeting · mission_support · review):
      * `type` must belong to `category`.
      * author must be able to post the mission — a MEMBER, or agreed-to-become
        one via a committed phase-1 stake (`can_post_mission`).
      * one post per (ben, type, mission); replies (`parent_id`) are exempt.
        Budgeting slots are rolling — a new one should open only once the prior
        item is paid out; payout isn't built yet, so the one-open limit stands
        (tracked in INSTRUCTIONS "Post model v2").

    Org/staff lanes are unchanged: org_update = authoring-org member ·
    editorial/headline = staff.
    """
    mission_id = _post_mission_id(db, data)
    staff = author is not None and getattr(author, "is_staff", False)
    is_reply = bool(data.parent_id)

    if data.category in _STAFF_ONLY_CATEGORIES:
        if author is None:
            raise PermissionError("editorial/headline posts require an employee account")
        require_staff(author)

    elif data.category == "org_update":
        org_id = data.org_author_id or data.org_id
        if author is None or org_id is None:
            raise PermissionError("org updates require a signed-in org member")
        if not staff and get_membership(db, author.id, org_id) is None:
            raise PermissionError("org updates require membership in the authoring organization")

    elif data.category in pcfg.POST_REQUIRES_MEMBERSHIP:
        if author is None:
            raise PermissionError(f"{data.category} posts require a signed-in account")
        t = pcfg.TYPES.get(data.type or "")
        if t is None or t.category != data.category:
            raise ValueError(
                f"'{data.type}' is not a valid type for category '{data.category}' "
                f"(expected one of {pcfg.CATEGORIES[data.category].type_keys})"
            )
        if mission_id is None:
            raise ValueError(f"{data.category} posts must target a mission or initiative")
        if not staff and not can_post_mission(db, author.id, mission_id):
            raise PermissionError(
                "you must be a mission member — or agree to become one by committing "
                "a phase-1 stake — before posting here"
            )
        # §2a (2026-08-08): a BUDGETING post is a costed suggestion. Without a
        # setup-time estimate and a cost estimate the budget builder has nothing
        # to rank it by, so both are required at creation. Replies are exempt —
        # a reply argues about an estimate, it doesn't restate one.
        # §1 (2026-08-12): the suggestion is now a COSTED LIST — service rows
        # carry an hourly rate and a day count, supply rows a cost — so the two
        # estimates may be DERIVED from `line_items` rather than typed. A post
        # still cannot be uncosted: it must arrive with either the estimates or
        # a list the estimates can be computed from.
        if pcfg.requires_estimates(data.category) and not is_reply:
            derived = pcfg.estimates_from_line_items(data.type, getattr(data, "line_items", None))
            for field, value in derived.items():
                if getattr(data, field, None) is None:
                    setattr(data, field, value)
            missing = [f for f in pcfg.ESTIMATE_FIELDS if getattr(data, f, None) is None]
            if missing:
                raise ValueError(
                    "a budgeting suggestion needs a costed line item — or one estimate "
                    "for the setup time and one for the cost (missing: "
                    + ", ".join(missing) + ")"
                )
            if any((getattr(data, f) or 0) < 0 for f in pcfg.ESTIMATE_FIELDS):
                raise ValueError("estimates cannot be negative")
            bad = pcfg.invalid_line_items(data.type, getattr(data, "line_items", None))
            if bad:
                raise ValueError("this budget row is incomplete: " + bad)

        if not is_reply:
            dup = db.scalar(
                select(models.Post).where(
                    models.Post.ben_author_id == author.id,
                    models.Post.mission_id == mission_id,
                    models.Post.type == data.type,
                    models.Post.parent_id.is_(None),
                )
            )
            if dup is not None:
                raise ValueError(
                    f"you already have a {data.type} post for this mission — edit it, "
                    f"or reply to add more (one {data.type} per mission)"
                )

    post = models.Post(**data.model_dump())
    # Post-support layer: every post is rated on the way in so the mission
    # annulus never has to deal with an unrated row. The classifier is a stub
    # and rates everything green; only org-tagged types are read off it.
    post.flag = pcfg.classify_flag(data.type, data.body, data.title)
    # Normalise the derived mission onto benefactor posts so the per-type limit
    # and the "my posts" history are reliable even when the post targets a tiv.
    if data.category in pcfg.POST_REQUIRES_MEMBERSHIP and post.mission_id is None:
        post.mission_id = mission_id
    # Attribute ben-authored posts to the signed-in account so the profile
    # "my posts" history + helpful-post rewards can find them.
    if author is not None and post.author_type == "ben" and post.ben_author_id is None:
        post.ben_author_id = author.id
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def react_to_post(db: Session, post_id: str, ben_id: int, value: str) -> models.Post:
    """Upsert a ben's reaction and keep the denormalised counts in sync.

    Reactions are one backend enum (helpful/neutral/harmful); a post type only
    exposes a SUBSET (post_config). Budgeting = helpful only; review = helpful/
    harmful (Fair/Unfair). Reject anything the type doesn't allow so hidden
    reactions can't be forced through the API."""
    _valence_ok(value)
    post = db.get(models.Post, post_id)
    if post is None:
        raise ValueError("Post not found")
    if post.type and pcfg.is_benefactor_type(post.type) and not pcfg.is_reaction_allowed(post.type, value):
        allowed = ", ".join(pcfg.reaction_label(post.type, r) for r in pcfg.allowed_reactions(post.type))
        raise ValueError(f"'{value}' isn't a valid reaction for a {post.type} post (allowed: {allowed})")
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


# ===========================================================================
# Post-support layer — the first layer of the mission annulus.
# ===========================================================================
def set_post_flag(db: Session, post_id: str, flag: str,
                  reason: Optional[str] = None) -> models.Post:
    """Staff override on a post's post-support rating (green/orange/red)."""
    if not pcfg.is_flag(flag):
        raise ValueError(f"unknown flag '{flag}' (expected one of {pcfg.FLAGS})")
    post = db.get(models.Post, post_id)
    if post is None:
        raise ValueError("post not found")
    post.flag = flag
    post.flag_reason = reason
    db.commit()
    db.refresh(post)
    return post


def post_support_layer(db: Session, mission_id: str) -> dict:
    """The mission annulus's first layer, per ORGANIZATION.

    Only ORG-TAGGED posts are rated — case, investigation and evaluation are
    the three types that name an organization (post_config.ORG_TAGGED_TYPES).
    Everything else on a mission is discussion about the mission, not about a
    philanthropy, and is not in this layer.

    The philanthropy on the other end gets a weekly digest built from exactly
    this shape, which is why the counts are grouped by org and every thread
    carries its own flag rather than an average.
    """
    rows = db.scalars(
        select(models.Post).where(
            models.Post.mission_id == mission_id,
            models.Post.type.in_(pcfg.ORG_TAGGED_TYPES),
            models.Post.parent_id.is_(None),
        ).order_by(models.Post.created_at.desc())
    ).all()

    orgs: dict[str, dict] = {}
    totals = {f: 0 for f in pcfg.FLAGS}
    for p in rows:
        flag = p.flag if pcfg.is_flag(p.flag or "") else "green"
        totals[flag] += 1
        key = p.org_id or "__untagged__"
        bucket = orgs.setdefault(key, {
            "org_id": p.org_id,
            "org_name": None,
            "counts": {f: 0 for f in pcfg.FLAGS},
            "threads": [],
        })
        bucket["counts"][flag] += 1
        bucket["threads"].append({
            "post_id": p.id,
            "type": p.type,
            "title": p.title or (p.body or "")[:70],
            "flag": flag,
            "flag_reason": p.flag_reason,
            "helpful_count": p.helpful_count or 0,
            "harmful_count": p.harmful_count or 0,
            "created_at": p.created_at,
        })

    for key, bucket in orgs.items():
        if bucket["org_id"]:
            org = db.get(models.Organization, bucket["org_id"])
            bucket["org_name"] = org.name if org else bucket["org_id"]
        else:
            bucket["org_name"] = "Untagged"

    return {
        "mission_id": mission_id,
        "rated_types": list(pcfg.ORG_TAGGED_TYPES),
        "flag_meaning": dict(pcfg.FLAG_MEANING),
        "total": len(rows),
        "counts": totals,
        # Most-flagged first so the digest leads with what needs an answer.
        "orgs": sorted(orgs.values(),
                       key=lambda b: (-b["counts"]["red"], -b["counts"]["orange"],
                                      -sum(b["counts"].values()))),
    }


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
    "org_claims": models.OrgClaim,
    "mission_steps": models.MissionStep,
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
