"""P4 · Event log + Inbox (2026-10-04) — the event log, its fan-out, the
weekly update, and member messages.

**One source.** Something happens once and is written once, as an `Event`:
who did it, what it was about, and a `dedupe` key where it must happen only
once (a like threshold, an election, a week). Notifications are the
per-benefactor fan-out of an event (`Notification`, read / unread); the weekly
update is assembled from the same log and published as an event itself; the
admin audit trail reads it later. D9: email is optional and not built here —
every notification is inbox-only until there is a mail transport.

**What notifies** (`KINDS`):

  reply          someone replied to your post (a benefactor, or an
                 organization answering it)
  reaction       your post reached 1 · 5 · 10 · 25 · 50 · 100 … votes
  cited_update   a post you cite has a new version ("cited v1 · now v3")
  org_nominated  an organization was suggested for, or is running for, an
                 initiative you proposed or watch
  tiv_elected    the initiative election you voted in closed — won or lost,
                 and what comes next
  org_elected    the organization election you voted in closed — won, lost,
                 or your stake followed the winner — and what comes next
  weekly_update  this week's edition

**Never in the way.** Every hook here runs AFTER the action it reports has
committed, through `safe()`: a failure to notify is printed and rolled back,
and never undoes or refuses the vote, post or election that caused it. No
function here moves money; the election hooks only read who voted for what.

**Messages (D10).** No friendships — a thread is between two benefactors who
share a mission (both voted in it), searchable by name or by mission. The
no-campaigning rule is stated in the page and here (`MESSAGE_RULE`), and any
message can be reported (`MessageReport`, read by staff).
"""
from __future__ import annotations

import json
import traceback
from datetime import datetime, timedelta
from typing import Iterable, Optional

from sqlalchemy import func as sqlfunc, or_, select
from sqlalchemy.orm import Session

from . import models, post_config as pcfg
from .bootstrap import GENESIS, WEEK

KINDS = {
    "reply": "Replies",
    "reaction": "Votes on your posts",
    "cited_update": "Posts you cite",
    "org_nominated": "Organizations for your initiatives",
    "tiv_elected": "Initiative elections",
    "org_elected": "Organization elections",
    "weekly_update": "Weekly update",
}
REACTION_THRESHOLDS = (1, 5, 10, 25, 50, 100, 250, 500, 1000)
MESSAGE_MAX = 2000
MESSAGE_RULE = ("Messages are for members of the same mission, working on it together. "
                "No campaigning: do not ask anyone to vote for an initiative or an organization, "
                "and never offer anything for a vote. Report a message that does.")


# ── time ────────────────────────────────────────────────────────────────────
def week_of(when: Optional[datetime] = None) -> int:
    """The cycle week (the anchor `wallet.current_week` and the frontend use)."""
    when = when or datetime.utcnow()
    return max(0, int((when - GENESIS) / WEEK))


def week_bounds(week: int) -> tuple[datetime, datetime]:
    start = GENESIS + week * WEEK
    return start, start + WEEK


def _iso(d: Optional[datetime]) -> Optional[str]:
    """UTC, marked as such — the database's clock is naive UTC, and a browser
    reads an unmarked time as local."""
    if not d:
        return None
    return d.isoformat() + ("Z" if d.tzinfo is None else "")


# ── the log ─────────────────────────────────────────────────────────────────
def safe(fn, db: Session, *a, **kw):
    """Run a hook; a failure is printed and rolled back, never raised."""
    try:
        return fn(db, *a, **kw)
    except Exception:  # noqa: BLE001 — notifying must never break the action
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass
        print("[events] hook failed:", getattr(fn, "__name__", fn))
        traceback.print_exc()
        return None


def peek(fn, *a, **kw):
    """Run a READ inside someone else's transaction; on failure return None
    and leave the transaction alone (no rollback — the caller's work stands)."""
    try:
        return fn(*a, **kw)
    except Exception:  # noqa: BLE001
        print("[events] read failed:", getattr(fn, "__name__", fn))
        traceback.print_exc()
        return None


