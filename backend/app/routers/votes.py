"""Phase-1 (tiv) + phase-2 (org) voting endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..config import get_settings
from ..database import get_db
from ..models import BenefactorAccount, VoteP2

router = APIRouter(tags=["votes"])
settings = get_settings()


# ----- phase 1 (initiative election) -----
@router.put("/missions/{mission_id}/p1/votes", response_model=dict)
def put_p1_shares(
    mission_id: str,
    body: schemas.VoteP1Shares,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Replace the ben's soft phase-1 shares for this mission, then return the
    running weighted tally."""
    try:
        crud.replace_p1_shares(db, user.id, mission_id, body.shares, ebx_total=body.ebx)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return crud.p1_tally(db, mission_id, settings.size_factor)


@router.post("/missions/{mission_id}/p1/commit", response_model=dict)
def commit_p1(
    mission_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return {"mission_id": mission_id, "locked": crud.commit_p1(db, user.id, mission_id)}


@router.get("/missions/{mission_id}/p1/tally", response_model=dict)
def p1_tally(mission_id: str, db: Session = Depends(get_db)):
    return crud.p1_tally(db, mission_id, settings.size_factor)


@router.post("/missions/{mission_id}/p1/withdraw", response_model=dict)
def withdraw_p1(
    mission_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Phase-2 withdrawal: pull back this ben's phase-1 commitment minus the send."""
    try:
        return crud.withdraw_p1(db, user.id, mission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/missions/{mission_id}/p1/mine", response_model=list[schemas.VoteP1Read])
def my_p1(
    mission_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """The signed-in ben's own phase-1 shares for this mission."""
    return crud.get_p1_votes(db, user.id, mission_id)


# ----- phase 2 (org election) -----
@router.put("/missions/{mission_id}/p2/vote", response_model=schemas.VoteP2Read)
def cast_p2(
    mission_id: str,
    body: schemas.VoteP2Create,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Vote for a single org (votes>1 = bought extra; valence='harmful' = block)."""
    try:
        return crud.cast_p2(db, user.id, mission_id, body.org_id,
                            votes=body.votes, ebx_spent=body.ebx_spent, valence=body.valence,
                            unapproved_ebx_cap=settings.unapproved_org_ebx_cap)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/missions/{mission_id}/p2/commit", response_model=dict)
def commit_p2(
    mission_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return {"mission_id": mission_id, "locked": crud.commit_p2(db, user.id, mission_id)}


@router.get("/missions/{mission_id}/p2/tally", response_model=dict)
def p2_tally(mission_id: str, db: Session = Depends(get_db)):
    return crud.p2_tally(db, mission_id)


@router.get("/missions/{mission_id}/p2/mine", response_model=Optional[schemas.VoteP2Read])
def my_p2(
    mission_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """The signed-in ben's own phase-2 org vote for this mission (or null)."""
    return db.scalar(
        select(VoteP2).where(VoteP2.ben_id == user.id, VoteP2.mission_id == mission_id)
    )
