"""Contact us (2026-09-25) — the footer's dialog posts here.

POST /contact           anyone; stores the message, emails it to CONTACT_TO
                        (jax@earthbux.net) when mail is configured.
GET  /admin/contact     staff; newest first.
PUT  /admin/contact/{id} staff; status new | read | answered.

Spam guard, kept small on purpose: a hidden `website` field that people never
fill (bots do — such a post is accepted and dropped), length limits, and at most
5 messages per address per 10 minutes.
"""
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import mailer, models
from ..auth import get_current_benefactor_optional
from ..config import get_settings
from ..database import SessionLocal, get_db
from ._deps import get_current_staff

router = APIRouter(tags=["contact"])

TOPICS = {
    "general": "General",
    "organization": "Organizations & philanthropies",
    "press": "Press & news",
    "problem": "Report a problem",
    "join": "Join the team",
}
_WINDOW, _MAX = 600, 5
_recent: dict[str, deque] = defaultdict(deque)


class ContactIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    topic: str = "general"
    body: str = Field(min_length=5, max_length=5000)
    page: Optional[str] = Field(default=None, max_length=300)
    website: Optional[str] = None     # honeypot — must stay empty


class ContactOut(BaseModel):
    ok: bool
    id: Optional[int] = None
    emailed: bool = False


class ContactRead(BaseModel):
    id: int
    name: str
    email: str
    topic: str
    body: str
    page: Optional[str] = None
    ben_id: Optional[int] = None
    status: str
    emailed: bool
    created_at: Optional[object] = None

    model_config = {"from_attributes": True}


def _email_it(msg_id: int) -> None:
    """Background: email one stored message and record whether it went."""
    print(f"[mailer] contact #{msg_id}: sending via {mailer.route()}")
    db = SessionLocal()
    try:
        m = db.get(models.ContactMessage, msg_id)
        if m is None:
            return
        body = (f"From: {m.name} <{m.email}>\nTopic: {TOPICS.get(m.topic, m.topic)}\n"
                f"Page: {m.page or '—'}\nAccount: {m.ben_id or 'signed out'}\n\n{m.body}\n")
        if mailer.send(get_settings().contact_to, f"[Earthbux contact] {TOPICS.get(m.topic, m.topic)} — {m.name}",
                       body, reply_to=m.email):
            m.emailed = True
            db.commit()
            print(f"[mailer] contact #{msg_id}: sent to {get_settings().contact_to}")
        else:
            print(f"[mailer] contact #{msg_id}: NOT sent (see the line above)")
    finally:
        db.close()


@router.post("/contact", response_model=ContactOut, status_code=201)
def contact(data: ContactIn, request: Request, tasks: BackgroundTasks, db: Session = Depends(get_db),
            user=Depends(get_current_benefactor_optional)):
    if data.website:                       # the honeypot: look accepted, keep nothing
        return ContactOut(ok=True)
    if data.topic not in TOPICS:
        raise HTTPException(status_code=400, detail="unknown topic")
    ip = (request.client.host if request.client else "?")
    q, now = _recent[ip], time.time()
    while q and now - q[0] > _WINDOW:
        q.popleft()
    if len(q) >= _MAX:
        raise HTTPException(status_code=429, detail="Too many messages — please try again in a few minutes.")
    q.append(now)
    m = models.ContactMessage(name=data.name.strip(), email=str(data.email), topic=data.topic,
                              body=data.body.strip(), page=data.page,
                              ben_id=getattr(user, "id", None))
    db.add(m)
    db.commit()
    db.refresh(m)
    if mailer.configured():
        tasks.add_task(_email_it, m.id)
    else:
        print(f"[mailer] contact #{m.id}: stored only — mail route is {mailer.route()}")
    return ContactOut(ok=True, id=m.id, emailed=False)


# 2026-09-26 — "no mail and no activity on the key": say which route the
# server actually sees, and send one test email synchronously so the reason for
# a failure comes back in the response instead of only in the deploy logs.
@router.get("/admin/mail/status")
def mail_status(staff=Depends(get_current_staff)):
    s = get_settings()
    return {"route": mailer.route(), "contact_to": s.contact_to,
            "resend_key_set": bool(s.resend_api_key), "smtp_host_set": bool(s.smtp_host)}


@router.post("/admin/mail/test")
def mail_test(staff=Depends(get_current_staff)):
    s = get_settings()
    if not mailer.configured():
        return {"sent": False, "route": mailer.route()}
    ok = mailer.send(s.contact_to, "[Earthbux] mail test",
                     f"This is a test from the Earthbux server via {mailer.route()}.")
    return {"sent": ok, "route": mailer.route(), "to": s.contact_to,
            "hint": None if ok else "Check the deploy logs for the [mailer] line with Resend's reason."}


@router.get("/admin/contact", response_model=list[ContactRead])
def list_contact(status: Optional[str] = None, limit: int = 200, db: Session = Depends(get_db),
                 staff=Depends(get_current_staff)):
    stmt = select(models.ContactMessage).order_by(models.ContactMessage.id.desc()).limit(min(limit, 1000))
    if status:
        stmt = stmt.where(models.ContactMessage.status == status)
    return list(db.scalars(stmt))


@router.put("/admin/contact/{msg_id}", response_model=ContactRead)
def set_contact_status(msg_id: int, status: str = Body(..., embed=True), db: Session = Depends(get_db),
                       staff=Depends(get_current_staff)):
    if status not in ("new", "read", "answered"):
        raise HTTPException(status_code=400, detail="status must be new, read or answered")
    m = db.get(models.ContactMessage, msg_id)
    if m is None:
        raise HTTPException(status_code=404, detail="message not found")
    m.status = status
    db.commit()
    db.refresh(m)
    return m