def record(db: Session, kind: str, recipients=None, *, actor_ben_id: Optional[int] = None,
           actor_org_id: Optional[str] = None, post_id: Optional[str] = None,
           mission_id: Optional[str] = None, tiv_id: Optional[str] = None,
           org_id: Optional[str] = None, week: Optional[int] = None,
           dedupe: Optional[str] = None, data: Optional[dict] = None,
           commit: bool = True) -> Optional[models.Event]:
    """Write one event and fan it out. `recipients` is an iterable of
    benefactor ids, or a dict {ben_id: detail-for-them}. The actor is never
    notified of their own act. Returns None when `dedupe` was already used."""
    if dedupe and db.scalar(select(models.Event.id).where(models.Event.dedupe == dedupe)) is not None:
        return None
    if recipients is None:
        recipients = {}
    if not isinstance(recipients, dict):
        recipients = {r: None for r in recipients}
    recipients = {int(r): d for r, d in recipients.items() if r and r != actor_ben_id}
    ev = models.Event(kind=kind, actor_ben_id=actor_ben_id, actor_org_id=actor_org_id,
                      post_id=post_id, mission_id=mission_id, tiv_id=tiv_id, org_id=org_id,
                      week=week if week is not None else week_of(), dedupe=dedupe, data=data or {})
    db.add(ev)
    db.flush()
    if recipients:
        live = {i for (i,) in db.execute(select(models.BenefactorAccount.id).where(
            models.BenefactorAccount.id.in_(list(recipients)),
            models.BenefactorAccount.is_active.is_(True))).all()}
        db.add_all([models.Notification(ben_id=r, event_id=ev.id, detail=d)
                    for r, d in recipients.items() if r in live])
    if commit:
        db.commit()
    return ev


def _excerpt(text: Optional[str], n: int = 140) -> str:
    t = " ".join(str(text or "").split())
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _post_label(p: Optional[models.Post]) -> str:
    if p is None:
        return "a post"
    return p.title or _excerpt(p.body, 70) or "a post"


def _handle(db: Session, ben_id: Optional[int]) -> Optional[str]:
    if not ben_id:
        return None
    b = db.get(models.BenefactorAccount, ben_id)
    return b.handle if b else None


def _org_name(db: Session, org_id: Optional[str]) -> Optional[str]:
    if not org_id:
        return None
    o = db.get(models.Organization, org_id)
    return o.name if o else org_id


def _mission_label(db: Session, mission_id: Optional[str]) -> Optional[str]:
    if not mission_id:
        return None
    from .posting import mission_labels
    return mission_labels(db, [mission_id]).get(mission_id, mission_id)


# ── hooks: posts ────────────────────────────────────────────────────────────
def on_post_created(db: Session, post: models.Post) -> Optional[models.Event]:
    """A reply notifies the author of the post it replies to; an
    organization's Suggest us notifies the initiative's proposer and watchers."""
    if post.category == "org_update" and post.type == "suggestion" and post.tiv_id:
        return on_org_nominated(db, org_id=post.org_author_id, tiv_id=post.tiv_id,
                                how="suggested", actor_org_id=post.org_author_id)
    if not post.parent_id:
        return None
    parent = db.get(models.Post, post.parent_id)
    if parent is None or not parent.ben_author_id:
        return None
    by_org = post.author_type == "org"
    return record(db, "reply", [parent.ben_author_id],
                  actor_ben_id=post.ben_author_id, actor_org_id=post.org_author_id if by_org else None,
                  post_id=post.id, mission_id=post.mission_id or parent.mission_id,
                  data={"parent_id": parent.id, "parent_label": _post_label(parent),
                        "excerpt": _excerpt(post.body),
                        "by": _org_name(db, post.org_author_id) if by_org else _handle(db, post.ben_author_id),
                        "by_org": by_org})


def on_post_versioned(db: Session, post: models.Post) -> Optional[models.Event]:
    """Everyone who cites this post at an older version hears it changed."""
    rows = db.execute(select(models.PostRef.ref_version, models.Post.ben_author_id, models.Post.id)
                      .join(models.Post, models.Post.id == models.PostRef.post_id)
                      .where(models.PostRef.ref_post_id == post.id)).all()
    who: dict[int, dict] = {}
    for ver, author, citing in rows:
        if author and author != post.ben_author_id and (ver or 0) < post.version:
            who.setdefault(author, {"cited_version": ver, "citing_post_id": citing})
    if not who:
        return None
    return record(db, "cited_update", who, actor_ben_id=post.ben_author_id, post_id=post.id,
                  mission_id=post.mission_id, dedupe=f"cited_update:{post.id}:{post.version}",
                  data={"label": _post_label(post), "version": post.version})


def helpful_votes(db: Session, post_id: str) -> int:
    return db.scalar(select(sqlfunc.count()).select_from(models.PostVote).where(
        models.PostVote.post_id == post_id, models.PostVote.value == "helpful")) or 0


