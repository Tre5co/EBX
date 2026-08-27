"""The wallet — reading and moving a benefactor's money.

`token_model.py` owns the arithmetic; this module is the only place that lets it
touch the database. Split deliberately: every rule in the model is testable
without a session, and every write here is a thin, auditable application of one.

Four operations and nothing else:

    read_wallet     what the segments hold right now
    ensure_grant    top the unallocated balance up to 10, once per week
    commit_stake    unallocated → a race. ONE WAY (2026-08-20b)
    convert_stake   a race → another race, directly, spending one of three
    set_org         name the philanthropy a stake in this race stands behind

`commit_stake` is money and `set_org` is a vote. Keeping them apart is what
makes an unassigned stake representable — which it has to be, because the
initiative election creates them automatically — while `convert_stake`
deliberately does both at once, because moving ct between races without saying
who it now backs is precisely what the model forbids.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, token_model as tm
from .bootstrap import GENESIS, WEEK

# ---------------------------------------------------------------------------


def current_week(now: Optional[datetime] = None) -> int:
    """Cycle week index — the same anchor the frontend's `EBX.Cycle` uses
    (`cycleStart 2026-04-28T12:00`). Grants and lot clocks are counted in these,
    never in wall-clock days, so a page loaded at 23:59 and one loaded at 00:01
    cannot disagree about which week it is."""
    now = now or datetime.utcnow()
    return max(0, int((now - GENESIS) / WEEK))


# "The OE table rows should not be expandable, and there should be 8 of them."
# Eight is the steady state — a mission enters phase 2 every week and leaves
# eight weeks later — but a database with a stalled or a hand-finalized race can
# hold more or fewer, and the table is a fixed shape either way. So the query is
# capped, and it is capped on the DEADLINE: the eight races that decide soonest
# are the eight a benefactor can still act on.
OE_TABLE_ROWS = 8


def _vote_day(m: models.Mission) -> datetime:
    """The day this mission's philanthropy election is decided: T + 15 weeks
    from the mission opening (initiative at +7, philanthropy 8 weeks later).
    Asked of the MISSION, never of the cause week — the cause-week formula
    answers for whichever sibling race finalizes soonest and prints the wrong
    date beside the other one."""
    return (m.started_at or GENESIS) + 15 * WEEK


def week_date(week: Optional[int]) -> Optional[datetime]:
    """A cycle week index as a wall-clock date — the day that week begins.

    Weeks are the unit everything money-shaped is counted in, but a deadline has
    to be printable ("commit by Sep 1"), and doing that conversion in the
    browser is how two surfaces end up a day apart.
    """
    if week is None:
        return None
    return GENESIS + int(week) * WEEK


def _open_p2_missions(db: Session) -> list[models.Mission]:
    """Missions whose organization election is open: an initiative has won and
    no philanthropy has yet. These are the rows of the OE table — the eight
    closing soonest, in the order they close."""
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
    """This row's stake in ct.

    `stake_ct` is authoritative once it has been written. Rows that predate the
    column fall back to the DERIVED phase-1 figure they were carrying before —
    the surviving `VoteP1.ebx_committed` for this mission — so an old race still
    renders its real numbers instead of a sudden column of zeroes.
    """
    if v is not None and int(v.stake_ct or 0) > 0:
        return int(v.stake_ct)
    return tm.ct_from_tokens(max(0.0, float(derived_ebx or 0.0)))


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------
def settles_as_won(v: models.VoteP2, m: models.Mission) -> Optional[bool]:
    """How a stake settles when its race closes: True (its philanthropy won),
    False (it lost), or None — meaning it does not settle here at all.

    Two rules the model states in words, applied in one place:

    * **An unassigned stake follows the winner of its OWN race.** It funded the
      mission and it carries no vote weight, but it is not a losing vote — there
      was no vote. Reading it as a loss (which the code did until 2026-08-20,
      against `docs/token_model.md` §8) charged silence a 10% penalty.
    * **An unassigned stake in a race that is NOT its origin goes home.** "In
      order for the user to convert their token to a different OE, they need to
      vote on a phl for it. If they don't, the token defaults to the OE from the
      tiv it was created within." So it settles nowhere here; `None` sends it
      back to the origin race, which is still open, or to the free balance if
      that race has closed too.
    """
    if not m.winning_org_id:
        return None
    if v.org_id is not None:
        return v.org_id == m.winning_org_id
    origin = v.origin_mission_id or m.id
    if origin != m.id:
        return None                    # never converted → it was never really here
    return True                        # silence follows the winner of its own race


def read_wallet(db: Session, ben_id: int, now: Optional[datetime] = None) -> tm.Wallet:
    """The wallet's segments, derived from the rows that exist.

    NOTE on `claimed`: `finalize_p2` books nothing per-benefactor, so claimed is
    DERIVED here by applying the model to closed races rather than read from a
    ledger. It is the correct number; it is just recomputed rather than
    remembered. (Since 2026-08-20 the ME half IS booked — `finalize_p1` writes
    the stake rows and the first coin element — so only the OE half is derived.)
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")

    from . import crud   # local import: crud imports this module's siblings

    staked = 0
    claimed = 0
    for v in db.scalars(select(models.VoteP2).where(models.VoteP2.ben_id == ben_id)).all():
        m = db.get(models.Mission, v.mission_id)
        derived = crud.p2_ebx_by_ben(db, v.mission_id).get(ben_id, 0.0)
        ct = stake_ct_of(v, derived)
        won = settles_as_won(v, m) if m is not None else None
        if won is None:
            staked += ct               # open race, or gone home to its origin
        else:
            claimed += tm.settle_oe(ct, won).claimed_ct

    minted = 0
    for c in db.scalars(select(models.CreditCoin).where(models.CreditCoin.owner_id == ben_id)).all():
        minted += tm.ct_from_tokens(float(getattr(c, "amount_ebx", 0) or 0))

    free = int(ben.free_ct or 0)
    return tm.Wallet(cash_ct=int(ben.cash_ct or 0), free_ct=free,
                     purchased_ct=min(int(ben.purchased_ct or 0), free),
                     staked_ct=staked, claimed_ct=claimed, minted_ct=minted,
                     # The date on this week's grant, rolled forward if it was
                     # missed. Reported even when it has been fully committed —
                     # the strip says "committed by <date>" either way, and a
                     # deadline that vanishes when you meet it teaches nothing.
                     commit_by_week=tm.roll_commit_by(
                         ben.grant_commit_by_week, current_week(now)))


