"""Initiative (tiv) endpoints — v2."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..database import get_db
from ._deps import get_current_staff
from ..models import BenefactorAccount

router = APIRouter(prefix="/initiatives", tags=["initiatives"])


@router.get("", response_model=list[schemas.InitiativeRead])
def list_tivs(
    cause_id: Optional[str] = None,
    mission_id: Optional[str] = None,
    status: Optional[str] = None,
    approved_only: bool = False,
    db: Session = Depends(get_db),
):
    tivs = crud.list_tivs(db, cause_id=cause_id, mission_id=mission_id,
                          status_filter=status, approved_only=approved_only)
    # Attach the committed-EBX aggregate so the cards/leaderboards rank by pool.
    sums = crud.p1_ebx_by_tiv(db, [t.id for t in tivs])
    for t in tivs:
        t.ebx_committed = sums.get(t.id, 0.0)
    return tivs


@router.get("/slugs", response_model=list[dict])
def list_slugs(db: Session = Depends(get_db)):
    """D13 (2026-09-24): every address an initiative has had. `current` marks
    the one its title gives now; the others forward to it (/m/<slug>)."""
    return crud.list_slugs(db)


@router.get("/{tiv_id}", response_model=schemas.InitiativeRead)
def get_tiv(tiv_id: str, db: Session = Depends(get_db)):
    tiv = crud.get_tiv(db, tiv_id)
    if tiv is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    tiv.ebx_committed = crud.p1_ebx_by_tiv(db, [tiv.id]).get(tiv.id, 0.0)
    return tiv


@router.post("", response_model=schemas.InitiativeRead, status_code=201)
def create_tiv(
    data: schemas.InitiativeCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    if crud.get_tiv(db, data.id):
        raise HTTPException(status_code=409, detail="Initiative already exists")
    # Mission pass (2026-10-01): the proposer is whoever is signed in — it is
    # what lets them rename it until it is elected (PUT /{id}/title).
    if not data.proposer_org_id:
        data.proposer_ben_id = user.id
    return crud.create_tiv(db, data)


@router.put("/{tiv_id}/title", response_model=schemas.InitiativeRead)
def rename_tiv(
    tiv_id: str,
    data: dict,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Rename an initiative. Its old /m/<slug> keeps forwarding (D13).

    Mission pass (2026-10-01): "The proposer of an initiative should be allowed
    to change its name, as long as it hasn't already been elected." Staff may
    rename any initiative at any time; the proposer, only their own and only
    until it wins an initiative election."""
    tiv = crud.get_tiv(db, tiv_id)
    if tiv is None:
        raise HTTPException(status_code=404, detail="Initiative not found")
    if not getattr(user, "is_staff", False):
        if tiv.proposer_ben_id != user.id:
            raise HTTPException(status_code=403, detail="only the initiative's proposer can rename it")
        if crud.tiv_is_elected(db, tiv_id):
            raise HTTPException(status_code=409, detail="this initiative has been elected — its name is settled")
    try:
        return crud.rename_tiv(db, tiv_id, str(data.get("title") or ""))
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))


@router.post("/{tiv_id}/approve", response_model=schemas.InitiativeRead)
def approve_tiv(
    tiv_id: str,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only: clear a tiv to enter elections."""
    try:
        return crud.approve_tiv(db, tiv_id, staff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{tiv_id}/commit", response_model=schemas.VoteP1Read, status_code=201)
def commit_ebx(
    tiv_id: str,
    data: schemas.VoteP1Create,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Commit EBX to this tiv in its mission's phase-1 election."""
    tiv = crud.get_tiv(db, tiv_id)
    if tiv is None or tiv.mission_id is None:
        raise HTTPException(status_code=404, detail="Initiative is not in an active mission")
    try:
        return crud.commit_p1_ebx(db, user.id, tiv.mission_id, tiv_id, data.ebx_committed)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 409, detail=msg)