def on_reaction(db: Session, post: models.Post, actor_id: Optional[int]) -> Optional[models.Event]:
    """A like threshold — the first vote, then 5, 10, 25 … — once each."""
    if not post.ben_author_id or post.ben_author_id == actor_id:
        return None
    n = helpful_votes(db, post.id)
    if n not in REACTION_THRESHOLDS:
        return None
    word = pcfg.reaction_label(post.type, "helpful") if post.type else "Upvote"
    return record(db, "reaction", [post.ben_author_id], actor_ben_id=actor_id, post_id=post.id,
                  mission_id=post.mission_id, dedupe=f"reaction:{post.id}:{n}",
                  data={"count": n, "label": _post_label(post), "word": word})


# ── hooks: organizations ────────────────────────────────────────────────────
def watchers_of(db: Session, tiv_id: str) -> set[int]:
    out = set()
    for bid, raw in db.execute(select(models.BenefactorAccount.id, models.BenefactorAccount.watched_tiv_ids)
                               .where(models.BenefactorAccount.watched_tiv_ids.like(f'%"{tiv_id}"%'))).all():
        try:
            if tiv_id in (json.loads(raw or "[]") or []):
                out.add(bid)
        except (TypeError, ValueError):
            pass
    return out


def on_org_nominated(db: Session, *, org_id: Optional[str], tiv_id: Optional[str] = None,
                     mission_id: Optional[str] = None, how: str = "nominated",
                     actor_ben_id: Optional[int] = None,
                     actor_org_id: Optional[str] = None) -> Optional[models.Event]:
    """An organization suggested for / running for an initiative: its proposer
    and everyone watching it hear about it, once per organization."""
    if not org_id:
        return None
    if not tiv_id and mission_id:
        m = db.get(models.Mission, mission_id)
        tiv_id = m.winning_tiv_id if m else None
    tiv = db.get(models.Initiative, tiv_id) if tiv_id else None
    if tiv is None:
        return None
    who = watchers_of(db, tiv.id)
    if tiv.proposer_ben_id:
        who.add(tiv.proposer_ben_id)
    if not who:
        return None
    return record(db, "org_nominated", who, actor_ben_id=actor_ben_id, actor_org_id=actor_org_id,
                  mission_id=mission_id or tiv.mission_id, tiv_id=tiv.id, org_id=org_id,
                  dedupe=f"org_nominated:{org_id}:{tiv.id}",
                  data={"org": _org_name(db, org_id), "initiative": tiv.title, "how": how})


# ── hooks: elections (read who voted, before the close moves anything) ──────
def p1_voters(db: Session, mission_id: str) -> dict[int, set]:
    out: dict[int, set] = {}
    for ben, tiv in db.execute(select(models.VoteP1.ben_id, models.VoteP1.tiv_id).where(
            models.VoteP1.mission_id == mission_id)).all():
        out.setdefault(ben, set()).add(tiv)
    return out


def p2_voters(db: Session, mission_id: str) -> dict[int, Optional[str]]:
    return {ben: org for ben, org in db.execute(select(models.VoteP2.ben_id, models.VoteP2.org_id).where(
        models.VoteP2.mission_id == mission_id)).all()}


def on_tiv_elected(db: Session, mission_id: str, winner_id: str, voters: dict) -> Optional[models.Event]:
    from .posting import oe_close
    m = db.get(models.Mission, mission_id)
    tiv = db.get(models.Initiative, winner_id)
    if m is None or tiv is None:
        return None
    who = {b: {"outcome": "won" if winner_id in tivs else "lost"} for b, tivs in voters.items()}
    if tiv.proposer_ben_id:
        who.setdefault(tiv.proposer_ben_id, {"outcome": "proposed"})
    return record(db, "tiv_elected", who, mission_id=m.id, tiv_id=tiv.id,
                  dedupe=f"tiv_elected:{m.id}",
                  data={"initiative": tiv.title, "cause": m.cause_id, "mission": _mission_label(db, m.id),
                        "next": {"label": "Organization election closes", "date": _iso(oe_close(m))}})


def on_org_elected(db: Session, mission_id: str, winner_org: str, voters: dict) -> Optional[models.Event]:
    from .posting import budget_day
    m = db.get(models.Mission, mission_id)
    if m is None:
        return None
    who = {b: {"outcome": "followed" if not org else ("won" if org == winner_org else "lost")}
           for b, org in voters.items()}
    return record(db, "org_elected", who, mission_id=m.id, org_id=winner_org, tiv_id=m.winning_tiv_id,
                  dedupe=f"org_elected:{m.id}",
                  data={"org": _org_name(db, winner_org), "mission": _mission_label(db, m.id),
                        "next": {"label": "Budget day (framing ends)", "date": _iso(budget_day(m))}})


