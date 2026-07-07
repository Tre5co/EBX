"""Post + reaction endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[schemas.PostRead])
def list_posts(
    mission_id: Optional[str] = None,
    tiv_id: Optional[str] = None,
    cause_id: Optional[str] = None,
    category: Optional[str] = None,
    parent_id: Optional[str] = None,
    roots_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return crud.list_posts(db, mission_id=mission_id, tiv_id=tiv_id,
                           cause_id=cause_id, category=category,
                           parent_id=parent_id, roots_only=roots_only, limit=limit)


@router.get("/{post_id}/comments", response_model=list[schemas.PostRead])
def list_comments(post_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Threaded replies to a post (oldest first)."""
    return crud.list_posts(db, parent_id=post_id, limit=limit)


@router.post("", response_model=schemas.PostRead, status_code=201)
def create_post(
    data: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Create a post. Editorial/headline categories require an employee account."""
    try:
        return crud.create_post(db, data, author=user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{post_id}/react", response_model=schemas.PostRead)
def react(
    post_id: str,
    data: schemas.PostVoteCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    try:
        return crud.react_to_post(db, post_id, user.id, data.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
