"""Posts (feed) endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[schemas.PostRead])
def read_posts(
    cause_id: Optional[str] = None,
    initiative_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.list_posts(db, cause_id=cause_id, initiative_id=initiative_id, limit=limit)


@router.post("", response_model=schemas.PostRead, status_code=201)
def create_post(data: schemas.PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db, data)
