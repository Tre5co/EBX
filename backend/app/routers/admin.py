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


@router.post("/accounts/{ben_id}/test", response_model=schemas.BenefactorRead)
def set_test(
    ben_id: int,
    is_test: bool = True,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only: mark (or unmark) an account as a bot (build-seq §2)."""
    ben = db.get(BenefactorAccount, ben_id)
    if ben is None:
        raise HTTPException(status_code=404, detail="Account not found")
    ben.is_test = bool(is_test)
    db.commit()
    db.refresh(ben)
    return ben


@router.get("/accounts", response_model=list[dict])
def list_accounts(
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Every account with a footprint summary — what removing it would take
    with it. Feeds the account console on admin.html (2026-08-06)."""
    return crud.account_footprints(db)


@router.post("/accounts/{ben_id}/reset-password", response_model=dict)
def reset_password(
    ben_id: int,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """§0d (2026-08-08): issue a one-off temporary password for a locked-out
    account. Earthbux has no mail transport, so the plaintext comes back here
    for staff to send to the address on the account; a real self-serve reset
    (emailed single-use token) is on the backlog. Returned exactly once."""
    try:
        return crud.issue_temp_password(db, ben_id, staff)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/accounts/{ben_id}", response_model=dict)
def remove_account(
    ben_id: int,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Delete a fraudulent or bug-created account and everything it cast.

    Staff-only, and deliberately destructive: votes are REMOVED (not zeroed) so
    the tallies they inflated go back to the truth. Posts are kept but
    orphaned — an argument someone answered shouldn't vanish from a thread.
    Returns what was deleted so the console can report it.
    """
    try:
        return crud.remove_account(db, ben_id, staff)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
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


@router.post("/elections/me-reset", response_model=dict)
def me_reset(
    dry_run: bool = True,
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only (build-seq §2, 2026-09-17): recount every OPEN initiative
    election by the whole-percentage rule. `?dry_run=false` writes."""
    return crud.reset_open_me_slates(db, dry_run=dry_run)


@router.get("/elections/unelected-orgs", response_model=list)
def unelected_orgs(
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only (build-seq §1): past organization elections that never elected
    an organization — the backfill list."""
    from datetime import datetime
    from sqlalchemy import select
    from .. import models, wallet as w
    now = datetime.utcnow()
    out = []
    for m in db.scalars(select(models.Mission).where(models.Mission.winning_tiv_id.is_not(None),
                                                     models.Mission.winning_org_id.is_(None))).all():
        if w._vote_day(m) <= now:
            out.append({"mission_id": m.id, "cause_id": m.cause_id, "tiv_id": m.winning_tiv_id,
                        "vote_date": w._vote_day(m).isoformat(),
                        "candidates": [{"org_id": c.org_id, "status": c.status,
                                        "has_statement": bool((c.mission_statement or "").strip())}
                                       for c in db.scalars(select(models.MissionCandidacy).where(
                                           models.MissionCandidacy.mission_id == m.id)).all()]})
    return out


@router.get("/elections/unelected-tivs", response_model=list)
def unelected_tivs(
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only (build-seq §1, 2026-09-18): initiative elections whose day has
    passed with nothing elected — the backfill list, with what is standing in
    each one so the choice can be made from this response."""
    from datetime import datetime
    from sqlalchemy import select
    from .. import models
    now = datetime.utcnow()
    out = []
    for m in db.scalars(select(models.Mission).where(models.Mission.winning_tiv_id.is_(None))).all():
        if crud._p1_decision_day(m) > now:
            continue
        out.append({
            "mission_id": m.id, "cause_id": m.cause_id, "cycle_num": m.cycle_num,
            "decision_day": crud._p1_decision_day(m).isoformat(),
            "running": [{"tiv_id": t.id, "title": t.title} for t in db.scalars(
                select(models.Initiative).where(models.Initiative.mission_id == m.id)).all()],
            "preferences": crud.p1_preferences(db, m.id),
        })
    return out


@router.post("/missions/{mission_id}/backfill-tiv", response_model=dict)
def backfill_tiv(
    mission_id: str,
    tiv_id: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only (build-seq §1): elect an initiative in a past initiative
    election that never elected one."""
    try:
        return crud.backfill_tiv_election(db, mission_id, staff, tiv_id)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/missions/{mission_id}/backfill-org", response_model=dict)
def backfill_org(
    mission_id: str,
    org_id: Optional[str] = Body(default=None, embed=True),
    mission_statement: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    staff: BenefactorAccount = Depends(get_current_staff),
):
    """Staff-only (build-seq §1): elect an organization in a past race that never
    got one."""
    try:
        return crud.backfill_org_election(db, mission_id, staff, org_id, mission_statement)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