# ── reading the inbox ───────────────────────────────────────────────────────
def describe(db: Session, ev: models.Event, detail: Optional[dict]) -> dict:
    """The words for one notification — written here so every page that lists
    them says the same thing."""
    d, det = ev.data or {}, detail or {}
    k = ev.kind
    title, body, link = KINDS.get(k, k), "", None
    if k == "reply":
        title = f"{d.get('by') or 'Someone'} replied to “{d.get('parent_label')}”"
        body = d.get("excerpt", "")
        link = {"post": d.get("parent_id")}
    elif k == "reaction":
        n = d.get("count", 0)
        title = (f"Your post got its first vote" if n == 1 else f"Your post reached {n} votes")
        body = f"“{d.get('label')}”"
        link = {"post": ev.post_id}
    elif k == "cited_update":
        title = f"A post you cite has a new version (now v{d.get('version')})"
        body = f"“{d.get('label')}” — you cited v{det.get('cited_version') or 1}."
        link = {"post": ev.post_id}
    elif k == "org_nominated":
        verb = {"suggested": "suggested itself for", "running": "is running for"}.get(d.get("how"), "was nominated for")
        title = f"{d.get('org')} {verb} {d.get('initiative')}"
        body = "An initiative you proposed or watch has a new organization in its corner."
        link = {"org": ev.org_id, "mission": ev.mission_id}
    elif k == "tiv_elected":
        out = det.get("outcome")
        title = f"{d.get('initiative')} won the initiative election"
        body = {"won": "Your vote won. ",
                "lost": "Your pick did not win — your stake carries into this mission's organization election. ",
                "proposed": "You proposed it. "}.get(out, "")
        nx = d.get("next") or {}
        body += f"Next: {nx.get('label')}" + (f" on {nx['date'][:10]}." if nx.get("date") else ".")
        link = {"mission": ev.mission_id}
    elif k == "org_elected":
        out = det.get("outcome")
        title = f"{d.get('org')} will run {d.get('mission')}"
        body = {"won": "Your vote won. ",
                "lost": "Your organization did not win — you can exchange into another mission during framing. ",
                "followed": "Your stake had no organization named, so it followed the winner. "}.get(out, "")
        nx = d.get("next") or {}
        body += f"Next: {nx.get('label')}" + (f" on {nx['date'][:10]}." if nx.get("date") else ".")
        link = {"mission": ev.mission_id}
    elif k == "weekly_update":
        title = f"Your weekly update — week {ev.week}"
        body = d.get("headline", "")
        link = {"weekly": ev.week}
    return {"title": title, "body": body, "link": link}


def notification_dict(db: Session, n: models.Notification) -> dict:
    ev = n.event
    out = {"id": n.id, "kind": ev.kind, "event_id": ev.id, "created_at": _iso(ev.created_at),
           "read": n.read_at is not None, "detail": n.detail or {}, "post_id": ev.post_id,
           "mission_id": ev.mission_id, "org_id": ev.org_id, "tiv_id": ev.tiv_id, "week": ev.week}
    out.update(describe(db, ev, n.detail))
    return out


def list_notifications(db: Session, ben_id: int, *, limit: int = 50, before: Optional[int] = None,
                       unread_only: bool = False, kind: Optional[str] = None) -> list[dict]:
    q = (select(models.Notification).join(models.Event)
         .where(models.Notification.ben_id == ben_id)
         .order_by(models.Notification.id.desc()).limit(max(1, min(limit, 200))))
    if before:
        q = q.where(models.Notification.id < before)
    if unread_only:
        q = q.where(models.Notification.read_at.is_(None))
    if kind:
        q = q.where(models.Event.kind == kind)
    return [notification_dict(db, n) for n in db.scalars(q).all()]


def mark_read(db: Session, ben_id: int, ids: Optional[Iterable[int]] = None) -> int:
    q = select(models.Notification).where(models.Notification.ben_id == ben_id,
                                          models.Notification.read_at.is_(None))
    if ids is not None:
        ids = [int(i) for i in ids]
        if not ids:
            return 0
        q = q.where(models.Notification.id.in_(ids))
    rows = db.scalars(q).all()
    now = datetime.utcnow()
    for n in rows:
        n.read_at = now
    db.commit()
    return len(rows)


def summary(db: Session, ben_id: int) -> dict:
    unread = db.scalar(select(sqlfunc.count()).select_from(models.Notification).where(
        models.Notification.ben_id == ben_id, models.Notification.read_at.is_(None))) or 0
    return {"unread_notifications": unread, "unread_threads": unread_threads(db, ben_id)}


