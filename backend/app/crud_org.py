"""crud_org — the organization experience (P2b, 2026-10-02).

Kept out of `crud.py` (4,300 lines) on purpose: everything an ORGANIZATION
account does, plus the two public pages (profile and campaign). It reads the
benefactor-side model (missions, candidacies, posts, the OE tally) and writes
only org accounts, applications, candidacies and org-authored posts.

Dates follow the scheduler's offsets (scheduler.P1_ELECTION_OFFSET /
P2_ELECTION_OFFSET), so "days left" here and the mission page agree.
"""
from __future__ import annotations

import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, select, func, String
from sqlalchemy.orm import Session

from . import crud, models, org_config as ocfg, posting
from .auth import hash_password, verify_password
from .scheduler import P1_ELECTION_OFFSET, P2_ELECTION_OFFSET

CAUSE_NAMES = dict(ocfg.CAUSES)


# ── small helpers ───────────────────────────────────────────────────────────
def _iso(d: Optional[datetime]) -> Optional[str]:
    return d.isoformat() if d else None


def _days_left(d: Optional[datetime], now: datetime) -> Optional[int]:
    if not d:
        return None
    return max(0, (d.date() - now.date()).days)


def is_claimed(db: Session, org_id: str) -> bool:
    return db.scalar(select(func.count()).select_from(models.OrgAccount).where(
        models.OrgAccount.org_id == org_id, models.OrgAccount.is_active.is_(True))) > 0


def account_dict(a: models.OrgAccount) -> dict:
    return {"id": a.id, "org_id": a.org_id, "email": a.email, "handle": a.handle,
            "display_name": a.display_name, "position": a.position, "role": a.role,
            "is_active": a.is_active, "is_test": a.is_test, "created_at": _iso(a.created_at)}


def org_dict(db: Session, o: models.Organization) -> dict:
    return {"id": o.id, "name": o.name, "description": o.description,
            "website_link": o.website_link, "founded_year": o.founded_year,
            "logo_url": o.logo_url, "verified": bool(o.verified),
            "joined_at": _iso(o.joined_at), "claimed": is_claimed(db, o.id)}


def mission_summary(db: Session, m: models.Mission, now: Optional[datetime] = None) -> dict:
    """One mission as the org pages show it: which election is open, when it closes."""
    now = now or datetime.utcnow()
    tiv = db.get(models.Initiative, m.winning_tiv_id) if m.winning_tiv_id else None
    org = db.get(models.Organization, m.winning_org_id) if m.winning_org_id else None
    me_close = m.started_at + P1_ELECTION_OFFSET if m.started_at else None
    oe_close = m.started_at + P2_ELECTION_OFFSET if m.started_at else None
    if m.current_phase == "initiative" and not m.winning_tiv_id:
        stage, closes = "initiative_election", me_close
    elif m.current_phase == "initiative" and not m.winning_org_id:
        stage, closes = "organization_election", oe_close
    elif m.current_phase == "pre":
        stage, closes = "upcoming", m.started_at
    else:
        stage, closes = ("resolved" if m.current_phase == "resolution" else "running"), None
    return {
        "id": m.id, "cause_id": m.cause_id, "cause": CAUSE_NAMES.get(m.cause_id, m.cause_id),
        "cycle": m.cycle_num, "phase": m.current_phase, "stage": stage,
        "initiative": ({"id": tiv.id, "title": tiv.title} if tiv else None),
        "winning_org": ({"id": org.id, "name": org.name} if org else None),
        "closes_at": _iso(closes), "days_left": _days_left(closes, now),
        "href": f"/m/{m.id}",
    }


# ── the application (= the claim) ───────────────────────────────────────────
def _new_org_id(db: Session, name: str) -> str:
    base = crud.slugify(name)[:60] or "org"
    oid, n = base, 2
    while db.get(models.Organization, oid) is not None:
        oid, n = f"{base}-{n}", n + 1
    return oid


def _check_login_free(db: Session, email: str, handle: str) -> None:
    if db.scalar(select(models.OrgAccount).where(func.lower(models.OrgAccount.email) == email.lower())):
        raise ValueError("That email already has an organization login")
    if db.scalar(select(models.OrgAccount).where(func.lower(models.OrgAccount.handle) == handle.lower())):
        raise ValueError("That organization handle is taken")


