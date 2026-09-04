"""The wallet — reading and moving a benefactor's money.

`token_model.py` owns the arithmetic; this module is the only place that lets it
touch the database. Split deliberately: every rule in the model is testable
without a session, and every write here is a thin, auditable application of one.

Rewritten 2026-08-27c for the finalized model (`docs/ME_OE_FINALIZATION.md`).
Seven operations, and the shape of the list is the model:

    read_wallet     what the four segments hold right now
    ensure_grant    ten tokens appear, against THIS WEEK'S CAUSE
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
    granted ct      appears in its cause's election week. Cannot be transferred
                    or withdrawn — there is no moment at which it exists and is
                    free — and if unspent it waits for that cause's next window.
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

from sqlalchemy import select
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
    """EBX still held: minted, less every tranche already donated."""
    if v is None:
        return 0
    return max(0, minted_ct_of(v) - max(0, int(getattr(v, "donated_ct", 0) or 0)))


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
    for v in db.scalars(select(models.VoteP2).where(models.VoteP2.ben_id == ben_id)).all():
        derived = crud.p2_ebx_by_ben(db, v.mission_id).get(ben_id, 0.0)
        committed += unminted_ct_of(v, week, derived)
        minted += held_ebx_ct_of(v)
        donated += max(0, int(getattr(v, "donated_ct", 0) or 0))

    # The ME side counts too. An initiative-election allocation is a token in an
    # election — the same `committed` state as an OE allocation that has not
    # hardened — and leaving it out is what made the allocations panel report
    # one balance twice before 2026-08-27c.
    for r in db.scalars(select(models.VoteP1).where(models.VoteP1.ben_id == ben_id)).all():
        m = db.get(models.Mission, r.mission_id)
        if m is not None and m.winning_tiv_id:
            continue          # the initiative election closed; the OE row holds it now
        committed += p1_stake_ct_of(r)

    free = int(ben.free_ct or 0)
    return tm.Wallet(cash_ct=int(ben.cash_ct or 0), free_ct=free,
                     purchased_ct=min(int(ben.purchased_ct or 0), free),
                     committed_ct=committed, minted_ct=minted, donated_ct=donated,
                     grant_cause_id=getattr(ben, "grant_cause_id", None))


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
        tiv = db.get(models.Initiative, m.winning_tiv_id) if m.winning_tiv_id else None
        v = _vote_row(db, ben_id, m.id) if ben_id else None
        derived = crud.p2_ebx_by_ben(db, m.id).get(ben_id, 0.0) if ben_id else 0.0
        my_ct = stake_ct_of(v, derived) if (v or derived) else 0
        unminted = unminted_ct_of(v, week, derived) if v else 0
        backed_winner = False
        if ben_id and m.winning_tiv_id:
            backed_winner = db.scalars(
                select(models.VoteP1).where(models.VoteP1.ben_id == ben_id,
                                            models.VoteP1.tiv_id == m.winning_tiv_id)
            ).first() is not None
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
            # "Correct voters get twice as much influence in the OE" — the ME
            # result, cashed in here. Weight, not money: the skim is a clean 10%
            # for everyone since 2026-08-27c.
            "backed_winner": backed_winner,
            "my_influence": tm.influence_mult("oe", me_correct=backed_winner),
            "my_weight": tm.weight_tokens(
                my_ct, tm.influence_mult("oe", me_correct=backed_winner)),
            "born_week": (v.born_week if v else None),
            "origin_mission_id": ((v.origin_mission_id if v and v.origin_mission_id
                                   else m.id)),
            "is_active_race": (m.id == active_id),
            "max_stake_ct": my_ct + headroom,
        })
    return out


# ---------------------------------------------------------------------------
# Write — the grant, the roll, and the four moves
# ---------------------------------------------------------------------------
def ensure_grant(db: Session, ben_id: int, now: Optional[datetime] = None) -> dict:
    """Ten tokens appear, against this week's cause. At most once per week.

    "10 tokens appear in your account each week." Ten is a FLOOR, not a ration:
    the top-up is `max(0, 10 - free)`, so holding six brings four and holding
    twenty brings none and takes none away. Idempotent by `last_grant_week`,
    because this runs on a read path and a grant that pays twice on a refresh is
    money invented by a page load.

    The grant carries the week's CAUSE rather than a deadline. There is no
    deadline to carry: "tokens aren't granted until election week when it's too
    late to transfer or withdraw", so a granted token has no free window to
    expire out of. What it has is a place — this week's races, and if it goes
    unspent, that cause's next window.
    """
    ben = db.get(models.BenefactorAccount, ben_id)
    if ben is None:
        raise ValueError("Benefactor not found")
    week = current_week(now)
    cause_id = active_cause_id(now)
    if ben.last_grant_week is not None and int(ben.last_grant_week) >= week:
        return {"granted_ct": 0, "week": week, "free_ct": int(ben.free_ct or 0),
                "grant_cause_id": getattr(ben, "grant_cause_id", None)}
    amount = tm.grant_ct(int(ben.free_ct or 0))
    ben.free_ct = int(ben.free_ct or 0) + amount
    ben.last_grant_week = week
    ben.grant_cause_id = cause_id
    db.commit()
    return {"granted_ct": amount, "week": week, "free_ct": int(ben.free_ct),
            "grant_cause_id": cause_id}


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


def _spendable_ct(ben: models.BenefactorAccount, is_active_race: bool) -> int:
    """What may enter THIS race out of the unallocated bar.

    A GRANTED token may only be spent in this week's elections — the initiative
    election of the week's cause, or the one organization election closing
    soonest. A PURCHASED token carries no such fence and may enter any race.
    Same tokens, different permissions, which is why the unallocated bar draws
    two colours.
    """
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    return free if is_active_race else purchased


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
    minted = minted_ct_of(v)
    unminted = max(0, have - minted)
    if unminted > 0 and not is_movable(v, week):
        raise ValueError("Those tokens hardened into EBX at the week change — "
                         "EBX stays with its mission")
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

    # Granted first, where granted ct is allowed; purchased only, everywhere
    # else. Getting this backwards would spend a grant through a door it is not
    # allowed through, and the benefactor would lose the wider permission by
    # accident.
    free = int(ben.free_ct or 0)
    purchased = min(int(ben.purchased_ct or 0), free)
    granted = max(0, free - purchased)
    if delta > 0:
        from_granted = min(delta, granted) if is_active else 0
        ben.free_ct = free - delta
        ben.purchased_ct = max(0, purchased - (delta - from_granted))
    elif delta < 0:
        # Money coming back out of a draft returns through the SAME door it went
        # through: granted-first up, granted-first down. On a non-active race
        # only purchased ct could have gone in, so only purchased ct comes back.
        #
        # The asymmetry is deliberate and it is named here because it has a cost.
        # A benefactor who exhausted their grant and then spent PURCHASED ct on
        # this week's race gets it back as grant-permission ct — narrower than
        # what they put in. Erring the other way would let a grant be laundered
        # into go-anywhere ct by dialling a race up and back down, which is the
        # failure that matters. Fixing it properly needs per-row provenance of
        # which slice funded which ct; it is on the backlog beside the purchase
        # endpoint, and until that endpoint exists the case cannot arise.
        back = -delta
        ben.free_ct = free + back
        if not is_active:
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
