"""The wallet — reading and moving a benefactor's money.

`token_model.py` owns the arithmetic; this module is the only place that lets it
touch the database. Split deliberately: every rule in the model is testable
without a session, and every write here is a thin, auditable application of one.

Rewritten 2026-08-27c for the finalized model (`docs/_to_delete/ME_OE_FINALIZATION.md`).
Seven operations, and the shape of the list is the model:

    read_wallet     what the four segments hold right now
    ensure_grant    keeps the bar grant-free: since 2026-10-09 (ruling 19) the
                    grant is ten tokens in EVERY initiative election, not a
                    weekly pile (`grant_info`, `crud.replace_p1_shares`)
    harden_due      the week roll — standing OE allocations become EBX
    set_stake       an allocation, as a POSITION: up or down, inside the week
    move_stake      ct from one race to another, carrying its philanthropy vote
    set_org         name the philanthropy this race's ct stand behind
    withdraw        purchased, unvoted ct back to cash

TWO THINGS THAT USED TO BE HERE ARE GONE, and they went together:
`commit_stake`'s one-way door and `convert_stake`'s budget of three. The week
change does both jobs now. Inside its own week an allocation is a draft — set
it, unset it, move it between races as often as you like — and at the roll every
standing OE allocation hardens into EBX and stops moving. That prices nothing,
punishes no deliberation, and gives every benefactor the same deadline instead
of a private counter nobody else could see.

WHAT IS SOFT, AND WHAT IS NOT
-----------------------------
    granted ct      ten in every initiative election, spent first, never in the
                    wallet (ruling 19, 2026-10-09). Cannot be transferred or
                    withdrawn — there is no moment at which it exists and is
                    free — and unused it never becomes money at all.
    purchased ct    exists the moment it is bought; transferable and
                    withdrawable right up until it enters this week's election.
    marked ct       lost an initiative election. Still a token, still movable —
                    but only by VOTING for a philanthropy somewhere, and never
                    back to the unallocated bar or out to cash.
    minted ct       EBX. Mission-tied, immovable, the benefactor's holding until
                    it is donated in tranches as the mission runs.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, token_model as tm
from .bootstrap import GENESIS, WEEK

# ---------------------------------------------------------------------------


def current_week(now: Optional[datetime] = None) -> int:
    """Cycle week index — the same anchor the frontend's `EBX.Cycle` uses
    (`cycleStart 2026-04-28T12:00`). Grants, allocations and the roll are all
    counted in these, never in wall-clock days, so a page loaded at 23:59 and
    one loaded at 00:01 cannot disagree about which week it is."""
    now = now or datetime.utcnow()
    return max(0, int((now - GENESIS) / WEEK))


def active_cause_id(now: Optional[datetime] = None) -> Optional[str]:
    """The cause whose window is open this week — the one a grant is issued
    against. A pure function of the calendar, so the grant's tag and the page's
    active cause cannot drift apart."""
    from . import bootstrap, crud
    try:
        return bootstrap._BY_INDEX[crud.active_cause_index(now)]
    except Exception:
        return None


# Eight is the steady state — a mission enters phase 2 every week and leaves
# eight weeks later — and it is also the whole table. The model's FOURTEEN is a
# lifetime, not a screen: wait six weeks and six more races have opened under a
# marked token, which is 8 + 6. The table is always the eight open now.
OE_TABLE_ROWS = tm.OE_TABLE_ROWS


def _vote_day(m: models.Mission) -> datetime:
    """The day this mission's philanthropy election is decided: T + 15 weeks
    from the mission opening (initiative at +7, philanthropy 8 weeks later)."""
    return (m.started_at or GENESIS) + 15 * WEEK


def week_date(week: Optional[int]) -> Optional[datetime]:
    """A cycle week index as a wall-clock date — the day that week begins."""
    if week is None:
        return None
    return GENESIS + int(week) * WEEK


def _open_p2_missions(db: Session) -> list[models.Mission]:
    """Missions whose organization election is open: an initiative has won and
    no philanthropy has yet. The eight closing soonest, in the order they
    close."""
    rows = db.scalars(
        select(models.Mission).where(
            models.Mission.winning_tiv_id.is_not(None),
            models.Mission.winning_org_id.is_(None),
        )
    ).all()
    return sorted(rows, key=_vote_day)[:OE_TABLE_ROWS]


def _vote_row(db: Session, ben_id: int, mission_id: str) -> Optional[models.VoteP2]:
    return db.scalars(
        select(models.VoteP2).where(models.VoteP2.ben_id == ben_id,
                                    models.VoteP2.mission_id == mission_id)
    ).first()


def stake_ct_of(v: models.VoteP2, derived_ebx: float = 0.0) -> int:
    """This row's total ct in its race — soft and minted together.

    `stake_ct` is authoritative once written. Rows that predate the column fall
    back to the DERIVED phase-1 figure they were carrying before, so an old race
    still renders its real numbers instead of a column of zeroes.
    """
    if v is not None and int(v.stake_ct or 0) > 0:
        return int(v.stake_ct)
    return tm.ct_from_tokens(max(0.0, float(derived_ebx or 0.0)))


def p1_stake_ct_of(r: models.VoteP1) -> int:
    """A phase-1 row's ct — the ME mirror of `stake_ct_of`.

    §0a (2026-08-28). `VoteP1.stake_ct` arrived with the finalized model
    (migration c5d8f2a91e67) and nothing backfilled it, so every row written
    before 2026-08-27c carries `stake_ct = 0` with its real amount still in the
    legacy float `ebx_committed`. `read_wallet` read the new column directly and
    counted all of that as nothing: 65 tokens standing in six open initiative
    elections reported as 0 committed.

    The P2 side has had exactly this fallback since the column landed
    (`stake_ct_of`); this is the same rule for P1, so an unbackfilled row can
    never read as a zero again. `ct_from_tokens` rounds UP at the ct boundary,
    which is also where the fractional legacy amounts (6.25, 1.7142857…, 8.1)
    stop being fractional — a ct is the smallest thing the model has.
    """
    if r is None:
        return 0
    if int(getattr(r, "stake_ct", 0) or 0) > 0:
        return int(r.stake_ct)
    return tm.ct_from_tokens(max(0.0, float(getattr(r, "ebx_committed", 0) or 0)))


def backfill_p1_stake_ct(db: Session) -> list[int]:
    """Write the legacy amount into `stake_ct` once, and report what moved.

    Idempotent: a row that already has a positive `stake_ct` is left alone, so
    this is safe to run at every boot. Returns the ids it wrote.
    """
    written: list[int] = []
    for r in db.scalars(select(models.VoteP1)).all():
        if int(getattr(r, "stake_ct", 0) or 0) > 0:
            continue
        ct = tm.ct_from_tokens(max(0.0, float(getattr(r, "ebx_committed", 0) or 0)))
        if ct > 0:
            r.stake_ct = ct
            written.append(int(r.id))
    if written:
        db.commit()
    return written


def minted_ct_of(v: Optional[models.VoteP2]) -> int:
    """The EBX this row has hardened into — mission-tied and immovable."""
    return max(0, int(getattr(v, "minted_ct", 0) or 0)) if v is not None else 0


def held_ebx_ct_of(v: Optional[models.VoteP2]) -> int:
    """EBX held: everything minted. 2026-09-16 — a skim only marks finality, so
    `donated_ct` (final-so-far) no longer comes off the position. What will come
    off it is deployment, which is not booked yet."""
    if v is None:
        return 0
    return minted_ct_of(v)


def unminted_ct_of(v: Optional[models.VoteP2], week: int = 0,
                   derived_ebx: float = 0.0) -> int:
    """The part of this row that is still a TOKEN — allocated, not yet EBX.

    Accounting, not permission: this is what the wallet's `committed` segment
    counts, whether or not the benefactor may still move it right now. Whether
    they may is `is_movable`, and keeping the two apart is what stops a row that
    is waiting for the roll from vanishing out of the conservation law.
    """
    if v is None:
        return 0
    return max(0, stake_ct_of(v, derived_ebx) - minted_ct_of(v))


def is_movable(v: Optional[models.VoteP2], week: int) -> bool:
    """Whether this row's unminted ct can be moved right now.

    Three ways ct in a race is still movable, and only three:

    * it was allocated THIS week (`tm.is_soft`), so the roll has not reached it;
    * it names no philanthropy, so there is nothing to harden into — an unvoted
      stake stays a token until its race finalizes, and then follows the winner;
    * it is MARKED — it lost an initiative election, and rule 4 hands its backer
      a live token rather than a settled one.

    Everything else is EBX, and EBX does not move.
    """
    if v is None:
        return False
    if unminted_ct_of(v) <= 0:
        return False
    if v.org_id is None or getattr(v, "marked_tiv_id", None):
        return True
    return tm.is_soft(getattr(v, "committed_week", None), week)


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------
def read_wallet(db: Session, ben_id: int, now: Optional[datetime] = None) -> tm.Wallet:
    """The four segments, from the rows that hold them.

    `unallocated -> committed -> minted -> donated`, and three of the four are
    now BOOKED rather than recomputed. The OE half of settlement used to be
    derived on every read — the right number in the wrong place — and
    `minted_ct` / `donated_ct` are the columns that end that. What is still
    summed here is only what a sum is honest for: how much of a benefactor's
    money is sitting in each state right now.
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")

    from . import crud   # local import: crud imports this module's siblings

    week = current_week(now)
    committed = 0
    minted = 0
    donated = 0
    final = 0
    for v in db.scalars(select(models.VoteP2).where(models.VoteP2.ben_id == ben_id)).all():
        derived = crud.p2_ebx_by_ben(db, v.mission_id).get(ben_id, 0.0)
        committed += unminted_ct_of(v, week, derived)
        minted += held_ebx_ct_of(v)
        donated += max(0, int(getattr(v, "donated_ct", 0) or 0))
        final += final_ct_of(db, v, now)

    # The ME side counts too. An initiative-election allocation is a token in an
    # election — the same `committed` state as an OE allocation that has not
    # hardened — and leaving it out is what made the allocations panel report
    # one balance twice before 2026-08-27c.
    #
    # §0a (2026-09-08) — **and the hand-off had a hole in it.** The rule was
    # "the initiative election closed, so the OE row holds it now", applied
    # whether or not there IS an OE row. `finalize_p1` writes one, but every
    # mission decided before 2026-08-27c closed without it, and for those the
    # skip did not hand the money on — it deleted it from every surface a
    # benefactor can see. jjager12 held 8 tokens in `oce0`, their only vote on
    # the platform, and the wallet reported ZERO committed; Jackson lost 1 more
    # the same way. The row is skipped now only when a phase-2 row actually
    # exists to carry it, so an allocation is counted exactly once and never
    # zero times. (The missing phase-2 POSITIONS are a separate, case-by-case
    # question — `oce0`'s organization election is already decided, so nothing
    # here mints one after the fact.)
    p2_missions = {
        m for (m,) in db.execute(
            select(models.VoteP2.mission_id).where(models.VoteP2.ben_id == ben_id)
        ).all()
    }
    for r in db.scalars(select(models.VoteP1).where(models.VoteP1.ben_id == ben_id)).all():
        m = db.get(models.Mission, r.mission_id)
        if m is not None and m.winning_tiv_id and r.mission_id in p2_missions:
            continue          # the initiative election closed; the OE row holds it now
        committed += p1_stake_ct_of(r)

    free = int(ben.free_ct or 0)
    return tm.Wallet(cash_ct=int(ben.cash_ct or 0), free_ct=free,
                     purchased_ct=min(int(ben.purchased_ct or 0), free),
                     committed_ct=committed, minted_ct=minted, donated_ct=donated,
                     grant_week=getattr(ben, "last_grant_week", None),
                     final_ct=final)


