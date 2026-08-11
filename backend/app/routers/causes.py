"""Cause endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/causes", tags=["causes"])


@router.get("", response_model=list[schemas.CauseRead])
def list_causes(status: Optional[str] = None, db: Session = Depends(get_db)):
    """The seven active causes by default; `?status=suggested` for the ones
    campaigning to replace one, `?status=all` for everything (§5)."""
    if status == "all":
        return crud.list_causes_all(db)
    if status:
        return crud.list_causes_all(db, status=status)
    return crud.list_causes_all(db, status="active")


# ── the cause election (§5, 2026-08-06) ────────────────────────────────────
@router.post("/suggest", response_model=schemas.CauseRead, status_code=201)
def suggest_cause(
    data: schemas.CauseSuggest,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Propose a cause: a name and the colour picked off the wheel."""
    try:
        return crud.suggest_cause(db, user.id, data.name, data.color,
                                  description=data.description, emoji=data.emoji)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/slate", response_model=dict)
def cause_slate(active_index: Optional[int] = None, db: Session = Depends(get_db)):
    """§2 (2026-08-08): every upcoming window in one call — who holds it, who is
    challenging it, and whether it is open to a vote this week. The vote settled
    this week decides the window SEVEN weeks out (one full rotation: the active
    cause's own next appearance), so that slot is always open; every other
    window is read-only unless a challenger has already been elected into it.
    `active_index` is the cause index running this week."""
    try:
        return crud.cause_slate(db, active_index)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ballot/{slot}", response_model=dict)
def cause_ballot(slot: int, incumbent_id: Optional[str] = None, db: Session = Depends(get_db)):
    """The seven columns for one contested window — column 1 aggregates the six
    weeks before the contest opened, columns 2..7 are a week each."""
    try:
        return crud.cause_ballot_state(db, slot, incumbent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/vote", response_model=dict)
def cast_cause_vote(
    data: schemas.CauseVoteCast,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """One vote per benefactor per window per week; voting again replaces it."""
    try:
        row = crud.cast_cause_vote(db, user.id, data.slot, data.cause_id)
        return {"slot": row.slot, "cause_id": row.cause_id, "week_start": row.week_start.isoformat()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/vote/mine", response_model=dict)
def my_cause_votes(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.my_cause_votes(db, user.id)


@router.get("/{cause_id}", response_model=schemas.CauseRead)
def get_cause(cause_id: str, db: Session = Depends(get_db)):
    cause = crud.get_cause(db, cause_id)
    if cause is None:
        raise HTTPException(status_code=404, detail="Cause not found")
    return cause


@router.post("", response_model=schemas.CauseRead, status_code=201)
def create_cause(
    data: schemas.CauseCreate,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    if crud.get_cause(db, data.id):
        raise HTTPException(status_code=409, detail="Cause already exists")
    return crud.create_cause(db, data)
