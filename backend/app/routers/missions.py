"""Mission (spine) endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..scheduler import maybe_run
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("", response_model=list[schemas.MissionRead])
def list_missions(
    cause_id: Optional[str] = None,
    phase: Optional[str] = None,
    db: Session = Depends(get_db),
):
    # Lazily advance any due phases (throttled) so the UI shifts on vote days.
    maybe_run(db)
    return crud.list_missions(db, cause_id=cause_id, phase=phase)


@router.get("/{mission_id}", response_model=schemas.MissionRead)
def get_mission(mission_id: str, db: Session = Depends(get_db)):
    m = crud.get_mission(db, mission_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return m


@router.post("", response_model=schemas.MissionRead, status_code=201)
def create_mission(
    data: schemas.MissionCreate,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    if crud.get_mission(db, data.id):
        raise HTTPException(status_code=409, detail="Mission already exists")
    return crud.create_mission(db, data)


@router.get("/{mission_id}/pool", response_model=schemas.PoolRead)
def get_pool(mission_id: str, db: Session = Depends(get_db)):
    if crud.get_mission(db, mission_id) is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return crud.recompute_pool(db, mission_id)


@router.get("/{mission_id}/budget-range", response_model=dict)
def get_budget_range(mission_id: str, db: Session = Depends(get_db)):
    """Budgeting-phase helper: org's concrete min and (uncapped) max budget."""
    if crud.get_mission(db, mission_id) is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return crud.mission_budget_range(db, mission_id)
