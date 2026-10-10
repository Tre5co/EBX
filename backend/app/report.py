"""The weekly report — Home's main display (INSTRUCTIONS › 10/9 Reshuffle, 2026-10-09).

Jax: "This will be displayed on the home page at all times, updated each week."
One week, one cause, and the timeline every mission walks:

    October 6 – 13: Land                                  (this week's cause)

    ABOVE   three updates on this week's cause —
              1  this week's new mission          its initiative election just closed (T)
              2  the final week of x              its organization election closes this week (T+8)
              3  the upcoming budget day for x    budget day is at the end of this week (T+15)

    THE TIMELINE, from the initiative election to a week after budget day, one
    dot per mission, coloured by cause and labelled with its number: three of
    this week's cause, two of last week's, one of next week's.

    BELOW   three more —
              4  last week's cause, just entered prep   (its organization election closed as the week began)
              5  last week's cause, just left prep      (its budget day was as the week began)
              6  next week's cause, the current initiative election and its leaders

    then    cause elections — a challenger that won a week's vote, the
            incumbent that secured the window confirmed this week — and the
            exchange's top movers (ranked by EBX held until there is a price;
            the weekly change reads +0 until trading exists — Jax, 2026-10-09).

Everything is read from the mission clock (`started_at`; T = +7 weeks, the
organization election closes at T+8, budget day is T+15) and from the tallies
the ballots already read. Read-only; nothing here moves money or writes a row.
A slot whose mission does not exist yet (the first weeks of the calendar)
comes back `missing` rather than raising.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func as sqlfunc, or_, select
from sqlalchemy.orm import Session

from . import models
from .bootstrap import GENESIS, WEEK

ROTATION = 7
OE_WEEKS = 8           # T → T+8
BUDGET_WEEKS = 15      # T → T+15


def _iso(d: Optional[datetime]) -> Optional[str]:
    if not d:
        return None
    return d.isoformat() + ("Z" if d.tzinfo is None else "")


def week_of(when: Optional[datetime] = None) -> int:
    when = when or datetime.utcnow()
    return max(0, int((when - GENESIS) / WEEK))


def _s_week(m: models.Mission) -> Optional[int]:
    """The cycle week a mission's initiative election OPENED in (`started_at`)."""
    if not m.started_at:
        return None
    return int(round((m.started_at - GENESIS) / WEEK))


def _cause_dict(c: Optional[models.Cause]) -> Optional[dict]:
    if c is None:
        return None
    return {"id": c.id, "name": c.name, "color": c.color, "emoji": c.emoji, "index": c.index}


def _number(m: models.Mission) -> int:
    return int(m.cycle_num or 0) + 1


def _label(m: models.Mission, causes: dict) -> str:
    c = causes.get(m.cause_id)
    return f"{c.name if c else m.cause_id} {_number(m)}"


def _tiv_title(db: Session, tiv_id: Optional[str]) -> Optional[str]:
    if not tiv_id:
        return None
    t = db.get(models.Initiative, tiv_id)
    return t.title if t else tiv_id


def _org_name(db: Session, org_id: Optional[str]) -> Optional[str]:
    if not org_id:
        return None
    o = db.get(models.Organization, org_id)
    return o.name if o else org_id


def _me_leaders(db: Session, m: models.Mission, n: int = 3) -> list[dict]:
    from . import crud
    try:
        ents = crud.p1_tally(db, m.id).get("entries", [])
    except Exception:  # noqa: BLE001 — a tally that cannot be read is an empty list, not a 500
        ents = []
    ents = [e for e in ents if (e.get("votes") or 0) > 0 or (e.get("voter_count") or 0) > 0]
    ents.sort(key=lambda e: (-(e.get("weighted_share") or 0), -(e.get("votes") or 0), -(e.get("voter_count") or 0)))
    out = []
    for e in ents[:n]:
        tokens = float(e.get("votes") or 0)
        out.append({"id": e["tiv_id"], "name": _tiv_title(db, e["tiv_id"]),
                    "tokens": round(tokens, 1), "share": round(float(e.get("weighted_share") or 0) * 100),
                    "voters": int(e.get("voter_count") or 0)})
    return out


def _oe_leaders(db: Session, m: models.Mission, n: int = 3) -> list[dict]:
    from . import crud
    try:
        ents = crud.p2_tally(db, m.id).get("entries", [])
    except Exception:  # noqa: BLE001
        ents = []
    ents.sort(key=lambda e: (-(e.get("net_votes") or 0), -(e.get("ebx") or 0)))
    return [{"id": e["org_id"], "name": _org_name(db, e["org_id"]),
             "votes": int(e.get("net_votes") or 0), "tokens": round(float(e.get("ebx") or 0), 1),
             "voters": int(e.get("voter_count") or 0)} for e in ents[:n]]


