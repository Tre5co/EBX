"""Post + reaction endpoints — v2, and P3 · Posting (2026-09-29).

Every read returns posts the way every page displays them (`posting.serialize`):
the target and its name, tags, the version, the reply count, the vote name,
and — read inside a mission (`mission_id=`) — that mission's vote counts and
the version the mission keeps.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import crud, events, feed_rank, models, post_config as pcfg, posting, schemas
from ..auth import get_current_benefactor
from ..config import get_settings
from ..database import get_db
from ..models import BenefactorAccount

router = APIRouter(prefix="/posts", tags=["posts"])
settings = get_settings()


def _refuse(e: Exception):
    """403 for a permission, 400 for a posting rule, 404 for a missing post."""
    if isinstance(e, PermissionError):
        raise HTTPException(status_code=403, detail=str(e))
    msg = str(e)
    if isinstance(e, posting.Refusal) or "not found" not in msg.lower():
        raise HTTPException(status_code=400, detail=msg)
    raise HTTPException(status_code=404, detail=msg)


@router.get("", response_model=list[schemas.PostRead])
def list_posts(
    mission_id: Optional[str] = None,
    tiv_id: Optional[str] = None,
    cause_id: Optional[str] = None,
    org_id: Optional[str] = None,
    category: Optional[str] = None,
    parent_id: Optional[str] = None,
    roots_only: bool = False,
    ben_author_id: Optional[int] = None,
    type: Optional[str] = None,
    tag: Optional[str] = None,
    target_kind: Optional[str] = None,
    target_id: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    sort: str = "recent",
    db: Session = Depends(get_db),
):
    """The post feed. `sort` is any strategy in `GET /posts/strategies`
    (`recent` = `latest`, `hot`, `trending`, `research`, `missions`).
    `source` = earthbux · charity · individual (comma-separated) — Home's toggles."""
    try:
        feed_rank.resolve(sort)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    rows = crud.list_posts(db, mission_id=mission_id, tiv_id=tiv_id, cause_id=cause_id,
                           category=category, parent_id=parent_id, roots_only=roots_only,
                           ben_author_id=ben_author_id, type=type, limit=min(max(limit, 1), 500),
                           sort=sort, org_id=org_id, tag=tag, target_kind=target_kind,
                           target_id=target_id, source=source)
    return posting.serialize(db, list(rows), mission_ctx=mission_id)


@router.get("/guide")
def guide():
    """Every post type, its target, limit, votes and user-facing guide — what
    post.html, the How to post section and each mission's outline read."""
    return pcfg.guide_payload()


@router.get("/strategies")
def strategies():
    """The feed orders `sort=` accepts, with their weights (feed_rank.py)."""
    return feed_rank.describe()


@router.get("/analysis-kit")
def analysis_kit(mission_id: str, db: Session = Depends(get_db)):
    """What the Analysis composer offers for a mission: the two leading posts
    (attached, can't be removed), every Background and Investigation it may
    cite, ranked by votes, and the initiative's budget items."""
    m = db.get(models.Mission, mission_id)
    if m is None:
        raise HTTPException(status_code=404, detail="mission not found")
    kit = posting.analysis_kit(db, m)
    db.commit()
    for k in ("backgrounds", "investigations", "budget_items"):
        kit[k] = posting.serialize(db, kit[k])
    return kit


