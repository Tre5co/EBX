"""Wallet + organization-election stakes.

One job each, and since 2026-08-27c the direction is the WEEK rather than the
verb:

    GET  /wallet          the four segments, the grant, the eight rows, the rules
    GET  /wallet/rows     the same rows for a signed-out visitor
    POST /wallet/commit   set this race's allocation — a position, up or down
    POST /wallet/move     race -> race, carrying the philanthropy vote with it
    POST /wallet/withdraw purchased, unvoted tokens back to cash
    PUT  /wallet/org      name the phl this race's ct stand behind

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


class OrgBody(BaseModel):
    mission_id: str
    org_id: Optional[str] = None      # null returns the stake to unassigned


@router.get("", response_model=dict)
def get_wallet(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """The four segments, the week's grant, and the OE table's rows.

    Two things are applied HERE, on read, because opening the page is when a
    benefactor's week catches up with them: the grant (idempotent per week, so a
    refresh cannot pay one twice) and the ROLL (`harden_due`, idempotent by
    construction — a row with nothing unminted is skipped). Neither invents
    anything; both are the calendar, applied late.
    """
    granted = w.ensure_grant(db, user.id)
    w.harden_due(db, user.id)
    wallet = w.read_wallet(db, user.id)
    week = granted["week"]
    return {
        "wallet": wallet.as_dict(),
        "granted_this_week_ct": granted["granted_ct"],
        "week": week,
        # The cause this week's grant was issued against, and can be spent in.
        # It replaces the commit-by date, which had nothing left to enforce.
        "grant_cause_id": granted.get("grant_cause_id"),
        "hardens_week": tm.hardens_at_week(week),
        "rows": w.oe_rows(db, user.id),
        "rules": {
            "weekly_grant_ct": tm.WEEKLY_GRANT_CT,
            "ct_per_token": tm.CT_PER_TOKEN,
            "max_split_tivs": tm.MAX_SPLIT_TIVS,
            # One skim, and it is the same for everyone. `me_skim` is reported
            # as 0 rather than dropped: a client that still prints a phase-1 cut
            # should print zero, not fall back to a stale default.
            "me_skim": tm.ME_SKIM,
            "oe_skim": tm.OE_SKIM,
            "weight_block_ct": tm.WEIGHT_BLOCK_CT,
            "weight_r": tm.WEIGHT_R,
            # What being right is worth, per arena. None of it is money.
            "me_correct_oe_mult": tm.ME_CORRECT_OE_MULT,
            "oe_correct_budget_mult": tm.OE_CORRECT_BUDGET_MULT,
            "research_mult_each": tm.RESEARCH_MULT_EACH,
            "research_mult_both": tm.influence_mult("research", True, True),
            "budget_set_weeks": tm.BUDGET_SET_WEEKS,
            "oe_table_rows": w.OE_TABLE_ROWS,
            "oe_lifetime_races": tm.OE_LIFETIME_RACES,
        },
    }


@router.get("/rows", response_model=list)
def get_rows(db: Session = Depends(get_db)):
    """The OE table for a signed-out visitor: the races, no commitments."""
    return w.oe_rows(db, None)


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