def budget_day(m: models.Mission) -> datetime:
    """T + 15 weeks: every donation to this mission is final (2026-09-16).
    The mission opens at `started_at`, T is 7 weeks later."""
    return (m.started_at or GENESIS) + (7 + tm.BUDGET_DAY_AFTER_ME_WEEKS) * WEEK


def final_ct_of(db: Session, v: Optional[models.VoteP2],
                now: Optional[datetime] = None) -> int:
    """This row's deductible, non-withdrawable ct (`tm.final_ct`)."""
    if v is None:
        return 0
    m = db.get(models.Mission, v.mission_id)
    reached = bool(m is not None and (now or datetime.utcnow()) >= budget_day(m))
    return tm.final_ct(stake_ct_of(v), int(getattr(v, "donated_ct", 0) or 0), reached)


def _oe_row(db: Session, m: models.Mission, ben_id: Optional[int], ben, free: int,
            purchased: int, active_id: Optional[str], week: int,
            now: Optional[datetime] = None) -> dict:
    """One organization race as the ballot reads it (the body of `oe_rows`)."""
    from . import crud
    tiv = db.get(models.Initiative, m.winning_tiv_id) if m.winning_tiv_id else None
    v = _vote_row(db, ben_id, m.id) if ben_id else None
    derived = crud.p2_ebx_by_ben(db, m.id).get(ben_id, 0.0) if ben_id else 0.0
    my_ct = stake_ct_of(v, derived) if (v or derived) else 0
    unminted = unminted_ct_of(v, week, derived) if v else 0
    backed_winner = False
    if ben_id and m.winning_tiv_id:
        backed_winner = db.scalars(
            select(models.VoteP1).where(models.VoteP1.ben_id == ben_id,
                                        models.VoteP1.mission_id == m.id,
                                        models.VoteP1.tiv_id == m.winning_tiv_id)
        ).first() is not None
    # 2026-10-09 (ruling 20, replaces 16): everyone has the nominal vote in every
    # open organization election; only a voter in its initiative election may
    # commit tokens to it (carried tokens count on the ladder either way).
    can_commit = bool(ben_id) and (_carried_from_me(v) or _voted_in_me(db, ben_id, m.id))
    headroom = purchased if can_commit else 0
    return {
        "mission_id": m.id,
        "cause_id": m.cause_id,
        "cycle_num": m.cycle_num,
        "tiv_id": m.winning_tiv_id,
        "tiv_title": (tiv.title if tiv else m.winning_tiv_id),
        "tiv_emoji": (tiv.emoji if tiv else None),
        "vote_date": _vote_day(m).isoformat(),
        "my_stake_ct": my_ct,
        # The three states, per row, so the table can say which of a
        # benefactor's ct here is still theirs to move.
        "my_committed_ct": unminted,
        "my_minted_ct": held_ebx_ct_of(v),
        "my_donated_ct": max(0, int(getattr(v, "donated_ct", 0) or 0)) if v else 0,
        "my_org_id": (v.org_id if v else None),
        "marked_tiv_id": (getattr(v, "marked_tiv_id", None) if v else None),
        "movable": is_movable(v, week),
        "committed_week": (getattr(v, "committed_week", None) if v else None),
        "hardens_week": (tm.hardens_at_week(v.committed_week)
                         if (v and getattr(v, "committed_week", None) is not None)
                         else None),
        # 2026-09-16 — backing the winning initiative is a fact worth showing
        # (bragging rights), not a multiplier. Being right is rewarded by the
        # deployment order, so weight is the stake through the block curve.
        "backed_winner": backed_winner,
        "my_weight": tm.weight_tokens(my_ct),
        "my_votes": tm.oe_votes(my_ct),            # 2026-09-17: the doubling ladder
        # ruling 20 (2026-10-09): the nominal vote is everyone's, in every race;
        # tokens are for the people who voted in its initiative election.
        "can_take_part": bool(ben_id),
        "can_commit": can_commit,
        "my_final_ct": final_ct_of(db, v, now) if v else 0,
        "born_week": (v.born_week if v else None),
        "origin_mission_id": ((v.origin_mission_id if v and v.origin_mission_id
                               else m.id)),
        "is_active_race": (m.id == active_id),
        "max_stake_ct": my_ct + headroom,
    }


