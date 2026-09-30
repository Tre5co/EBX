"""P3 · Posting — one way to make a post, and every post displayable anywhere.

INSTRUCTIONS › P3 · Posting is the spec (D8, D19–D21 answered 2026-09-28);
`post_config.py` is the taxonomy and each type's guide. This module is the
rules those two describe:

* **Targets.** Research and budget posts need one, a general post may have one
  (cause · initiative · organization · mission · post · budget item). The FK
  columns stay filled for the kinds that have one, so every old filter works.
* **Limits.** Background: one per person per cause. Investigation: one per
  person per organization. Analysis: one per person per mission. Budget: one
  OPEN item per type per person per initiative. General: none. No membership
  gate on any of them — "everyone can post, everyone can reply".
* **Versions (D21).** Every edit is a new version. A mission keeps the version
  that stood when its election for that type closed (`post_missions.
  pinned_version`) — computed from the version timestamps, so it is the same
  answer whenever it is asked.
* **Missions (D19).** A Background lives: it is electable in its cause's open
  initiative election, and once that election closes it ROLLS into the cause's
  next mission, keeping the closed mission's version there. An Investigation
  belongs to every organization race its organization stands in. Any author can
  PULL an old post into a new mission.
* **Votes count per mission (D21).** A vote is scoped to the mission it was cast
  in; a post rolled, pulled or cited into a new mission starts from zero there.
* **Leads (D20).** The most-voted Background at T and the most-voted
  Investigation on any of the mission's candidate organizations at T+8 are
  fixed once, and every Analysis of the mission carries both.

Nothing here moves money. The research payout that reads these tables is P5
(D22).
"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy import func as sqlfunc, or_, select
from sqlalchemy.orm import Session

from . import models, post_config as pcfg
from .bootstrap import GENESIS, WEEK

# ---------------------------------------------------------------------------
# The mission clock, as the posting rules read it (mission_model.md §1):
# the mission opens at `started_at`; T (initiative election closes) is 7 weeks
# later; T+8 the organization election; T+15 budget day.
# ---------------------------------------------------------------------------


def _start(m: models.Mission) -> datetime:
    return m.started_at or GENESIS


def me_close(m: models.Mission) -> datetime:
    return _start(m) + 7 * WEEK


def oe_close(m: models.Mission) -> datetime:
    return _start(m) + 15 * WEEK


def budget_day(m: models.Mission) -> datetime:
    return _start(m) + 22 * WEEK


_CLOSE = {"me_close": me_close, "oe_close": oe_close, "budget_day": budget_day}


def pin_time(post_type: Optional[str], m: models.Mission) -> Optional[datetime]:
    """When `m` fixes the version of a post of this type, or None."""
    t = pcfg.TYPES.get(post_type or "")
    fn = _CLOSE.get(t.pins_at) if t and t.pins_at else None
    return fn(m) if fn else None


def _now(now: Optional[datetime]) -> datetime:
    return now or datetime.utcnow()


def _naive(d: Optional[datetime]) -> Optional[datetime]:
    if d is not None and d.tzinfo is not None:
        return d.replace(tzinfo=None)
    return d


def open_initiative_mission(db: Session, cause_id: str,
                            now: Optional[datetime] = None) -> Optional[models.Mission]:
    """The mission of `cause_id` whose initiative election is open now — the one
    a new Background is electable in. Falls back to the cause's newest mission
    when none is open (a cause between rotations)."""
    now = _now(now)
    rows = db.scalars(select(models.Mission).where(models.Mission.cause_id == cause_id)).all()
    open_ = [m for m in rows if not m.winning_tiv_id and me_close(m) > now]
    if open_:
        return min(open_, key=me_close)
    return max(rows, key=lambda m: m.cycle_num) if rows else None


def open_org_races(db: Session, org_id: str,
                   now: Optional[datetime] = None) -> list[models.Mission]:
    """The missions whose organization election has `org_id` standing in it and
    has not closed, soonest first."""
    now = _now(now)
    mids = [c.mission_id for c in db.scalars(
        select(models.MissionCandidacy).where(models.MissionCandidacy.org_id == org_id)).all()]
    ms = [db.get(models.Mission, mid) for mid in set(mids)]
    ms = [m for m in ms if m is not None and not m.winning_org_id and oe_close(m) > now]
    return sorted(ms, key=oe_close)


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------
class Refusal(ValueError):
    """A posting rule said no. Always a 400 (a PermissionError is a 403)."""


def _mission_of_tiv(db: Session, tiv_id: Optional[str]) -> Optional[str]:
    if not tiv_id:
        return None
    tiv = db.get(models.Initiative, tiv_id)
    return tiv.mission_id if tiv is not None else None


def _fill_target(db: Session, post: models.Post, kind: Optional[str], tid: Optional[str]) -> None:
    """Record the target and fill the FK column(s) it implies."""
    if kind in (None, "", "none"):
        post.target_kind, post.target_id = "none", None
        return
    if kind not in pcfg.TARGET_KINDS:
        raise Refusal(f"unknown target kind '{kind}' (expected one of {', '.join(pcfg.TARGET_KINDS)})")
    if not tid:
        raise Refusal(f"a {kind} target needs its id")
    if kind == "cause":
        if db.get(models.Cause, tid) is None:
            raise Refusal(f"cause '{tid}' not found")
        post.cause_id = tid
    elif kind == "initiative":
        tiv = db.get(models.Initiative, tid)
        if tiv is None:
            raise Refusal(f"initiative '{tid}' not found")
        post.tiv_id = tid
        post.mission_id = post.mission_id or tiv.mission_id
        if tiv.mission_id and not post.cause_id:
            m = db.get(models.Mission, tiv.mission_id)
            post.cause_id = m.cause_id if m else None
    elif kind == "organization":
        if db.get(models.Organization, tid) is None:
            raise Refusal(f"organization '{tid}' not found")
        post.org_id = tid
    elif kind == "mission":
        m = db.get(models.Mission, tid)
        if m is None:
            raise Refusal(f"mission '{tid}' not found")
        post.mission_id = tid
        post.cause_id = post.cause_id or m.cause_id
    elif kind in ("post", "budget"):
        other = db.get(models.Post, tid)
        if other is None:
            raise Refusal(f"post '{tid}' not found")
        if kind == "budget" and other.category not in ("budgeting", "resolution"):
            raise Refusal("that post is not a budget item")
        post.mission_id = post.mission_id or other.mission_id
        post.cause_id = post.cause_id or other.cause_id
    post.target_kind, post.target_id = kind, tid


# ---------------------------------------------------------------------------
# Creating
# ---------------------------------------------------------------------------
def _one_per(db: Session, author_id: int, post_type: str, **where) -> Optional[models.Post]:
    stmt = select(models.Post).where(
        models.Post.ben_author_id == author_id,
        models.Post.type == post_type,
        models.Post.parent_id.is_(None),
    )
    for col, val in where.items():
        stmt = stmt.where(getattr(models.Post, col) == val)
    return db.scalar(stmt.limit(1))


def prepare_new(db: Session, post: models.Post, *, target_kind: Optional[str],
                target_id: Optional[str], tags, references,
                author: Optional[models.BenefactorAccount],
                now: Optional[datetime] = None) -> list[dict]:
    """Apply P3's rules to a new, unsaved benefactor post. Returns the
    references to write once it is saved (`attach_refs`)."""
    now = _now(now)
    cat, typ, legacy_tag = pcfg.normalize_legacy(post.category, post.type)
    post.category, post.type = cat, typ
    tags = pcfg.clean_tags(tags)
    if legacy_tag and legacy_tag not in tags:
        tags.insert(0, legacy_tag)

    # ── replies: anyone, anything, no limit ───────────────────────────────
    if post.parent_id:
        parent = db.get(models.Post, post.parent_id)
        if parent is None:
            raise Refusal("the post you are replying to was not found")
        # A reply takes its parent's lane, as it always has, so every thread
        # reader that groups by category keeps working.
        # (A reply to an editorial or an org update is a general reply.)
        post.category = parent.category if parent.category in pcfg.CATEGORIES else "general"
        post.type = parent.type if (parent.type in pcfg.TYPES and post.category != "general") else "general"
        post.mission_id = post.mission_id or parent.mission_id
        post.cause_id = post.cause_id or parent.cause_id
        post.target_kind, post.target_id = "post", parent.id
        post.tags = tags or None
        return []

    t = pcfg.TYPES.get(typ)
    if t is None or t.category != cat:
        raise Refusal(
            f"'{typ}' is not a type of '{cat}' — the types are: "
            + "; ".join(f"{c.label}: {', '.join(pcfg.TYPES[k].label for k in c.type_keys)}"
                        for c in pcfg.CATEGORIES.values()))
    if author is None:
        raise PermissionError("posting needs a signed-in account")

    # ── the target, per type ──────────────────────────────────────────────
    if typ == pcfg.BACKGROUND:
        cause_id = target_id if target_kind == "cause" else post.cause_id
        if not cause_id and post.mission_id:
            m = db.get(models.Mission, post.mission_id)
            cause_id = m.cause_id if m else None
        if not cause_id and post.tiv_id:
            m = db.get(models.Mission, _mission_of_tiv(db, post.tiv_id) or "")
            cause_id = m.cause_id if m else None
        if not cause_id:
            raise Refusal("a Background is about a cause — name it (target_kind='cause')")
        post.mission_id = None
        _fill_target(db, post, "cause", cause_id)
        # The initiatives it covers are tags (D19) — kept only if they are real.
        if post.tiv_id and ("tiv:" + post.tiv_id) not in tags:
            tags.append("tiv:" + post.tiv_id)
        post.tiv_id = None
        m = open_initiative_mission(db, cause_id, now)
        post.mission_id = m.id if m else None
        dup = _one_per(db, author.id, typ, cause_id=cause_id)
        if dup is not None:
            raise Refusal("you already have a Background for this cause — edit it (every edit is a "
                          "new version), or reply to add more (one Background per person per cause)")

    elif typ == pcfg.INVESTIGATION:
        org_id = target_id if target_kind == "organization" else post.org_id
        if not org_id:
            raise Refusal("an Investigation must name the organization it investigates (org_id)")
        mission_hint = post.mission_id
        _fill_target(db, post, "organization", org_id)
        races = open_org_races(db, org_id, now)
        hinted = next((m for m in races if m.id == mission_hint), None)
        # Its votes count in the race it is read in: the one it was written
        # from if the organization stands there, else the soonest open race.
        home = hinted or (races[0] if races else None)
        post.mission_id = home.id if home is not None else mission_hint
        dup = _one_per(db, author.id, typ, org_id=org_id)
        if dup is not None:
            raise Refusal("you already have an Investigation of this organization — edit it, or reply "
                          "to add more (one Investigation per person per organization)")

    elif typ == pcfg.ANALYSIS:
        mid = target_id if target_kind == "mission" else post.mission_id
        m = db.get(models.Mission, mid) if mid else None
        if m is None:
            raise Refusal("an Analysis is about a mission — name it (target_kind='mission')")
        if not m.winning_org_id and now < oe_close(m):
            raise Refusal("Analyses open when the organization election closes "
                          f"({oe_close(m):%b %d}) — until then, write a Background or an Investigation")
        if now >= budget_day(m):
            raise Refusal(f"this mission's Analysis was elected on budget day ({budget_day(m):%b %d}) — "
                          "it is closed")
        _fill_target(db, post, "mission", m.id)
        post.tiv_id = post.tiv_id or m.winning_tiv_id
        dup = _one_per(db, author.id, typ, mission_id=m.id)
        if dup is not None:
            raise Refusal("you already have an Analysis for this mission — edit it (one per person per mission)")

    elif typ in pcfg.BUDGET_TYPES:
        tiv_id = target_id if target_kind == "initiative" else post.tiv_id
        if not tiv_id and post.mission_id:
            m = db.get(models.Mission, post.mission_id)
            tiv_id = m.winning_tiv_id if m else None
        if not tiv_id:
            raise Refusal("a budget item is for an initiative — name it (target_kind='initiative')")
        _fill_target(db, post, "initiative", tiv_id)
        tiv = db.get(models.Initiative, tiv_id)
        post.mission_id = tiv.mission_id or post.mission_id
        open_item = db.scalar(select(models.Post).where(
            models.Post.ben_author_id == author.id, models.Post.type == typ,
            models.Post.tiv_id == tiv_id, models.Post.category == "budgeting",
            models.Post.parent_id.is_(None)).limit(1))
        if open_item is not None:
            raise Refusal(f"you already have an open {t.label} item for this initiative — edit it; a new "
                          "slot opens when it is paid out (one open item per type per person per initiative)")

    else:   # general
        if target_kind and target_kind != "none":
            _fill_target(db, post, target_kind, target_id)
        elif post.org_id:
            _fill_target(db, post, "organization", post.org_id)
        elif post.tiv_id:
            _fill_target(db, post, "initiative", post.tiv_id)
        elif post.mission_id:
            _fill_target(db, post, "mission", post.mission_id)
        elif post.cause_id:
            _fill_target(db, post, "cause", post.cause_id)
        else:
            post.target_kind, post.target_id = "none", None
        if "response" in tags and post.target_kind != "post":
            raise Refusal("a Response is 'in response to' another post — target the post (target_kind='post')")

    # Entity tags must name something real; the rest are words.
    post.tags = _valid_entity_tags(db, tags) or None
    return _check_refs(db, post, references, now)


def _valid_entity_tags(db: Session, tags: list[str]) -> list[str]:
    table = {"cause": models.Cause, "tiv": models.Initiative, "org": models.Organization,
             "mission": models.Mission, "post": models.Post, "budget": models.Post}
    out = []
    for tg in tags:
        if ":" in tg:
            kind, _, ident = tg.partition(":")
            if db.get(table[kind], ident) is None:
                continue
        out.append(tg)
    return out


# ---------------------------------------------------------------------------
# References (the Analysis's 12 + 12, and anyone's citations)
# ---------------------------------------------------------------------------
def _check_refs(db: Session, post: models.Post, references, now: datetime) -> list[dict]:
    refs: list[dict] = []
    seen = set()
    for r in (references or []):
        if not isinstance(r, dict):
            continue
        kind = (r.get("kind") or ("post" if r.get("post_id") else "link" if r.get("url") else "")).lower()
        if kind == "post":
            pid = r.get("post_id")
            other = db.get(models.Post, pid) if pid else None
            if other is None:
                raise Refusal(f"cited post '{pid}' not found")
            if pid in seen or pid == post.id:
                continue
            seen.add(pid)
            v = r.get("version")
            v = int(v) if v else int(other.version or 1)
            refs.append({"kind": "post", "ref_post_id": pid, "ref_version": v, "auto": False,
                         "_type": other.type, "_cat": other.category})
        elif kind == "mission":
            mid = r.get("mission_id")
            if not mid or db.get(models.Mission, mid) is None:
                raise Refusal(f"cited mission '{mid}' not found")
            refs.append({"kind": "mission", "ref_mission_id": mid})
        elif kind == "link":
            url = (r.get("url") or "").strip()
            if not url.startswith(("http://", "https://")):
                raise Refusal("a link reference needs an http(s) URL")
            refs.append({"kind": "link", "url": url[:2000], "label": (r.get("label") or "")[:200] or None})
    if post.type == pcfg.ANALYSIS:
        m = db.get(models.Mission, post.mission_id)
        lead = leads(db, m, now)
        for key in ("investigation", "background"):
            lid = lead.get(key + "_id")
            if lid and lid not in seen:
                other = db.get(models.Post, lid)
                refs.insert(0, {"kind": "post", "ref_post_id": lid, "ref_version": lead.get(key + "_version") or other.version,
                                "auto": True, "_type": other.type, "_cat": other.category})
                seen.add(lid)
            elif lid:
                for r in refs:
                    if r.get("ref_post_id") == lid:
                        r["auto"] = True
        bgs = [r for r in refs if r.get("_type") == pcfg.BACKGROUND]
        invs = [r for r in refs if r.get("_type") == pcfg.INVESTIGATION]
        if len(bgs) > pcfg.ANALYSIS_MAX_BACKGROUNDS:
            raise Refusal(f"an Analysis cites at most {pcfg.ANALYSIS_MAX_BACKGROUNDS} Backgrounds (the leading one included)")
        if len(invs) > pcfg.ANALYSIS_MAX_INVESTIGATIONS:
            raise Refusal(f"an Analysis cites at most {pcfg.ANALYSIS_MAX_INVESTIGATIONS} Investigations (the leading one included)")
        for r in refs:
            if r["kind"] == "post" and r["_type"] not in (pcfg.BACKGROUND, pcfg.INVESTIGATION) \
                    and r["_cat"] not in ("budgeting", "resolution"):
                raise Refusal("an Analysis cites Backgrounds, Investigations and budget items")
    return refs


def attach_refs(db: Session, post: models.Post, refs: list[dict], *, keep_auto: bool = False) -> None:
    """Write `refs` for `post`, replacing what it had. An Analysis's citations
    also bring each cited post into the Analysis's mission (`via='cite'`), where
    its votes start from zero (D21)."""
    old = db.scalars(select(models.PostRef).where(models.PostRef.post_id == post.id)).all()
    for r in old:
        db.delete(r)
    for i, r in enumerate(refs):
        db.add(models.PostRef(post_id=post.id, kind=r["kind"], ref_post_id=r.get("ref_post_id"),
                              ref_version=r.get("ref_version"), ref_mission_id=r.get("ref_mission_id"),
                              url=r.get("url"), label=r.get("label"), auto=bool(r.get("auto")), position=i))
        if post.type == pcfg.ANALYSIS and r.get("ref_post_id") and post.mission_id:
            link_mission(db, r["ref_post_id"], post.mission_id, via="cite")


def link_mission(db: Session, post_id: str, mission_id: str, via: str) -> models.PostMission:
    row = db.scalar(select(models.PostMission).where(
        models.PostMission.post_id == post_id, models.PostMission.mission_id == mission_id))
    if row is None:
        row = models.PostMission(post_id=post_id, mission_id=mission_id, via=via)
        db.add(row)
        db.flush()
    return row


def after_create(db: Session, post: models.Post, refs: list[dict]) -> None:
    """Version 1, the origin mission, the references. Call after `db.add`."""
    post.version = 1
    db.add(models.PostVersion(post_id=post.id, version=1, title=post.title, body=post.body,
                              tags=post.tags, line_items=post.line_items))
    if post.mission_id and not post.parent_id:
        link_mission(db, post.id, post.mission_id, via="origin")
    if post.type == pcfg.INVESTIGATION and post.org_id and not post.parent_id:
        for m in open_org_races(db, post.org_id):
            link_mission(db, post.id, m.id, via="race")
    if refs:
        attach_refs(db, post, refs)


# ---------------------------------------------------------------------------
# Versions and pins
# ---------------------------------------------------------------------------
def version_at(db: Session, post_id: str, when: datetime) -> Optional[int]:
    """The version that stood at `when` (the newest created at or before it)."""
    return db.scalar(select(sqlfunc.max(models.PostVersion.version)).where(
        models.PostVersion.post_id == post_id, models.PostVersion.created_at <= when))


def pin_due(db: Session, post: models.Post, now: Optional[datetime] = None) -> list[models.PostMission]:
    """Pin every mission of `post` whose election for its type has closed.
    Idempotent, and the answer does not depend on when it is asked: the pinned
    version is the one standing at the close."""
    now = _now(now)
    pinned = []
    rows = db.scalars(select(models.PostMission).where(
        models.PostMission.post_id == post.id, models.PostMission.pinned_version.is_(None))).all()
    for row in rows:
        m = db.get(models.Mission, row.mission_id)
        at = pin_time(post.type, m) if m is not None else None
        if at is None or now < at:
            continue
        v = version_at(db, post.id, at)
        if v is None:        # written after the close: nothing to keep here
            continue
        row.pinned_version, row.pinned_at = v, at
        pinned.append(row)
    if pinned:
        db.flush()
    return pinned


def locked_versions(db: Session, post_id: str) -> set[int]:
    """Versions an election or an Analysis used — locked for good (D21)."""
    a = {v for (v,) in db.execute(select(models.PostMission.pinned_version).where(
        models.PostMission.post_id == post_id, models.PostMission.pinned_version.is_not(None))).all()}
    b = {v for (v,) in db.execute(select(models.PostRef.ref_version).where(
        models.PostRef.ref_post_id == post_id, models.PostRef.ref_version.is_not(None))).all()}
    return a | b


def new_version(db: Session, post: models.Post, fields: dict, now: Optional[datetime] = None) -> int:
    """Apply an edit as version n+1 (D21). The post row carries the newest."""
    now = _now(now)
    pin_due(db, post, now)
    for f, v in fields.items():
        setattr(post, f, v)
    post.version = int(post.version or 1) + 1
    post.updated_at = now
    db.add(models.PostVersion(post_id=post.id, version=post.version, title=post.title, body=post.body,
                              tags=post.tags, line_items=post.line_items, created_at=now))
    if post.type == pcfg.BACKGROUND:
        roll(db, post, now)
    return post.version


# ---------------------------------------------------------------------------
# Rolling, pulling, and votes per mission
# ---------------------------------------------------------------------------
def scope_of(post: models.Post) -> str:
    return post.mission_id or ""


def recount(db: Session, post: models.Post) -> None:
    """The post's counts in its current mission (D21)."""
    rows = db.execute(select(models.PostVote.value, sqlfunc.count(models.PostVote.id)).where(
        models.PostVote.post_id == post.id, models.PostVote.mission_scope == scope_of(post)
    ).group_by(models.PostVote.value)).all()
    c = dict(rows)
    post.helpful_count = int(c.get("helpful", 0))
    post.neutral_count = int(c.get("neutral", 0))
    post.harmful_count = int(c.get("harmful", 0))


