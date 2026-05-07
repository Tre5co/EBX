"""Mission endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("", response_model=list[schemas.MissionRead])
def read_missions(status: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.list_missions(db, status_filter=status)


@router.get("/{mission_id}", response_model=schemas.MissionRead)
def read_mission(mission_id: str, db: Session = Depends(get_db)):
    mission = crud.get_mission(db, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.post("", response_model=schemas.MissionRead, status_code=201)
def create_mission(data: schemas.MissionCreate, db: Session = Depends(get_db)):
    if crud.get_mission(db, data.id):
        raise HTTPException(status_code=409, detail="Mission already exists")
    return crud.create_mission(db, data)
