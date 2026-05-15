"""Initiative endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/initiatives", tags=["initiatives"])


@router.get("", response_model=list[schemas.InitiativeRead])
def read_initiatives(
    cause_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.list_initiatives(db, cause_id=cause_id, status_filter=status)


@router.get("/{initiative_id}", response_model=schemas.InitiativeRead)
def read_initiative(initiative_id: str, db: Session = Depends(get_db)):
    init = crud.get_initiative(db, initiative_id)
    if init is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return init


@router.post("", response_model=schemas.InitiativeRead, status_code=201)
def create_initiative(data: schemas.InitiativeCreate, db: Session = Depends(get_db)):
    if crud.get_initiative(db, data.id):
        raise HTTPException(status_code=409, detail="Initiative already exists")
    return crud.create_initiative(db, data)


@router.post(
    "/{initiative_id}/commit",
    response_model=schemas.ContributionRead,
    status_code=201,
)
def commit_ebx(
    initiative_id: str,
    data: schemas.ContributionCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    if data.initiative_id != initiative_id:
        raise HTTPException(status_code=400, detail="Initiative id mismatch")
    try:
        return crud.commit_ebx(db, initiative_id, user.id, data.amount_ebx)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{initiative_id}/vote",
    response_model=schemas.VoteRead,
    status_code=201,
)
def cast_vote(
    initiative_id: str,
    data: schemas.VoteCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Cast (or update) a benefactor's org-election vote for an initiative."""
    init = crud.get_initiative(db, initiative_id)
    if init is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    try:
        return crud.cast_vote(db, initiative_id, user.id, data.org_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{initiative_id}/vote/tally",
    response_model=dict,
)
def vote_tally(initiative_id: str, db: Session = Depends(get_db)):
    """Return org_id -> vote count for an initiative (public)."""
    return crud.get_vote_tally(db, initiative_id)