def apply(db: Session, *, org_id: Optional[str], answers: dict, email: str, handle: str,
          password: str, is_test: bool = False) -> dict:
    """Create the application, the PENDING admin account, and the organization
    if it is new. Refused when the organization already has an administrator —
    that person creates further logins (D29)."""
    errs = ocfg.validate_answers(answers)
    if errs:
        raise ValueError("; ".join(errs))
    email, handle = email.strip(), handle.strip()
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not handle or len(handle) < 2:
        raise ValueError("Choose a handle for the organization login")
    _check_login_free(db, email, handle)
    created = False
    if org_id:
        org = db.get(models.Organization, org_id)
        if org is None:
            raise ValueError("Organization not found")
        if is_claimed(db, org_id):
            raise PermissionError("This organization is already claimed — ask its administrator "
                                  "on Earthbux to create your login.")
    else:
        name = (answers.get("public_name") or answers.get("legal_name") or "").strip()
        org = models.Organization(id=_new_org_id(db, name), name=name, verified=False)
        created = True
        db.add(org)
    # The answers fill the profile's empty fields; nothing already there is overwritten.
    if not org.description and answers.get("one_line"):
        org.description = answers["one_line"].strip()
    if not org.website_link and answers.get("website"):
        org.website_link = answers["website"].strip()
    if not org.founded_year and answers.get("founded_year"):
        try:
            org.founded_year = int(answers["founded_year"])
        except (TypeError, ValueError):
            pass
    db.flush()
    acct = models.OrgAccount(org_id=org.id, email=email, handle=handle,
                             pass_hash=hash_password(password),
                             display_name=(answers.get("full_name") or "").strip() or None,
                             position=(answers.get("position") or "").strip() or None,
                             role="admin", is_active=False, is_test=is_test)
    db.add(acct)
    db.flush()
    app = models.OrgApplication(org_id=org.id, account_id=acct.id, answers=answers,
                                attestation_version=ocfg.ATTESTATION_VERSION,
                                status="pending", created_org=created)
    db.add(app)
    db.commit()
    return {"application_id": app.id, "org_id": org.id, "status": "pending", "created_org": created}


def application_dict(db: Session, a: models.OrgApplication) -> dict:
    org = db.get(models.Organization, a.org_id)
    acct = db.get(models.OrgAccount, a.account_id) if a.account_id else None
    return {"id": a.id, "org_id": a.org_id, "org_name": org.name if org else a.org_id,
            "status": a.status, "created_org": a.created_org, "answers": a.answers or {},
            "account": account_dict(acct) if acct else None, "review_note": a.review_note,
            "created_at": _iso(a.created_at), "reviewed_at": _iso(a.reviewed_at)}


def list_applications(db: Session, status: Optional[str] = None) -> list[dict]:
    q = select(models.OrgApplication).order_by(models.OrgApplication.created_at.desc())
    if status:
        q = q.where(models.OrgApplication.status == status)
    return [application_dict(db, a) for a in db.scalars(q).all()]


def review_application(db: Session, app_id: int, staff: models.BenefactorAccount,
                       approve: bool, note: Optional[str] = None) -> dict:
    a = db.get(models.OrgApplication, app_id)
    if a is None:
        raise ValueError("Application not found")
    if a.status != "pending":
        raise ValueError(f"Application is already {a.status}")
    if approve and is_claimed(db, a.org_id):
        raise ValueError("Organization was claimed by another application in the meantime")
    a.status = "approved" if approve else "rejected"
    a.review_note, a.reviewed_by_id, a.reviewed_at = note, staff.id, datetime.utcnow()
    acct = db.get(models.OrgAccount, a.account_id) if a.account_id else None
    if approve and acct:
        acct.is_active = True
        org = db.get(models.Organization, a.org_id)
        if org and not org.joined_at:
            org.joined_at = datetime.utcnow()
    db.commit()
    return application_dict(db, a)


