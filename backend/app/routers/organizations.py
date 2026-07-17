"""Organization endpoints (v2).

Build Phase 2 (org experience): public self-registration/nomination (no staff
gate), duplicate pre-check, membership create/list, and the public org profile
bundle rendered by the org panel on mission.html and the org admin on admin.html
(orgs have no standalone page since the 2026-07-10 restructure).
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..config import get_settings
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/organizations", tags=["organizations"])
settings = get_settings()


@router.get("", response_model=list[schemas.OrganizationRead])
def list_orgs(cause_id: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.list_orgs(db, cause_id=cause_id)


# NOTE: static paths must be declared before the /{org_id} matcher.
@router.get("/match", response_model=list[schemas.OrgMatch])
def match_orgs(name: str, db: Session = Depends(get_db)):
    """Fuzzy duplicate pre-check for the application form ('did you mean an
    existing org?'). Threshold is config-driven."""
    return crud.fuzzy_org_matches(db, name, threshold=settings.org_dup_threshold)


@router.post("/register", response_model=schemas.OrgRegisterResult, status_code=201)
def register_org(
    data: schemas.OrganizationRegister,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Public org application — self-registration (kind='registration', the
    authed benefactor becomes founding member + executive) or nomination
    (kind='nomination', no membership). Returns fuzzy matches instead of
    creating when near-duplicates exist (override with force=true)."""
    try:
        return crud.register_org(db, data, user, dup_threshold=settings.org_dup_threshold)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 400, detail=msg)


@router.get("/{org_id}", response_model=schemas.OrganizationRead)
def get_org(org_id: str, db: Session = Depends(get_db)):
    org = crud.get_org(db, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/{org_id}/causes", response_model=list[str])
def get_org_causes(org_id: str, db: Session = Depends(get_db)):
    """Derived causes for an org (through its mission candidacies)."""
    if crud.get_org(db, org_id) is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.org_cause_ids(db, org_id)


@router.get("/{org_id}/profile", response_model=dict)
def get_org_profile(org_id: str, db: Session = Depends(get_db)):
    """The public organization page bundle: org + derived causes + candidacies
    + org-authored posts + members. One round-trip for the org panel/admin views."""
    org = crud.get_org(db, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    cands = crud.list_candidacies(db, org_id=org_id)
    posts = crud.list_org_posts(db, org_id)
    return {
        "org": schemas.OrganizationRead.model_validate(org).model_dump(mode="json"),
        "cause_ids": crud.org_cause_ids(db, org_id),
        "candidacies": [
            schemas.MissionCandidacyRead.model_validate(c).model_dump(mode="json") for c in cands
        ],
        "posts": [schemas.PostRead.model_validate(p).model_dump(mode="json") for p in posts],
        "members": [
            {**m, "joined_at": m["joined_at"].isoformat() if m["joined_at"] else None}
            for m in crud.list_org_members(db, org_id)
        ],
    }


@router.get("/{org_id}/memberships", response_model=list[schemas.MembershipDetail])
def org_memberships(org_id: str, db: Session = Depends(get_db)):
    """Public members list (handles + org-roles)."""
    if crud.get_org(db, org_id) is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.list_org_members(db, org_id)


@router.post("/{org_id}/memberships", response_model=schemas.MembershipRead, status_code=201)
def create_membership(
    org_id: str,
    data: schemas.MembershipCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Invite/add a member or set a member's org-role. Self-service 'community'
    joins are open; any other change needs a rep/executive membership (or staff)."""
    try:
        return crud.create_membership(db, org_id, data, user)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 400, detail=msg)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("", response_model=schemas.OrganizationRead, status_code=201)
def create_org(
    data: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff path (seed/admin tooling) — the public path is POST /organizations/register."""
    if crud.get_org(db, data.id):
        raise HTTPException(status_code=409, detail="Organization already exists")
    return crud.create_org(db, data)
