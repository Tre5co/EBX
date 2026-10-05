"""Organization accounts and the organization experience (P2b, 2026-10-02).

  /org/application                 GET   the form (org_config) — public
  /org/apply                       POST  the claim: org + pending admin login + application
  /org/login                       POST  OAuth2 form → an organization token ("org:<id>")
  /org/me                          GET   the account and its organization
  /org/home                        GET   Home tab — campaigns, what changed, Earthbux updates
  /org/initiatives                 GET   Initiatives tab — mission steps 2–3
  /org/profile                     PUT   Profile tab — the outward-facing fields
  /org/posts                       POST  update · plan · answer · suggestion
  /org/candidacies                 POST  Run for this
  /org/campaigns/{mission_id}      PUT   a campaign tab — the promise
  /org/members                     GET/POST  logins (POST: administrators only, D29)
  /org/applications                GET   staff — the review queue
  /org/applications/{id}/approve   POST  staff
  /org/applications/{id}/reject    POST  staff
  /organizations/{id}/public       GET   the public profile (claimed or UNCLAIMED)
  /organizations/{id}/campaigns/{mission_id}  GET  the campaign page

An organization token is refused by every benefactor route (auth.py), so an
organization cannot vote, commit, withdraw or hold a wallet.
"""
import hmac
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import crud_org, events, models, org_config
from ..auth import create_org_token, get_current_org_account
from ..config import get_settings
from ..database import get_db
from ..models import BenefactorAccount, OrgAccount
from ._deps import get_current_staff

router = APIRouter(tags=["organization accounts"])


def _refuse(e: Exception):
    if isinstance(e, PermissionError):
        raise HTTPException(status_code=403, detail=str(e))
    if isinstance(e, LookupError):
        raise HTTPException(status_code=401, detail=str(e))
    msg = str(e)
    raise HTTPException(status_code=404 if "not found" in msg.lower() else 400, detail=msg)


class ApplyIn(BaseModel):
    org_id: Optional[str] = None           # claiming an existing page; None = a new organization
    answers: dict
    email: str = Field(min_length=3, max_length=200)
    handle: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8, max_length=72)


class ReviewIn(BaseModel):
    note: Optional[str] = None


class ProfileIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website_link: Optional[str] = None
    logo_url: Optional[str] = None
    founded_year: Optional[int] = None


class OrgPostIn(BaseModel):
    kind: str
    body: str
    title: Optional[str] = None
    mission_id: Optional[str] = None
    tiv_id: Optional[str] = None
    parent_id: Optional[str] = None


class RunIn(BaseModel):
    mission_id: str
    mission_statement: str


class PromiseIn(BaseModel):
    mission_statement: str


class MemberIn(BaseModel):
    email: str
    handle: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8, max_length=72)
    display_name: Optional[str] = None
    position: Optional[str] = None
    role: str = "member"


# ── public ──────────────────────────────────────────────────────────────────
@router.get("/org/application")
def application_form():
    return org_config.public_form()


@router.post("/org/apply", status_code=201)
def apply(data: ApplyIn, db: Session = Depends(get_db),
          x_ebx_bot_key: Optional[str] = Header(default=None)):
    key = get_settings().ebx_bot_key
    is_test = bool(key and x_ebx_bot_key and hmac.compare_digest(key, x_ebx_bot_key))
    try:
        return crud_org.apply(db, org_id=data.org_id, answers=data.answers, email=data.email,
                              handle=data.handle, password=data.password, is_test=is_test)
    except (ValueError, PermissionError) as e:
        db.rollback()
        _refuse(e)


