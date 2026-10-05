"""P4 · Event log + Inbox (2026-10-04) — the inbox API.

  /inbox/summary                         GET   unread notifications · unread threads (the nav badge)
  /inbox/notifications                   GET   the stream (?unread=1 · ?kind= · ?before=<id>)
  /inbox/notifications/read              POST  {ids: [...]} or {all: true}
  /inbox/weekly                          GET   an edition (?week=, default the latest) + YOUR part
  /inbox/weekly/latest                   GET   public — the latest edition (Home, News)
  /inbox/weekly/publish                  POST  staff — publish a week's edition now (?week=)
  /inbox/weekly/preview                  GET   staff — assemble a week without publishing
  /inbox/threads                         GET   my threads (?q= name or mission)
  /inbox/threads                         POST  {to_id, mission_id?} start or reopen a thread
  /inbox/threads/{id}                    GET   the messages (marks the thread read)
  /inbox/threads/{id}/messages           POST  {body}
  /inbox/people                          GET   members of my missions (?q= · ?mission_id=)
  /inbox/messages/{id}/report            POST  {reason}
  /inbox/reports                         GET   staff — reported messages
  /inbox/reports/{id}                    POST  staff — {uphold: bool}

Benefactor accounts only: an organization token is refused here like on
every other benefactor route (auth.get_current_benefactor).
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import events
from ..auth import get_current_benefactor, get_current_benefactor_optional
from ..database import get_db
from ..models import BenefactorAccount
from ._deps import get_current_staff

router = APIRouter(prefix="/inbox", tags=["inbox"])


def _refuse(e: Exception):
    if isinstance(e, PermissionError):
        raise HTTPException(status_code=403, detail=str(e))
    if isinstance(e, LookupError):
        raise HTTPException(status_code=404, detail=str(e))
    raise HTTPException(status_code=400, detail=str(e))


class ReadIn(BaseModel):
    ids: Optional[list[int]] = None
    all: bool = False


class ThreadIn(BaseModel):
    to_id: int
    mission_id: Optional[str] = None


class MessageIn(BaseModel):
    body: str = Field(min_length=1, max_length=events.MESSAGE_MAX)


class ReportIn(BaseModel):
    reason: Optional[str] = None


class ResolveIn(BaseModel):
    uphold: bool


@router.get("/summary")
def summary(db: Session = Depends(get_db), user: BenefactorAccount = Depends(get_current_benefactor)):
    return events.summary(db, user.id)


@router.get("/notifications")
def notifications(unread: bool = False, kind: Optional[str] = None, before: Optional[int] = None,
                  limit: int = 50, db: Session = Depends(get_db),
                  user: BenefactorAccount = Depends(get_current_benefactor)):
    return {"kinds": events.KINDS,
            "items": events.list_notifications(db, user.id, limit=limit, before=before,
                                               unread_only=unread, kind=kind)}


@router.post("/notifications/read")
def mark_read(data: ReadIn, db: Session = Depends(get_db),
              user: BenefactorAccount = Depends(get_current_benefactor)):
    n = events.mark_read(db, user.id, None if data.all else (data.ids or []))
    return {"marked": n, **events.summary(db, user.id)}


@router.get("/weekly/latest")
def weekly_latest(db: Session = Depends(get_db)):
    ev = events.latest_weekly(db)
    return events.weekly_dict(db, ev) if ev else None


@router.get("/weekly/preview")
def weekly_preview(week: Optional[int] = None, db: Session = Depends(get_db),
                   staff: BenefactorAccount = Depends(get_current_staff)):
    w = week if week is not None else events.week_of() - 1
    out = events.assemble_weekly(db, w)
    db.rollback()       # assembling may fix a lead in the session; a preview keeps nothing
    return out


@router.post("/weekly/publish")
def weekly_publish(week: Optional[int] = None, db: Session = Depends(get_db),
                   staff: BenefactorAccount = Depends(get_current_staff)):
    w = week if week is not None else events.week_of() - 1
    ev = events.publish_weekly(db, w)
    if ev is None:
        raise HTTPException(status_code=409, detail=f"Week {w}'s edition is already published")
    return events.weekly_dict(db, ev)


@router.get("/weekly")
def weekly(week: Optional[int] = None, db: Session = Depends(get_db),
           user: Optional[BenefactorAccount] = Depends(get_current_benefactor_optional)):
    ev = events.published_week(db, week) if week is not None else events.latest_weekly(db)
    if ev is None:
        return None
    return events.weekly_dict(db, ev, user.id if user else None)


@router.get("/threads")
def threads(q: Optional[str] = None, db: Session = Depends(get_db),
            user: BenefactorAccount = Depends(get_current_benefactor)):
    return {"rule": events.MESSAGE_RULE, "items": events.list_threads(db, user.id, q)}


@router.post("/threads", status_code=201)
def start_thread(data: ThreadIn, db: Session = Depends(get_db),
                 user: BenefactorAccount = Depends(get_current_benefactor)):
    try:
        return events.open_thread(db, user, data.to_id, data.mission_id)
    except (PermissionError, LookupError, ValueError) as e:
        db.rollback()
        _refuse(e)


@router.get("/threads/{thread_id}")
def read_thread(thread_id: int, db: Session = Depends(get_db),
                user: BenefactorAccount = Depends(get_current_benefactor)):
    try:
        return events.read_thread(db, user.id, thread_id)
    except LookupError as e:
        _refuse(e)


@router.post("/threads/{thread_id}/messages", status_code=201)
def send(thread_id: int, data: MessageIn, db: Session = Depends(get_db),
         user: BenefactorAccount = Depends(get_current_benefactor)):
    try:
        return events.send(db, user.id, thread_id, data.body)
    except (LookupError, ValueError) as e:
        db.rollback()
        _refuse(e)


@router.get("/people")
def people(q: Optional[str] = None, mission_id: Optional[str] = None, db: Session = Depends(get_db),
           user: BenefactorAccount = Depends(get_current_benefactor)):
    return events.people(db, user, q, mission_id)


@router.post("/messages/{message_id}/report", status_code=201)
def report(message_id: int, data: ReportIn, db: Session = Depends(get_db),
           user: BenefactorAccount = Depends(get_current_benefactor)):
    try:
        return events.report(db, user.id, message_id, data.reason)
    except (LookupError, ValueError) as e:
        db.rollback()
        _refuse(e)


@router.get("/reports")
def reports(status: Optional[str] = "open", db: Session = Depends(get_db),
            staff: BenefactorAccount = Depends(get_current_staff)):
    return events.list_reports(db, status or None)


@router.post("/reports/{report_id}")
def resolve(report_id: int, data: ResolveIn, db: Session = Depends(get_db),
            staff: BenefactorAccount = Depends(get_current_staff)):
    try:
        return events.resolve_report(db, report_id, data.uphold)
    except LookupError as e:
        _refuse(e)
