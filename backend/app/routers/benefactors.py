"""Benefactor-scoped routes: /benefactors/me and watchlist (build-seq 4)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ..models import BenefactorAccount


router = APIRouter(prefix="/benefactors/me", tags=["benefactors"])


@router.get("/watch", response_model=list[str])
def list_my_watchlist(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.list_watched(db, user)


@router.post("/watch/{init_id}", response_model=list[str])
def add_to_watchlist(
    init_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.add_watch(db, user, init_id)


@router.delete("/watch/{init_id}", response_model=list[str])
def remove_from_watchlist(
    init_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.remove_watch(db, user, init_id)