def roll(db: Session, post: models.Post, now: Optional[datetime] = None) -> bool:
    """D19: a Background whose mission's initiative election has closed moves on
    to the cause's open initiative election, keeping the closed mission's
    version there. An Investigation whose race closed moves to the next open
    race its organization stands in. True if it moved."""
    now = _now(now)
    if post.parent_id or post.type not in (pcfg.BACKGROUND, pcfg.INVESTIGATION):
        return False
    cur = db.get(models.Mission, post.mission_id) if post.mission_id else None
    close = pin_time(post.type, cur) if cur is not None else None
    if cur is not None and close is not None and now < close:
        return False
    if post.type == pcfg.BACKGROUND:
        nxt = open_initiative_mission(db, post.cause_id, now) if post.cause_id else None
    else:
        races = open_org_races(db, post.org_id, now) if post.org_id else []
        nxt = races[0] if races else None
    if nxt is None or (cur is not None and nxt.id == cur.id):
        return False
    pin_due(db, post, now)
    post.mission_id = nxt.id
    link_mission(db, post.id, nxt.id, via="roll")
    recount(db, post)
    return True


def roll_cause(db: Session, cause_id: Optional[str] = None, org_id: Optional[str] = None,
               now: Optional[datetime] = None) -> int:
    """Roll every Background of a cause (and Investigation of an organization)
    that is due. Cheap and idempotent; readers call it before they list."""
    now = _now(now)
    stmt = select(models.Post).where(models.Post.parent_id.is_(None))
    if cause_id:
        stmt = stmt.where(models.Post.type == pcfg.BACKGROUND, models.Post.cause_id == cause_id)
    elif org_id:
        stmt = stmt.where(models.Post.type == pcfg.INVESTIGATION, models.Post.org_id == org_id)
    else:
        stmt = stmt.where(models.Post.type.in_((pcfg.BACKGROUND, pcfg.INVESTIGATION)))
    n = 0
    for p in db.scalars(stmt).all():
        pin_due(db, p, now)
        n += roll(db, p, now)
    return n


