"""Un-elect atm0's philanthropy — its election has not finalized yet.

WHY
---
Jax, 2026-08-09: "This mission has been causing problems. It should not be
elected until the end of this week."

`atm0` (Carbon Capture Expansion) carries `winning_org_id = 'org-001'` and
`current_phase = 'budget'`, i.e. its philanthropy election is recorded as OVER.
It is not: it finalizes at the end of the active cause window.

That one wrong row is why the OE card kept reading Methane. A cause can have
several philanthropy elections open at once — they run 8 weeks and the cause
comes round every 7 — and the OE card wants the OLDEST open one, the race about
to finalize. atm0 looked closed, so the only open race was atm1 and both cards
fell through to the same mission.

REQUIRED for main.html to read correctly. Verified in a headless DOM:
    with this fix     ME -> Methane Leak Detection Grid (atm1, just elected)
                      OE -> Carbon Capture Expansion    (atm0, finalizing)
    without it        ME -> Methane Leak Detection Grid
                      OE -> Methane Leak Detection Grid  <- the bug

WHAT IT CHANGES
---------------
  missions.winning_org_id  -> NULL      (nobody has won yet)
  missions.current_phase   -> 'initiative'  (the phase-2 window is still open)
  mission_candidacies.status for atm0: 'won' -> 'approved'  (still running,
                                        no longer the winner)

It does NOT touch votes, EBX, the pool or the ledger — org-001 keeps every vote
it has, it simply is not declared the winner yet. Fully reversible: the
--redo flag puts the election back exactly as it was.

USAGE
-----
    cd backend
    python ../scripts/unelect_atm0.py            # dry run, prints the plan
    python ../scripts/unelect_atm0.py --apply
    python ../scripts/unelect_atm0.py --redo --apply     # put it back

A timestamped backup of the db is written before any write.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

MISSION = "atm0"
ORG = "org-001"


def find_db() -> Path:
    here = Path(__file__).resolve().parent
    for cand in (here.parent / "backend" / "earthbucks.db",
                 Path.cwd() / "earthbucks.db",
                 here.parent / "earthbucks.db"):
        if cand.exists():
            return cand
    print("Could not find earthbucks.db — run this from backend/.", file=sys.stderr)
    raise SystemExit(2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="actually write (default: dry run)")
    ap.add_argument("--redo", action="store_true", help="re-elect org-001 (undo this script)")
    args = ap.parse_args()

    db = find_db()
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    row = con.execute(
        "SELECT id, winning_tiv_id, winning_org_id, current_phase FROM missions WHERE id = ?",
        (MISSION,)).fetchone()
    if row is None:
        print(f"No mission {MISSION} in {db}.")
        return 1

    print(f"db: {db}")
    print(f"before: {MISSION} tiv={row['winning_tiv_id']} org={row['winning_org_id']} "
          f"phase={row['current_phase']}")

    if args.redo:
        new_org, new_phase, new_status, old_status = ORG, "budget", "won", "approved"
    else:
        new_org, new_phase, new_status, old_status = None, "initiative", "approved", "won"

    print(f"after:  {MISSION} tiv={row['winning_tiv_id']} org={new_org} phase={new_phase}")
    print(f"        mission_candidacies({MISSION}, {ORG}).status {old_status!r} -> {new_status!r}")

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return 0

    backup = db.with_suffix(db.suffix + ".bak_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copy2(db, backup)
    print(f"backup: {backup}")

    con.execute("UPDATE missions SET winning_org_id = ?, current_phase = ? WHERE id = ?",
                (new_org, new_phase, MISSION))
    con.execute("UPDATE mission_candidacies SET status = ? WHERE mission_id = ? AND org_id = ?",
                (new_status, MISSION, ORG))
    con.commit()

    after = con.execute(
        "SELECT winning_org_id, current_phase FROM missions WHERE id = ?", (MISSION,)).fetchone()
    print(f"written: org={after['winning_org_id']} phase={after['current_phase']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
