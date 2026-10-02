"""Password hashing + JWT issuance for Earthbucks accounts."""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import models
from .config import get_settings
from .database import get_db

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# P2b (2026-10-02) — organization accounts sign tokens with subject "org:<id>".
ORG_SUB_PREFIX = "org:"
ORG_REFUSAL = ("Organization accounts cannot vote or use benefactor features — "
               "sign in with your personal Earthbux account for that.")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------
def _pw_bytes(password: str) -> bytes:
    """Encode password to UTF-8 and hard-cap at 72 bytes (bcrypt's limit).
    bcrypt >= 4.x raises ValueError for longer inputs; we enforce the limit
    ourselves so the behaviour is consistent regardless of library version."""
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_pw_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_pw_bytes(plain), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Dependency: current user
# ---------------------------------------------------------------------------
def get_current_benefactor(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.BenefactorAccount:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sub = decode_token(token)
    if sub is None:
        raise credentials_error
    if sub.startswith(ORG_SUB_PREFIX):
        # P2b (D26): an organization account cannot vote, hold a wallet or act
        # as a benefactor. Every benefactor route depends on this function, so
        # refusing here refuses them all — the server, not just the page.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=ORG_REFUSAL)
    try:
        user_id = int(sub)
    except ValueError:
        raise credentials_error
    user = db.get(models.BenefactorAccount, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


def get_current_benefactor_optional(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[models.BenefactorAccount]:
    if not token:
        return None
    sub = decode_token(token)
    if sub is None or sub.startswith(ORG_SUB_PREFIX):
        return None
    try:
        user_id = int(sub)
    except ValueError:
        return None
    return db.get(models.BenefactorAccount, user_id)


# ---------------------------------------------------------------------------
# P2b — organization accounts (D28): their own token, their own dependency.
# ---------------------------------------------------------------------------
def create_org_token(account_id: int) -> str:
    return create_access_token(f"{ORG_SUB_PREFIX}{account_id}")


def get_current_org_account(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> "models.OrgAccount":
    err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sign in with an organization account",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sub = decode_token(token)
    if not sub or not sub.startswith(ORG_SUB_PREFIX):
        raise err
    try:
        acct_id = int(sub[len(ORG_SUB_PREFIX):])
    except ValueError:
        raise err
    acct = db.get(models.OrgAccount, acct_id)
    if acct is None or not acct.is_active:
        raise err
    return acct