def pull(db: Session, post: models.Post, mission_id: str, author: models.BenefactorAccount,
         now: Optional[datetime] = None) -> models.Post:
    """D21: bring your own post from an earlier mission into this one. Its votes
    start again from zero here; the old mission keeps its version and votes."""
    now = _now(now)
    if post.parent_id:
        raise Refusal("replies stay in their thread — pull the post they belong to")
    if not getattr(author, "is_staff", False) and post.ben_author_id != author.id:
        raise PermissionError("you can only pull your own posts")
    if post.type == pcfg.ANALYSIS:
        raise Refusal("an Analysis belongs to its mission — write a new one, citing the research you want to keep")
    m = db.get(models.Mission, mission_id)
    if m is None:
        raise Refusal(f"mission '{mission_id}' not found")
    if post.mission_id == mission_id:
        raise Refusal("that post is already in this mission")
    if post.type == pcfg.BACKGROUND and post.cause_id and m.cause_id != post.cause_id:
        raise Refusal("a Background belongs to its cause — pull it into a mission of the same cause")
    pin_due(db, post, now)
    post.mission_id = mission_id
    link_mission(db, post.id, mission_id, via="pull")
    recount(db, post)
    return post


# ---------------------------------------------------------------------------
# Leads (D20)
# ---------------------------------------------------------------------------
def _most_voted(db: Session, candidates: list[models.Post], until: datetime,
                scope: Optional[str]) -> Optional[models.Post]:
    if not candidates:
        return None
    ids = [p.id for p in candidates]
    stmt = select(models.PostVote.post_id, models.PostVote.value, sqlfunc.count(models.PostVote.id)).where(
        models.PostVote.post_id.in_(ids), models.PostVote.created_at <= until)
    if scope is not None:
        stmt = stmt.where(models.PostVote.mission_scope == scope)
    tally: dict[str, dict] = {}
    for pid, val, n in db.execute(stmt.group_by(models.PostVote.post_id, models.PostVote.value)).all():
        tally.setdefault(pid, {})[val] = n

    def key(p):
        t = tally.get(p.id, {})
        return (-(t.get("helpful", 0)), -(t.get("helpful", 0) - t.get("harmful", 0)),
                _naive(p.created_at) or until, p.id)
    return sorted(candidates, key=key)[0]