@router.get("/votes/mine", response_model=dict)
def my_votes(
    ids: str = "",
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Posting pass (2026-10-01): the signed-in benefactor's vote on each of
    `ids` (comma-separated) — {post_id: helpful|harmful|neutral} — so a card
    can show which arrow is theirs. Any mission's vote counts."""
    want = [i for i in ids.split(",") if i][:300]
    if not want:
        return {}
    rows = db.execute(select(models.PostVote.post_id, models.PostVote.value).where(
        models.PostVote.ben_id == user.id, models.PostVote.post_id.in_(want))).all()
    return {pid: v for pid, v in rows}


@router.get("/{post_id}/comments", response_model=list[schemas.PostRead])
def list_comments(post_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Threaded replies to a post (oldest first)."""
    return posting.serialize(db, list(crud.list_posts(db, parent_id=post_id, limit=limit)))


@router.get("/{post_id}", response_model=schemas.PostDetail)
def get_post(post_id: str, mission_id: Optional[str] = None, db: Session = Depends(get_db)):
    """The full view of one post: references (and whether each has changed
    since it was cited), who cites it, its versions and missions."""
    p = db.get(models.Post, post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="post not found")
    posting.pin_due(db, p)
    db.commit()
    return posting.detail(db, p, mission_ctx=mission_id)


@router.get("/{post_id}/versions/{version}")
def get_version(post_id: str, version: int, db: Session = Depends(get_db)):
    """One version of a post, exactly as it stood (D21)."""
    v = db.query(models.PostVersion).filter_by(post_id=post_id, version=version).first()
    if v is None:
        raise HTTPException(status_code=404, detail="version not found")
    return {"post_id": post_id, "version": v.version, "title": v.title, "body": v.body,
            "tags": v.tags or [], "line_items": v.line_items, "created_at": v.created_at,
            "locked": v.version in posting.locked_versions(db, post_id)}


@router.post("", response_model=schemas.PostRead, status_code=201)
def create_post(
    data: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Create a post — any type, from anywhere, by anyone signed in (P3).
    Editorial/headline need staff; an org update needs the org's member."""
    try:
        p = crud.create_post(db, data, author=user)
    except (PermissionError, ValueError) as e:
        db.rollback()
        _refuse(e)
    events.safe(events.on_post_created, db, p)      # P4: a reply notifies
    return posting.serialize(db, [p])[0]


@router.put("/{post_id}", response_model=schemas.PostRead)
def update_post(
    post_id: str,
    data: schemas.PostUpdate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Edit your own post. Every edit is a NEW VERSION (D21): the version an
    election or an Analysis used stays exactly as it was."""
    try:
        p = crud.update_post(db, post_id, data, author=user)
    except (PermissionError, ValueError) as e:
        db.rollback()
        _refuse(e)
    events.safe(events.on_post_versioned, db, p)    # P4: whoever cites it hears
    return posting.serialize(db, [p])[0]


@router.post("/{post_id}/pull", response_model=schemas.PostRead)
def pull_post(
    post_id: str,
    data: schemas.PostPull,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Bring your post from an earlier mission into this one (D21). Its votes
    start again from zero here; the old mission keeps its version and votes."""
    p = db.get(models.Post, post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="post not found")
    try:
        posting.pull(db, p, data.mission_id, user)
        db.commit()
    except (PermissionError, ValueError) as e:
        db.rollback()
        _refuse(e)
    db.refresh(p)
    return posting.serialize(db, [p], mission_ctx=data.mission_id)[0]


@router.post("/{post_id}/resolve", response_model=schemas.PostRead)
def resolve_suggestion(
    post_id: str,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Mark a budget item as achieved — it becomes a RESOLUTION and moves the
    mission's credit-coin value (org members / staff)."""
    try:
        p = crud.resolve_suggestion(db, post_id, user, value_bump=settings.resolution_value_bump)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 409, detail=msg)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return posting.serialize(db, [p])[0]


@router.post("/{post_id}/flag", response_model=schemas.PostRead)
def set_flag(
    post_id: str,
    data: schemas.PostFlagUpdate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """Post-support layer override (staff only) — green | orange | red."""
    crud.require_staff(user)
    try:
        p = crud.set_post_flag(db, post_id, data.flag, data.reason)
    except ValueError as e:
        msg = str(e)
        raise HTTPException(status_code=404 if "not found" in msg.lower() else 400, detail=msg)
    return posting.serialize(db, [p])[0]


@router.post("/{post_id}/react", response_model=schemas.PostRead)
def react(
    post_id: str,
    data: schemas.PostVoteCreate,
    db: Session = Depends(get_db),
    user: BenefactorAccount = Depends(get_current_benefactor),
):
    """A Research vote, an Analysis vote or an upvote, by the post's type. It
    counts in `mission_id` when the post belongs to that mission (D21)."""
    try:
        p = crud.react_to_post(db, post_id, user.id, data.value, mission_id=data.mission_id)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    if data.value == "helpful":
        events.safe(events.on_reaction, db, p, user.id)   # P4: like thresholds
    return posting.serialize(db, [p], mission_ctx=data.mission_id)[0]