# ── the weekly update ───────────────────────────────────────────────────────
def _in(d: datetime, start: datetime, end: datetime) -> bool:
    return start <= d < end


def assemble_weekly(db: Session, week: int, now: Optional[datetime] = None) -> dict:
    """The edition for `week` (the week that has just ended), from the mission
    clock and the event log. The same edition is Home's most recent one and
    News's; YOUR part is added when it is read (`personal`)."""
    from . import posting
    now = now or datetime.utcnow()
    start, end = week_bounds(week)
    labels = posting.mission_labels(db, [m.id for m in db.scalars(select(models.Mission)).all()])
    causes = {c.id: c.name for c in db.scalars(select(models.Cause)).all()}

    def post_ref(pid):
        p = db.get(models.Post, pid) if pid else None
        return {"id": p.id, "title": _post_label(p), "author": _handle(db, p.ben_author_id)} if p else None

    new_tivs, new_orgs, exchange, prep, upcoming = [], [], [], [], []
    for m in db.scalars(select(models.Mission).where(models.Mission.started_at.isnot(None))).all():
        base = {"mission_id": m.id, "mission": labels.get(m.id, m.id), "cause": causes.get(m.cause_id, m.cause_id)}
        me, oe, bd = posting.me_close(m), posting.oe_close(m), posting.budget_day(m)
        if _in(me, start, end) and m.winning_tiv_id:
            lead = posting.leads(db, m, max(now, me))
            tiv = db.get(models.Initiative, m.winning_tiv_id)
            new_tivs.append(dict(base, initiative=tiv.title if tiv else m.winning_tiv_id,
                                 winning_post=post_ref(lead.get("background_id")),
                                 post_kind="Background"))
        if _in(oe, start, end) and m.winning_org_id:
            lead = posting.leads(db, m, max(now, oe))
            new_orgs.append(dict(base, org=_org_name(db, m.winning_org_id), org_id=m.winning_org_id,
                                 winning_post=post_ref(lead.get("investigation_id")),
                                 post_kind="Investigation"))
        if _in(bd, start, end):
            best = db.scalars(select(models.Post).where(
                models.Post.type == pcfg.ANALYSIS, models.Post.mission_id == m.id,
                models.Post.parent_id.is_(None)).order_by(models.Post.helpful_count.desc())).first()
            pool = db.get(models.Pool, m.id)
            exchange.append(dict(base, org=_org_name(db, m.winning_org_id),
                                 winning_post=post_ref(best.id) if best else None, post_kind="Analysis",
                                 tokens_released=round(float(getattr(pool, "total_locked", 0) or 0), 2) if pool else None,
                                 research_prize="Paid with P5 (D22) — the winning Analysis's author will be paid "
                                                "the research share."))
        if oe <= end < bd and m.winning_org_id:
            items = db.scalar(select(sqlfunc.count()).select_from(models.Post).where(
                models.Post.category == "budgeting", models.Post.parent_id.is_(None),
                or_(models.Post.mission_id == m.id,
                    models.Post.tiv_id == (m.winning_tiv_id or "")))) or 0
            prep.append(dict(base, org=_org_name(db, m.winning_org_id), budget_day=_iso(bd),
                             days_to_budget=max(0, (bd - end).days), budget_items=items))
        nxt_end = end + WEEK
        for label, when, pending in (("Initiative election closes", me, not m.winning_tiv_id),
                                     ("Organization election closes", oe, not m.winning_org_id),
                                     ("Budget day", bd, True)):
            if pending and _in(when, end, nxt_end):
                upcoming.append(dict(base, what=label, date=_iso(when)))
    counts = dict(db.execute(select(models.Event.kind, sqlfunc.count(models.Event.id)).where(
        models.Event.created_at >= start, models.Event.created_at < end,
        models.Event.kind != "weekly_update").group_by(models.Event.kind)).all())
    posts = db.scalar(select(sqlfunc.count()).select_from(models.Post).where(
        models.Post.created_at >= start, models.Post.created_at < end)) or 0
    bits = []
    if new_tivs:
        bits.append("new initiative" + ("s" if len(new_tivs) > 1 else "") + ": " +
                    ", ".join(x["initiative"] for x in new_tivs))
    if new_orgs:
        bits.append("elected: " + ", ".join(x["org"] or "?" for x in new_orgs))
    if exchange:
        bits.append("entered exchange: " + ", ".join(x["mission"] for x in exchange))
    headline = "; ".join(bits) or "A quiet week — the elections are still open."
    return {"week": week, "starts": _iso(start), "ends": _iso(end), "headline": headline[:1].upper() + headline[1:],
            "new_initiatives": new_tivs, "new_organizations": new_orgs, "entered_exchange": exchange,
            "prep": prep, "next_week": sorted(upcoming, key=lambda x: x["date"]),
            "activity": {"posts": posts, "events": counts}}