# ── signing in ──────────────────────────────────────────────────────────────
def authenticate(db: Session, username: str, password: str) -> models.OrgAccount:
    u = (username or "").strip().lower()
    acct = db.scalar(select(models.OrgAccount).where(or_(
        func.lower(models.OrgAccount.email) == u, func.lower(models.OrgAccount.handle) == u)))
    if acct is None or not verify_password(password, acct.pass_hash):
        raise LookupError("Invalid credentials")
    if not acct.is_active:
        raise PermissionError("This organization login is waiting for Earthbux to approve the application")
    return acct


# ── members (D29: the administrator creates the logins) ─────────────────────
def list_members(db: Session, org_id: str) -> list[dict]:
    rows = db.scalars(select(models.OrgAccount).where(models.OrgAccount.org_id == org_id)
                      .order_by(models.OrgAccount.created_at)).all()
    return [account_dict(a) for a in rows]


def create_member(db: Session, admin: models.OrgAccount, *, email: str, handle: str, password: str,
                  display_name: Optional[str], position: Optional[str], role: str = "member") -> dict:
    if admin.role != "admin":
        raise PermissionError("Only an organization administrator creates logins")
    if role not in ocfg.MEMBER_ROLES:
        raise ValueError(f"role must be one of {', '.join(ocfg.MEMBER_ROLES)}")
    if len(password or "") < 8:
        raise ValueError("Password must be at least 8 characters")
    _check_login_free(db, email.strip(), handle.strip())
    a = models.OrgAccount(org_id=admin.org_id, email=email.strip(), handle=handle.strip(),
                          pass_hash=hash_password(password), display_name=display_name,
                          position=position, role=role, is_active=True,
                          is_test=admin.is_test, created_by_id=admin.id)
    db.add(a)
    db.commit()
    return account_dict(a)


# ── profile ─────────────────────────────────────────────────────────────────
PROFILE_FIELDS = ("name", "description", "website_link", "logo_url", "founded_year")


def update_profile(db: Session, acct: models.OrgAccount, fields: dict) -> dict:
    org = db.get(models.Organization, acct.org_id)
    for k in PROFILE_FIELDS:
        if k in fields and fields[k] is not None:
            v = fields[k]
            if k == "name" and not str(v).strip():
                raise ValueError("The name cannot be empty")
            setattr(org, k, v.strip() if isinstance(v, str) else v)
    db.commit()
    return org_dict(db, org)


# ── campaigns ───────────────────────────────────────────────────────────────
def _rank_in_race(db: Session, mission_id: str, org_id: str) -> dict:
    t = crud.p2_tally(db, mission_id)
    entries = t.get("entries") or []
    for i, e in enumerate(entries):
        if e["org_id"] == org_id:
            return {"rank": i + 1, "of": len(entries), "net_votes": e["net_votes"],
                    "voter_count": e["voter_count"], "ebx": e["ebx"], "pool_ebx": t.get("pool_ebx")}
    return {"rank": None, "of": len(entries), "net_votes": 0, "voter_count": 0, "ebx": 0.0,
            "pool_ebx": t.get("pool_ebx")}


def campaigns(db: Session, org_id: str) -> list[dict]:
    now = datetime.utcnow()
    out = []
    for c in db.scalars(select(models.MissionCandidacy).where(
            models.MissionCandidacy.org_id == org_id)
            .order_by(models.MissionCandidacy.created_at.desc())).all():
        m = db.get(models.Mission, c.mission_id)
        if m is None:
            continue
        ms = mission_summary(db, m, now)
        won = m.winning_org_id == org_id
        ms.update({
            "candidacy_id": c.id, "status": ("won" if won else c.status),
            "promise": c.mission_statement,
            "standing": _rank_in_race(db, m.id, org_id) if ms["stage"] == "organization_election" else None,
            "campaign_href": f"/o/{org_id}/{m.id}",
        })
        out.append(ms)
    return out


def _campaign_or_refuse(db: Session, org_id: str, mission_id: str) -> models.MissionCandidacy:
    c = db.scalar(select(models.MissionCandidacy).where(
        models.MissionCandidacy.org_id == org_id, models.MissionCandidacy.mission_id == mission_id))
    if c is None:
        raise ValueError("No campaign for this mission — run for it first")
    return c


