"""Admin / employee endpoints: query console + staff actions — v2."""
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/admin", tags=["admin"])


# ----- query console (the "navigate the database" tool) -----
@router.get("/query/entities", response_model=list[str])
def query_entities(staff: BenefactorAccount = Depends(get_current_staff)):
    """Filetree of browsable tables for admin.html."""
    return crud.query_entities()


@router.post("/query/run", response_model=list[dict])
def query_run(
    entity: str = Body(..., embed=True),
    filters: Optional[dict] = Body(default=None, embed=True),
    limit: int = Body(default=100, embed=True),
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    try:
        return crud.run_query(db, staff, entity, filters=filters, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/queries", response_model=list[schemas.QueryRead])
def list_queries(
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    return crud.list_queries(db, staff)


@router.post("/queries", response_model=schemas.QueryRead, status_code=201)
def create_query(
    data: schemas.QueryCreate,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    return crud.create_query(db, data, staff)


# ----- staff actions -----
@router.post("/accounts/{ben_id}/role", response_model=schemas.BenefactorRead)
def set_role(
    ben_id: int,
    role: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    try:
        return crud.set_role(db, ben_id, role, staff)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/missions/{mission_id}/distribute", response_model=dict)
def distribute(
    mission_id: str,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Lock the pool and write the guaranteed allocation ledger."""
    try:
        return crud.distribute_mission(db, mission_id)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 409, detail=msg)
