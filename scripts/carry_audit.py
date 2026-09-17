#!/usr/bin/env python3
"""Phase-1 positions that no phase-2 row ever carried — the case-by-case list.

WHY THIS EXISTS (2026-09-08, build-seq §0a). When an initiative election closes,
`finalize_p1` writes each backer a phase-2 row: the winner's backers as EARLY
EBX, everyone else MARKED. That row is what the wallet reads afterwards, and
`read_wallet` skips the phase-1 row on the ground that "the OE row holds it now".

Every mission decided BEFORE the finalized model landed (2026-08-27c) closed
without that row, and for those the skip handed the money to nobody: it was
counted zero times. `read_wallet` no longer skips a row that has nothing to
carry it, so the tokens are visible again — but the missing phase-2 POSITION is
a different question, and not one code should answer on its own. Where the
organization election has already been decided, minting a position after the
fact would inject money into a settled race.

So this prints them and stops. Each line is a decision for Jax:
  * carry it  — write the phase-2 row the finalizer would have written;
  * refund it — return the ct to the benefactor's unallocated bin;
  * leave it  — it stays a phase-1 token, visible in the wallet, spent from
                unallocated, standing in a race that is over.

    python3 scripts/carry_audit.py            # against backend/earthbucks.db
    DATABASE_URL=sqlite:///path python3 scripts/carry_audit.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{ROOT / 'backend' / 'earthbucks.db'}")

from sqlalchemy import select                      # noqa: E402

from app import models, wallet                     # noqa: E402
from app.database import SessionLocal              # noqa: E402


def main() -> int:
    db = SessionLocal()
    accounts = {
        a.id: a for a in db.scalars(select(models.BenefactorAccount)).all()
    }
    rows: list[tuple] = []
    for r in db.scalars(select(models.VoteP1)).all():
        m = db.get(models.Mission, r.mission_id)
        if m is None or not m.winning_tiv_id:
            continue                      # the initiative election is still open
        has_p2 = db.scalars(
            select(models.VoteP2).where(models.VoteP2.ben_id == r.ben_id,
                                        models.VoteP2.mission_id == r.mission_id)
        ).first() is not None
        if has_p2:
            continue                      # carried, nothing to decide
        ct = wallet.p1_stake_ct_of(r)
        if ct <= 0:
            continue
        a = accounts.get(r.ben_id)
        rows.append((r.mission_id, r.ben_id, (a.handle if a else "?"),
                     (a.role if a else "?"), r.tiv_id, ct,
                     r.tiv_id == m.winning_tiv_id, bool(m.winning_org_id)))

    if not rows:
        print("no orphaned phase-1 positions — every closed election carried its backers")
        return 0

    rows.sort(key=lambda t: (t[0], -t[5]))
    print(f"{len(rows)} phase-1 position(s) on a DECIDED initiative election with no "
          f"phase-2 row to carry them\n")
    print(f"{'mission':<8}{'ben':>4} {'handle':<12}{'role':<11}{'ct':>6}  "
          f"{'backed':<8}{'OE':<10}initiative")
    print("-" * 96)
    total = 0
    for mid, ben, handle, role, tiv, ct, won, oe_done in rows:
        total += ct
        print(f"{mid:<8}{ben:>4} {handle:<12}{role:<11}{ct:>6}  "
              f"{'WINNER' if won else 'lost':<8}"
              f"{'DECIDED' if oe_done else 'open':<10}{tiv}")
    print("-" * 96)
    print(f"{'':31}{total:>6} ct = {total / 100:.2f} tokens = "
          f"${total / 100 * 0.10:.2f}\n")
    print("`OE = DECIDED` means the organization election for that mission is already")
    print("settled: carrying the position now would add money to a finished race, so")
    print("those are the ones that need a human answer rather than a migration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