def run_for(db: Session, acct: models.OrgAccount, mission_id: str, statement: Optional[str]) -> dict:
    """Run for this — a candidacy, pending staff approval like any other."""
    m = db.get(models.Mission, mission_id)
    if m is None:
        raise ValueError("Mission not found")
    if m.winning_org_id:
        raise ValueError("This mission's organization election is already decided")
    if not (statement or "").strip():
        raise ValueError("Say what you would do — a short mission statement is what makes a "
                         "candidate electable")
    from . import schemas
    c = crud.create_candidacy(db, schemas.MissionCandidacyCreate(
        mission_id=mission_id, org_id=acct.org_id, mission_statement=statement.strip()))
    return {"candidacy_id": c.id, "mission_id": mission_id, "status": c.status}


def set_promise(db: Session, acct: models.OrgAccount, mission_id: str, statement: str) -> dict:
    c = _campaign_or_refuse(db, acct.org_id, mission_id)
    m = db.get(models.Mission, mission_id)
    if c.status in ("lost", "withdrawn") or (m and m.winning_org_id and m.winning_org_id != acct.org_id):
        raise ValueError("This campaign is over — its promise stays as benefactors voted on it")
    if not (statement or "").strip():
        raise ValueError("The promise cannot be empty")
    c.mission_statement = statement.strip()
    db.commit()
    return {"mission_id": mission_id, "promise": c.mission_statement}


# ── organization posts ──────────────────────────────────────────────────────
def _about_org(db: Session, org_id: str):
    """The condition for 'a post about this organization' (the Q&A source)."""
    return or_(models.Post.org_id == org_id,
               models.Post.tags.cast(String).like(f'%"org:{org_id}"%'))


def create_org_post(db: Session, acct: models.OrgAccount, *, kind: str, body: str,
                    title: Optional[str] = None, mission_id: Optional[str] = None,
                    tiv_id: Optional[str] = None, parent_id: Optional[str] = None) -> dict:
    if kind not in ocfg.ORG_POST_KINDS:
        raise ValueError(f"kind must be one of {', '.join(ocfg.ORG_POST_KINDS)}")
    if not (body or "").strip():
        raise ValueError("A post needs a body")
    p = models.Post(id="op-" + secrets.token_hex(6), category="org_update", type=kind,
                    title=(title or "").strip() or None, body=body.strip(),
                    author_type="org", org_author_id=acct.org_id,
                    tags=[f"org:{acct.org_id}"])
    if kind == "update":
        posting._fill_target(db, p, "organization", acct.org_id)
    elif kind == "plan":
        _campaign_or_refuse(db, acct.org_id, mission_id or "")
        posting._fill_target(db, p, "mission", mission_id)
    elif kind == "suggestion":
        tiv = db.get(models.Initiative, tiv_id or "")
        if tiv is None:
            raise ValueError("Initiative not found")
        m = db.get(models.Mission, tiv.mission_id) if tiv.mission_id else None
        if m is not None and m.winning_tiv_id and m.winning_tiv_id != tiv.id:
            raise ValueError("That initiative lost its election")
        posting._fill_target(db, p, "initiative", tiv.id)
        p.tags = [f"org:{acct.org_id}", f"tiv:{tiv.id}", "suggestion"]
    elif kind == "answer":
        parent = db.get(models.Post, parent_id or "")
        if parent is None:
            raise ValueError("The post you are answering was not found")
        mine = {c.mission_id for c in db.scalars(select(models.MissionCandidacy).where(
            models.MissionCandidacy.org_id == acct.org_id)).all()}
        about = (parent.org_id == acct.org_id or f"org:{acct.org_id}" in (parent.tags or [])
                 or (parent.mission_id in mine))
        if not about:
            raise PermissionError("An organization answers posts about itself or its campaigns")
        p.parent_id = parent.id
        p.mission_id, p.org_id, p.tiv_id, p.cause_id = (parent.mission_id, parent.org_id,
                                                        parent.tiv_id, parent.cause_id)
        p.target_kind, p.target_id = "post", parent.id
    p.flag = "green"
    db.add(p)
    db.flush()
    posting.after_create(db, p, [])
    db.commit()
    return posting.serialize(db, [p])[0]


