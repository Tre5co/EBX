"""Organization endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[schemas.OrganizationRead])
def list_orgs(cause_id: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.list_orgs(db, cause_id=cause_id)


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


@router.post("", response_model=schemas.OrganizationRead, status_code=201)
def create_org(
    data: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    if crud.get_org(db, data.id):
        raise HTTPException(status_code=409, detail="Organization already exists")
    return crud.create_org(db, data)
