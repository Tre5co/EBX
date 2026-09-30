"""The feed framework — how posts are ordered, as named, swappable strategies.

Inbox 2026-09-29: "You put my algorithm posts in 'notes for later', but we
should start testing now … I do want to set up the framework here so that I am
prepared later on." So P3 builds the FRAME and P5 tunes what goes in it.

A strategy is a name, a sentence saying what it is for, its weights, and a
function from (posts, signals) to an order. `GET /posts?sort=<name>` uses one;
`GET /posts/strategies` lists them all with their weights, so a page (or a test)
can put two orders side by side. Every strategy breaks ties the same way —
newest first, then by id — because "posts with identical timestamps will cause
problems" (P3 notes): a tie that is not broken deterministically reorders on
every request.

The signals are the ones the platform has TODAY: votes (and when they were
cast), replies (and when), recency, the post-support flag, type and tags.
Everything personal — follows, views, "already seen", network proximity, topic
affinity — needs the event log (P4) and belongs to Home's personalized cut;
News is algorithmic but never personalized (P3b). The list of signals still to
come is kept in `FUTURE_SIGNALS`, so the frame names what it will read before
it can read it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from sqlalchemy import func as sqlfunc, select
from sqlalchemy.orm import Session

from . import models

RESEARCH_TYPES = ("context", "investigation", "analysis")

# Signals the personalized and quality strategies will read once they exist
# (P3 › Notes, kept here so the frame names them). None is read today.
FUTURE_SIGNALS = (
    "people you follow", "things you follow", "causes you engage with",
    "initiatives you engage with", "missions you've viewed", "organizations you've viewed",
    "posts you've voted on", "posts you've replied to", "network proximity",
    "topic/tag affinity", "diversity/novelty", "whether you've already seen the post",
)


@dataclass
class Signals:
    """What a strategy may read about a page of posts."""
    now: datetime
    replies: dict[str, int] = field(default_factory=dict)
    recent_votes: dict[str, int] = field(default_factory=dict)     # helpful votes inside the window
    recent_replies: dict[str, int] = field(default_factory=dict)   # replies inside the window


@dataclass(frozen=True)
class Strategy:
    key: str
    label: str
    purpose: str
    weights: dict
    score: Callable[["models.Post", Signals, dict], float]
    only_types: Optional[tuple] = None


def _age_h(p, now: datetime) -> float:
    c = p.created_at or now
    if getattr(c, "tzinfo", None) is not None:
        c = c.astimezone(timezone.utc).replace(tzinfo=None)
    return max(0.0, (now - c).total_seconds() / 3600.0)


def _latest(p, s: Signals, w: dict) -> float:
    return -_age_h(p, s.now)


def _trending(p, s: Signals, w: dict) -> float:
    """Velocity with time decay: what is being voted on and replied to NOW,
    not what gathered the most over its life. Harm does not add — the norm of
    ranking outrage is exactly what this is meant not to do (P3 notes)."""
    v = (w["vote"] * s.recent_votes.get(p.id, 0) + w["reply"] * s.recent_replies.get(p.id, 0))
    if (p.flag or "green") == "red":
        return -1.0
    return v / ((_age_h(p, s.now) + w["offset_h"]) ** w["gravity"])


def _research(p, s: Signals, w: dict) -> float:
    """The research that is helping: net helpful, a little credit for being
    argued with, a slow decay so a strong old post is not buried in a week."""
    net = float(p.helpful_count or 0) - w["harm"] * float(p.harmful_count or 0) \
        + w["reply"] * s.replies.get(p.id, 0)
    return net / ((_age_h(p, s.now) / 24.0 + 2.0) ** w["gravity"])


def _hot(p, s: Signals, w: dict) -> float:
    """The existing feed order (crud._rank_hot, 2026-09-08), restated here."""
    age = _age_h(p, s.now)
    e = (float(p.helpful_count or 0) + w["reply"] * s.replies.get(p.id, 0)
         + w["neutral"] * float(p.neutral_count or 0) - w["harm"] * float(p.harmful_count or 0)
         + (w["gravity_by_category"].get(p.category or "", 0.0) if age <= w["gravity_hours"] else 0.0))
    if (p.flag or "green") == "red":
        e = min(e, 0.0)
    return e / ((age + 2.0) ** w["halflife_pow"])


HOT_WEIGHTS = {"reply": 2.0, "neutral": 0.25, "harm": 0.5, "halflife_pow": 1.5, "gravity_hours": 48.0,
               "gravity_by_category": {"headline": 12.0, "editorial": 8.0, "org_update": 6.0,
                                       "mission_update": 6.0}}

STRATEGIES: dict[str, Strategy] = {s.key: s for s in (
    Strategy("latest", "Latest", "Newest first. The honest default.", {}, _latest),
    Strategy("hot", "Hot", "Decayed engagement — the feed order since 2026-09-08.", HOT_WEIGHTS, _hot),
    Strategy("trending", "Trending", "Velocity with time decay — votes and replies in the last two days.",
             {"window_h": 48.0, "vote": 1.0, "reply": 2.0, "offset_h": 2.0, "gravity": 1.2}, _trending),
    Strategy("research", "Research", "Backgrounds, Investigations and Analyses, by how much they are helping.",
             {"harm": 1.0, "reply": 0.5, "gravity": 0.6}, _research, only_types=RESEARCH_TYPES),
    Strategy("missions", "Missions", "Grouped by mission — the missions with the newest activity first, each one's posts hot-first.",
             HOT_WEIGHTS, _hot),
)}
# `recent` is the name every existing caller uses for newest-first.
ALIASES = {"recent": "latest"}


def names() -> list[str]:
    return list(STRATEGIES) + list(ALIASES)


def describe() -> list[dict]:
    return [{"key": s.key, "label": s.label, "purpose": s.purpose, "weights": s.weights,
             "only_types": list(s.only_types) if s.only_types else None}
            for s in STRATEGIES.values()] + [{"key": "future_signals", "signals": list(FUTURE_SIGNALS)}]


def resolve(name: Optional[str]) -> Strategy:
    key = ALIASES.get(name or "latest", name or "latest")
    if key not in STRATEGIES:
        raise ValueError(f"unknown order '{name}' (expected one of {', '.join(names())})")
    return STRATEGIES[key]


def gather(db: Session, posts: list, window_h: float = 48.0, now: Optional[datetime] = None) -> Signals:
    now = now or datetime.utcnow()
    ids = [p.id for p in posts]
    sig = Signals(now=now)
    if not ids:
        return sig
    since = now - timedelta(hours=window_h)
    sig.replies = dict(db.execute(select(models.Post.parent_id, sqlfunc.count(models.Post.id)).where(
        models.Post.parent_id.in_(ids)).group_by(models.Post.parent_id)).all())
    sig.recent_replies = dict(db.execute(select(models.Post.parent_id, sqlfunc.count(models.Post.id)).where(
        models.Post.parent_id.in_(ids), models.Post.created_at >= since).group_by(models.Post.parent_id)).all())
    sig.recent_votes = dict(db.execute(select(models.PostVote.post_id, sqlfunc.count(models.PostVote.id)).where(
        models.PostVote.post_id.in_(ids), models.PostVote.value == "helpful",
        models.PostVote.created_at >= since).group_by(models.PostVote.post_id)).all())
    return sig


def _tiebreak(p, now: datetime):
    c = p.created_at or now
    if getattr(c, "tzinfo", None) is not None:
        c = c.astimezone(timezone.utc).replace(tzinfo=None)
    return (-c.timestamp(), p.id)


def rank(db: Session, posts: list, strategy: str, limit: int,
         now: Optional[datetime] = None) -> list:
    """Order `posts` by `strategy` and keep `limit`. Ties: newest, then id."""
    s = resolve(strategy)
    now = now or datetime.utcnow()
    if s.only_types:
        posts = [p for p in posts if p.type in s.only_types]
    sig = gather(db, posts, s.weights.get("window_h", 48.0), now)
    if s.key == "missions":
        last: dict = {}
        for p in posts:
            k = p.mission_id or ""
            t = _tiebreak(p, now)
            last[k] = min(last.get(k, t), t)
        return sorted(posts, key=lambda p: (last[p.mission_id or ""], p.mission_id or "~",
                                            -s.score(p, sig, s.weights), _tiebreak(p, now)))[:limit]
    return sorted(posts, key=lambda p: (-s.score(p, sig, s.weights), _tiebreak(p, now)))[:limit]