def published_week(db: Session, week: int) -> Optional[models.Event]:
    return db.scalar(select(models.Event).where(models.Event.dedupe == f"weekly:{week}"))


def publish_weekly(db: Session, week: int, now: Optional[datetime] = None) -> Optional[models.Event]:
    """Publish `week`'s edition once, to every active (non-test) benefactor."""
    if published_week(db, week) is not None:
        return None
    edition = assemble_weekly(db, week, now)
    who = [i for (i,) in db.execute(select(models.BenefactorAccount.id).where(
        models.BenefactorAccount.is_active.is_(True), models.BenefactorAccount.is_test.is_(False))).all()]
    return record(db, "weekly_update", who, week=week, dedupe=f"weekly:{week}", data=edition)


def publish_due(db: Session, now: Optional[datetime] = None) -> Optional[models.Event]:
    """The scheduler's call: the last finished week's edition, if not out yet."""
    now = now or datetime.utcnow()
    w = week_of(now) - 1
    if now < GENESIS + WEEK or w < 0:
        return None
    return publish_weekly(db, w, now)


def latest_weekly(db: Session) -> Optional[models.Event]:
    return db.scalars(select(models.Event).where(models.Event.kind == "weekly_update")
                      .order_by(models.Event.week.desc(), models.Event.id.desc())).first()


def personal(db: Session, ben_id: int, week: int) -> dict:
    """YOUR part of the weekly update — what happened to you that week."""
    start, end = week_bounds(week)
    rows = db.execute(select(models.Event.kind, models.Notification.detail, models.Event.data)
                      .join(models.Event, models.Event.id == models.Notification.event_id)
                      .where(models.Notification.ben_id == ben_id, models.Event.kind != "weekly_update",
                             models.Event.created_at >= start, models.Event.created_at < end)).all()
    counts: dict[str, int] = {}
    results = []
    for kind, det, data in rows:
        counts[kind] = counts.get(kind, 0) + 1
        if kind in ("tiv_elected", "org_elected"):
            results.append({"kind": kind, "outcome": (det or {}).get("outcome"),
                            "what": (data or {}).get("initiative") or (data or {}).get("org"),
                            "mission": (data or {}).get("mission")})
    posts = db.scalar(select(sqlfunc.count()).select_from(models.Post).where(
        models.Post.ben_author_id == ben_id, models.Post.created_at >= start,
        models.Post.created_at < end)) or 0
    return {"counts": counts, "results": results, "posts_written": posts,
            "missions": sorted(mission_ids_of(db, ben_id))}


def weekly_dict(db: Session, ev: models.Event, ben_id: Optional[int] = None) -> dict:
    out = dict(ev.data or {})
    out["published_at"] = _iso(ev.created_at)
    if ben_id:
        out["you"] = personal(db, ben_id, ev.week)
    return out


# ── messages (D10) ──────────────────────────────────────────────────────────
def mission_ids_of(db: Session, ben_id: int) -> set[str]:
    a = {m for (m,) in db.execute(select(models.VoteP1.mission_id).where(models.VoteP1.ben_id == ben_id)).all()}
    b = {m for (m,) in db.execute(select(models.VoteP2.mission_id).where(models.VoteP2.ben_id == ben_id)).all()}
    return {x for x in a | b if x}


def members_of(db: Session, mission_ids: Iterable[str]) -> dict[int, set]:
    ids = list(set(mission_ids))
    out: dict[int, set] = {}
    if not ids:
        return out
    for M in (models.VoteP1, models.VoteP2):
        for ben, mid in db.execute(select(M.ben_id, M.mission_id).where(M.mission_id.in_(ids))).all():
            out.setdefault(ben, set()).add(mid)
    return out


def people(db: Session, me: models.BenefactorAccount, q: Optional[str] = None,
           mission_id: Optional[str] = None, limit: int = 20) -> list[dict]:
    """Members of the missions I am in, to start a thread with."""
    mine = mission_ids_of(db, me.id)
    if mission_id:
        mine &= {mission_id}
    mem = members_of(db, mine)
    mem.pop(me.id, None)
    if not mem:
        return []
    qq = select(models.BenefactorAccount).where(models.BenefactorAccount.id.in_(list(mem)),
                                                models.BenefactorAccount.is_active.is_(True))
    if q:
        qq = qq.where(models.BenefactorAccount.handle.ilike(f"%{q.strip()}%"))
    rows = db.scalars(qq.order_by(models.BenefactorAccount.handle).limit(limit)).all()
    labels = _labels(db, {m for s in mem.values() for m in s})
    return [{"id": b.id, "handle": b.handle,
             "missions": [{"id": m, "label": labels.get(m, m)} for m in sorted(mem[b.id])]} for b in rows]


