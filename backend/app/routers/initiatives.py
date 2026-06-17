"""Initiative (tiv) endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/initiatives", tags=["initiatives"])


@router.get("", response_model=list[schemas.InitiativeRead])
def list_tivs(
    cause_id: Optional[str] = None,
    mission_id: Optional[str] = None,
    status: Optional[str] = None,
    approved_only: bool = False,
    db: Session = Depends(get_db),
):
    return crud.list_tivs(db, cause_id=cause_id, mission_id=mission_id,
                          status_filter=status, approved_only=approved_only)


@router.get("/{tiv_id}", response_model=schemas.InitiativeRead)
def get_tiv(tiv_id: str, db: Session = Depends(get_db)):
    tiv = crud.get_tiv(db, tiv_id)
    if tiv is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return tiv


@router.post("", response_model=schemas.InitiativeRead, status_code=201)
def create_tiv(
    data: schemas.InitiativeCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    if crud.get_tiv(db, data.id):
        raise HTTPException(status_code=409, detail="Initiative already exists")
    return crud.create_tiv(db, data)


@router.post("/{tiv_id}/approve", response_model=schemas.InitiativeRead)
def approve_tiv(
    tiv_id: str,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only: clear a tiv to enter elections."""
    try:
        return crud.approve_tiv(db, tiv_id, staff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{tiv_id}/commit", response_model=schemas.VoteP1Read, status_code=201)
def commit_ebx(
    tiv_id: str,
    data: schemas.VoteP1Create,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Commit EBX to this tiv in its mission's phase-1 election."""
    tiv = crud.get_tiv(db, tiv_id)
    if tiv is None or tiv.mission_id is None:
        raise HTTPException(status_code=404, detail="Initiative is not in an active mission")
    try:
        return crud.commit_p1_ebx(db, user.id, tiv.mission_id, tiv_id, data.ebx_committed)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 409, detail=msg)