def oe_rows(db: Session, ben_id: Optional[int]) -> list[dict]:
    """The OE table: one row per mission with an open philanthropy election.

    Always the eight of them at steady state — a mission enters phase 2 every
    week and leaves eight weeks later — but N until there are eight, and never a
    row with no race behind it. Rows are labelled by INITIATIVE, not by cause:
    the rotation is seven weeks and the phase-2 window is eight, so two missions
    of the same cause are open at once and a cause-labelled table would show the
    same name twice.
    """
    from . import crud

    ben = db.get(models.BenefactorAccount, ben_id) if ben_id else None
    free = int(ben.free_ct or 0) if ben else 0
    # Unallocated is granted + purchased and nothing else. The two differ only in
    # permission: granted ct may enter this week's two doors, purchased ct may
    # enter any race. Which is why a non-active row's ceiling is the purchased
    # part alone.
    purchased = min(int(ben.purchased_ct or 0), free) if ben else 0

    out: list[dict] = []
    open_missions = _open_p2_missions(db)
    # "This week's active-cause OE" is the race that finalizes SOONEST — the one
    # the cause week belongs to. It is the only row this week's grant may enter
    # ("2 options, not 9"); the other seven accept purchased ct only, and the
    # table sets that row apart visibly so the difference is not a surprise
    # discovered at the moment of committing.
    active_id = open_missions[0].id if open_missions else None
    for m in open_missions:
        tiv = db.get(models.Initiative, m.winning_tiv_id) if m.winning_tiv_id else None
        v = _vote_row(db, ben_id, m.id) if ben_id else None
        derived = crud.p2_ebx_by_ben(db, m.id).get(ben_id, 0.0) if ben_id else 0.0
        my_ct = stake_ct_of(v, derived) if (v or derived) else 0
        backed_winner = False
        if ben_id and m.winning_tiv_id:
            backed_winner = db.scalars(
                select(models.VoteP1).where(models.VoteP1.ben_id == ben_id,
                                            models.VoteP1.tiv_id == m.winning_tiv_id)
            ).first() is not None
        # Where this row's ct was born, and how much of its conversion budget is
        # spent. Ct committed from the unallocated bar is born in the race it
        # lands in; ct that arrived by conversion carries the count with it.
        origin = (v.origin_mission_id if (v and v.origin_mission_id) else m.id)
        used = int(v.conversions or 0) if v else 0
        left = tm.conversions_left(used)
        is_origin = (origin == m.id)
        # What may still be COMMITTED into this row out of the unallocated bar.
        # Committing is one-way now, so this is a ceiling on a decision, not on a
        # slider position.
        headroom = free if m.id == active_id else purchased
        out.append({
            "mission_id": m.id,
            "cause_id": m.cause_id,
            "cycle_num": m.cycle_num,
            "tiv_id": m.winning_tiv_id,
            "tiv_title": (tiv.title if tiv else m.winning_tiv_id),
            "tiv_emoji": (tiv.emoji if tiv else None),
            "vote_date": _vote_day(m).isoformat(),
            "my_stake_ct": my_ct,
            "my_org_id": (v.org_id if v else None),
            # "Correct voters get twice as much influence in the OE" — the ME
            # result, cashed in here. It is weight, not money: the skim is the
            # same 10% for everyone now.
            "backed_winner": backed_winner,
            "my_influence": tm.influence_mult("oe", me_correct=backed_winner),
            "my_weight": tm.weight_tokens(
                my_ct, tm.influence_mult("oe", me_correct=backed_winner)),
            "born_week": (v.born_week if v else None),
            "origin_mission_id": origin,
            "is_origin_race": is_origin,
            "conversions_used": used,
            "conversions_left": left,
            # Naming what the rule costs, so the row can say it in words rather
            # than the slider simply refusing to move.
            "needs_conversion": (not is_origin),
            "is_active_race": (m.id == active_id),
            # What this row's slider may be dragged to: what is already on it,
            # plus the ct allowed to enter it.
            "max_stake_ct": my_ct + headroom,
        })
    return out


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Write — and there are only three ways money moves
# ---------------------------------------------------------------------------
# 2026-08-20b. `set_stake` used to be a POSITION: pass a number, and the row
# moved up or down, giving ct back to the free balance on the way down. That is
# gone. "Users can no longer move tokens from an OE to unallocated." So:
#
#     ensure_grant     the balance is topped up to 10 (the only way free grows)
#     commit_stake     unallocated → a race. One way. Add-only.
#     convert_stake    a race → another race, directly. Costs one of three,
#                      and carries the destination philanthropy with it.
#     set_org          name the philanthropy inside the race the ct is native to
#
# There is deliberately no fourth. A benefactor who wants out of a race converts
# into one they prefer; a benefactor who wants their money back waits for the
# race to settle, where a loss returns 90% as CASH — never as tokens.
def ensure_grant(db: Session, ben_id: int, now: Optional[datetime] = None) -> dict:
    """Top the unallocated balance up to 10 tokens, at most once per cycle week.

    "Your uncommitted balance is topped up to 10 every week." Idempotent by
    `last_grant_week`, because this runs on a read path (opening the page) and a
    grant that pays twice on a refresh is money invented by a page load.

    An uncommitted grant is NOT demoted at the top-up. It keeps its two doors and
    takes next week's date — the whole content of "if they are not committed …
    by that date, the date changes 1 week forward".
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    week = current_week(now)
    if ben.last_grant_week is not None and int(ben.last_grant_week) >= week:
        # Already paid this week. The DATE still has to be right — an account
        # granted weeks ago and not opened since is holding a deadline in the
        # past, and a deadline in the past is not a deadline.
        rolled = tm.roll_commit_by(ben.grant_commit_by_week, week)
        if rolled != ben.grant_commit_by_week:
            ben.grant_commit_by_week = rolled
            db.commit()
        return {"granted_ct": 0, "week": week, "free_ct": int(ben.free_ct or 0),
                "commit_by_week": ben.grant_commit_by_week}
    amount = tm.grant_ct(int(ben.free_ct or 0))
    ben.free_ct = int(ben.free_ct or 0) + amount
    ben.last_grant_week = week
    ben.grant_commit_by_week = tm.commit_by_week(week)
    db.commit()
    return {"granted_ct": amount, "week": week, "free_ct": int(ben.free_ct),
            "commit_by_week": ben.grant_commit_by_week}


def _spendable_ct(ben: models.BenefactorAccount, is_active_race: bool) -> int:
    """What may enter THIS race out of the unallocated bar.

    Two doors for granted ct — this week's initiative slate, or the ONE
    active-cause organization election ("2 options, not 9"). Purchased ct has no
    such restriction: "users can commit purchased tokens anywhere."
    """
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    return free if is_active_race else purchased


def commit_stake(db: Session, ben_id: int, mission_id: str, add_ct: int,
                 org_id: Optional[str] = None,
                 now: Optional[datetime] = None) -> dict:
    """Commit `add_ct` more of the unallocated balance to one race. One way.

    Optionally names the philanthropy in the same call, because that is what the
    dialog asks for in one gesture — an amount and a choice — and splitting it
    into two writes is how a benefactor ends up with money in a race they never
    meant to vote in.

    The amount is CLAMPED to what the bar can pay rather than rejected, and
    granted ct is spent BEFORE purchased ct, so a benefactor never burns the
    wider permission by accident.
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
    if int(add_ct or 0) < 0:
        raise ValueError("Committed tokens cannot return to your unallocated "
                         "balance — convert them to another organization "
                         "election instead")

    from . import crud

    open_missions = _open_p2_missions(db)
    is_active = bool(open_missions) and open_missions[0].id == mission_id
    add = min(max(0, int(add_ct or 0)), max(0, _spendable_ct(ben, is_active)))

    v = _vote_row(db, ben_id, mission_id)
    derived = crud.p2_ebx_by_ben(db, mission_id).get(ben_id, 0.0)
    have = stake_ct_of(v, derived) if (v or derived) else 0
    week = current_week(now)
    if v is None:
        v = models.VoteP2(ben_id=ben_id, mission_id=mission_id, org_id=None,
                          votes=1, ebx_spent=0, valence="helpful", committed=False,
                          origin_mission_id=mission_id, born_week=week, conversions=0)
        db.add(v)
    if v.born_week is None:
        v.born_week = week
    if v.origin_mission_id is None:
        v.origin_mission_id = mission_id
    v.stake_ct = have + add

    # Granted first — but only where granted ct is ALLOWED. On the active-cause
    # race the grant is spent before the purchase, so a benefactor never burns
    # the wider permission by accident; on any other row granted ct cannot go at
    # all, so the whole amount comes out of the purchased slice. Getting this
    # backwards would spend the grant through a door it is not allowed through.
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    granted = max(0, free - purchased)
    from_granted = min(add, granted) if is_active else 0
    ben.free_ct = free - add
    ben.purchased_ct = max(0, purchased - (add - from_granted))

    if org_id is not None:
        if db.get(models.Organization, org_id) is None:
            raise ValueError("Organization not found")
        v.org_id = org_id
        _record(v, tm.coin_element_oe(week=week, mission_id=mission_id, org_id=org_id,
                                      amount_ct=int(v.stake_ct or 0), converted=False))
    db.commit()
    return {"mission_id": mission_id, "stake_ct": int(v.stake_ct or 0),
            "committed_ct": add, "free_ct": int(ben.free_ct),
            "purchased_ct": int(ben.purchased_ct),
            "grant_held_ct": max(0, int(ben.free_ct) - int(ben.purchased_ct)),
            "org_id": v.org_id, "is_active_race": is_active,
            "conversions_used": int(v.conversions or 0),
            "conversions_left": tm.conversions_left(int(v.conversions or 0))}


