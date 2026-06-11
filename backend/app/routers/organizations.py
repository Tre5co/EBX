"""Organization endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[schemas.OrganizationRead])
def read_organizations(cause_id: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.list_organizations(db, cause_id=cause_id)


# NOTE: declared before /{org_id} so the literal path wins the route match.
@router.get("/registrations", response_model=list[schemas.OrgRegistrationRead])
def read_org_registrations(
    initiative_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.list_org_registrations(db, initiative_id=initiative_id, status=status)


@router.post("/registrations", response_model=schemas.OrgRegistrationRead, status_code=201)
def submit_org_registration(
    data: schemas.OrgRegistrationCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Nominate an org (benefactor) or register one as a member (pass 34, build-seq 2)."""
    if data.kind == "registration" and not (data.member_name and data.member_position):
        raise HTTPException(
            status_code=400,
            detail="Member name and position are required when registering as an org member",
        )
    return crud.create_org_registration(db, data, benefactor_id=user.id)


@router.get("/{org_id}", response_model=schemas.OrganizationRead)
def read_organization(org_id: str, db: Session = Depends(get_db)):
    org = crud.get_organization(db, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.post("", response_model=schemas.OrganizationRead, status_code=201)
def create_organization(data: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    if crud.get_organization(db, data.id):
        raise HTTPException(status_code=409, detail="Organization already exists")
    return crud.create_organization(db, data)


@router.get("/{org_id}/reviews", response_model=list[schemas.ReviewRead])
def read_org_reviews(org_id: str, db: Session = Depends(get_db)):
    return crud.list_reviews(db, org_id)


@router.post("/{org_id}/reviews", response_model=schemas.ReviewRead, status_code=201)
def post_review(
    org_id: str,
    data: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    if data.organization_id != org_id:
        raise HTTPException(status_code=400, detail="Org id mismatch")
    if crud.get_organization(db, org_id) is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.create_review(db, data, benefactor_id=user.id)
