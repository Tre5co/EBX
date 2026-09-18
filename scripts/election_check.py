"""election_check — the vote counting rules of 2026-09-17, end to end.

    python3 scripts/election_check.py

INSTRUCTIONS build-seq §2 (Elections). Runs the real app against a throwaway
copy of `earthbucks.db` and asserts:

  * losing votes never carry into the next election — neither in the tally,
    nor in an initiative's committed total, nor as a blocked re-vote;
  * the ME slate is whole percentages of one commit, and adding tokens keeps
    the ratios;
  * a decided initiative election refuses a new slate;
  * organization-election votes follow the doubling ladder
    (0 tokens = 1 vote, 10 = 2, 20 = 3, 40 = 4, 80 = 5);
  * without an ME stake, only this week's organization election is open.
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

_src = BACKEND / "earthbucks.db"
_tmp = Path(tempfile.mkdtemp(prefix="ebx_election_check_")) / "earthbucks.db"
shutil.copy2(_src, _tmp)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}"

# Migrate the COPY before the ORM touches it. `TestClient(app)` without a
# context manager never fires the startup hook that does this in the app, so a
# check written the week a migration lands would otherwise fail on a column the
# code is right about and the file has not got yet.
from alembic import command as _alembic          # noqa: E402
from alembic.config import Config as _AlembicCfg  # noqa: E402
_cfg = _AlembicCfg(str(BACKEND / "alembic.ini"))
_cfg.set_main_option("script_location", str(BACKEND / "alembic"))
_cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
_alembic.upgrade(_cfg, "head")

from fastapi.testclient import TestClient        # noqa: E402
from app.main import app                          # noqa: E402
from app import models as _m, crud, token_model as tm, wallet as _w  # noqa: E402
from app.database import SessionLocal             # noqa: E402

BAD = N = 0


def _dt_now():
    from datetime import datetime as _d
    return _d.utcnow()


def ok(cond, what, detail=""):
    global BAD, N
    N += 1
    BAD += 0 if cond else 1
    print(f"  {'ok  ' if cond else 'FAIL'}  {what}" + (f"  {detail}" if detail else ""))


def section(t):
    print(f"\n=== {t}")


T = tm.CT_PER_TOKEN
c = TestClient(app)


def signup(handle):
    email = f"{handle}@election-check.example.com"
    r = c.post("/auth/signup", json={"email": email, "handle": handle, "password": "check-pw-123"})
    assert r.status_code in (200, 201), r.text
    r = c.post("/auth/login", data={"username": email, "password": "check-pw-123"})
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def ben_id(handle):
    db = SessionLocal()
    try:
        return db.query(_m.BenefactorAccount).filter(_m.BenefactorAccount.handle == handle).one().id
    finally:
        db.close()


def give(handle, tokens):
    db = SessionLocal()
    b = db.query(_m.BenefactorAccount).filter(_m.BenefactorAccount.handle == handle).one()
    b.free_ct = int(b.free_ct or 0) + tokens * T
    b.purchased_ct = int(b.purchased_ct or 0) + tokens * T
    db.commit(); db.close()


# ---------------------------------------------------------------------------
section("the ladders, as pure functions")
ok([tm.oe_votes(t * T) for t in (0, 9, 10, 20, 40, 80)] == [1, 1, 2, 3, 4, 5],
   "OE votes: 0 → 1, 10 → 2, 20 → 3, 40 → 4, 80 → 5")
ok(tm.whole_percent_shares({"a": 1, "b": 1, "c": 1}) == {"a": 34, "b": 33, "c": 33},
   "a three-way split is whole percentages summing to 100")
ok(tm.whole_percent_shares({"a": 0.999, "b": 0.001}) == {"a": 99, "b": 1},
   "…and every initiative on the slate keeps at least 1%")

# ---------------------------------------------------------------------------
section("an ME slate is whole percentages of one commit")
HA, HB = signup("electcheckA"), signup("electcheckB")
c.get("/wallet", headers=HA); c.get("/wallet", headers=HB)
give("electcheckA", 100); give("electcheckB", 100)
db = SessionLocal()
race = None
for mm in db.query(_m.Mission).filter(_m.Mission.winning_tiv_id.is_(None),
                                      _m.Mission.current_phase.in_(("pre", "initiative"))).all():
    ts = [t.id for t in db.query(_m.Initiative).filter(_m.Initiative.mission_id == mm.id).all()]
    if len(ts) >= 2:
        race = (mm.id, mm.cause_id, mm.cycle_num, ts[:2])
        break
db.close()
assert race, "the pilot data has no open initiative election with two candidates"
MID, CAUSE, CYCLE, (WIN, LOSE) = race
r = c.put(f"/missions/{MID}/p1/votes", headers=HA,
          json={"mission_id": MID, "shares": {WIN: 1, LOSE: 2}, "ebx": 30})
ok(r.status_code == 200, "a slate is accepted", f"HTTP {r.status_code} {r.text[:120]}")
db = SessionLocal()
rows = {v.tiv_id: v for v in db.query(_m.VoteP1).filter(
    _m.VoteP1.ben_id == ben_id("electcheckA"), _m.VoteP1.mission_id == MID).all()}
db.close()
ok(round(rows[WIN].share, 2) == 0.33 and round(rows[LOSE].share, 2) == 0.67,
   "1:2 is stored as 33% / 67%", f"{rows[WIN].share} / {rows[LOSE].share}")
ok(sum(v.stake_ct for v in rows.values()) == 30 * T, "…and the rows sum to the commit")
r = c.put(f"/missions/{MID}/p1/votes", headers=HA,
          json={"mission_id": MID, "shares": {WIN: 0.33, LOSE: 0.67}, "ebx": 60})
db = SessionLocal()
rows = {v.tiv_id: v for v in db.query(_m.VoteP1).filter(
    _m.VoteP1.ben_id == ben_id("electcheckA"), _m.VoteP1.mission_id == MID).all()}
db.close()
ok(rows[WIN].stake_ct == 1980 and rows[LOSE].stake_ct == 4020,
   "adding tokens keeps the ratios — 60 tokens split 33/67",
   f"{rows[WIN].stake_ct} / {rows[LOSE].stake_ct}")

# B carries the winner.
c.put(f"/missions/{MID}/p1/votes", headers=HB,
      json={"mission_id": MID, "shares": {WIN: 1}, "ebx": 100})
tally = c.get(f"/missions/{MID}/p1/tally").json()
ok(tally["entries"][0]["tiv_id"] == WIN, "the tally leads with the winner")

# ---------------------------------------------------------------------------
section("a losing initiative is re-listed WITHOUT its votes")
db = SessionLocal()
before_other = {v.tiv_id: v.ebx_committed for v in db.query(_m.VoteP1).filter(_m.VoteP1.mission_id == MID)}
winner = crud.finalize_p1(db, MID)
lose_mission = db.get(_m.Initiative, LOSE).mission_id
db.close()
ok(winner == WIN, "finalize_p1 elects the leader")
ok(lose_mission != MID, "the loser moved to the cause's next election", lose_mission)
tiv = c.get(f"/initiatives/{LOSE}").json()
ok(float(tiv.get("ebx_committed") or 0) == 0.0,
   "its committed total starts at zero there — last race's tokens do not follow it",
   str(tiv.get("ebx_committed")))
listed = {t["id"]: t for t in c.get("/initiatives", params={"mission_id": lose_mission}).json()}
ok(float((listed.get(LOSE) or {}).get("ebx_committed") or 0) == 0.0,
   "…in the list endpoint the cards read as well")
t2 = c.get(f"/missions/{lose_mission}/p1/tally").json()
ok(all(e["tiv_id"] != LOSE for e in t2["entries"]), "…and in the new race's tally")
r = c.put(f"/missions/{lose_mission}/p1/votes", headers=HA,
          json={"mission_id": lose_mission, "shares": {LOSE: 1}, "ebx": 0})
ok(r.status_code == 200, "its old backer can vote for it again in the new race",
   f"HTTP {r.status_code} {r.text[:120]}")
r = c.put(f"/missions/{MID}/p1/votes", headers=HA,
          json={"mission_id": MID, "shares": {WIN: 1}, "ebx": 5})
ok(r.status_code == 400, "a decided initiative election refuses a new slate", f"HTTP {r.status_code}")

# ---------------------------------------------------------------------------
section("organization votes follow the stake on the doubling ladder")
rows = c.get("/wallet/rows").json()
ACTIVE = next(x["mission_id"] for x in rows if x["is_active_race"])
FAR = next((x["mission_id"] for x in rows if not x["is_active_race"]), None)
db = SessionLocal()
orgs = [o.id for o in db.query(_m.Organization).limit(2).all()]
db.close()
HC, HD, HE = signup("electcheckC"), signup("electcheckD"), signup("electcheckE")
for h in ("electcheckC", "electcheckD", "electcheckE"):
    give(h, 90)
for h in (HC, HD, HE):
    c.get("/wallet", headers=h)
before = {e["org_id"]: e["net_votes"] for e in c.get(f"/missions/{ACTIVE}/p2/tally").json()["entries"]}
r = c.put("/wallet/org", headers=HC, json={"mission_id": ACTIVE, "org_id": orgs[0]})
ok(r.status_code == 200, "anyone may vote in this week's race with no tokens", f"HTTP {r.status_code} {r.text[:100]}")
c.post("/wallet/commit", headers=HD, json={"mission_id": ACTIVE, "target_ct": 20 * T, "org_id": orgs[0]})
c.post("/wallet/commit", headers=HE, json={"mission_id": ACTIVE, "target_ct": 80 * T, "org_id": orgs[1]})
after = {e["org_id"]: e["net_votes"] for e in c.get(f"/missions/{ACTIVE}/p2/tally").json()["entries"]}
ok(after.get(orgs[0], 0) - before.get(orgs[0], 0) == 1 + 3,
   "0 tokens = 1 vote, 20 tokens = 3 votes", f"+{after.get(orgs[0], 0) - before.get(orgs[0], 0)}")
ok(after.get(orgs[1], 0) - before.get(orgs[1], 0) == 5,
   "80 tokens = 5 votes", f"+{after.get(orgs[1], 0) - before.get(orgs[1], 0)}")
row = next(x for x in c.get("/wallet", headers=HE).json()["rows"] if x["mission_id"] == ACTIVE)
ok(row["my_votes"] == 5 and row["can_take_part"], "the row reports my_votes and can_take_part")

section("without an ME stake, only this week's race is open")
if FAR:
    r = c.put("/wallet/org", headers=HC, json={"mission_id": FAR, "org_id": orgs[0]})
    ok(r.status_code == 400, "a far race refuses a free vote", f"HTTP {r.status_code}")
    r = c.post("/wallet/commit", headers=HC, json={"mission_id": FAR, "target_ct": 10 * T})
    ok(r.status_code == 400, "…and money", f"HTTP {r.status_code}")
    far_row = next(x for x in c.get("/wallet", headers=HC).json()["rows"] if x["mission_id"] == FAR)
    ok(not far_row["can_take_part"], "…and the row says so")
    r = c.put("/wallet/org", headers=HA, json={"mission_id": MID, "org_id": orgs[0]})
    ok(r.status_code == 200, "a backer of a mission's initiative election may vote in its race any week",
       f"HTTP {r.status_code} {r.text[:100]}")
else:
    ok(True, "(only one open race)")

# ---------------------------------------------------------------------------
section("staff: the ME reset and the organization backfill")
HS = signup("electcheckStaff")
db = SessionLocal()
st = db.query(_m.BenefactorAccount).filter(_m.BenefactorAccount.handle == "electcheckStaff").one()
st.role = "admin"
db.commit(); db.close()
r = c.post("/admin/elections/me-reset", headers=HS)
ok(r.status_code == 200 and r.json()["dry_run"], "the ME reset is a dry run by default", f"HTTP {r.status_code}")
r = c.post("/admin/elections/me-reset?dry_run=false", headers=HS)
again = c.post("/admin/elections/me-reset", headers=HS).json()
ok(all(v["rows_changed"] == 0 and v["rows_dropped"] == 0 for v in again["missions"].values()),
   "…and after it runs, a second pass finds nothing to change")
ok(c.post("/admin/elections/me-reset", headers=HA).status_code == 403, "…and it is staff-only")
past = c.get("/admin/elections/unelected-orgs", headers=HS).json()
ok(isinstance(past, list), "past races with no organization are listed", f"{len(past)} race(s)")
if past:
    target = past[0]
    r = c.post(f"/admin/missions/{target['mission_id']}/backfill-org", headers=HS,
               json={"org_id": orgs[0], "mission_statement": "Backfill check statement."})
    ok(r.status_code == 200 and r.json().get("winning_org_id"),
       "backfill elects an organization in a past race", r.text[:140])
    m = c.get(f"/missions/{target['mission_id']}").json()
    ok(m.get("winning_org_id") and m.get("current_phase") == "budget",
       "…through finalize_p2: the mission moves on to budgeting")
    left = [x["mission_id"] for x in c.get("/admin/elections/unelected-orgs", headers=HS).json()]
    ok(target["mission_id"] not in left, "…and drops off the backfill list")
open_race = next((x["mission_id"] for x in c.get("/wallet/rows").json()), None)
if open_race:
    db = SessionLocal()
    mm = db.get(_m.Mission, open_race)
    from datetime import datetime as _dt
    still_open = _w._vote_day(mm) > _dt.utcnow()
    db.close()
    if still_open:
        r = c.post(f"/admin/missions/{open_race}/backfill-org", headers=HS, json={"org_id": orgs[0]})
        ok(r.status_code == 400, "an organization election still open cannot be backfilled", f"HTTP {r.status_code}")

# ---------------------------------------------------------------------------
section("what the count is made of (2026-09-17b)")
# `ebx_committed` is derived from the money (`stake_ct`) and is what every
# phase-1 tally and the phase-2 carry actually count. A row where the two
# disagree is an election counting what the wallet does not hold — the reset
# repairs it wherever it is, including in a decided election, because a repair
# is not a re-vote.
db = SessionLocal()
drift = db.query(_m.VoteP1).filter(_m.VoteP1.stake_ct > 0).first()
drift_id, before_ct = drift.id, int(drift.stake_ct)
drift.ebx_committed = float(drift.ebx_committed or 0) + 0.37
db.commit(); db.close()
rep = c.post("/admin/elections/me-reset", headers=HS).json()
ok(rep["rows_repaired"] >= 1, "a dry run SEES a row whose ebx and its ct disagree",
   f"{rep['rows_repaired']} row(s)")
db = SessionLocal()
ok(abs(float(db.get(_m.VoteP1, drift_id).ebx_committed) - before_ct / T) > 0.005,
   "…and a dry run does not touch it")
db.close()
c.post("/admin/elections/me-reset?dry_run=false", headers=HS)
db = SessionLocal()
row = db.get(_m.VoteP1, drift_id)
ok(int(row.stake_ct) == before_ct, "the repair moves no money — the ct is untouched")
ok(abs(float(row.ebx_committed) - before_ct / T) < 1e-9,
   "…and the counted figure is the money again", f"{row.ebx_committed} = {before_ct}ct")
db.close()
ok(c.post("/admin/elections/me-reset", headers=HS).json()["rows_repaired"] == 0,
   "…and a second pass finds nothing left to repair")

# A re-listed loser starts its next race with nothing behind it. That is true of
# the RATING too: it is a vote like any other and does not follow the idea.
db = SessionLocal()
loser = db.get(_m.Initiative, LOSE)
old_mission, new_mission = None, None
old_mission = db.get(_m.Initiative, LOSE).mission_id
for v in db.query(_m.VoteP1).filter(_m.VoteP1.tiv_id == LOSE).all():
    v.valence = "harmful"
db.commit()
crud.recompute_tiv_rating(db, LOSE)
db.expire_all()
rated_here = float(db.get(_m.Initiative, LOSE).rating_avg or 0), int(db.get(_m.Initiative, LOSE).rating_count or 0)
ok(rated_here[1] > 0, "an initiative is rated by the votes cast in its own race",
   f"{rated_here[1]} voter(s), avg {rated_here[0]}")
from app import bootstrap as _bs                       # noqa: E402
_bs.ensure_mission(db, CAUSE, (CYCLE or 0) + 1)
db.commit()
here_now = db.query(_m.VoteP1).filter(_m.VoteP1.tiv_id == LOSE,
                                      _m.VoteP1.mission_id == old_mission).count()
everywhere = db.query(_m.VoteP1).filter(_m.VoteP1.tiv_id == LOSE).count()
ok(everywhere > here_now,
   "the re-listed loser still has rows standing in the race it LOST",
   f"{everywhere} row(s) in all, {here_now} in {old_mission}")
ok(int(db.get(_m.Initiative, LOSE).rating_count or 0) == here_now,
   "…and its rating counts only the ones in the race it is running in now",
   f"rating_count {db.get(_m.Initiative, LOSE).rating_count} vs {here_now} here")
db.close()

# The unique key is per (ben, mission, tiv) now, so adopting an orphan into a
# mission where its backer already voted for it must FOLD, not collide.
db = SessionLocal()
orphan = _m.Initiative(id="electcheck-orphan", title="Election check orphan",
                       cause_id=CAUSE, mission_id=None, approved=True, status="suggested")
db.add(orphan)
db.add(_m.VoteP1(ben_id=ben_id("electcheckA"), mission_id=MID, tiv_id=orphan.id,
                 share=0.2, stake_ct=200, ebx_committed=2.0, valence="helpful"))
db.commit()
stray_mission = db.query(_m.Mission).filter(_m.Mission.cause_id == CAUSE,
                                            _m.Mission.id != MID).first()
if stray_mission is not None:
    db.add(_m.VoteP1(ben_id=ben_id("electcheckA"), mission_id=stray_mission.id,
                     tiv_id=orphan.id, share=0.1, stake_ct=100, ebx_committed=1.0,
                     valence="helpful"))
    db.commit()
db.close()
try:
    db = SessionLocal()
    crud.adopt_orphan_tivs(db)
    rows = db.query(_m.VoteP1).filter(_m.VoteP1.tiv_id == "electcheck-orphan").all()
    ok(len({(r.ben_id, r.mission_id) for r in rows}) == len(rows),
       "adopting an orphan leaves one row per benefactor per mission — no collision",
       f"{len(rows)} row(s)")
    ok(sum(int(r.stake_ct or 0) for r in rows) == (300 if stray_mission is not None else 200),
       "…and the money it carried is all still there",
       f"{sum(int(r.stake_ct or 0) for r in rows)}ct")
    db.close()
except Exception as e:                                   # pragma: no cover
    ok(False, "adopting an orphan does not raise", repr(e)[:160])

# ---------------------------------------------------------------------------
section("staff: the retroactive INITIATIVE election (2026-09-18)")
# The hmr1 case: a decision day that passed with preferences standing and no
# tokens behind them. A live election cannot elect on that — 10 EBX = 1 vote —
# so the backfill elects on the PEOPLE, and says that is what it did.
db = SessionLocal()
from datetime import timedelta as _td                      # noqa: E402
stuck = _m.Mission(id="electcheck-stuck", cause_id=CAUSE, cycle_num=97,
                   started_at=_dt_now() - _td(weeks=9), current_phase="initiative")
db.add(stuck)
db.add(_m.Initiative(id="electcheck-wanted", title="The one people stood behind",
                     cause_id=CAUSE, mission_id=stuck.id, approved=True, status="suggested"))
db.add(_m.Initiative(id="electcheck-other", title="The one nobody backed",
                     cause_id=CAUSE, mission_id=stuck.id, approved=True, status="suggested"))
db.commit()
# two preferences, no money at all
for h in ("electcheckA", "electcheckB"):
    db.add(_m.VoteP1(ben_id=ben_id(h), mission_id=stuck.id, tiv_id="electcheck-wanted",
                     share=1.0, stake_ct=0, ebx_committed=0.0, valence="helpful"))
db.commit()
db.close()
ok(c.post(f"/admin/missions/{'electcheck-stuck'}/backfill-tiv", headers=HA).status_code == 403,
   "the initiative backfill is staff-only")
stuck_list = c.get("/admin/elections/unelected-tivs", headers=HS).json()
row = next((x for x in stuck_list if x["mission_id"] == "electcheck-stuck"), None)
ok(row is not None, "a past election with nothing elected is on the backfill list",
   f"{len(stuck_list)} race(s)")
ok(row and row["preferences"] and row["preferences"][0]["tiv_id"] == "electcheck-wanted",
   "…and the list says who is standing behind what, most people first",
   str(row["preferences"][0]) if row and row["preferences"] else "none")
r = c.post("/admin/missions/electcheck-stuck/backfill-tiv", headers=HS)
ok(r.status_code == 200 and r.json().get("winning_tiv_id") == "electcheck-wanted",
   "the backfill elects the initiative with the most people behind it", r.text[:150])
ok(r.status_code == 200 and "preference" in (r.json().get("on") or ""),
   "…and records that it elected on preferences, not money",
   (r.json().get("on") if r.status_code == 200 else ""))
m = c.get("/missions/electcheck-stuck").json()
ok(m.get("winning_tiv_id") == "electcheck-wanted", "the mission carries the winner")
ok(not any(x["mission_id"] == "electcheck-stuck"
           for x in c.get("/admin/elections/unelected-tivs", headers=HS).json()),
   "…and drops off the backfill list")
db = SessionLocal()
loser = db.get(_m.Initiative, "electcheck-other")
ok(loser is not None and loser.mission_id != "electcheck-stuck",
   "the loser is re-listed in the cause's next election, as it would have been",
   f"now in {loser.mission_id if loser else '—'}")
ok(db.get(_m.Initiative, "electcheck-wanted").status == "active",
   "…and the winner is active")
db.close()
ok(c.post("/admin/missions/electcheck-stuck/backfill-tiv", headers=HS).json().get("already") is True,
   "running it again is a no-op, not a second election")
# an election still to come is refused
db = SessionLocal()
# 99, not 98: electing `stuck` (97) re-listed its loser into the cause's next
# cycle, which created 98 — the same behaviour a real election has.
soon = _m.Mission(id="electcheck-soon", cause_id=CAUSE, cycle_num=99,
                  started_at=_dt_now(), current_phase="initiative")
db.add(soon)
db.add(_m.Initiative(id="electcheck-soon-tiv", title="Not yet", cause_id=CAUSE,
                     mission_id=soon.id, approved=True, status="suggested"))
db.commit(); db.close()
rs = c.post("/admin/missions/electcheck-soon/backfill-tiv", headers=HS)
ok(rs.status_code == 400 and "still open" in rs.text,
   "an election whose day has not come is refused", f"HTTP {rs.status_code}")

print(f"\n{N} assertions · " + ("ELECTIONS CLEAN" if BAD == 0 else f"PROBLEMS: {BAD}"))
sys.exit(1 if BAD else 0)