def oe_rows(db: Session, ben_id: Optional[int],
            now: Optional[datetime] = None) -> list[dict]:
    """The OE table: one row per mission with an open philanthropy election.

    Always the eight of them at steady state, labelled by INITIATIVE rather than
    by cause — the rotation is seven weeks and the phase-2 window is eight, so
    two missions of the same cause are open at once and a cause-labelled table
    would print the same name twice.
    """
    from . import crud

    week = current_week(now)
    ben = db.get(models.BenefactorAccount, ben_id) if ben_id else None
    free = int(ben.free_ct or 0) if ben else 0
    purchased = min(int(ben.purchased_ct or 0), free) if ben else 0

    out: list[dict] = []
    open_missions = _open_p2_missions(db)
    # The race that finalizes soonest is THIS WEEK'S — the only row a granted
    # token may enter, because a granted token may only be spent in this week's
    # elections. Purchased ct may enter any of the eight; marked ct may enter
    # any of them by voting.
    active_id = open_missions[0].id if open_missions else None
    for m in open_missions:
        out.append(_oe_row(db, m, ben_id, ben, free, purchased, active_id, week, now))
    return out


def oe_row_for(db: Session, ben_id: Optional[int], mission_id: str,
               now: Optional[datetime] = None) -> Optional[dict]:
    """Mission pass (2026-10-01): one organization race's row, whether or not it
    is among the eight `oe_rows` returns. A race outside the eight (OPEN
    DEFECTS F11) still holds stakes, and its ballot needs the same row to show
    the stake and offer Withdraw. Read-only."""
    m = db.get(models.Mission, mission_id)
    if m is None or not m.winning_tiv_id or m.winning_org_id:
        return None
    week = current_week(now)
    ben = db.get(models.BenefactorAccount, ben_id) if ben_id else None
    free = int(ben.free_ct or 0) if ben else 0
    purchased = min(int(ben.purchased_ct or 0), free) if ben else 0
    open_missions = _open_p2_missions(db)
    active_id = open_missions[0].id if open_missions else None
    row = _oe_row(db, m, ben_id, ben, free, purchased, active_id, week, now)
    row["in_table"] = any(x.id == m.id for x in open_missions)
    return row


