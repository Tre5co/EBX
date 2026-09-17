"""Auth (signup + login) for benefactor accounts — v2."""
import hmac
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import create_access_token, get_current_benefactor, verify_password
from ..config import get_settings
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.BenefactorRead, status_code=201)
def signup(data: schemas.BenefactorCreate, db: Session = Depends(get_db),
           x_ebx_bot_key: Optional[str] = Header(default=None)):
    if crud.get_ben_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if crud.get_ben_by_handle(db, data.handle):
        raise HTTPException(status_code=409, detail="Handle already taken")
    ben = crud.create_ben(db, data)
    # The bot signature (build-seq §2): only a request carrying the server's
    # EBX_BOT_KEY can create a test account. A wrong key is ignored, not refused,
    # so a probe learns nothing.
    key = get_settings().ebx_bot_key
    if key and x_ebx_bot_key and hmac.compare_digest(key, x_ebx_bot_key):
        ben.is_test = True
        db.commit()
        db.refresh(ben)
    return ben


@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password flow. `username` may be email or handle."""
    user = crud.get_ben_by_email(db, form.username) or crud.get_ben_by_handle(db, form.username)
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