def convert_stake(db: Session, ben_id: int, from_mission_id: str, to_mission_id: str,
                  ct: int, org_id: str, now: Optional[datetime] = None) -> dict:
    """Move committed ct from one organization election straight into another.

    The only way ct leaves a race before it settles, and a single transaction on
    purpose: "every token has a record of where it has traveled, so moving
    tokens requires a specific transaction." It never touches the unallocated
    balance, so there is no moment at which a moved token looks like a fresh one.

    A philanthropy at the destination is REQUIRED — "in order for the user to
    convert their token to a different OE, they need to vote on a phl for it" —
    and the move spends one of three conversions. The count travels with the ct
    (`merge_conversion` takes the higher of the two rows, plus this move), so
    splitting a stake across races cannot buy extra moves.
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
        raise ValueError("A decided philanthropy election cannot be converted "
                         "into or out of")
    if not dst_m.winning_tiv_id:
        raise ValueError("That mission has no elected initiative yet")
    if db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")

    from . import crud

    src = _vote_row(db, ben_id, from_mission_id)
    derived = crud.p2_ebx_by_ben(db, from_mission_id).get(ben_id, 0.0)
    have = stake_ct_of(src, derived) if (src or derived) else 0
    move = min(max(0, int(ct or 0)), have)
    if move <= 0:
        raise ValueError("There is nothing committed in that election to convert")
    if src is None:
        raise ValueError("There is nothing committed in that election to convert")
    if not tm.can_convert(int(src.conversions or 0)):
        raise ValueError(
            f"These tokens have used all {tm.MAX_CONVERSIONS} of their conversions — "
            "they can only stay where they are")

    week = current_week(now)
    dst = _vote_row(db, ben_id, to_mission_id)
    dst_derived = crud.p2_ebx_by_ben(db, to_mission_id).get(ben_id, 0.0)
    dst_have = stake_ct_of(dst, dst_derived) if (dst or dst_derived) else 0
    if dst is None:
        dst = models.VoteP2(ben_id=ben_id, mission_id=to_mission_id, org_id=None,
                            votes=1, ebx_spent=0, valence="helpful", committed=False,
                            origin_mission_id=to_mission_id, born_week=week,
                            conversions=0)
        db.add(dst)
    if dst.born_week is None:
        dst.born_week = week

    src.stake_ct = have - move
    dst.stake_ct = dst_have + move
    dst.conversions = tm.merge_conversion(dst_have, int(dst.conversions or 0),
                                          int(src.conversions or 0))
    # The destination is home from now on: a converted stake defaults to the
    # winner HERE if its benefactor never votes again, not to the race it left.
    dst.origin_mission_id = to_mission_id
    dst.org_id = org_id
    _record(dst, tm.coin_element_oe(week=week, mission_id=to_mission_id, org_id=org_id,
                                    amount_ct=move, converted=True))
    if src.stake_ct <= 0:
        # An emptied row keeps its history but stops carrying a vote: a stake of
        # zero standing behind a philanthropy would still be counted a voter.
        src.org_id = None
    db.commit()
    return {"from_mission_id": from_mission_id, "to_mission_id": to_mission_id,
            "moved_ct": move, "from_stake_ct": int(src.stake_ct or 0),
            "to_stake_ct": int(dst.stake_ct or 0), "org_id": org_id,
            "conversions_used": int(dst.conversions or 0),
            "conversions_left": tm.conversions_left(int(dst.conversions or 0))}


def set_org(db: Session, ben_id: int, mission_id: str, org_id: Optional[str],
            now: Optional[datetime] = None) -> dict:
    """Name (or clear) the philanthropy a stake already in this race stands behind.

    A vote, not a payment. `org_id=None` returns the row to the unassigned state
    the initiative election creates: it still funds the mission, it carries no
    weight, and at close it follows the winner of the race it was born in.

    Changing which RACE the ct is in is not this call — that is `convert_stake`,
    which is one transaction carrying the money and the vote together.
    """
    mission = db.get(models.Mission, mission_id)
    if mission is None:
        raise ValueError("Mission not found")
    if mission.winning_org_id:
        raise ValueError("That philanthropy election is already decided")
    if org_id is not None and db.get(models.Organization, org_id) is None:
        raise ValueError("Organization not found")

    week = current_week(now)
    v = _vote_row(db, ben_id, mission_id)
    if v is None:
        v = models.VoteP2(ben_id=ben_id, mission_id=mission_id, votes=1, ebx_spent=0,
                          valence="helpful", committed=False, stake_ct=0,
                          origin_mission_id=mission_id, born_week=week, conversions=0)
        db.add(v)
    origin = v.origin_mission_id or mission_id
    if org_id is not None and origin != mission_id:
        # Only reachable for rows written before conversions existed. Say what to
        # do instead of silently spending one of three.
        raise ValueError("Those tokens came from another election — use a "
                         "conversion to move them, which spends one of "
                         f"{tm.MAX_CONVERSIONS}")
    v.org_id = org_id
    if org_id is not None:
        _record(v, tm.coin_element_oe(week=week, mission_id=mission_id, org_id=org_id,
                                      amount_ct=int(v.stake_ct or 0), converted=False))
    db.commit()
    return {"mission_id": mission_id, "org_id": org_id,
            "stake_ct": int(v.stake_ct or 0),
            "conversions_used": int(v.conversions or 0),
            "conversions_left": tm.conversions_left(int(v.conversions or 0))}


def _record(v: models.VoteP2, event: tm.ProvenanceEvent) -> None:
    """Append a registered vote to the row's history.

    Only committed votes land here — and since committing is one-way, every
    entry describes something a benefactor actually did rather than a slider
    position they passed through on the way to deciding.
    """
    chain = list(v.provenance or [])
    chain.append(event.as_dict())
    v.provenance = chain