def leads(db: Session, m: Optional[models.Mission], now: Optional[datetime] = None) -> dict:
    """The leading Background (fixed at T) and Investigation (fixed at T+8) of
    a mission, fixing either the first time it is asked after its close. Before
    a close, the answer is the provisional leader, marked `fixed: False`."""
    now = _now(now)
    out = {"mission_id": m.id if m else None, "background_id": None, "background_version": None,
           "background_fixed": False, "investigation_id": None, "investigation_version": None,
           "investigation_fixed": False}
    if m is None:
        return out
    row = db.get(models.MissionLead, m.id)
    if row is None:
        row = models.MissionLead(mission_id=m.id)
        db.add(row)
        db.flush()
    # Background: every Background of the cause that stood in this election.
    t_me = me_close(m)
    if row.background_fixed_at is None:
        linked = {pid for (pid,) in db.execute(select(models.PostMission.post_id).where(
            models.PostMission.mission_id == m.id)).all()}
        bgs = [p for p in db.scalars(select(models.Post).where(
            models.Post.type == pcfg.BACKGROUND, models.Post.parent_id.is_(None),
            or_(models.Post.cause_id == m.cause_id, models.Post.id.in_(linked or {""})))).all()
            if (_naive(p.created_at) or now) <= min(now, t_me)]
        best = _most_voted(db, bgs, min(now, t_me), m.id)
        if best is not None:
            out["background_id"] = best.id
            out["background_version"] = version_at(db, best.id, min(now, t_me)) or best.version
            if now >= t_me:
                row.background_id, row.background_version = out["background_id"], out["background_version"]
                row.background_fixed_at = t_me
        elif now >= t_me:
            row.background_fixed_at = t_me
    if row.background_fixed_at is not None:
        out.update(background_id=row.background_id, background_version=row.background_version,
                   background_fixed=True)
    # Investigation: any Investigation of any candidate organization.
    t_oe = oe_close(m)
    if row.investigation_fixed_at is None:
        orgs = {c.org_id for c in db.scalars(select(models.MissionCandidacy).where(
            models.MissionCandidacy.mission_id == m.id)).all()}
        if m.winning_org_id:
            orgs.add(m.winning_org_id)
        invs = [p for p in db.scalars(select(models.Post).where(
            models.Post.type == pcfg.INVESTIGATION, models.Post.parent_id.is_(None),
            models.Post.org_id.in_(orgs or {""}))).all()
            if (_naive(p.created_at) or now) <= min(now, t_oe)]
        best = _most_voted(db, invs, min(now, t_oe), None)
        if best is not None:
            out["investigation_id"] = best.id
            out["investigation_version"] = version_at(db, best.id, min(now, t_oe)) or best.version
            if now >= t_oe:
                row.investigation_id, row.investigation_version = out["investigation_id"], out["investigation_version"]
                row.investigation_fixed_at = t_oe
        elif now >= t_oe:
            row.investigation_fixed_at = t_oe
    if row.investigation_fixed_at is not None:
        out.update(investigation_id=row.investigation_id, investigation_version=row.investigation_version,
                   investigation_fixed=True)
    return out