# ── the org's own Home and Initiatives ──────────────────────────────────────
def home(db: Session, acct: models.OrgAccount) -> dict:
    org = db.get(models.Organization, acct.org_id)
    camps = campaigns(db, acct.org_id)
    mids = [c["id"] for c in camps]
    changed = []
    if mids:
        rows = db.scalars(select(models.Post).where(
            models.Post.mission_id.in_(mids), models.Post.parent_id.is_(None),
            or_(models.Post.org_author_id.is_(None), models.Post.org_author_id != acct.org_id))
            .order_by(models.Post.created_at.desc()).limit(15)).all()
        changed = posting.serialize(db, list(rows))
    about = db.scalars(select(models.Post).where(_about_org(db, acct.org_id),
                                                 models.Post.parent_id.is_(None),
                                                 or_(models.Post.org_author_id.is_(None),
                                                     models.Post.org_author_id != acct.org_id))
                       .order_by(models.Post.created_at.desc()).limit(15)).all()
    news = db.scalars(select(models.Post).where(models.Post.author_type == "earthbux",
                                                models.Post.parent_id.is_(None))
                      .order_by(models.Post.created_at.desc()).limit(8)).all()
    return {"org": org_dict(db, org), "account": account_dict(acct), "campaigns": camps,
            "activity": changed, "about_you": posting.serialize(db, list(about)),
            "earthbux": posting.serialize(db, list(news))}


def initiatives(db: Session, acct: models.OrgAccount) -> dict:
    """Mission steps 2–3, from the organization's side."""
    now = datetime.utcnow()
    mine = {c.mission_id: c for c in db.scalars(select(models.MissionCandidacy).where(
        models.MissionCandidacy.org_id == acct.org_id)).all()}
    suggested = {p.tiv_id for p in db.scalars(select(models.Post).where(
        models.Post.org_author_id == acct.org_id, models.Post.type == "suggestion")).all()}
    me_rows, oe_rows = [], []
    for m in db.scalars(select(models.Mission).where(models.Mission.current_phase == "initiative")
                        .order_by(models.Mission.started_at)).all():
        ms = mission_summary(db, m, now)
        # A race whose close has passed is waiting for the scheduler, not open.
        closes = m.started_at + (P1_ELECTION_OFFSET if ms["stage"] == "initiative_election"
                                 else P2_ELECTION_OFFSET) if m.started_at else None
        if closes is not None and closes < now:
            continue
        if ms["stage"] == "initiative_election":
            tivs = db.scalars(select(models.Initiative).where(
                models.Initiative.mission_id == m.id)).all()
            ms["initiatives"] = [{"id": t.id, "title": t.title, "suggested_us": t.id in suggested}
                                 for t in tivs]
            ms["running"] = m.id in mine
            me_rows.append(ms)
        elif ms["stage"] == "organization_election":
            t = crud.p2_tally(db, m.id)
            names = {o.id: o.name for o in db.scalars(select(models.Organization)).all()}
            cands = db.scalars(select(models.MissionCandidacy).where(
                models.MissionCandidacy.mission_id == m.id)).all()
            votes = {e["org_id"]: e for e in t.get("entries") or []}
            ms["candidates"] = sorted([
                {"org_id": c.org_id, "name": names.get(c.org_id, c.org_id), "status": c.status,
                 "net_votes": votes.get(c.org_id, {}).get("net_votes", 0),
                 "ebx": votes.get(c.org_id, {}).get("ebx", 0.0),
                 "campaign_href": f"/o/{c.org_id}/{m.id}"} for c in cands],
                key=lambda r: (-r["net_votes"], -r["ebx"]))
            ms["running"] = m.id in mine
            # A suggestion on the initiative that WON reads as an invitation to run
            # (the proposed tiv_id migration would make it a candidacy automatically).
            ms["you_suggested_winner"] = bool(m.winning_tiv_id in suggested and m.id not in mine)
            oe_rows.append(ms)
    return {"initiative_elections": me_rows, "organization_elections": oe_rows}