@router.post("/org/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        acct = crud_org.authenticate(db, form.username, form.password)
    except crud_org.LoginWaiting as e:
        # 2026-10-04: say WHY, with the application — the sign-in page shows
        # "under review" (and, to a signed-in staff member, Approve it now).
        raise HTTPException(status_code=403, detail={
            "message": str(e), "status": e.status, "application_id": e.application_id,
            "org_name": e.org_name, "note": e.note})
    except (LookupError, PermissionError) as e:
        _refuse(e)
    return {"access_token": create_org_token(acct.id), "token_type": "bearer"}


@router.get("/organizations/{org_id}/public")
def public_profile(org_id: str, db: Session = Depends(get_db)):
    try:
        return crud_org.public_profile(db, org_id)
    except ValueError as e:
        _refuse(e)


@router.get("/organizations/{org_id}/campaigns/{mission_id}")
def campaign_page(org_id: str, mission_id: str, db: Session = Depends(get_db)):
    try:
        return crud_org.campaign_page(db, org_id, mission_id)
    except ValueError as e:
        _refuse(e)


# ── the organization's own site ─────────────────────────────────────────────
@router.get("/org/me")
def me(acct: OrgAccount = Depends(get_current_org_account), db: Session = Depends(get_db)):
    from ..models import Organization
    return {"account": crud_org.account_dict(acct),
            "org": crud_org.org_dict(db, db.get(Organization, acct.org_id))}


@router.get("/org/home")
def home(acct: OrgAccount = Depends(get_current_org_account), db: Session = Depends(get_db)):
    return crud_org.home(db, acct)


@router.get("/org/initiatives")
def initiatives(acct: OrgAccount = Depends(get_current_org_account), db: Session = Depends(get_db)):
    return crud_org.initiatives(db, acct)


@router.put("/org/profile")
def update_profile(data: ProfileIn, acct: OrgAccount = Depends(get_current_org_account),
                   db: Session = Depends(get_db)):
    try:
        return crud_org.update_profile(db, acct, data.model_dump(exclude_unset=True))
    except ValueError as e:
        _refuse(e)


@router.post("/org/posts", status_code=201)
def create_post(data: OrgPostIn, acct: OrgAccount = Depends(get_current_org_account),
                db: Session = Depends(get_db)):
    try:
        out = crud_org.create_org_post(db, acct, **data.model_dump())
    except (ValueError, PermissionError) as e:
        db.rollback()
        _refuse(e)
    p = db.get(models.Post, out["id"])
    if p is not None:       # P4: an answer notifies the asker; Suggest us, the initiative's people
        events.safe(events.on_post_created, db, p)
    return out


@router.post("/org/candidacies", status_code=201)
def run_for(data: RunIn, acct: OrgAccount = Depends(get_current_org_account),
            db: Session = Depends(get_db)):
    try:
        out = crud_org.run_for(db, acct, data.mission_id, data.mission_statement)
    except ValueError as e:
        db.rollback()
        _refuse(e)
    events.safe(events.on_org_nominated, db, org_id=acct.org_id, mission_id=data.mission_id,
                how="running", actor_org_id=acct.org_id)
    return out


@router.put("/org/campaigns/{mission_id}")
def set_promise(mission_id: str, data: PromiseIn, acct: OrgAccount = Depends(get_current_org_account),
                db: Session = Depends(get_db)):
    try:
        return crud_org.set_promise(db, acct, mission_id, data.mission_statement)
    except ValueError as e:
        _refuse(e)


@router.get("/org/members")
def members(acct: OrgAccount = Depends(get_current_org_account), db: Session = Depends(get_db)):
    return crud_org.list_members(db, acct.org_id)


@router.post("/org/members", status_code=201)
def create_member(data: MemberIn, acct: OrgAccount = Depends(get_current_org_account),
                  db: Session = Depends(get_db)):
    try:
        return crud_org.create_member(db, acct, **data.model_dump())
    except (ValueError, PermissionError) as e:
        db.rollback()
        _refuse(e)


# ── staff ───────────────────────────────────────────────────────────────────
@router.get("/org/applications")
def list_applications(status: Optional[str] = "pending", db: Session = Depends(get_db),
                      staff: BenefactorAccount = Depends(get_current_staff)):
    return crud_org.list_applications(db, status=status or None)


@router.post("/org/applications/{app_id}/approve")
def approve(app_id: int, data: ReviewIn = ReviewIn(), db: Session = Depends(get_db),
            staff: BenefactorAccount = Depends(get_current_staff)):
    try:
        return crud_org.review_application(db, app_id, staff, True, data.note)
    except ValueError as e:
        _refuse(e)


@router.post("/org/applications/{app_id}/reject")
def reject(app_id: int, data: ReviewIn = ReviewIn(), db: Session = Depends(get_db),
           staff: BenefactorAccount = Depends(get_current_staff)):
    try:
        return crud_org.review_application(db, app_id, staff, False, data.note)
    except ValueError as e:
        _refuse(e)
