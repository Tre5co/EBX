"""Mission candidacy endpoints (an org's bid to run a mission) — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(tags=["candidacies"])


@router.post("/candidacies", response_model=schemas.MissionCandidacyRead, status_code=201)
def create_candidacy(
    data: schemas.MissionCandidacyCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    try:
        return crud.create_candidacy(db, data, submitted_by_id=user.id)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 409, detail=msg)


@router.get("/candidacies", response_model=list[schemas.MissionCandidacyRead])
def list_candidacies(
    mission_id: Optional[str] = None,
    org_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.list_candidacies(db, mission_id=mission_id, org_id=org_id, status_filter=status)


@router.post("/candidacies/{candidacy_id}/approve", response_model=schemas.MissionCandidacyRead)
def approve_candidacy(
    candidacy_id: int,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only: clear an org to build the mission page."""
    try:
        return crud.approve_candidacy(db, candidacy_id, staff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/candidacies/{candidacy_id}/reject", response_model=schemas.MissionCandidacyRead)
def reject_candidacy(
    candidacy_id: int,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only: reject an org's bid — all EBX committed to it is refunded
    to its backers and their vote rows are freed."""
    try:
        return crud.reject_candidacy(db, candidacy_id, staff)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 409, detail=msg)