def _labels(db: Session, ids) -> dict:
    from .posting import mission_labels
    return mission_labels(db, ids)


def _pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def _side(t: models.MessageThread, me_id: int) -> str:
    return "a" if t.a_id == me_id else "b"


def _thread_or_refuse(db: Session, me_id: int, thread_id: int) -> models.MessageThread:
    t = db.get(models.MessageThread, thread_id)
    if t is None or me_id not in (t.a_id, t.b_id):
        raise LookupError("Thread not found")
    return t


def _unread(t: models.MessageThread, me_id: int) -> bool:
    seen = t.a_read_at if _side(t, me_id) == "a" else t.b_read_at
    return bool(t.last_message_at and (seen is None or seen < t.last_message_at))


def unread_threads(db: Session, ben_id: int) -> int:
    rows = db.scalars(select(models.MessageThread).where(
        or_(models.MessageThread.a_id == ben_id, models.MessageThread.b_id == ben_id))).all()
    n = 0
    for t in rows:
        if not _unread(t, ben_id):
            continue
        last = db.scalars(select(models.Message).where(models.Message.thread_id == t.id)
                          .order_by(models.Message.id.desc())).first()
        if last is not None and last.sender_id != ben_id:
            n += 1
    return n


def thread_dict(db: Session, t: models.MessageThread, me_id: int, labels: Optional[dict] = None) -> dict:
    other_id = t.b_id if t.a_id == me_id else t.a_id
    last = db.scalars(select(models.Message).where(models.Message.thread_id == t.id)
                      .order_by(models.Message.id.desc())).first()
    labels = labels if labels is not None else _labels(db, [t.mission_id] if t.mission_id else [])
    return {"id": t.id, "other": {"id": other_id, "handle": _handle(db, other_id) or "removed account"},
            "mission_id": t.mission_id, "mission": labels.get(t.mission_id) if t.mission_id else None,
            "last": ({"body": _excerpt(last.body, 90) if not last.hidden else "(hidden)",
                      "mine": last.sender_id == me_id, "at": _iso(last.created_at)} if last else None),
            "unread": _unread(t, me_id) and bool(last and last.sender_id != me_id),
            "last_message_at": _iso(t.last_message_at or t.created_at)}


def list_threads(db: Session, me_id: int, q: Optional[str] = None) -> list[dict]:
    """My threads, newest first — searchable by name or by mission (D10)."""
    rows = db.scalars(select(models.MessageThread).where(
        or_(models.MessageThread.a_id == me_id, models.MessageThread.b_id == me_id))).all()
    labels = _labels(db, {t.mission_id for t in rows if t.mission_id})
    out = [thread_dict(db, t, me_id, labels) for t in rows]
    if q:
        s = q.strip().lower()
        out = [x for x in out if s in (x["other"]["handle"] or "").lower()
               or s in (x["mission"] or "").lower() or s in (x["mission_id"] or "").lower()]
    out.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
    return out


def open_thread(db: Session, me: models.BenefactorAccount, other_id: int,
                mission_id: Optional[str] = None) -> dict:
    """Start (or reopen) the thread with another member of a mission I am in."""
    if other_id == me.id:
        raise ValueError("You cannot message yourself")
    other = db.get(models.BenefactorAccount, other_id)
    if other is None or not other.is_active:
        raise LookupError("That person was not found")
    a, b = _pair(me.id, other_id)
    t = db.scalar(select(models.MessageThread).where(models.MessageThread.a_id == a,
                                                     models.MessageThread.b_id == b))
    if t is None:
        shared = mission_ids_of(db, me.id) & mission_ids_of(db, other_id)
        if not shared:
            raise PermissionError("Messages are between members of the same mission — "
                                  "you and this person do not share one yet")
        if mission_id and mission_id not in shared:
            raise PermissionError("You are not both members of that mission")
        t = models.MessageThread(a_id=a, b_id=b, mission_id=mission_id or sorted(shared)[-1])
        db.add(t)
        db.commit()
    return thread_dict(db, t, me.id)


