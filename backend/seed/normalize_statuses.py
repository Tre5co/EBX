"""Repair election state so every due mission reflects a properly-run vote day.

Background: the status vocabulary is suggested | active | resolved, and a mission
opens at started_at (program week 0) with its initiative elected 7 weeks later
(UX week 0). Some persisted missions ended up with a winner that was never attached
to the mission (the vote references the tiv, but the tiv's mission_id was unset), so
the winner never went 'active' and phase 2 looked "skipped".

For each DUE mission (started_at + 7 weeks <= now):
  * If the winner is already attached to the mission and active/resolved -> leave it.
  * Otherwise clear the broken winner and re-run finalize_p1, which now attaches the
    winner to the mission, marks it 'active', tallies the votes, and carries the
    losing votes into the cause's next-cycle mission (10% skim -> commitment fund).
Missions whose election is still in the future are untouched. A light status sweep
normalizes any straggling won/lost/org_vote values.

Idempotent. Run from backend/:  python -m seed.normalize_statuses
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app import crud, models

ELECTION_OFFSET = timedelta(weeks=7)


def _counts(db) -> dict:
    return dict(Counter(s for (s,) in db.execute(select(models.Initiative.status)).all()))


def repair(db, now: datetime | None = None) -> None:
    now = now or datetime.utcnow()
    print("before:", _counts(db))

    # Light vocabulary sweep (no-op if already clean).
    for t in db.scalars(select(models.Initiative)).all():
        if t.status not in ("suggested", "active", "resolved"):
            t.status = "active" if t.status in ("won", "org_vote") else "suggested"
    db.commit()

    for m in db.scalars(select(models.Mission)).all():
        if not m.started_at or now < m.started_at + ELECTION_OFFSET:
            continue  # election still in the future — leave the mission in phase 1
        w = m.winning_tiv_id
        if w:
            winner = db.get(models.Initiative, w)
            if winner and winner.mission_id == m.id and winner.status in ("active", "resolved"):
                continue  # already correct (e.g. atm0)
            m.winning_tiv_id = None  # broken/detached winner — re-elect cleanly
            db.commit()
        elected = crud.finalize_p1(db, m.id)
        if elected:
            print(f"  re-elected {m.id}: winner {elected}")

    print("after: ", _counts(db))
    winners = db.execute(
        select(models.Mission.id, models.Mission.winning_tiv_id, models.Initiative.status)
        .join(models.Initiative, models.Initiative.id == models.Mission.winning_tiv_id)
        .where(models.Mission.winning_tiv_id.is_not(None))
    ).all()
    print("elected missions:", [tuple(w) for w in winners])


if __name__ == "__main__":
    _db = SessionLocal()
    try:
        repair(_db)
    finally:
        _db.close()
