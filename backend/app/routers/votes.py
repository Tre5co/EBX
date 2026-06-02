"""Cause-scoped initiative-election vote endpoints (build-seq 3, Pass 16).

These are the soft-vote share allocator routes the cause.html phase-1 widget
talks to. They are distinct from the existing `/initiatives/{id}/vote` route,
which is the hard org-election vote (one vote per benefactor per mission).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_benefactor
from ..config import get_settings
from ..database import get_db
from ..models import BenefactorAccount


router = APIRouter(tags=["votes"])
settings = get_settings()


@router.put("/benefactors/me/votes", response_model=schemas.CauseVoteTally)
def put_my_cause_votes(
    body: schemas.CauseVoteShares,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Replace the benefactor's soft shares for a single cause.

    Body: `{cause_id, shares: {init_id: share}}`. Server validates the 0.1
    floor and the sum<=1.0 cap. Committed rows cannot be rewritten.
    """
    try:
        crud.replace_cause_votes(db, user.id, body.cause_id, body.shares)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return crud.get_cause_vote_tally(db, body.cause_id, settings.size_factor)


@router.get("/causes/{cause_id}/votes", response_model=schemas.CauseVoteTally)
def get_cause_votes(cause_id: str, db: Session = Depends(get_db)):
    """Public: running tally for a cause with the vote-weight formula applied."""
    return crud.get_cause_vote_tally(db, cause_id, settings.size_factor)


@router.post("/votes/commit")
def commit_my_cause_votes(
    body: schemas.CauseVoteCommit,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Lock the benefactor's current shares for the named cause."""
    count = crud.commit_cause_votes(db, user.id, body.cause_id)
    return {"cause_id": body.cause_id, "locked": count}