def analysis_kit(db: Session, m: models.Mission, now: Optional[datetime] = None) -> dict:
    """Everything the Analysis composer offers: the two leads (attached, fixed),
    the Backgrounds and Investigations it may cite (any mission, any age),
    ranked by their votes, and the initiative's budget items."""
    now = _now(now)
    lead = leads(db, m, now)
    bgs = db.scalars(select(models.Post).where(
        models.Post.type == pcfg.BACKGROUND, models.Post.parent_id.is_(None)
    ).order_by(models.Post.helpful_count.desc(), models.Post.created_at.desc()).limit(200)).all()
    # this cause's first — they are the ones this mission's voters read
    bgs = sorted(bgs, key=lambda p: (p.cause_id != m.cause_id,))
    invs = db.scalars(select(models.Post).where(
        models.Post.type == pcfg.INVESTIGATION, models.Post.parent_id.is_(None)
    ).order_by(models.Post.helpful_count.desc(), models.Post.created_at.desc()).limit(200)).all()
    cands = {c.org_id for c in db.scalars(select(models.MissionCandidacy).where(
        models.MissionCandidacy.mission_id == m.id)).all()}
    invs = sorted(invs, key=lambda p: (p.org_id not in cands and p.org_id != m.winning_org_id,))
    budget = []
    if m.winning_tiv_id:
        budget = db.scalars(select(models.Post).where(
            models.Post.tiv_id == m.winning_tiv_id, models.Post.parent_id.is_(None),
            models.Post.category.in_(("budgeting", "resolution"))
        ).order_by(models.Post.helpful_count.desc())).all()
    return {
        "mission_id": m.id, "open": bool((m.winning_org_id or now >= oe_close(m)) and now < budget_day(m)),
        "opens_at": oe_close(m), "closes_at": budget_day(m),
        "leads": lead,
        "max_backgrounds": pcfg.ANALYSIS_MAX_BACKGROUNDS,
        "max_investigations": pcfg.ANALYSIS_MAX_INVESTIGATIONS,
        "backgrounds": bgs, "investigations": invs, "budget_items": budget,
    }