def _budget_items(db: Session, m: models.Mission) -> int:
    return db.scalar(select(sqlfunc.count()).select_from(models.Post).where(
        models.Post.category == "budgeting", models.Post.parent_id.is_(None),
        or_(models.Post.mission_id == m.id,
            models.Post.tiv_id == (m.winning_tiv_id or "")))) or 0


def _stats(db: Session, m: models.Mission, now: datetime) -> dict:
    from . import wallet
    try:
        pub = wallet._public_mission(db, m, now)
    except Exception:  # noqa: BLE001
        pub = {}
    return {"members": int(pub.get("members") or 0), "committed_ct": int(pub.get("committed_ct") or 0),
            "final_ct": int(pub.get("final_ct") or 0), "posts": int(pub.get("posts") or 0),
            "initiatives": int(pub.get("initiatives") or 0),
            "lead_tiv_id": pub.get("lead_tiv_id"), "lead_org_id": pub.get("lead_org_id")}


def _fmt(d: datetime) -> str:
    """"Oct 6" — spelled out by hand, because `%-d` does not exist on Windows."""
    return f"{d.strftime('%b')} {d.day}" if hasattr(d, "strftime") else str(d)


# What each of the six updates is, in Jax's words, keyed by its role.
ROLES = {
    "new":          {"kicker": "This week's new mission", "side": "above"},
    "oe_final":     {"kicker": "Final week of the organization election", "side": "above"},
    "budget_day":   {"kicker": "Budget day this week", "side": "above"},
    "entered_prep": {"kicker": "Just entered prep", "side": "below"},
    "left_prep":    {"kicker": "Just left prep", "side": "below"},
    "current_me":   {"kicker": "This week's initiative election", "side": "below"},
}


def _update(db: Session, role: str, cause: Optional[models.Cause], m: Optional[models.Mission],
            age: int, causes: dict, now: datetime, t_week: int) -> dict:
    """One of the six mission updates."""
    base = {"role": role, "kicker": ROLES[role]["kicker"], "side": ROLES[role]["side"],
            "cause": _cause_dict(cause), "age": age}
    T = GENESIS + t_week * WEEK
    dates = {"me": _iso(T), "oe": _iso(T + OE_WEEKS * WEEK), "budget": _iso(T + BUDGET_WEEKS * WEEK)}
    if m is None:
        return dict(base, missing=True, mission_id=None, label=None, number=None, dates=dates,
                    title=None, line="No mission in this slot yet", leaders=[], leaders_kind=None,
                    org=None, stats=None)
    st = _stats(db, m, now)
    tiv = _tiv_title(db, m.winning_tiv_id)
    org = {"id": m.winning_org_id, "name": _org_name(db, m.winning_org_id)} if m.winning_org_id else None
    leaders, kind, title, line = [], None, tiv, ""
    me, oe, bd = T, T + OE_WEEKS * WEEK, T + BUDGET_WEEKS * WEEK
    if role == "current_me":
        leaders, kind = _me_leaders(db, m), "initiatives"
        title = leaders[0]["name"] if leaders else None
        line = (f"Closes {_fmt(me)}. " + (f"{len(leaders)} initiative{'s' if len(leaders) != 1 else ''} with votes"
                                          if leaders else "No votes yet — every vote carries 10 granted tokens"))
    elif role == "new":
        leaders, kind = _oe_leaders(db, m), "organizations"
        line = (f"Elected {_fmt(me)}. The organization election is open until {_fmt(oe)}"
                if m.winning_tiv_id else f"No initiative was elected on {_fmt(me)}")
    elif role == "oe_final":
        if m.winning_org_id:
            line = f"{org['name']} was elected"
        else:
            leaders, kind = _oe_leaders(db, m), "organizations"
            line = (f"The organization election closes {_fmt(oe)}" if m.winning_tiv_id
                    else "No initiative was elected, so there is no organization election")
    elif role == "budget_day":
        st["budget_items"] = _budget_items(db, m)
        line = (f"Budget day {_fmt(bd)} — every donation to it becomes final; {org['name']} claims its share"
                if org else f"Budget day {_fmt(bd)} — no organization was elected")
    elif role == "entered_prep":
        st["budget_items"] = _budget_items(db, m)
        line = (f"{org['name']} was elected {_fmt(oe)}. Prep runs to budget day, {_fmt(bd)}"
                if org else f"No organization was elected on {_fmt(oe)}")
    elif role == "left_prep":
        line = (f"Budget day was {_fmt(bd)}. Its EBX trades in the exchange now"
                if org else f"Budget day was {_fmt(bd)}, with no organization elected")
    return dict(base, missing=False, mission_id=m.id, label=_label(m, causes), number=_number(m),
                dates=dates, title=title, line=line, leaders=leaders, leaders_kind=kind,
                org=org, stats=st, coin=float(m.credit_value or 1.0))


