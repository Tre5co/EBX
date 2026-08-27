"""Wallet + organization-election stakes.

One job each, and since 2026-08-20b one DIRECTION each:

    GET  /wallet          the segments, the grant, the eight rows, the rules
    GET  /wallet/rows     the same rows for a signed-out visitor
    POST /wallet/commit   unallocated → a race, optionally naming the phl. ONE WAY
    POST /wallet/convert  a race → another race, spending one of three conversions
    PUT  /wallet/org      name the phl a stake already in this race stands behind

`PUT /wallet/stake` is GONE. It set a POSITION — pass a smaller number and the
row gave ct back to the unallocated balance — and that is the exact move the
model now forbids: "users can no longer move tokens from an OE to unallocated."
A one-way action deserves a verb that cannot be read as a slider, so it is a
POST that says how much to ADD.
"""
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import token_model as tm, wallet as w
from ..database import get_db
from ..models import BenefactorAccount
from ._deps import get_current_benefactor

router = APIRouter(prefix="/wallet", tags=["wallet"])


class CommitBody(BaseModel):
    mission_id: str
    # How much to ADD, in CENTITOKENS — never a position. `ge=0` is the schema
    # half of one-way commitment; the other half is the 400 in `commit_stake`.
    # The client never divides by 100: `ct_per_token` rides along in every
    # wallet payload so there is one place the unit is defined.
    add_ct: int = Field(ge=0)
    # Naming the philanthropy in the same call is the point of the dialog: an
    # amount and a choice are one gesture, and one write.
    org_id: Optional[str] = None


class ConvertBody(BaseModel):
    from_mission_id: str
    to_mission_id: str
    ct: int = Field(gt=0)
    # REQUIRED: a conversion IS a vote at the destination. Moving ct without
    # saying who it now backs is the thing the model forbids.
    org_id: str


class OrgBody(BaseModel):
    mission_id: str
    org_id: Optional[str] = None      # null returns the stake to unassigned


@router.get("", response_model=dict)
def get_wallet(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """The four segments, the week's grant, and the OE table's rows.

    The grant is applied HERE, on read: opening the page is what tops you up.
    `ensure_grant` is idempotent per cycle week, so a refresh cannot pay one
    twice — which is the only reason it is safe on a GET.
    """
    granted = w.ensure_grant(db, user.id)
    wallet = w.read_wallet(db, user.id)
    commit_by = w.week_date(wallet.commit_by_week)
    return {
        "wallet": wallet.as_dict(),
        "granted_this_week_ct": granted["granted_ct"],
        "week": granted["week"],
        # The date on this week's grant. Sent as a date, not just a week index,
        # so the strip above the OE table and the ME table cannot disagree about
        # which day the week ends on.
        "commit_by_week": wallet.commit_by_week,
        "commit_by": (commit_by.isoformat() if commit_by else None),
        "rows": w.oe_rows(db, user.id),
        "rules": {
            "weekly_grant_ct": tm.WEEKLY_GRANT_CT,
            "ct_per_token": tm.CT_PER_TOKEN,
            # One skim, after the organization election. `me_skim` is reported
            # as 0 rather than dropped: a client that still prints a
            # phase-1 cut should print zero, not fall back to a stale default.
            "me_skim": tm.ME_SKIM,
            "oe_send_win": tm.OE_SEND_WIN,
            "oe_send_lose": tm.OE_SEND_LOSE,
            "weight_block_ct": tm.WEIGHT_BLOCK_CT,
            "weight_r": tm.WEIGHT_R,
            # What being right is worth, per arena.
            "me_correct_oe_mult": tm.ME_CORRECT_OE_MULT,
            "oe_correct_budget_mult": tm.OE_CORRECT_BUDGET_MULT,
            "research_mult_each": tm.RESEARCH_MULT_EACH,
            "research_mult_both": tm.influence_mult("research", True, True),
            "max_conversions": tm.MAX_CONVERSIONS,
            "grant_commit_by_weeks": tm.GRANT_COMMIT_BY_WEEKS,
            "token_life_weeks": tm.TOKEN_LIFE_WEEKS,
            "oe_table_rows": w.OE_TABLE_ROWS,
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
    """Commit more of the unallocated balance to one race, and optionally name
    the philanthropy in the same transaction. One way: this can only add."""
    try:
        return w.commit_stake(db, user.id, body.mission_id, body.add_ct, body.org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/convert", response_model=dict)
def post_convert(
    body: ConvertBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Move committed ct straight from one organization election into another,
    voting for a philanthropy there. Spends one of three conversions."""
    try:
        return w.convert_stake(db, user.id, body.from_mission_id, body.to_mission_id,
                               body.ct, body.org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/org", response_model=dict)
def put_org(
    body: OrgBody,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Name the philanthropy a stake stands behind, or clear it."""
    try:
        return w.set_org(db, user.id, body.mission_id, body.org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
