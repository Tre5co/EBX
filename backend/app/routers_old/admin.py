"""Admin votes console (build-seq 1, INSTRUCTIONS step 1).

A back-office view over ALL live voting data across every election and
account. Exposes the full vote table (search / filter / sort / CSV export),
roll-up summaries (by user, election, or target), and integrity checks
(duplicate votes, votes without users, invalid elections).

NOTE (pilot security): there is no admin-role auth in the pilot yet, so these
routes are intentionally unauthenticated for now — they read aggregate data
only and perform no writes. Lock them behind an admin guard before any public
deployment (tracked in README / backlog).
"""
import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


def _csv_response(headers: list[str], rows: list[list], filename: str) -> StreamingResponse:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    for r in rows:
        w.writerow(r)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/votes")
def admin_votes(
    user: Optional[str] = None,
    election: Optional[str] = None,
    organization: Optional[str] = None,
    sort: str = "timestamp_desc",
    format: str = "json",
    db: Session = Depends(get_db),
):
    """Full live-vote table. Filter by `user` (handle substring or id),
    `election` (initiative id), `organization` (org id); `sort` by timestamp;
    `format=csv` to export."""
    rows = crud.admin_list_votes(
        db, user=user, election=election, organization=organization, sort=sort
    )
    if format == "csv":
        headers = ["id", "benefactor_id", "handle", "initiative_id",
                   "initiative_title", "cause_id", "org_id", "org_name",
                   "share", "committed", "kind", "created_at"]
        data = [[r.get(h) for h in headers] for r in rows]
        return _csv_response(headers, data, "earthbux_votes.csv")
    return {"count": len(rows), "votes": rows}


@router.get("/votes/summary")
def admin_votes_summary(by: str = "user", db: Session = Depends(get_db)):
    """Roll-up vote/event counts grouped by `user`, `election`, or `target`."""
    return {"by": by, "entries": crud.admin_vote_summary(db, by=by)}


@router.get("/votes/checks", response_model=schemas.AdminChecks)
def admin_votes_checks(db: Session = Depends(get_db)):
    """Integrity flags: duplicate votes, votes without users, invalid elections."""
    return crud.admin_vote_checks(db)


@router.get("/vote-events")
def admin_vote_events(
    user: Optional[str] = None,
    election: Optional[str] = None,
    sort: str = "timestamp_desc",
    format: str = "json",
    db: Session = Depends(get_db),
):
    """The append-only vote_events audit log (CAST / UPDATE / REMOVE)."""
    events = crud.admin_list_vote_events(db, user=user, election=election, sort=sort)
    if format == "csv":
        headers = ["id", "user_id", "election_id", "cause_id", "target",
                   "kind", "action", "old_value", "new_value", "created_at"]
        data = [[getattr(e, h) for h in headers] for e in events]
        return _csv_response(headers, data, "earthbux_vote_events.csv")
    return {
        "count": len(events),
        "events": [schemas.VoteEventRead.model_validate(e).model_dump() for e in events],
    }