def read_thread(db: Session, me_id: int, thread_id: int) -> dict:
    t = _thread_or_refuse(db, me_id, thread_id)
    msgs = db.scalars(select(models.Message).where(models.Message.thread_id == t.id)
                      .order_by(models.Message.id)).all()
    now = datetime.utcnow()
    if _side(t, me_id) == "a":
        t.a_read_at = now
    else:
        t.b_read_at = now
    db.commit()
    out = thread_dict(db, t, me_id)
    out["messages"] = [{"id": m.id, "mine": m.sender_id == me_id, "at": _iso(m.created_at),
                        "body": m.body if not m.hidden else "(hidden by Earthbux staff)",
                        "hidden": m.hidden} for m in msgs]
    out["rule"] = MESSAGE_RULE
    return out


def send(db: Session, me_id: int, thread_id: int, body: str) -> dict:
    t = _thread_or_refuse(db, me_id, thread_id)
    text = (body or "").strip()
    if not text:
        raise ValueError("Write something first")
    if len(text) > MESSAGE_MAX:
        raise ValueError(f"A message is at most {MESSAGE_MAX} characters")
    m = models.Message(thread_id=t.id, sender_id=me_id, body=text)
    db.add(m)
    now = datetime.utcnow()
    t.last_message_at = now
    if _side(t, me_id) == "a":
        t.a_read_at = now
    else:
        t.b_read_at = now
    db.commit()
    return {"id": m.id, "mine": True, "at": _iso(m.created_at or now), "body": m.body, "hidden": False}


def report(db: Session, me_id: int, message_id: int, reason: Optional[str]) -> dict:
    m = db.get(models.Message, message_id)
    if m is None:
        raise LookupError("Message not found")
    _thread_or_refuse(db, me_id, m.thread_id)
    if m.sender_id == me_id:
        raise ValueError("You cannot report your own message")
    r = models.MessageReport(message_id=m.id, reporter_id=me_id, reason=(reason or "").strip()[:1000] or None)
    db.add(r)
    db.flush()
    record(db, "message_report", None, actor_ben_id=me_id, commit=False,
           data={"report_id": r.id, "message_id": m.id, "thread_id": m.thread_id})
    db.commit()
    return {"report_id": r.id, "status": r.status}


def list_reports(db: Session, status: Optional[str] = "open") -> list[dict]:
    q = select(models.MessageReport).order_by(models.MessageReport.id.desc())
    if status:
        q = q.where(models.MessageReport.status == status)
    out = []
    for r in db.scalars(q).all():
        m = db.get(models.Message, r.message_id)
        out.append({"id": r.id, "status": r.status, "reason": r.reason, "created_at": _iso(r.created_at),
                    "reporter": _handle(db, r.reporter_id),
                    "message": {"id": m.id, "body": m.body, "hidden": m.hidden,
                                "sender": _handle(db, m.sender_id), "thread_id": m.thread_id} if m else None})
    return out


def resolve_report(db: Session, report_id: int, uphold: bool) -> dict:
    r = db.get(models.MessageReport, report_id)
    if r is None:
        raise LookupError("Report not found")
    r.status = "upheld" if uphold else "dismissed"
    if uphold:
        m = db.get(models.Message, r.message_id)
        if m is not None:
            m.hidden = True
    db.commit()
    return {"id": r.id, "status": r.status}


# ── account removal ─────────────────────────────────────────────────────────
def forget_benefactor(db: Session, ben_id: int) -> None:
    """Called by `crud.remove_account` before the row goes: their inbox goes
    with them; events they caused stay in the log, unattributed."""
    for n in db.scalars(select(models.Notification).where(models.Notification.ben_id == ben_id)).all():
        db.delete(n)
    for e in db.scalars(select(models.Event).where(models.Event.actor_ben_id == ben_id)).all():
        e.actor_ben_id = None
    threads = db.scalars(select(models.MessageThread).where(
        or_(models.MessageThread.a_id == ben_id, models.MessageThread.b_id == ben_id))).all()
    tids = [t.id for t in threads]
    if tids:
        mids = [m for (m,) in db.execute(select(models.Message.id).where(models.Message.thread_id.in_(tids))).all()]
        if mids:
            for r in db.scalars(select(models.MessageReport).where(models.MessageReport.message_id.in_(mids))).all():
                db.delete(r)
        for m in db.scalars(select(models.Message).where(models.Message.thread_id.in_(tids))).all():
            db.delete(m)
        db.flush()
        for t in threads:
            db.delete(t)
    for r in db.scalars(select(models.MessageReport).where(models.MessageReport.reporter_id == ben_id)).all():
        db.delete(r)
    db.flush()