# ---------------------------------------------------------------------------
# Reading — what every page displays
# ---------------------------------------------------------------------------
def _names(db: Session, posts: Iterable[models.Post]) -> dict:
    """Display names for every target in a page of posts, in a few queries."""
    want: dict[str, set] = {"cause": set(), "initiative": set(), "organization": set(),
                            "mission": set(), "post": set()}
    for p in posts:
        k = p.target_kind
        if k in want and p.target_id:
            want[k].add(p.target_id)
        elif k == "budget" and p.target_id:
            want["post"].add(p.target_id)
        if p.mission_id:
            want["mission"].add(p.mission_id)
    out: dict = {}
    if want["cause"]:
        out.update({("cause", c.id): c.name for c in db.scalars(
            select(models.Cause).where(models.Cause.id.in_(want["cause"]))).all()})
    if want["initiative"]:
        out.update({("initiative", t.id): t.title for t in db.scalars(
            select(models.Initiative).where(models.Initiative.id.in_(want["initiative"]))).all()})
    if want["organization"]:
        out.update({("organization", o.id): o.name for o in db.scalars(
            select(models.Organization).where(models.Organization.id.in_(want["organization"]))).all()})
    if want["post"]:
        for o in db.scalars(select(models.Post).where(models.Post.id.in_(want["post"]))).all():
            label = o.title or (o.body or "")[:60]
            out[("post", o.id)] = label
            out[("budget", o.id)] = label
    if want["mission"]:
        out.update({("mission", k): v for k, v in mission_labels(db, want["mission"]).items()})
    return out


