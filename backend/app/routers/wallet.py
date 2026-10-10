"""Wallet + organization-election stakes.

One job each, and since 2026-08-27c the direction is the WEEK rather than the
verb:

    GET  /wallet          the four segments, the grant, the eight rows, the rules
    GET  /wallet/rows     the same rows for a signed-out visitor
    GET  /wallet/row/{id} one race's row, even outside the eight (2026-10-01)
    POST /wallet/commit   set this race's allocation — a position, up or down
    POST /wallet/move     race -> race, carrying the philanthropy vote with it
    POST /wallet/withdraw purchased, unvoted tokens back to cash
    PUT  /wallet/org      name the phl this race's ct stand behind
    POST /wallet/add-funds dollars in, purchased tokens out (2026-10-07; TEST mode
                          until a payment processor is connected)
    GET  /wallet/positions one row per mission — the coins (2026-10-07)

`POST /wallet/convert` is GONE with the budget of three it spent. Moving ct is
free and unlimited inside its own week and impossible after the roll, so a
conversion is not a scarce thing to be counted — it is just a move, and the
endpoint says so.

`/commit` went the other way. It was an ADD, because commitment was one-way;
inside the week an allocation is a draft, so it is a position again — which is
also why the number in the dialog can be typed down as well as up.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import token_model as tm, wallet as w
from ..database import get_db
from ..models import BenefactorAccount
from ._deps import get_current_benefactor

router = APIRouter(prefix="/wallet", tags=["wallet"])


class CommitBody(BaseModel):
    mission_id: str
    # The allocation this race should HOLD, in CENTITOKENS — a position, not a
    # delta. The floor is whatever has already minted: EBX is mission-tied, and
    # a target below it lands on it rather than raising.
    target_ct: int = Field(ge=0)
    # Naming the philanthropy in the same call is the point of the dialog: an
    # amount and a choice are one gesture, and one write.
    org_id: Optional[str] = None


class MoveBody(BaseModel):
    from_mission_id: str
    to_mission_id: str
    ct: int = Field(gt=0)
    # REQUIRED: a move IS a vote at the destination. Moving ct without saying
    # who it now backs is the thing the model forbids.
    org_id: str


class WithdrawBody(BaseModel):
    ct: int = Field(gt=0)


class WithdrawStakeBody(BaseModel):
    mission_id: str
    ct: int = Field(gt=0)


class AddFundsBody(BaseModel):
    # Whole cents. $1 = 10 tokens; the smallest deposit is 10¢ (one token).
    usd_cents: int = Field(gt=0)


class OrgBody(BaseModel):
    mission_id: str
    org_id: Optional[str] = None      # null returns the stake to unassigned


@router.get("", response_model=dict)
def get_wallet(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """The four segments, the grant, and the OE table's rows.

    Two things are applied HERE, on read, because opening the page is when a
    benefactor's week catches up with them: `ensure_grant` (since 2026-10-09,
    ruling 19, it only retires a D31 weekly pile — the grant is each initiative
    election's own ten, listed in `grant`) and the ROLL (`harden_due`,
    idempotent by construction — a row with nothing unminted is skipped).
    Neither invents anything; both are the calendar, applied late.
    """
    granted = w.ensure_grant(db, user.id)
    w.harden_due(db, user.id)
    wallet = w.read_wallet(db, user.id)
    week = granted["week"]
    return {
        "wallet": wallet.as_dict(),
        "granted_this_week_ct": granted["granted_ct"],
        "week": week,
        # The week this grant was issued in — the only thing that limits where a
        # granted token may go (2026-09-16: a week id, never a cause).
        "grant_week": granted.get("grant_week"),
        "hardens_week": tm.hardens_at_week(week),
        "rows": w.oe_rows(db, user.id),
        # 2026-10-07 (the wallet build): the grant as its own entity, and how
        # funds get in. Since 2026-10-09 (ruling 19) `grant` lists every open
        # initiative election with the ten tokens it carries and what is used
        # of each; `expired_this_week_ct` is a D31 weekly pile just retired.
        "grant": w.grant_info(db, user),
        "expired_this_week_ct": granted.get("expired_ct", 0),
        "funds": {"mode": w.funds_mode(),
                  "test_deposits_ct": w.test_deposits_ct(db, user.id),
                  "max_deposit_cents": w._funds_settings().funds_max_deposit_cents,
                  "max_test_cents": w._funds_settings().funds_max_test_cents},
        "rules": {
            "weekly_grant_ct": tm.WEEKLY_GRANT_CT,
            "me_grant_ct": tm.ME_GRANT_CT,             # ruling 19: ten in every initiative election
            "ct_per_token": tm.CT_PER_TOKEN,
            "max_split_tivs": tm.MAX_SPLIT_TIVS,
            # The finality ladder (2026-09-16): 10% at the ME, another 10% at
            # the OE, 100% on budget day. Same rates for winners and losers.
            "me_skim": tm.ME_SKIM,
            "oe_skim": tm.OE_SKIM,
            "weight_block_ct": tm.WEIGHT_BLOCK_CT,
            "weight_r": tm.WEIGHT_R,
            "budget_set_weeks": tm.BUDGET_SET_WEEKS,
            "budget_day_after_me_weeks": tm.BUDGET_DAY_AFTER_ME_WEEKS,
            "org_budget_day_32nds": tm.ORG_BUDGET_DAY_32NDS,
            "oe_min_stake_ct": tm.OE_MIN_STAKE_CT,     # build-seq §3: $1 to vote in an OE
            "oe_table_rows": w.OE_TABLE_ROWS,
            "oe_lifetime_races": tm.OE_LIFETIME_RACES,
        },
    }


@router.get("/rows", response_model=list)
def get_rows(db: Session = Depends(get_db)):
    """The OE table for a signed-out visitor: the races, no commitments."""
    return w.oe_rows(db, None)


@router.get("/row/{mission_id}", response_model=dict)
def get_row(
    mission_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """One organization race's row for the signed-in benefactor, even when it
    is not among the eight `/wallet` carries (mission pass, 2026-10-01)."""
    row = w.oe_row_for(db, user.id, mission_id)
    if row is None:
        raise HTTPException(status_code=404, detail="No organization election is open for that mission")
    return row


@router.post("/commit", response_model=dict)
def post_commit(
    body: CommitBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Set one race's allocation, and optionally name the philanthropy in the
    same transaction. Inside the week this can go down as well as up."""
    try:
        return w.set_stake(db, user.id, body.mission_id, body.target_ct, body.org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/move", response_model=dict)
def post_move(
    body: MoveBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Move ct from one organization election into another, voting for a
    philanthropy there. Free, and unlimited inside the week."""
    try:
        return w.move_stake(db, user.id, body.from_mission_id, body.to_mission_id,
                            body.ct, body.org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw", response_model=dict)
def post_withdraw(
    body: WithdrawBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Take purchased, unvoted tokens back as cash. Granted tokens cannot be
    withdrawn — nothing was paid for them, and they are never both real and
    free."""
    try:
        return w.withdraw(db, user.id, body.ct)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw-stake", response_model=dict)
def post_withdraw_stake(
    body: WithdrawStakeBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Withdraw the non-final part of a stake as cash, until budget day (T+15)."""
    try:
        return w.withdraw_stake(db, user.id, body.mission_id, body.ct)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/org", response_model=dict)
def put_org(
    body: OrgBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Name the philanthropy a stake stands behind, or clear it. For a MARKED
    token this is the vote that commits it."""
    try:
        return w.set_org(db, user.id, body.mission_id, body.org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/add-funds", response_model=dict)
def post_add_funds(
    body: AddFundsBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Add funds to the wallet as PURCHASED tokens. TEST mode until a payment
    processor is connected: credited at once, logged as a test deposit."""
    try:
        return w.add_funds(db, user.id, body.usd_cents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions", response_model=list)
def get_positions(
    include: Optional[str] = None,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """One row per mission the benefactor is in — the wallet's coins — plus any
    missions named in `include` (comma-separated), for the profile's arch."""
    ids = [x.strip() for x in (include or "").split(",") if x.strip()][:12]
    return w.positions(db, user.id, ids)


@router.get("/stats", response_model=dict)
def get_stats(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """The profile's numbers: account age, elections, posts, votes."""
    return w.stats(db, user.id)