# ── the two public pages ────────────────────────────────────────────────────
def public_profile(db: Session, org_id: str) -> dict:
    org = db.get(models.Organization, org_id)
    if org is None:
        raise ValueError("Organization not found")
    claimed = is_claimed(db, org_id)
    camps = campaigns(db, org_id)
    updates = db.scalars(select(models.Post).where(
        models.Post.org_author_id == org_id, models.Post.parent_id.is_(None))
        .order_by(models.Post.created_at.desc()).limit(30)).all()
    discussion = db.scalars(select(models.Post).where(
        _about_org(db, org_id), models.Post.parent_id.is_(None),
        or_(models.Post.org_author_id.is_(None), models.Post.org_author_id != org_id))
        .order_by(models.Post.created_at.desc()).limit(30)).all()
    members = [{"display_name": a["display_name"] or a["handle"], "position": a["position"],
                "role": a["role"]} for a in list_members(db, org_id) if a["is_active"]]
    return {
        "org": org_dict(db, org),
        "claimed": claimed,
        "unclaimed_panel": None if claimed else ocfg.UNCLAIMED_PANEL,
        "members": members,
        "campaigns": camps,
        "missions_won": [c for c in camps if c["status"] == "won"],
        "updates": posting.serialize(db, list(updates)) if claimed else [],
        "discussion": posting.serialize(db, list(discussion)),
    }


def campaign_page(db: Session, org_id: str, mission_id: str) -> dict:
    """The five sections — Plan · Receipts · Live ballot slate · Q&A · Promise."""
    org = db.get(models.Organization, org_id)
    if org is None:
        raise ValueError("Organization not found")
    m = db.get(models.Mission, mission_id)
    if m is None:
        raise ValueError("Mission not found")
    cand = _campaign_or_refuse(db, org_id, mission_id)
    ms = mission_summary(db, m)
    plan_posts = db.scalars(select(models.Post).where(
        models.Post.org_author_id == org_id, models.Post.type == "plan",
        models.Post.mission_id == mission_id).order_by(models.Post.created_at.desc())).all()
    budget = []
    if m.winning_tiv_id:
        budget = db.scalars(select(models.Post).where(
            models.Post.category == "budgeting", models.Post.tiv_id == m.winning_tiv_id,
            models.Post.parent_id.is_(None)).order_by(models.Post.helpful_count.desc())).all()
    # Receipts: what this organization has done on Earthbux so far.
    camps = campaigns(db, org_id)
    won = [c for c in camps if c["status"] == "won"]
    completed = [c for c in won if c["phase"] == "resolution"]
    # Q&A: every root post about the organization or on this campaign's mission
    # that is not the organization's own, with the organization's answers.
    qa_roots = db.scalars(select(models.Post).where(
        models.Post.parent_id.is_(None),
        or_(models.Post.org_author_id.is_(None), models.Post.org_author_id != org_id),
        or_(_about_org(db, org_id),
            (models.Post.mission_id == mission_id) & (models.Post.category == "general")))
        .order_by(models.Post.created_at.desc()).limit(40)).all()
    qa = []
    for root in posting.serialize(db, list(qa_roots)):
        answers = db.scalars(select(models.Post).where(
            models.Post.parent_id == root["id"], models.Post.org_author_id == org_id)
            .order_by(models.Post.created_at)).all()
        root["org_answers"] = posting.serialize(db, list(answers))
        qa.append(root)
    standing = _rank_in_race(db, mission_id, org_id)
    return {
        "org": org_dict(db, org),
        "mission": ms,
        "status": "won" if m.winning_org_id == org_id else cand.status,
        "promise": cand.mission_statement,
        "plan": {"org_plan": posting.serialize(db, list(plan_posts)),
                 "budget_items": posting.serialize(db, list(budget)),
                 "budget_total_usd": round(sum((p.est_cost_usd or 0) for p in budget), 2)},
        "receipts": {"missions_won": len(won), "missions_completed": len(completed),
                     "won": won, "first_receipt": _first_receipt(db, org_id)},
        "slate": {**standing, "closes_at": ms["closes_at"], "days_left": ms["days_left"],
                  "open": ms["stage"] == "organization_election"},
        "qa": qa,
    }


def _first_receipt(db: Session, org_id: str) -> Optional[str]:
    """The 'past outcome with a number' from the approved application."""
    a = db.scalar(select(models.OrgApplication).where(
        models.OrgApplication.org_id == org_id, models.OrgApplication.status == "approved")
        .order_by(models.OrgApplication.reviewed_at.desc()))
    return (a.answers or {}).get("receipt") if a else None
