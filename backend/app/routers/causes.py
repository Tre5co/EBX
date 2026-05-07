"""Causes endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/causes", tags=["causes"])


@router.get("", response_model=list[schemas.CauseRead])
def read_causes(db: Session = Depends(get_db)):
    return crud.list_causes(db)


@router.get("/{cause_id}", response_model=schemas.CauseRead)
def read_cause(cause_id: str, db: Session = Depends(get_db)):
    cause = crud.get_cause(db, cause_id)
    if cause is None:
        raise HTTPException(status_code=404, detail="Cause not found")
    return cause


@router.post("", response_model=schemas.CauseRead, status_code=201)
def create_cause(data: schemas.CauseCreate, db: Session = Depends(get_db)):
    if crud.get_cause(db, data.id):
        raise HTTPException(status_code=409, detail="Cause already exists")
    return crud.create_cause(db, data)
