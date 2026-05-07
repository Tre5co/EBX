"""Load the legacy JSON files into the database.

Run from the backend/ directory:
    python -m seed.seed
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine

DATA_DIR = Path(__file__).parent / "data"


def _load_json(filename: str):
    with open(DATA_DIR / filename, encoding="utf-8") as fh:
        return json.load(fh)


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seed_causes(db) -> dict[str, models.Cause]:
    by_id: dict[str, models.Cause] = {}
    for row in _load_json("causes.json"):
        cause = db.get(models.Cause, row["id"])
        if cause is None:
            cause = models.Cause(
                id=row["id"],
                index=row["index"],
                name=row["name"],
                color=row["color"],
                emoji=row.get("emoji"),
                description=row.get("description"),
            )
            db.add(cause)
        by_id[row["id"]] = cause
    db.flush()
    return by_id


def seed_organizations(db, causes: dict[str, models.Cause]) -> dict[str, models.Organization]:
    by_id: dict[str, models.Organization] = {}
    cause_by_index = {c.index: c for c in causes.values()}
    for row in _load_json("orgs.json"):
        org = db.get(models.Organization, row["id"])
        if org is None:
            org = models.Organization(
                id=row["id"],
                name=row["name"],
                description=row.get("description"),
                verified=row.get("verified", False),
                founded_year=row.get("founded"),
            )
            org.causes = [
                cause_by_index[idx] for idx in row.get("causes", []) if idx in cause_by_index
            ]
            db.add(org)
        by_id[row["id"]] = org
    db.flush()
    return by_id


def seed_initiatives(db, orgs: dict[str, models.Organization]) -> dict[str, models.Initiative]:
    by_id: dict[str, models.Initiative] = {}
    org_by_name = {o.name: o for o in orgs.values()}
    for row in _load_json("initiatives.json"):
        init = db.get(models.Initiative, row["id"])
        if init is None:
            winning_org_id = None
            if row.get("winning_org"):
                org = org_by_name.get(row["winning_org"])
                winning_org_id = org.id if org else None
            init = models.Initiative(
                id=row["id"],
                index=row.get("index"),
                cause_id=row["cause_id"],
                cycle_num=row.get("cycle_num", 0),
                title=row["title"],
                description=row.get("description"),
                emoji=row.get("emoji"),
                proposed_by=row.get("proposed_by", "benefactor"),
                ebx_committed=row.get("committed_ebx", 0),
                status=row.get("status", "suggested"),
                winning_org_id=winning_org_id,
            )
            db.add(init)
        by_id[row["id"]] = init
    db.flush()
    return by_id


def seed_posts(db) -> None:
    for row in _load_json("feed.json"):
        post = db.get(models.Post, row["id"])
        if post is not None:
            continue
        post = models.Post(
            id=row["id"],
            type=row.get("type", "editorial"),
            title=row.get("title"),
            body=row.get("body", ""),
            likes=row.get("likes", 0),
            created_at=_parse_dt(row.get("created_at")) or datetime.utcnow(),
            author_type=row.get("author_type", "earthbux"),
            author_label=row.get("author"),
            cause_id=_cause_id_from_index(db, row.get("cause_index")),
            initiative_id=row.get("initiative_id"),
            opinion_type=row.get("opinion_type"),
        )
        db.add(post)


def _cause_id_from_index(db, idx) -> str | None:
    if idx is None:
        return None
    cause = db.scalar(select(models.Cause).where(models.Cause.index == idx))
    return cause.id if cause else None


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        causes = seed_causes(db)
        orgs = seed_organizations(db, causes)
        seed_initiatives(db, orgs)
        seed_posts(db)
        db.commit()
    print("Seeded successfully.")


if __name__ == "__main__":
    main()
