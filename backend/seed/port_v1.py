"""One-off data port: copy v1 data from the pre-cutover backup into the new v2
schema. Idempotent — skips rows that already exist (keyed by id).

What it ports
-------------
  causes                 verbatim (identical columns)
  benefactor_accounts    + role='benefactor', watched_initiative_ids -> watched_tiv_ids
  organizations          catalog (drops mission_statement / date_approved)
  initiatives            catalog only — election state RESET (mission_id=NULL,
                         status='suggested', approved=False)

What it does NOT port (v1 election state — start these fresh on v2):
  missions, votes, contributions, vote_events, org_registrations,
  organization_causes, posts, memberships, credit_coins

Run from backend/::

    python -m seed.port_v1               # uses ./earthbucks.db.pre-v2.bak
    python -m seed.port_v1 path/to.bak   # explicit backup path
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from app import models
from app.database import SessionLocal

DEFAULT_BACKUP = Path(__file__).resolve().parents[1] / "earthbucks.db.pre-v2.bak"


def _dt(v):
    """Best-effort parse of a stored timestamp; None -> column default."""
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "").split(".")[0])
    except ValueError:
        return None


def port(backup_path: Path) -> dict[str, int]:
    if not backup_path.exists():
        raise SystemExit(f"Backup not found: {backup_path}")
    old = sqlite3.connect(backup_path)
    old.row_factory = sqlite3.Row
    db = SessionLocal()
    added = {"causes": 0, "benefactor_accounts": 0, "organizations": 0, "initiatives": 0}

    try:
        # --- causes (verbatim) ---
        for r in old.execute("select * from causes"):
            if db.get(models.Cause, r["id"]):
                continue
            db.add(models.Cause(
                id=r["id"], index=r["index"], name=r["name"], color=r["color"],
                emoji=r["emoji"], description=r["description"],
            ))
            added["causes"] += 1

        # --- benefactor accounts (preserve password hashes + ids) ---
        for r in old.execute("select * from benefactor_accounts"):
            if db.get(models.BenefactorAccount, r["id"]):
                continue
            kw = dict(
                id=r["id"], email=r["email"], handle=r["handle"],
                pass_hash=r["pass_hash"], is_active=bool(r["is_active"]),
                role="benefactor", vvv=bool(r["vvv"]),
                watched_tiv_ids=r["watched_initiative_ids"],
            )
            if _dt(r["created_at"]):
                kw["created_at"] = _dt(r["created_at"])
            db.add(models.BenefactorAccount(**kw))
            added["benefactor_accounts"] += 1

        # --- organizations (catalog) ---
        for r in old.execute("select * from organizations"):
            if db.get(models.Organization, r["id"]):
                continue
            db.add(models.Organization(
                id=r["id"], name=r["name"], description=r["description"],
                website_link=r["website_link"], founded_year=r["founded_year"],
                verified=bool(r["verified"]), score=r["score"] or 0.0,
                logo_url=r["logo_url"],
            ))
            added["organizations"] += 1

        db.flush()  # causes/orgs/accounts visible for the FK references below

        valid_bens = {x.id for x in db.scalars(__import__("sqlalchemy").select(models.BenefactorAccount)).all()}
        valid_orgs = {x.id for x in db.scalars(__import__("sqlalchemy").select(models.Organization)).all()}

        # --- initiatives (catalog only — election state reset) ---
        for r in old.execute("select * from initiatives"):
            if db.get(models.Initiative, r["id"]):
                continue
            pb = r["proposer_benefactor_id"] if r["proposer_benefactor_id"] in valid_bens else None
            po = r["proposer_org_id"] if r["proposer_org_id"] in valid_orgs else None
            db.add(models.Initiative(
                id=r["id"], title=r["title"], description=r["description"],
                emoji=r["emoji"], cause_id=r["cause_id"],
                mission_id=None,                     # reset — no mission yet
                proposer_ben_id=pb, proposer_org_id=po,
                rating_avg=r["rating_avg"] or 0.0, rating_count=r["rating_count"] or 0,
                logo_url=r["logo_url"], status="suggested", approved=False,
            ))
            added["initiatives"] += 1

        db.commit()
    finally:
        old.close()
        db.close()
    return added


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BACKUP
    result = port(path)
    print("Ported from", path.name)
    for k, v in result.items():
        print(f"  {k:22} +{v}")
