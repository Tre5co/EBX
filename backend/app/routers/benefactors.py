"""Benefactor self-service endpoints (watchlist, wallet, memberships) — v2."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/benefactors/me", tags=["benefactors"])


@router.get("/watchlist", response_model=list[str])
def get_watchlist(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.list_watched(db, user)


@router.put("/watchlist/{tiv_id}", response_model=list[str])
def add_watch(
    tiv_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.add_watch(db, user, tiv_id)


@router.delete("/watchlist/{tiv_id}", response_model=list[str])
def remove_watch(
    tiv_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.remove_watch(db, user, tiv_id)


@router.get("/credit-coins", response_model=list[schemas.CreditCoinRead])
def my_credit_coins(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.list_credit_coins(db, user.id)


@router.get("/memberships", response_model=list[schemas.MembershipRead])
def my_memberships(
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    return crud.list_memberships(db, ben_id=user.id)
