"""Auth (signup + login) endpoints for benefactor accounts."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import (
    create_access_token,
    get_current_benefactor,
    verify_password,
)
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.BenefactorRead, status_code=201)
def signup(data: schemas.BenefactorCreate, db: Session = Depends(get_db)):
    if crud.get_benefactor_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if crud.get_benefactor_by_handle(db, data.handle):
        raise HTTPException(status_code=409, detail="Handle already taken")
    return crud.create_benefactor(db, data)


@router.post("/login", response_model=schemas.Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 password flow. `username` may be email or handle."""
    user = crud.get_benefactor_by_email(db, form.username) or crud.get_benefactor_by_handle(
        db, form.username
    )
    if user is None or not verify_password(form.password, user.pass_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=schemas.BenefactorRead)
def me(user: BenefactorAccount = Depends(get_current_benefactor)):
    return user