def _cause_elections(db: Session, w: int, causes_by_index: dict) -> dict:
    """Cause-election news: the window confirmed as this week began (its
    holder secured it, or a challenger took it), and any challenger that won a
    week's vote for an open window."""
    from . import crud
    try:
        sl = crud.cause_slate(db)
    except Exception:  # noqa: BLE001
        return {"secured": [], "won": [], "leading": []}
    conf = int(sl.get("confirmed_slots") or 6)
    secured, won, leading = [], [], []
    for s in sl.get("slots", []):
        slot = int(s["slot"])
        inc = db.get(models.Cause, s["incumbent_id"]) if s.get("incumbent_id") else None
        holder = db.get(models.Cause, s["holder_id"]) if s.get("holder_id") else None
        s_week = w + slot - ROTATION                      # the week this window's election opens
        number = s_week // ROTATION + 1 if s_week >= 0 else 1
        window = f"{holder.name if holder else '?'} {number}" if holder and holder.id == (inc.id if inc else None) \
            else (f"{holder.name} (new cause)" if holder else None)
        T = GENESIS + (w + slot) * WEEK
        item = {"slot": slot, "weeks_out": slot, "window": window, "closes": _iso(T),
                "incumbent": _cause_dict(inc), "holder": _cause_dict(holder),
                "streak": int(s.get("streak") or 0), "required": int(s.get("weeks_required") or 6)}
        if slot == conf:
            secured.append(dict(item, outcome=("took" if s.get("swapped") else "secured")))
        if s.get("swapped") and slot != conf:
            won.append(dict(item, challenger=_cause_dict(holder), outcome="took"))
            continue
        if not s.get("votable"):
            continue
        try:
            state = crud.cause_ballot_state(db, slot, inc.id if inc else None)
        except Exception:  # noqa: BLE001
            continue
        cols = state.get("columns") or []
        last = cols[1]["winner"] if len(cols) > 1 else None
        now_w = cols[0]["winner"] if cols else None
        # Only a PROPOSED cause can take a window (crud.cause_ballot_state's
        # `_eligible`): a week won by one of the seven running causes is not a
        # challenger's week, and the slate does not count it either.
        def challenger(cid):
            ch = db.get(models.Cause, cid) if cid else None
            return ch if (ch is not None and ch.status == "suggested" and (not inc or ch.id != inc.id)) else None
        ch_last, ch_now = challenger(last), challenger(now_w)
        if ch_last:
            won.append(dict(item, challenger=_cause_dict(ch_last), outcome="won_week",
                            votes=int(cols[1].get("votes") or 0)))
        if ch_now:
            leading.append(dict(item, challenger=_cause_dict(ch_now), outcome="leading",
                                votes=int(cols[0].get("votes") or 0)))
    return {"secured": secured, "won": won, "leading": leading}


def _exchange(db: Session, w: int, now: datetime, causes: dict, n: int = 5) -> dict:
    """The exchange's top movers. There is no price until the DEX exists, so
    the ranking is EBX held (Jax, 2026-10-09: "size now, change later"), with
    each mission's change this week beside it — +0 until trading exists."""
    rows = db.scalars(select(models.Mission).where(models.Mission.winning_org_id.is_not(None),
                                                   models.Mission.started_at.is_not(None))).all()
    out = []
    for m in rows:
        if now < m.started_at + (7 + BUDGET_WEEKS) * WEEK:
            continue                                   # not past budget day: not in the exchange
        vs = db.scalars(select(models.VoteP2).where(models.VoteP2.mission_id == m.id)).all()
        # After budget day every stake is EBX (and final), so what the mission
        # holds is its committed money — read the way the mission page's
        # overview reads it, legacy stakes included (`wallet.mission_overview`).
        from . import wallet
        try:
            ov = wallet.mission_overview(db, m, now)
        except Exception:  # noqa: BLE001
            ov = {"committed_ct": 0, "members": 0}
        held = int(ov.get("committed_ct") or 0)
        change = 0
        for v in vs:
            for e in (v.provenance or []):
                if int((e or {}).get("week") or -1) != w:
                    continue
                if e.get("kind") == "mint_ebx":
                    change += int(e.get("amount_ct") or 0)
                elif e.get("kind") == "refund":
                    change -= int(e.get("amount_ct") or 0)
        members = int(ov.get("members") or 0)
        out.append({"mission_id": m.id, "label": _label(m, causes), "cause": _cause_dict(causes.get(m.cause_id)),
                    "title": _tiv_title(db, m.winning_tiv_id), "org": _org_name(db, m.winning_org_id),
                    "ebx_held_ct": held, "change_ct": change, "members": members,
                    "coin": float(m.credit_value or 1.0)})
    out.sort(key=lambda r: (-abs(r["change_ct"]), -r["ebx_held_ct"], r["mission_id"]))
    return {"movers": out[:n], "in_exchange": len(out),
            "note": "Ranked by EBX held until the exchange has a price. The weekly change reads +0 until trading opens."}