# ---------------------------------------------------------------------------
# Write — the grant, the roll, and the four moves
# ---------------------------------------------------------------------------
def ensure_grant(db: Session, ben_id: int, now: Optional[datetime] = None) -> dict:
    """Keep the unallocated bar grant-free (ruling 19, 2026-10-09).

    Until today this paid "ten tokens a week" into `free_ct` (D31: for that
    week's one initiative election, expiring at the week change). Jax, 10/9
    Reshuffle: "if it is an initiative election, there should be exactly 10
    granted tokens available, no matter what." The grant is each initiative
    election's own ten now (`grant_info`, `crud.replace_p1_shares`), so nothing
    is paid into the wallet any more. What this does — on every read path,
    idempotently — is retire whatever is left of a D31 weekly grant, so the bar
    holds purchased tokens and nothing else. Nobody loses a vote by it: every
    open initiative election, the one that pile was for included, carries its
    own ten.

    The name is kept because every read path already calls it.
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    week = current_week(now)
    free = int(ben.free_ct or 0)
    new_free, retired = tm.retire_weekly_grant(free, int(ben.purchased_ct or 0))
    changed = False
    if new_free != free or int(ben.purchased_ct or 0) != new_free:
        ben.free_ct = new_free
        ben.purchased_ct = new_free
        changed = True
    if ben.last_grant_week is None or int(ben.last_grant_week) < week:
        ben.last_grant_week = week
        changed = True
    if changed:
        db.commit()
    return {"granted_ct": 0, "week": week, "free_ct": int(ben.free_ct or 0),
            "grant_week": week, "expired_ct": retired}


def harden_due(db: Session, ben_id: Optional[int] = None,
               now: Optional[datetime] = None) -> int:
    """The week roll: every standing OE allocation becomes EBX.

    "The conversion only happens at a week-change ... All OE allocations." An
    allocation made in week *w* hardens in week *w+1*: those ct become EBX for
    that mission, mission-tied and immovable, and the coin's second element is
    written for them.

    Two rows are deliberately NOT hardened:

    * one that names no philanthropy. There is nothing to harden into — an
      unvoted stake is a token sitting in a race, and it commits to that race's
      winner when the race finalizes, not when a Tuesday arrives.
    * one that is MARKED. Its initiative lost, and rule 4 hands its backer a
      live token; it hardens when they vote for a philanthropy and the NEXT roll
      comes, which is what clearing the mark in `set_org` sets up.

    Idempotent, and safe on a read path: a row with nothing unminted is skipped,
    so calling this on every page load costs one query and changes nothing.
    Returns the number of rows hardened.
    """
    week = current_week(now)
    q = select(models.VoteP2)
    if ben_id is not None:
        q = q.where(models.VoteP2.ben_id == ben_id)
    hardened = 0
    for v in db.scalars(q).all():
        unminted = unminted_ct_of(v)
        if unminted <= 0 or v.org_id is None:
            continue
        if getattr(v, "marked_tiv_id", None):
            continue
        cw = getattr(v, "committed_week", None)
        if cw is None or int(week) <= int(cw):
            continue                     # still inside its own week: a draft
        m = db.get(models.Mission, v.mission_id)
        if m is None:
            continue
        v.minted_ct = minted_ct_of(v) + unminted
        _record(v, tm.coin_element_oe(week=week, mission_id=v.mission_id,
                                      org_id=v.org_id, amount_ct=unminted))
        hardened += 1
    if hardened:
        db.commit()
    return hardened


def _carried_from_me(v: Optional[models.VoteP2]) -> bool:
    """True if this race row holds money carried in from the mission's own
    initiative election (a `settle_me` element on its coin)."""
    return bool(v is not None and any((e or {}).get("kind") == "settle_me"
                                      for e in (v.provenance or [])))


def _voted_in_me(db: Session, ben_id: Optional[int], mission_id: str) -> bool:
    """2026-09-28 (P1 mission edits, Jax's org-vote bug): True if the benefactor
    VOTED in this mission's own initiative election, with or without tokens.

    A vote in an initiative election outside the week's cause carries no granted
    tokens (a granted token only enters its own week's elections), so it lands
    as a preference with `stake_ct = 0` and `_open_oe_stakes` has nothing to
    carry — no `settle_me` element, and the organization race then locked the
    benefactor out. Ruling 16 says whoever backed the initiative election may vote
    in its organization election in any week; a preference is backing it."""
    if not ben_id:
        return False
    return db.scalars(select(models.VoteP1.id).where(
        models.VoteP1.ben_id == ben_id, models.VoteP1.mission_id == mission_id,
        (models.VoteP1.share > 0) | (models.VoteP1.ebx_committed > 0)
        | (models.VoteP1.stake_ct > 0))).first() is not None


def _in_an_initiative_election(db: Session, ben_id: int) -> bool:
    """True if the benefactor has money standing in an initiative election."""
    return db.scalars(select(models.VoteP1.id).where(
        models.VoteP1.ben_id == ben_id, models.VoteP1.stake_ct > 0)).first() is not None


def _check_oe_minimum(v: Optional[models.VoteP2], target_ct: int,
                      db: Optional[Session] = None, ben_id: Optional[int] = None) -> None:
    """build-seq §3 (2026-09-16): at least $1 to vote in an organization election —
    unless the benefactor carried money in from this mission's initiative
    election, or already has money in an initiative election."""
    if int(target_ct) <= 0 or int(target_ct) >= tm.OE_MIN_STAKE_CT or _carried_from_me(v):
        return
    if db is not None and ben_id is not None and _in_an_initiative_election(db, ben_id):
        return
    raise ValueError(
        f"It takes at least {tm.tokens(tm.OE_MIN_STAKE_CT):g} tokens ($1) to vote in an "
        "organization election — commit your full grant, add more, or vote in the "
        "initiative election first")


def _check_takes_part(v: Optional[models.VoteP2], adding_tokens: bool,
                      voted_me: bool = False) -> None:
    """Who may put TOKENS into an organization election (ruling 20, 2026-10-09).

    Jax, 10/9 Reshuffle: "During the organization election, a user needs to have
    voted in the initiative election in order to commit more than the nominal 1
    vote (This is sort of analogous to the grant). Any tokens that carry over
    from the initiative election increase the weight of their OE vote."

    So the NOMINAL vote is everyone's, in every open organization election
    (0 tokens = 1 vote on the doubling ladder) — naming an organization never
    needs this check. Raising a stake does: only someone who voted in this
    mission's initiative election (with or without tokens), or who carried
    tokens in from it, may commit more. Lowering, clearing, and naming an
    organization for tokens already in the race are always allowed.

    Replaces ruling 16 (2026-09-17), which opened only THIS WEEK'S race to
    people who had not backed the initiative election."""
    if not adding_tokens or voted_me or _carried_from_me(v):
        return
    raise ValueError(
        "Only people who voted in this mission's initiative election can commit "
        "tokens to its organization election. Everyone has one vote here — pick "
        "an organization to cast it")


def _spendable_ct(ben: models.BenefactorAccount, is_active_race: bool) -> int:
    """What may enter an ORGANIZATION race out of the unallocated bar.

    D31 (2026-10-07): a granted token may enter only its week's initiative
    election, so no organization race — not even this week's — can take one.
    Only PURCHASED tokens (added funds) enter an organization election from the
    bar. `is_active_race` still decides who may take part (`_check_takes_part`);
    it no longer decides which tokens pay.
    """
    free = int(ben.free_ct or 0)
    return min(int(ben.purchased_ct or 0), free)


def set_stake(db: Session, ben_id: int, mission_id: str, target_ct: int,
              org_id: Optional[str] = None,
              now: Optional[datetime] = None) -> dict:
    """Set this race's allocation to `target_ct`. A position, not an addition.

    Inside its own week an allocation is a draft, so this can go DOWN as well as
    up — the difference comes back to the unallocated bar, and nothing is spent
    for the privilege. What it cannot do is reach into ct that has already
    hardened: EBX is mission-tied and the floor here is `minted_ct`.

    Naming the philanthropy in the same call is the point of the dialog — an
    amount and a choice are one gesture, and one write.
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if mission.winning_org_id:
        raise ValueError("That philanthropy election is already decided")
    if not mission.winning_tiv_id:
        raise ValueError("That mission has no elected initiative yet")

    from . import crud

    week = current_week(now)
    harden_due(db, ben_id, now)
    open_missions = _open_p2_missions(db)
    is_active = bool(open_missions) and open_missions[0].id == mission_id

    v = _vote_row(db, ben_id, mission_id)
    derived = crud.p2_ebx_by_ben(db, mission_id).get(ben_id, 0.0)
    have = stake_ct_of(v, derived) if (v or derived) else 0
    # ruling 20 (2026-10-09): raising the stake takes an initiative-election
    # vote; naming an organization (the nominal vote) never does.
    _check_takes_part(v, int(target_ct or 0) > have, _voted_in_me(db, ben_id, mission_id))
    minted = minted_ct_of(v)
    unminted = max(0, have - minted)
    if unminted > 0 and not is_movable(v, week):
        raise ValueError("Those tokens hardened into EBX at the week change — "
                         "EBX stays with its mission")
    final_floor = max(0, int(getattr(v, "donated_ct", 0) or 0)) if v is not None else 0
    if int(target_ct or 0) < final_floor and final_floor > minted:
        raise ValueError(
            f"{tm.tokens(final_floor):g} of those tokens are already final — a final "
            "donation cannot come back out of its race")
    if int(target_ct or 0) < minted:
        # Refused rather than clamped. Silently landing on the floor would tell
        # a benefactor their instruction was carried out, and it was not: EBX is
        # mission-tied, and the number they typed cannot be reached from here.
        raise ValueError(
            f"{tm.tokens(minted):g} of those tokens are already EBX for this "
            "mission — EBX stays where it is, so this race cannot go below it")

    want = max(minted, int(target_ct or 0))
    delta = want - have
    if delta > 0:
        delta = min(delta, max(0, _spendable_ct(ben, is_active)))
    want = have + delta
    _check_oe_minimum(v, want, db, ben_id)

    if v is None:
        v = models.VoteP2(ben_id=ben_id, mission_id=mission_id, org_id=None,
                          votes=1, ebx_spent=0, valence="helpful", committed=False,
                          origin_mission_id=mission_id, born_week=week,
                          conversions=0, minted_ct=0, donated_ct=0)
        db.add(v)
    if v.born_week is None:
        v.born_week = week
    if v.origin_mission_id is None:
        v.origin_mission_id = mission_id
    v.stake_ct = want
    if delta != 0:
        # The clock restarts on every deliberate change, which is the whole of
        # "as many times as they want within the same week": what hardens at the
        # roll is the allocation as it STANDS, not the first one made.
        v.committed_week = week

    # D31 (2026-10-07): purchased only, in every organization race — granted
    # ct belongs to the week's initiative election. So what comes back out of a
    # draft comes back as PURCHASED ct: nothing granted went in. (Before D31 a
    # return from this week's race refilled the grant, which would now expire a
    # benefactor's own added funds at the week change.)
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    if delta > 0:
        ben.free_ct = free - delta
        ben.purchased_ct = max(0, purchased - delta)
    elif delta < 0:
        back = -delta
        ben.free_ct = free + back
        ben.purchased_ct = purchased + back

    if org_id is not None:
        if db.get(models.Organization, org_id) is None:
            raise ValueError("Organization not found")
        v.org_id = org_id
        v.marked_tiv_id = None
        v.committed_week = week

    db.commit()
    return _row_state(db, v, ben, week)


def move_stake(db: Session, ben_id: int, from_mission_id: str, to_mission_id: str,
               ct: int, org_id: str, now: Optional[datetime] = None) -> dict:
    """Move ct from one organization election into another, carrying a vote.

    The move a MARKED token makes — "you can move your tokens to a different OE
    once you vote for a phl in that OE" — and the same move an ordinary
    allocation may make freely inside its own week. A philanthropy at the
    destination is REQUIRED either way: moving ct between races without saying
    who it now backs is precisely what the model forbids, and it is why this is
    one transaction rather than a withdrawal followed by a commitment.

    It never touches the unallocated bar, so there is no moment at which moved
    ct looks like a fresh grant — which is what the FIFO lot ledger used to
    exist to prevent, and why that ledger could be deleted.

    Free, and unlimited within the week. The budget of three conversions that
    used to be spent here is gone; the week change is the bound now.
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    if from_mission_id == to_mission_id:
        raise ValueError("That is the same organization election")
    src_m = db.get(models.Mission, from_mission_id)
    dst_m = db.get(models.Mission, to_mission_id)
    if src_m is None or dst_m is None:
        raise ValueError("Mission not found")
    if src_m.winning_org_id or dst_m.winning_org_id:
        raise ValueError("A decided philanthropy election cannot be moved "
                         "into or out of")
    if not dst_m.winning_tiv_id:
        raise ValueError("That mission has no elected initiative yet")
    if db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")

    from . import crud

    week = current_week(now)
    harden_due(db, ben_id, now)
    src = _vote_row(db, ben_id, from_mission_id)
    derived = crud.p2_ebx_by_ben(db, from_mission_id).get(ben_id, 0.0)
    have = stake_ct_of(src, derived) if (src or derived) else 0
    movable = unminted_ct_of(src, week, derived) if src is not None else 0
    if src is None or movable <= 0:
        raise ValueError("There is nothing movable in that election")
    if not is_movable(src, week):
        raise ValueError("Those tokens hardened into EBX at the week change — "
                         "EBX stays with its mission")
    move = min(max(0, int(ct or 0)), movable)
    if move <= 0:
        raise ValueError("There is nothing to move")

    dst = _vote_row(db, ben_id, to_mission_id)
    dst_derived = crud.p2_ebx_by_ben(db, to_mission_id).get(ben_id, 0.0)
    dst_have = stake_ct_of(dst, dst_derived) if (dst or dst_derived) else 0
    # ruling 20 (2026-10-09): moving tokens INTO a race commits them there, so it
    # takes a vote in that race's initiative election like any other commit.
    _check_takes_part(dst, True, _voted_in_me(db, ben_id, to_mission_id))
    _check_oe_minimum(dst, dst_have + move, db, ben_id)
    if dst is None:
        dst = models.VoteP2(ben_id=ben_id, mission_id=to_mission_id, org_id=None,
                            votes=1, ebx_spent=0, valence="helpful", committed=False,
                            origin_mission_id=to_mission_id, born_week=week,
                            conversions=0, minted_ct=0, donated_ct=0)
        db.add(dst)
    if dst.born_week is None:
        dst.born_week = week
    src.stake_ct = have - move
    dst.stake_ct = dst_have + move
    # 2026-09-16 — the FINAL part travels with the ct, in proportion, so a
    # finalized skim is never stranded on an emptied row (or doubled).
    src_final = max(0, int(getattr(src, "donated_ct", 0) or 0))
    if src_final > 0 and have > 0:
        carry = min(src_final, int(round(src_final * move / have)))
        carry = max(carry, src_final - int(src.stake_ct))   # never leave final > stake
        src.donated_ct = src_final - carry
        dst.donated_ct = max(0, int(getattr(dst, "donated_ct", 0) or 0)) + carry
    # The vote travels with the money, and the destination is home from now on:
    # a moved stake follows the winner HERE if its benefactor never votes again,
    # not the race it left.
    dst.org_id = org_id
    dst.origin_mission_id = to_mission_id
    dst.marked_tiv_id = None
    dst.committed_week = week
    if src.stake_ct <= max(0, minted_ct_of(src)):
        # An emptied row keeps its history but stops carrying a vote: a stake of
        # zero standing behind a philanthropy would still be counted a voter.
        if src.stake_ct <= 0:
            src.org_id = None
            src.marked_tiv_id = None
    db.commit()
    return {"from_mission_id": from_mission_id, "to_mission_id": to_mission_id,
            "moved_ct": move, "from_stake_ct": int(src.stake_ct or 0),
            "to_stake_ct": int(dst.stake_ct or 0), "org_id": org_id,
            "hardens_week": tm.hardens_at_week(week)}


def set_org(db: Session, ben_id: int, mission_id: str, org_id: Optional[str],
            now: Optional[datetime] = None) -> dict:
    """Name (or clear) the philanthropy this race's ct stand behind.

    A vote, not a payment — and for a MARKED token it is the vote that commits
    it: "you can move your tokens to a different OE once you vote for a phl in
    that OE. Committed tokens become EBX for that mission." Naming a
    philanthropy here clears the mark and starts the row's week clock, so the
    next roll mints it.

    `org_id=None` returns the row to the unassigned state the initiative
    election creates: it still funds the mission, carries no weight, and at
    close follows the winner of the race it is sitting in.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if mission.winning_org_id:
        raise ValueError("That philanthropy election is already decided")
    if org_id is not None and db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")

    week = current_week(now)
    harden_due(db, ben_id, now)
    v = _vote_row(db, ben_id, mission_id)
    if not mission.winning_tiv_id:
        raise ValueError("That mission has no elected initiative yet")
    # ruling 20 (2026-10-09): naming an organization is the nominal vote, and
    # everyone has it in every open organization election — no check here.
    if v is None:
        v = models.VoteP2(ben_id=ben_id, mission_id=mission_id, votes=1, ebx_spent=0,
                          valence="helpful", committed=False, stake_ct=0,
                          origin_mission_id=mission_id, born_week=week,
                          conversions=0, minted_ct=0, donated_ct=0)
        db.add(v)
    if unminted_ct_of(v) > 0 and not is_movable(v, week):
        raise ValueError("Those tokens hardened into EBX at the week change — "
                         "the philanthropy they minted behind is settled")
    v.org_id = org_id
    if org_id is not None:
        v.marked_tiv_id = None
        v.committed_week = week
    db.commit()
    ben = db.get(models.BenefactorAccount, ben_id)
    return _row_state(db, v, ben, week)


def withdraw(db: Session, ben_id: int, ct: int,
             now: Optional[datetime] = None) -> dict:
    """Take purchased, unvoted tokens back as cash.

    The one exit from the token bin, and it is only open to PURCHASED ct that
    has not entered an election. A granted token cannot be withdrawn because it
    is never both real and free — it appears in its cause's election week, and
    nothing was paid for it in the first place. Committed ct cannot be
    withdrawn because a vote is not a purchase you can return.

    Refunds land in CASH and never back in tokens, which is what keeps
    `available = max(10, held)` honest: nobody is ever billed a grant for money
    handed back to them.
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    take = max(0, int(ct or 0))
    if take <= 0:
        raise ValueError("Nothing to withdraw")
    if take > purchased:
        raise ValueError(
            "Only purchased tokens can be withdrawn, and only before they enter "
            f"an election — you hold {tm.tokens(purchased):g} of those")
    ben.free_ct = free - take
    ben.purchased_ct = purchased - take
    ben.cash_ct = int(ben.cash_ct or 0) + take
    db.commit()
    return {"withdrawn_ct": take, "free_ct": int(ben.free_ct),
            "purchased_ct": int(ben.purchased_ct), "cash_ct": int(ben.cash_ct)}


def withdraw_stake(db: Session, ben_id: int, mission_id: str, ct: int,
                   now: Optional[datetime] = None) -> dict:
    """Take the NON-FINAL part of a stake back out as cash, before budget day.

    money_model.md §0.4 (2026-09-16): "Until T+15 the non-final part can be
    withdrawn as cash." Final ct (`donated_ct`: the 10% ME skim, the +10% OE
    skim) never comes back, and from budget day on nothing does. Unminted ct
    goes first, then minted EBX. Refunds land in CASH, never back in tokens, so
    nobody is billed a grant for money handed back to them.

    Open for a mission whose initiative election has closed (a stake exists in a
    decided initiative, or in an organization race, or in framing).
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    m = db.get(models.Mission, mission_id)
    if m is None:
        raise ValueError("Mission not found")
    if not m.winning_tiv_id:
        raise ValueError("That mission's initiative election has not closed — "
                         "lower your commit there instead")
    now = now or datetime.utcnow()
    if now >= budget_day(m):
        raise ValueError("Budget day has passed: every donation to this mission is final")
    week = current_week(now)
    harden_due(db, ben_id, now)
    # Mission pass (2026-10-01) — "Even when it detects me as having a slate, I
    # can't withdraw because it says I have no slate." The page reads a stake
    # the way every other wallet path does: the row's `stake_ct`, or, for a row
    # written before that column (or a carry that never made a row — F20), the
    # DERIVED initiative-election money the race holds for this benefactor.
    # This read only `stake_ct`, so those stakes showed and could not leave.
    # Now it reads the same figure, writes it onto the row it withdraws from,
    # and treats the initiative-election skim as final if the row never
    # recorded it (F15) — a legacy row cannot hand back money the ladder says
    # is already donated.
    from . import crud
    v = _vote_row(db, ben_id, mission_id)
    derived = crud.p2_ebx_by_ben(db, mission_id).get(ben_id, 0.0)
    stake = stake_ct_of(v, derived) if (v is not None or derived) else 0
    if stake <= 0:
        raise ValueError("You have no stake in that mission")
    if v is None:
        v = models.VoteP2(ben_id=ben_id, mission_id=mission_id, org_id=None,
                          votes=1, ebx_spent=0, valence="helpful", committed=False,
                          origin_mission_id=mission_id, born_week=week,
                          conversions=0, minted_ct=0, donated_ct=0)
        db.add(v)
    if int(v.stake_ct or 0) <= 0:
        v.stake_ct = stake                      # materialize the derived figure
        if int(getattr(v, "donated_ct", 0) or 0) <= 0:
            v.donated_ct = tm.settle_me(stake).donated_ct
    final = max(0, int(getattr(v, "donated_ct", 0) or 0))
    open_ct = max(0, stake - final)
    take = min(max(0, int(ct or 0)), open_ct)
    if take <= 0:
        raise ValueError("Nothing withdrawable: the rest of this stake is already final")
    unminted = max(0, stake - minted_ct_of(v))
    from_unminted = min(take, unminted)
    from_minted = take - from_unminted
    v.stake_ct = stake - take
    v.minted_ct = minted_ct_of(v) - from_minted
    _record(v, tm.ProvenanceEvent(week=week, kind="refund", mission_id=mission_id,
                                  amount_ct=take, outcome="cash_withdrawal"))
    if v.stake_ct <= 0:
        v.org_id = None
        v.marked_tiv_id = None
    ben.cash_ct = int(ben.cash_ct or 0) + take
    db.commit()
    return {"mission_id": mission_id, "withdrawn_ct": take,
            "stake_ct": int(v.stake_ct), "final_ct": final,
            "cash_ct": int(ben.cash_ct), "budget_day": budget_day(m).isoformat()}


def _row_state(db: Session, v: models.VoteP2, ben: Optional[models.BenefactorAccount],
               week: int) -> dict:
    """One row, as the client needs to see it after a write."""
    free = int(ben.free_ct or 0) if ben is not None else 0
    purchased = min(int(ben.purchased_ct or 0), free) if ben is not None else 0
    return {
        "mission_id": v.mission_id,
        "stake_ct": int(v.stake_ct or 0),
        "committed_ct": unminted_ct_of(v),
        "minted_ct": held_ebx_ct_of(v),
        "donated_ct": max(0, int(getattr(v, "donated_ct", 0) or 0)),
        "org_id": v.org_id,
        "marked_tiv_id": getattr(v, "marked_tiv_id", None),
        "movable": is_movable(v, week),
        "committed_week": getattr(v, "committed_week", None),
        "hardens_week": (tm.hardens_at_week(v.committed_week)
                         if getattr(v, "committed_week", None) is not None else None),
        "free_ct": free,
        "purchased_ct": purchased,
        "grant_held_ct": max(0, free - purchased),
    }


def _record(v: models.VoteP2, event: tm.ProvenanceEvent) -> None:
    """Append a registered event to the row's history.

    Only what STANDS AT THE ROLL is registered. A benefactor who moves an
    allocation three times on a Thursday leaves one event behind, not three,
    because the first two were drafts — and second thoughts are not part of the
    public record of what someone's money supported.
    """
    chain = list(v.provenance or [])
    chain.append(event.as_dict())
    v.provenance = chain


# ===========================================================================
# The mission overview — build-seq P1 (2026-09-24), D3.
# ===========================================================================
def mission_overview(db: Session, m: models.Mission,
                     now: Optional[datetime] = None) -> dict:
    """The money and membership facts the mission page's overview prints.

    READ-ONLY. Two pools, both in ct, both from the rows the ladder already
    reads, so the numbers here are the ones `read_wallet` would add up:

      committed_ct   every ct standing behind this mission. Before the
                     initiative election closes that is the phase-1 slates in
                     it (`p1_stake_ct_of`); after, it is the stakes in its
                     organization election (`stake_ct_of`), which is where the
                     close moves them.
      guaranteed_ct  the FINAL part of `committed_ct` — deductible, no longer
                     withdrawable (money_model §0 rulings 1–4, `final_ct_of`).
                     0 before T; the skims after T and T+8; all of it at T+15.

    `members` counts distinct benefactors with a stake here (either election).
    """
    from . import crud            # local: crud imports wallet back
    now = now or datetime.utcnow()
    p1 = db.scalars(select(models.VoteP1).where(models.VoteP1.mission_id == m.id)).all()
    members = {r.ben_id for r in p1 if p1_stake_ct_of(r) > 0 or r.committed}
    if m.winning_tiv_id:
        # The race pool's own reading (`crud.p2_stake_by_ben`): the stake column
        # where it is written, the phase-1 carry where it is not — so this
        # number and the ballot's "Race pool" can never disagree.
        stakes = crud.p2_stake_by_ben(db, m.id)
        carried = crud.p2_ebx_by_ben(db, m.id)
        reached = now >= budget_day(m)
        rows = {v.ben_id: v for v in db.scalars(select(models.VoteP2).where(
            models.VoteP2.mission_id == m.id)).all()}
        committed = guaranteed = 0
        for ben, tokens in stakes.items():
            ct = tm.ct_from_tokens(max(0.0, float(tokens or 0)))
            if ct <= 0:
                continue
            members.add(ben)
            committed += ct
            v = rows.get(ben)
            if v is not None:
                guaranteed += tm.final_ct(stake_ct_of(v, carried.get(ben, 0.0)),
                                          int(v.donated_ct or 0), reached)
            else:
                # carried in from the initiative election, never re-voted: the
                # ME skim is final (ruling 2), all of it on budget day.
                guaranteed += ct if reached else tm.settle_me(ct).donated_ct
    else:
        committed = sum(p1_stake_ct_of(r) for r in p1)
        guaranteed = 0
    return {
        "mission_id": m.id,
        "committed_ct": int(committed),
        "guaranteed_ct": int(min(guaranteed, committed)),
        "members": len(members),
        "budget_day": budget_day(m).isoformat(),
        "budget_day_reached": now >= budget_day(m),
        "credit_value": float(m.credit_value or 1.0),
        "spent": m.spent or 0,
    }


# ===========================================================================
# The wallet build (2026-10-07, INSTRUCTIONS › BUILD SEQUENCE › Profile).
#
# "Each benefactor needs to add funds to their account first, which appear in
# their wallet. The grants should appear as a separate entity in the wallet, as
# should EBX and pre-EBX tokens. Every transaction made should rely on what is
# already in the wallet … if a user participates in a tiv election, the
# subsequent org election becomes a wallet item in the form of a membership
# coin. If there are no unallocated funds in the wallet, it should prompt
# something like 'Add funds…'."
#
# Three reads and one write, none of them a new table:
#   add_funds   cash in -> PURCHASED tokens, one ledger row per deposit
#   grant_info  this week's grant as its own entity: amount, door, expiry
#   positions   one row per mission the benefactor is in — the coins
#   stats       what the profile's right-hand panel counts
# ===========================================================================
def _funds_settings():
    from .config import get_settings
    return get_settings()


def funds_mode() -> str:
    mode = (_funds_settings().ebx_funds_mode or "test").strip().lower()
    return mode if mode in ("test", "off") else "test"


def test_deposits_ct(db: Session, ben_id: int) -> int:
    """Every test deposit this account has made, in ct (from the ledger)."""
    rows = db.scalars(select(models.Transaction).where(
        models.Transaction.ben_id == ben_id, models.Transaction.type == "transfer",
        models.Transaction.bucket == "deposit")).all()
    return sum(max(0, int(r.amount_ebx or 0)) for r in rows)


def add_funds(db: Session, ben_id: int, usd_cents: int) -> dict:
    """Add funds: dollars in, PURCHASED tokens out ($1 = 10 tokens = 1000 ct).

    Purchased tokens are the mobile money of the model (money_model §4): they
    exist the moment they are bought, may enter any election, and may be
    withdrawn back to cash until they are committed. Granted tokens are never
    touched here.

    TEST MODE. No payment processor is connected (D12). In `test` mode the
    deposit is credited at once and written to the ledger as
    `transfer / deposit` with a note saying so — one row per deposit, so every
    test dollar can be found and reversed before real money is used. `off`
    refuses. Capped per deposit and per account (config).
    """
    st = _funds_settings()
    if funds_mode() == "off":
        raise ValueError("Adding funds is switched off on this server")
    cents = int(usd_cents or 0)
    if cents < 10:
        raise ValueError("The smallest deposit is 10¢ (1 token)")
    if cents > int(st.funds_max_deposit_cents):
        raise ValueError(f"The most one deposit can add is ${st.funds_max_deposit_cents / 100:g}")
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    ct = cents * tm.CT_PER_TOKEN // 10           # 1 token = 10¢
    already = test_deposits_ct(db, ben_id)
    cap_ct = int(st.funds_max_test_cents) * tm.CT_PER_TOKEN // 10
    if already + ct > cap_ct:
        left = max(0, cap_ct - already)
        raise ValueError(
            f"Test funds are capped at ${st.funds_max_test_cents / 100:g} per account "
            f"while payments are not connected — ${tm.usd(left):.2f} left")
    ensure_grant(db, ben_id)
    db.refresh(ben)
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    ben.free_ct = free + ct
    ben.purchased_ct = purchased + ct
    db.add(models.Transaction(
        type="transfer", ben_id=ben_id, bucket="deposit", amount_ebx=ct,
        note=(f"TEST deposit ${cents / 100:.2f} = {ct} ct — no payment processor "
              f"connected (EBX_FUNDS_MODE=test). Reverse before real money is used.")))
    db.commit()
    return {"added_ct": ct, "usd_cents": cents, "mode": funds_mode(),
            "free_ct": int(ben.free_ct), "purchased_ct": int(ben.purchased_ct),
            "test_deposits_ct": already + ct}


def open_initiative_elections(db: Session, now: Optional[datetime] = None) -> list[models.Mission]:
    """Every initiative election open right now — seven at steady state, one per
    cause, one closing each week — soonest to close first. Each carries its own
    ten granted tokens for every benefactor (ruling 19, 2026-10-09)."""
    now = now or datetime.utcnow()
    rows = db.scalars(select(models.Mission).where(
        models.Mission.winning_tiv_id.is_(None), models.Mission.started_at.is_not(None),
        models.Mission.current_phase.in_(("pre", "initiative")))).all()
    live = [m for m in rows if m.started_at <= now < m.started_at + 7 * WEEK]
    return sorted(live, key=lambda m: m.started_at)


def door_mission(db: Session, now: Optional[datetime] = None) -> Optional[models.Mission]:
    """The initiative election closing soonest. Until 2026-10-09 this was the
    ONE election the week's grant could enter (D31); every open initiative
    election carries its own grant now (ruling 19), and this is only the
    nearest place to use one."""
    ms = open_initiative_elections(db, now)
    return ms[0] if ms else None


def grant_info(db: Session, ben: models.BenefactorAccount,
               now: Optional[datetime] = None) -> dict:
    """The grant as its own wallet entity — ten tokens in EACH open initiative
    election (ruling 19, 2026-10-09), with what this benefactor has used of
    each. Grant first: the first ten tokens of a commit are the grant's."""
    week = current_week(now)
    ms = open_initiative_elections(db, now)
    held: dict[str, int] = {}
    if ms:
        for r in db.scalars(select(models.VoteP1).where(
                models.VoteP1.ben_id == ben.id,
                models.VoteP1.mission_id.in_([m.id for m in ms]))).all():
            held[r.mission_id] = held.get(r.mission_id, 0) + p1_stake_ct_of(r)
    els = []
    for m in ms:
        c = held.get(m.id, 0)
        used = tm.me_grant_part(c)
        els.append({"mission_id": m.id, "cause_id": m.cause_id, "cycle_num": m.cycle_num,
                    "closes": (m.started_at + 7 * WEEK).isoformat(),
                    "committed_ct": int(c), "used_ct": int(used),
                    "left_ct": int(tm.ME_GRANT_CT - used)})
    left = sum(e["left_ct"] for e in els)
    used = sum(e["used_ct"] for e in els)
    nxt = next((e for e in els if e["left_ct"] > 0), els[0] if els else None)
    return {
        "week": week,
        "per_election_ct": tm.ME_GRANT_CT,
        "amount_ct": tm.ME_GRANT_CT,
        "elections": els,
        "open": len(els),
        "left_ct": int(left),
        "used_ct": int(used),
        "held_ct": int(left),
        # the nearest initiative election with grant left ("Use it →")
        "mission_id": nxt["mission_id"] if nxt else None,
        "cause_id": nxt["cause_id"] if nxt else None,
        "mission_closes": nxt["closes"] if nxt else None,
        "expires": nxt["closes"] if nxt else None,
        "rule": "Ten tokens from Earthbux in every initiative election. They go in first, "
                "stay with that election, and can't be withdrawn.",
    }


def _mission_dates(m: models.Mission) -> dict:
    s = m.started_at or GENESIS
    return {"opened": s.isoformat(), "me": (s + 7 * WEEK).isoformat(),
            "oe": (s + 15 * WEEK).isoformat(), "budget": (s + 22 * WEEK).isoformat()}


def mission_phase(m: models.Mission, now: Optional[datetime] = None) -> str:
    """me · oe · prep · exchange — and `closed` for an organization race that
    passed its date with no organization (F11)."""
    now = now or datetime.utcnow()
    s = m.started_at or GENESIS
    if not m.winning_tiv_id:
        return "me"
    if not m.winning_org_id:
        return "oe" if now < s + 15 * WEEK else "closed"
    return "prep" if now < s + 22 * WEEK else "exchange"


def _public_mission(db: Session, m: models.Mission, now: Optional[datetime]) -> dict:
    """What anyone can see about a mission: its leaders and its size."""
    from . import crud
    lead_tiv = None
    if m.winning_tiv_id:
        lead_tiv = m.winning_tiv_id
    else:
        try:
            ent = sorted(crud.p1_tally(db, m.id).get("entries", []),
                         key=lambda e: (-(e.get("weighted_share") or 0), -(e.get("voter_count") or 0)))
            lead_tiv = ent[0]["tiv_id"] if ent and ((ent[0].get("weighted_share") or 0) > 0
                                                    or (ent[0].get("voter_count") or 0) > 0) else None
        except Exception:
            lead_tiv = None
    lead_org = m.winning_org_id
    if not lead_org and m.winning_tiv_id:
        try:
            ent = sorted(crud.p2_tally(db, m.id).get("entries", []),
                         key=lambda e: (-(e.get("net_votes") or 0), -(e.get("ebx") or 0)))
            lead_org = ent[0]["org_id"] if ent else None
        except Exception:
            lead_org = None
    ov = mission_overview(db, m, now)
    tiv_count = len(db.scalars(select(models.Initiative.id).where(
        models.Initiative.mission_id == m.id)).all())
    posts = db.scalar(select(func.count(models.Post.id)).where(models.Post.mission_id == m.id)) or 0
    return {"lead_tiv_id": lead_tiv, "lead_org_id": lead_org,
            "members": ov["members"], "committed_ct": ov["committed_ct"],
            "final_ct": ov["guaranteed_ct"], "initiatives": tiv_count, "posts": int(posts)}


def positions(db: Session, ben_id: int, include: Optional[list[str]] = None,
              now: Optional[datetime] = None) -> list[dict]:
    """One row per mission: every mission this benefactor is in, plus any
    asked for by id (the profile's three arch sections).

    A row is the benefactor's COIN for that mission. Its `coin` says what it is:
      ballot      money or a vote standing in an open initiative election
      membership  backed the initiative election, so a member of the mission:
                  may commit tokens in its organization election (ruling 20,
                  2026-10-09 — everyone else has the one nominal vote there),
                  and holds whatever stake carried in
      ebx         a stake that minted into EBX (prep / exchange)
      none        an included mission this benefactor has not touched
    """
    from . import crud
    now = now or datetime.utcnow()
    week = current_week(now)
    p1_rows = db.scalars(select(models.VoteP1).where(models.VoteP1.ben_id == ben_id)).all()
    p2_rows = {v.mission_id: v for v in db.scalars(select(models.VoteP2).where(
        models.VoteP2.ben_id == ben_id)).all()}
    by_m: dict[str, list[models.VoteP1]] = {}
    for r in p1_rows:
        by_m.setdefault(r.mission_id, []).append(r)
    ids = list(dict.fromkeys(list(by_m) + list(p2_rows) + list(include or [])))
    # my posts, by mission
    my_posts = db.scalars(select(models.Post).where(models.Post.ben_author_id == ben_id)).all()
    link = {}
    pids = [p.id for p in my_posts]
    if pids:
        for pm in db.scalars(select(models.PostMission).where(models.PostMission.post_id.in_(pids))).all():
            link.setdefault(pm.post_id, set()).add(pm.mission_id)
    out = []
    for mid in ids:
        m = db.get(models.Mission, mid)
        if m is None:
            continue
        phase = mission_phase(m, now)
        rows = by_m.get(mid, [])
        shares = {r.tiv_id: float(r.share or 0) for r in rows if (r.share or 0) > 0}
        me_ct = sum(p1_stake_ct_of(r) for r in rows)
        top = max(shares.items(), key=lambda kv: kv[1])[0] if shares else None
        v = p2_rows.get(mid)
        derived = crud.p2_ebx_by_ben(db, mid).get(ben_id, 0.0) if m.winning_tiv_id else 0.0
        oe_ct = stake_ct_of(v, derived) if (v is not None or derived) else 0
        minted = minted_ct_of(v)
        final = final_ct_of(db, v, now) if v is not None else 0
        voted_me = bool(shares) or me_ct > 0
        if phase == "me":
            coin = "ballot" if voted_me else "none"
            stake = me_ct
        else:
            stake = oe_ct if (oe_ct or v is not None) else 0
            if minted > 0 or (phase in ("prep", "exchange") and stake > 0):
                coin = "ebx"
            elif voted_me or stake > 0 or (v is not None and v.org_id):
                coin = "membership"
            else:
                coin = "none"
        posts = [p for p in my_posts if p.mission_id == mid or mid in link.get(p.id, ())]
        out.append({
            "mission_id": mid, "cause_id": m.cause_id, "cycle_num": m.cycle_num,
            "phase": phase, "dates": _mission_dates(m),
            "winning_tiv_id": m.winning_tiv_id, "winning_org_id": m.winning_org_id,
            "coin": coin,
            "stake_ct": int(stake),
            "me": {"ct": int(me_ct), "shares": shares, "top_tiv_id": top,
                   "backed_winner": bool(m.winning_tiv_id and top == m.winning_tiv_id)},
            "oe": {"ct": int(oe_ct), "org_id": (v.org_id if v is not None else None),
                   "minted_ct": int(minted), "final_ct": int(final),
                   "movable": bool(v is not None and is_movable(v, week)),
                   "marked_tiv_id": (getattr(v, "marked_tiv_id", None) if v is not None else None),
                   # ruling 20 (2026-10-09): the nominal vote is everyone's;
                   # tokens are for initiative-election voters.
                   "can_vote": bool(phase == "oe"),
                   "can_commit": bool(phase == "oe" and (voted_me or stake > 0))},
            "posts": {"count": len([p for p in posts if not p.parent_id]),
                      "comments": len([p for p in posts if p.parent_id]),
                      "helpful": sum(int(p.helpful_count or 0) for p in posts),
                      "latest": [{"id": p.id, "title": p.title or (p.body or "")[:80],
                                  "type": p.type, "category": p.category,
                                  "created_at": p.created_at.isoformat() if p.created_at else None}
                                 for p in sorted(posts, key=lambda p: p.created_at or GENESIS,
                                                 reverse=True)[:3]]},
            "public": _public_mission(db, m, now),
        })
    order = {"oe": 0, "me": 1, "prep": 2, "exchange": 3, "closed": 4}
    out.sort(key=lambda r: (r["coin"] == "none", order.get(r["phase"], 9), r["dates"]["me"]))
    return out


def stats(db: Session, ben_id: int, now: Optional[datetime] = None) -> dict:
    """The profile's numbers: how long, how often, how much."""
    now = now or datetime.utcnow()
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    p1 = db.scalars(select(models.VoteP1).where(models.VoteP1.ben_id == ben_id)).all()
    me_missions = {r.mission_id for r in p1 if (r.share or 0) > 0 or p1_stake_ct_of(r) > 0}
    p2 = db.scalars(select(models.VoteP2).where(models.VoteP2.ben_id == ben_id)).all()
    oe_missions = {v.mission_id for v in p2 if v.org_id or int(v.stake_ct or 0) > 0}
    cause_votes = db.scalar(select(func.count(models.CauseVote.id)).where(
        models.CauseVote.ben_id == ben_id)) or 0
    posts = db.scalars(select(models.Post).where(models.Post.ben_author_id == ben_id)).all()
    post_votes = db.scalar(select(func.count(models.PostVote.id)).where(
        models.PostVote.ben_id == ben_id)) or 0
    vote_changes = db.scalar(select(func.count(models.Transaction.id)).where(
        models.Transaction.ben_id == ben_id, models.Transaction.type == "vote")) or 0
    won = 0
    for mid in me_missions:
        m = db.get(models.Mission, mid)
        if m is None or not m.winning_tiv_id:
            continue
        mine = [r for r in p1 if r.mission_id == mid and (r.share or 0) > 0]
        if mine and max(mine, key=lambda r: r.share).tiv_id == m.winning_tiv_id:
            won += 1
    suggested = db.scalar(select(func.count(models.Initiative.id)).where(
        models.Initiative.proposer_ben_id == ben_id)) or 0
    created = ben.created_at or now
    w = read_wallet(db, ben_id, now)
    return {
        "joined": created.isoformat(),
        "account_age_days": max(0, (now - created).days),
        "initiative_elections": len(me_missions),
        "organization_elections": len(oe_missions),
        "cause_votes": int(cause_votes),
        "vote_changes": int(vote_changes),
        "winners_backed": won,
        "posts": len([p for p in posts if not p.parent_id]),
        "comments": len([p for p in posts if p.parent_id]),
        "post_votes": int(post_votes),
        "helpful_received": sum(int(p.helpful_count or 0) for p in posts),
        "initiatives_suggested": int(suggested),
        "final_ct": w.final_ct,
        "test_deposits_ct": test_deposits_ct(db, ben_id),
    }
