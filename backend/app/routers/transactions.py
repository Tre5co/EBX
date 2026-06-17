"""Transaction ledger endpoints (staff-only) — v2."""
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[schemas.TransactionRead])
def list_transactions(
    mission_id: Optional[str] = None,
    ben_id: Optional[int] = None,
    type: Optional[str] = None,
    bucket: Optional[str] = None,
    limit: int = 200,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    return crud.list_transactions(db, mission_id=mission_id, ben_id=ben_id,
                                  type_filter=type, bucket=bucket, limit=limit)