def mission_labels(db: Session, ids) -> dict[str, str]:
    """A mission's name: its elected initiative, else "<Cause> <n>"."""
    ids = set(ids or [])
    if not ids:
        return {}
    ms = db.scalars(select(models.Mission).where(models.Mission.id.in_(ids))).all()
    tivs = {t.id: t.title for t in db.scalars(select(models.Initiative).where(
        models.Initiative.id.in_({m.winning_tiv_id for m in ms if m.winning_tiv_id} or {""}))).all()}
    causes = {c.id: c.name for c in db.scalars(select(models.Cause)).all()}
    return {m.id: tivs.get(m.winning_tiv_id) or f"{causes.get(m.cause_id, m.cause_id)} {int(m.cycle_num or 0) + 1}"
            for m in ms}


def reply_counts(db: Session, ids: list[str]) -> dict[str, int]:
    if not ids:
        return {}
    return dict(db.execute(select(models.Post.parent_id, sqlfunc.count(models.Post.id)).where(
        models.Post.parent_id.in_(ids)).group_by(models.Post.parent_id)).all())


def scoped_counts(db: Session, ids: list[str], scope: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not ids:
        return out
    for pid, val, n in db.execute(select(models.PostVote.post_id, models.PostVote.value,
                                         sqlfunc.count(models.PostVote.id)).where(
            models.PostVote.post_id.in_(ids), models.PostVote.mission_scope == scope
    ).group_by(models.PostVote.post_id, models.PostVote.value)).all():
        out.setdefault(pid, {})[val] = n
    return out


def serialize(db: Session, posts: list[models.Post], mission_ctx: Optional[str] = None) -> list[dict]:
    """Posts as every page displays them: the target and its name, tags, the
    version, reply count, the vote name — and, read IN A MISSION, that
    mission's vote counts and the version the mission keeps (D21)."""
    posts = list(posts)
    if not posts:
        return []
    ids = [p.id for p in posts]
    names = _names(db, posts)
    replies = reply_counts(db, ids)
    pins: dict[str, models.PostMission] = {}
    counts: dict[str, dict] = {}
    if mission_ctx:
        for row in db.scalars(select(models.PostMission).where(
                models.PostMission.mission_id == mission_ctx, models.PostMission.post_id.in_(ids))).all():
            pins[row.post_id] = row
        counts = scoped_counts(db, ids, mission_ctx)
    pinned_versions: dict[tuple, models.PostVersion] = {}
    need = [(pid, r.pinned_version) for pid, r in pins.items() if r.pinned_version]
    if need:
        for v in db.scalars(select(models.PostVersion).where(
                models.PostVersion.post_id.in_([n[0] for n in need]))).all():
            pinned_versions[(v.post_id, v.version)] = v
    handles = dict(db.execute(select(models.BenefactorAccount.id, models.BenefactorAccount.handle).where(
        models.BenefactorAccount.id.in_({p.ben_author_id for p in posts if p.ben_author_id} or {0}))).all())
    org_names = dict(db.execute(select(models.Organization.id, models.Organization.name).where(
        models.Organization.id.in_({p.org_author_id for p in posts if p.org_author_id} or {""}))).all())
    out = []
    for p in posts:
        d = {c.key: getattr(p, c.key) for c in models.Post.__table__.columns}
        d["author_name"] = ("Earthbux News" if p.author_type == "earthbux" else
                            org_names.get(p.org_author_id) or p.org_author_id if p.author_type == "org" else
                            handles.get(p.ben_author_id) or (f"Benefactor #{p.ben_author_id}" if p.ben_author_id else "Benefactor"))
        d["tags"] = list(p.tags or [])
        d["target_label"] = names.get((p.target_kind, p.target_id)) if p.target_kind not in (None, "none") else None
        d["mission_label"] = names.get(("mission", p.mission_id)) if p.mission_id else None
        d["reply_count"] = int(replies.get(p.id, 0))
        d["vote_name"] = pcfg.vote_name(p.type)
        d["latest_version"] = int(p.version or 1)
        d["version_shown"] = int(p.version or 1)
        d["in_mission"] = None
        if mission_ctx and p.parent_id is None:
            row = pins.get(p.id)
            if row is not None or p.mission_id == mission_ctx:
                c = counts.get(p.id, {})
                d["helpful_count"] = int(c.get("helpful", 0))
                d["neutral_count"] = int(c.get("neutral", 0))
                d["harmful_count"] = int(c.get("harmful", 0))
                d["in_mission"] = {"mission_id": mission_ctx, "via": row.via if row else "origin",
                                   "pinned_version": row.pinned_version if row else None}
                if row is not None and row.pinned_version:
                    v = pinned_versions.get((p.id, row.pinned_version))
                    if v is not None and row.pinned_version != p.version:
                        d["title"], d["body"] = v.title, v.body
                        d["line_items"] = v.line_items
                        d["version_shown"] = row.pinned_version
        out.append(d)
    return out


def detail(db: Session, post: models.Post, mission_ctx: Optional[str] = None) -> dict:
    """The full view: the post, what it cites (and whether each has changed
    since), who cites it, its versions and the missions it belongs to."""
    d = serialize(db, [post], mission_ctx)[0]
    refs = db.scalars(select(models.PostRef).where(models.PostRef.post_id == post.id)
                      .order_by(models.PostRef.position)).all()
    ref_posts = {p.id: p for p in db.scalars(select(models.Post).where(
        models.Post.id.in_([r.ref_post_id for r in refs if r.ref_post_id] or [""]))).all()}
    names = _names(db, ref_posts.values())
    d["references"] = []
    for r in refs:
        item = {"kind": r.kind, "auto": r.auto, "url": r.url, "label": r.label,
                "mission_id": r.ref_mission_id}
        o = ref_posts.get(r.ref_post_id) if r.ref_post_id else None
        if o is not None:
            item.update(post_id=o.id, type=o.type, category=o.category,
                        title=o.title or (o.body or "")[:80], cited_version=r.ref_version,
                        latest_version=o.version, changed=bool(r.ref_version and o.version != r.ref_version),
                        helpful_count=o.helpful_count, target_label=names.get((o.target_kind, o.target_id)))
        d["references"].append(item)
    d["cited_by"] = int(db.scalar(select(sqlfunc.count(models.PostRef.id)).where(
        models.PostRef.ref_post_id == post.id)) or 0)
    d["versions"] = [{"version": v.version, "created_at": v.created_at,
                      "locked": v.version in locked_versions(db, post.id)}
                     for v in db.scalars(select(models.PostVersion).where(
                         models.PostVersion.post_id == post.id).order_by(models.PostVersion.version)).all()]
    rows = db.scalars(select(models.PostMission).where(
        models.PostMission.post_id == post.id).order_by(models.PostMission.created_at)).all()
    labels = mission_labels(db, [r.mission_id for r in rows])
    d["missions"] = [{"mission_id": r.mission_id, "via": r.via, "pinned_version": r.pinned_version,
                      "label": labels.get(r.mission_id)} for r in rows]
    return d