def weekly_report(db: Session, week: Optional[int] = None, now: Optional[datetime] = None) -> dict:
    """The report for `week` (default: this week)."""
    now = now or datetime.utcnow()
    w = week_of(now) if week is None else int(week)
    start, end = GENESIS + w * WEEK, GENESIS + (w + 1) * WEEK
    all_causes = db.scalars(select(models.Cause)).all()
    causes = {c.id: c for c in all_causes}
    by_index = {c.index: c for c in all_causes if c.status == "active" and c.index is not None}
    k = w % ROTATION
    this_c, last_c, next_c = by_index.get(k), by_index.get((k - 1) % ROTATION), by_index.get((k + 1) % ROTATION)

    missions = db.scalars(select(models.Mission).where(models.Mission.started_at.is_not(None))).all()
    at: dict[tuple, models.Mission] = {}
    for m in missions:
        sw = _s_week(m)
        if sw is not None:
            at[(m.cause_id, sw + 7)] = m                # keyed by the week T falls in

    def pick(cause, t_week):
        return at.get((cause.id, t_week)) if cause else None

    # Each row in timeline order (youngest first), so a page can hang card i
    # from dot i: above — new (0) · final OE week (7) · budget day (14); below —
    # next week's initiative election (−1) · entered prep (8) · left prep (15).
    plan = [  # role, cause, T-week
        ("new", this_c, w), ("oe_final", this_c, w - 7), ("budget_day", this_c, w - 14),
        ("current_me", next_c, w + 1), ("entered_prep", last_c, w - 8), ("left_prep", last_c, w - 15),
    ]
    updates = [_update(db, role, cz, pick(cz, tw), w - tw, causes, now, tw) for role, cz, tw in plan]
    dots = [{"mission_id": u["mission_id"], "label": u["label"], "number": u["number"],
             "cause": u["cause"], "age": u["age"], "role": u["role"], "side": u["side"],
             "missing": u["missing"]} for u in updates]
    # "October 6 – 13: Land" (Jax's own header), or "September 29 – October 6".
    title_dates = (f"{start.strftime('%B')} {start.day} – {end.day}" if start.month == end.month
                   else f"{start.strftime('%B')} {start.day} – {end.strftime('%B')} {end.day}")
    return {
        "week": w,
        "starts": _iso(start), "ends": _iso(end),
        "title": f"{title_dates}: {this_c.name}" if this_c else title_dates,
        "cause": _cause_dict(this_c), "last_cause": _cause_dict(last_c), "next_cause": _cause_dict(next_c),
        "above": [u for u in updates if u["side"] == "above"],
        "below": [u for u in updates if u["side"] == "below"],
        "timeline": {
            "from": -2, "to": BUDGET_WEEKS + 1,
            "phases": [
                {"key": "me", "label": "Initiative election", "from": -7, "to": 0},
                {"key": "oe", "label": "Organization election", "from": 0, "to": OE_WEEKS},
                {"key": "prep", "label": "Prep", "from": OE_WEEKS, "to": BUDGET_WEEKS},
                {"key": "ex", "label": "Exchange", "from": BUDGET_WEEKS, "to": BUDGET_WEEKS + 1},
            ],
            "marks": [{"at": 0, "label": "Initiative elected"}, {"at": OE_WEEKS, "label": "Organization elected"},
                      {"at": BUDGET_WEEKS, "label": "Budget day"}],
            "dots": dots,
        },
        "cause_elections": _cause_elections(db, w, by_index),
        "exchange": _exchange(db, w, now, causes),
        "generated_at": _iso(now),
    }
