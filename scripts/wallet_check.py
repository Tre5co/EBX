"""wallet_check — the wallet and OE-stake endpoints, end to end.

    python3 scripts/wallet_check.py

Runs the real FastAPI app against a **throwaway copy** of `earthbucks.db`, so it
signs up accounts, moves money and never touches the pilot data. Nothing here
mocks the routers: every assertion goes through HTTP the way the page does.

What it is really guarding is the conservation law. The slate and the field
share one cell (`free`), an allocation can move between eight races, and the
failure mode is money that quietly appears or vanishes on a change of mind.

Rewritten 2026-08-27c for the finalized model
(`docs/ME_OE_FINALIZATION.md`): an allocation is a POSITION inside its own week
and EBX after the roll, the skim is a clean 10% for everyone, and the wallet's
four states are `unallocated -> committed -> minted -> donated`.
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
_tmp = Path(tempfile.mkdtemp(prefix="ebx_wallet_check_")) / "earthbucks.db"
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
from app import models as _m                      # noqa: E402
from app import token_model as tm                 # noqa: E402
from app import wallet as _w                      # noqa: E402
from app.database import SessionLocal             # noqa: E402

BAD = 0
N = 0


def ok(cond, what, detail=""):
    global BAD, N
    N += 1
    if not cond:
        BAD += 1
    print(f"  {'ok  ' if cond else 'FAIL'}  {what}" + (f"  {detail}" if detail else ""))


def section(t):
    print(f"\n=== {t}")


T = tm.CT_PER_TOKEN
c = TestClient(app)


def signup(handle):
    r = c.post("/auth/signup", json={"email": f"{handle}@wallet-check.example.com",
                                     "handle": handle, "password": "check-pw-123"})
    assert r.status_code in (200, 201), r.text
    r = c.post("/auth/login", data={"username": f"{handle}@wallet-check.example.com",
                                    "password": "check-pw-123"})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


H = signup("walletcheck1")


def wallet():
    return c.get("/wallet", headers=H).json()


def total_ct(payload):
    """Every ct this benefactor holds as a TOKEN, wherever it sits. Minted EBX
    is deliberately outside this sum — it has left the token bin, which is what
    minting means."""
    return payload["wallet"]["free_ct"] + payload["wallet"]["committed_ct"]


# ---------------------------------------------------------------------------
section("the OE table: eight open races, and fourteen over a token's life")
rows = c.get("/wallet/rows").json()
ok(len(rows) <= 8, "at most 8 rows — one per mission in phase 2", f"{len(rows)} rows")
ok(len(rows) > 0, "and not zero on the pilot data")
dates = [r["vote_date"][:10] for r in rows]
ok(dates == sorted(dates), "ordered by the philanthropy-election date")
ok(len(set(dates)) == len(dates), "one race closes per week — no two share a date")
ok(all(r["tiv_title"] for r in rows), "every row is labelled by its INITIATIVE")
ok(all(r["my_stake_ct"] == 0 and r["my_org_id"] is None for r in rows),
   "signed out, nobody has a commitment")
# ---------------------------------------------------------------------------
section("the grant: ten tokens, against this week's cause")
w = wallet()
ok(w["granted_this_week_ct"] == 10 * T, "a new account is granted 10 tokens")
ok(w["wallet"]["free_ct"] == 10 * T, "…and holds them free")
ok(w["wallet"]["next_grant_ct"] == 0, "holding 10 → next grant is 0")
ok(w["wallet"]["available_ct"] == 10 * T, "…and 10 is what is votable next")
ok(w["grant_cause_id"], "the grant carries the CAUSE it was issued against",
   str(w["grant_cause_id"]))
ok("commit_by" not in w and "commit_by_week" not in w,
   "…and no deadline, because a granted token is never both real and free")
again = wallet()
ok(again["granted_this_week_ct"] == 0, "a refresh does NOT pay a second grant")
ok(again["wallet"]["free_ct"] == 10 * T, "…and the balance is unchanged")
ok(again["rules"]["ct_per_token"] == 100, "the unit rides along in the payload")
ok(again["rules"]["oe_skim"] == 0.10, "so does the one rate")
ok(again["rules"]["oe_table_rows"] == 8, "the table is eight rows")
ok(again["rules"]["oe_lifetime_races"] == 14,
   "…and fourteen is the lifetime, not the screen")
ok("max_conversions" not in again["rules"],
   "…and the conversion budget is not advertised, because it does not exist")

# ---------------------------------------------------------------------------
section("inside its week an allocation is a POSITION — up, and down")
mid = rows[0]["mission_id"]           # the race finalizing soonest = active
before = total_ct(wallet())
r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 4 * T}).json()
ok(r["stake_ct"] == 4 * T, "set 4 tokens on a race")
ok(r["free_ct"] == 6 * T, "…unallocated drops to 6")
ok(total_ct(wallet()) == before, "conservation: nothing created", str(total_ct(wallet())))

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 6 * T}).json()
ok(r["stake_ct"] == 6 * T, "setting it again REPLACES rather than adding")
ok(r["free_ct"] == 4 * T, "…and takes the difference from the bar")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 2 * T}).json()
ok(r["stake_ct"] == 2 * T, "and it can go DOWN — this is a draft, not a ratchet")
ok(r["free_ct"] == 8 * T, "…with the difference handed back to unallocated")
ok(total_ct(wallet()) == before, "conservation holds on the way down too")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": -3 * T})
ok(r.status_code == 422, "a negative target is refused by the schema",
   f"HTTP {r.status_code}")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 999 * T}).json()
ok(r["stake_ct"] == 10 * T, "asking for more than exists lands on what there is",
   f'{r["stake_ct"]} ct')
ok(r["free_ct"] == 0, "…and the bar floors at zero, never negative")
ok(total_ct(wallet()) == before, "conservation holds at the clamp")
w2 = wallet()
ok(w2["wallet"]["committed_ct"] == before,
   "everything is committed — segments agree with rows")
ok(w2["wallet"]["minted_ct"] == 0, "and none of it is EBX yet: the week has not rolled")
ok("staked_ct" not in w2["wallet"] and "claimed_ct" not in w2["wallet"],
   "`staked` is `committed`, and `claimed` went back to meaning an org claim")

# ---------------------------------------------------------------------------
section("a stake with no philanthropy named is legal, and weighs nothing")
row = next(x for x in wallet()["rows"] if x["mission_id"] == mid)
ok(row["my_org_id"] is None, "ct can sit in a race with no philanthropy named")
ok(row["my_stake_ct"] == 10 * T, "…funding it in full")
ok(row["movable"], "…and it stays movable: there is nothing to harden into")

# ---------------------------------------------------------------------------
section("the amount and the philanthropy arrive in one transaction")
_db = SessionLocal()
_org = _db.query(_m.Organization).first()
_org_id = _org.id if _org else None
_db.close()
if _org_id:
    r = c.post("/wallet/commit", headers=H,
               json={"mission_id": mid, "target_ct": 10 * T, "org_id": _org_id}).json()
    ok(r["org_id"] == _org_id, "one call sets the amount and the vote")
    ok(r["hardens_week"] == wallet()["hardens_week"],
       "…and the row says which week it hardens in")
    ok(r["movable"], "…while staying movable until then")
else:
    ok(False, "(no organization in the database to vote for)")


# ---------------------------------------------------------------------------
section("the week roll: a standing OE allocation becomes EBX")
# Age the row by a week rather than waiting one. `committed_week` is the whole
# of the rule, so setting it back is exactly what a Tuesday does.
_db = SessionLocal()
_b1_id = _db.query(_m.BenefactorAccount).filter(
    _m.BenefactorAccount.handle == "walletcheck1").first().id
_v = _db.query(_m.VoteP2).filter(_m.VoteP2.ben_id == _b1_id,
                                 _m.VoteP2.mission_id == mid).first()
_v.committed_week = _w.current_week() - 1
_db.commit()
_db.close()

w3 = wallet()          # GET /wallet applies the roll lazily
ok(w3["wallet"]["minted_ct"] == 10 * T, "the allocation minted into EBX",
   f'{w3["wallet"]["minted_ct"]} ct')
ok(w3["wallet"]["committed_ct"] == 0, "…and left the committed segment")
ok(w3["wallet"]["tokens_ct"] == 0, "…and the token bin entirely: EBX is not a token")
_row = next(x for x in w3["rows"] if x["mission_id"] == mid)
ok(not _row["movable"], "hardened ct is not movable")
ok(_row["my_minted_ct"] == 10 * T, "…and the row says so")
r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 2 * T})
ok(r.status_code == 400, "…so setting it lower is refused", f"HTTP {r.status_code}")
ok("EBX" in r.json().get("detail", ""),
   "…and the refusal says why, in the model's own word", r.json().get("detail", "")[:60])
_db = SessionLocal()
_v = _db.query(_m.VoteP2).filter(_m.VoteP2.ben_id == _b1_id,
                                 _m.VoteP2.mission_id == mid).first()
_mint_events = [e for e in (_v.provenance or []) if e.get("kind") == "mint_ebx"]
ok(len(_mint_events) == 1, "one mint event is written, not one per dial",
   f"{len(_mint_events)} events")
ok(_mint_events[0]["target_id"] == _org_id,
   "…naming the philanthropy the ct minted behind")
_db.close()
w4 = wallet()
ok(w4["granted_this_week_ct"] == 0, "the roll did not pay a grant")

# ---------------------------------------------------------------------------
section("moving between races is free, and unlimited inside the week")
H3 = signup("walletcheck3")
_rows3 = c.get("/wallet", headers=H3).json()["rows"]
_a, _b = _rows3[0]["mission_id"], _rows3[1]["mission_id"]
c.post("/wallet/commit", headers=H3, json={"mission_id": _a, "target_ct": 6 * T})
moved = 0
for _ in range(5):
    r = c.post("/wallet/move", headers=H3,
               json={"from_mission_id": _a, "to_mission_id": _b, "ct": 1 * T,
                     "org_id": _org_id})
    if r.status_code == 200:
        moved += 1
ok(moved == 5, "five moves in one week, and none of them refused", f"{moved} of 5")
w5 = c.get("/wallet", headers=H3).json()
ok(sum(r["my_stake_ct"] for r in w5["rows"]) == 6 * T,
   "…and the money is conserved across every one")
_dest = next(r for r in w5["rows"] if r["mission_id"] == _b)
ok(_dest["my_org_id"] == _org_id, "a move carries its philanthropy vote with it")
ok(_dest["my_stake_ct"] == 5 * T, "…and lands the ct it moved", f'{_dest["my_stake_ct"]}')
r = c.post("/wallet/move", headers=H3,
           json={"from_mission_id": _a, "to_mission_id": _b, "ct": 1 * T})
ok(r.status_code == 422, "a move without a philanthropy is refused by the schema",
   f"HTTP {r.status_code}")
r = c.post("/wallet/convert", headers=H3, json={"from_mission_id": _a,
                                                "to_mission_id": _b, "ct": T,
                                                "org_id": _org_id})
ok(r.status_code == 404, "/wallet/convert is gone with the budget it spent",
   f"HTTP {r.status_code}")

# ---------------------------------------------------------------------------
section("withdrawal: purchased tokens only, and only before they vote")
r = c.post("/wallet/withdraw", headers=H3, json={"ct": 1 * T})
ok(r.status_code == 400, "a granted token cannot be withdrawn",
   f"HTTP {r.status_code}")
ok("purchased" in r.json().get("detail", "").lower(),
   "…and the refusal says which tokens can be", r.json().get("detail", "")[:60])
H4 = signup("walletcheck4")
c.get("/wallet", headers=H4)
_db = SessionLocal()
_b4 = _db.query(_m.BenefactorAccount).filter(
    _m.BenefactorAccount.handle == "walletcheck4").first()
_b4.free_ct = int(_b4.free_ct or 0) + 5 * T
_b4.purchased_ct = 5 * T                     # as a purchase would write it
_db.commit()
_db.close()
w6 = c.get("/wallet", headers=H4).json()["wallet"]
ok(w6["purchased_ct"] == 5 * T and w6["grant_held_ct"] == 10 * T,
   "the bar draws granted and purchased apart")
r = c.post("/wallet/withdraw", headers=H4, json={"ct": 2 * T}).json()
ok(r["withdrawn_ct"] == 2 * T, "purchased ct withdraws")
ok(r["cash_ct"] == 2 * T, "…into CASH, never back into tokens")
ok(r["purchased_ct"] == 3 * T and r["free_ct"] == 13 * T,
   "…and both balances drop by exactly what left")
r = c.post("/wallet/withdraw", headers=H4, json={"ct": 99 * T})
ok(r.status_code == 400, "…and you cannot withdraw more purchased ct than you hold",
   f"HTTP {r.status_code}")

# ---------------------------------------------------------------------------
section("two doors: granted ct enters this week's race, purchased ct enters any")
_rows4 = c.get("/wallet", headers=H4).json()["rows"]
_active = _rows4[0]["mission_id"]
_far = _rows4[-1]["mission_id"]
ok(_rows4[0]["is_active_race"], "the race closing soonest is this week's")
ok(not _rows4[-1]["is_active_race"], "…and the last row is not")
r = c.post("/wallet/commit", headers=H4,
           json={"mission_id": _far, "target_ct": 99 * T}).json()
ok(r["stake_ct"] == 3 * T,
   "a far race takes the PURCHASED slice and no more", f'{r["stake_ct"]} ct')
r = c.post("/wallet/commit", headers=H4,
           json={"mission_id": _active, "target_ct": 99 * T}).json()
ok(r["stake_ct"] == 10 * T,
   "…while this week's race can take the whole balance", f'{r["stake_ct"]} ct')
ok(r["free_ct"] == 0, "…leaving nothing unallocated")


# ---------------------------------------------------------------------------
section("the initiative election: one amount, one slate, and the WALLET pays")
# The ME table spent `10 + localStorage.ebx_purchased_ebx` until 2026-08-27c —
# a budget invented in the browser, which is why the allocations panel could
# report the same tokens twice. `replace_p1_shares` reconciles against the
# account now, and the slate is percentages of the one amount.
H6 = signup("walletcheck6")
_w6 = c.get("/wallet", headers=H6).json()
_cause6 = _w6["grant_cause_id"]
_db = SessionLocal()
_open6 = [mm for mm in _db.query(_m.Mission).filter(
    _m.Mission.winning_tiv_id.is_(None)).all() if mm.cause_id == _cause6]
_target6 = None
for mm in _open6:
    _t = _db.query(_m.Initiative).filter(_m.Initiative.mission_id == mm.id).all()
    if len(_t) >= 2:
        _target6 = (mm.id, [x.id for x in _t[:2]])
        break
_other = next((mm.id for mm in _db.query(_m.Mission).filter(
    _m.Mission.winning_tiv_id.is_(None)).all() if mm.cause_id != _cause6), None)
_other_tivs = ([x.id for x in _db.query(_m.Initiative).filter(
    _m.Initiative.mission_id == _other).all()[:1]] if _other else [])
_db.close()
if _target6 is None:
    ok(True, f"(no open initiative election for {_cause6} with two candidates)")
else:
    _mid6, _t6 = _target6
    r = c.put(f"/missions/{_mid6}/p1/votes", headers=H6,
              json={"mission_id": _mid6, "shares": {_t6[0]: 0.75, _t6[1]: 0.25},
                    "ebx": 8})
    ok(r.status_code == 200, "a slate with an amount is accepted", f"HTTP {r.status_code}")
    _wal = c.get("/wallet", headers=H6).json()["wallet"]
    ok(_wal["free_ct"] == 2 * T, "the WALLET paid for it — 8 of 10 tokens left the bar",
       f'{_wal["free_ct"]} ct')
    ok(_wal["committed_ct"] == 8 * T,
       "…and the committed segment holds them, ME and OE in one number")
    _db = SessionLocal()
    _b6 = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == "walletcheck6").first()
    _p1 = {v.tiv_id: v for v in _db.query(_m.VoteP1).filter(
        _m.VoteP1.ben_id == _b6.id, _m.VoteP1.mission_id == _mid6).all()}
    ok(sum(int(v.stake_ct or 0) for v in _p1.values()) == 8 * T,
       "the rows sum to the commit exactly — largest-remainder, nothing lost")
    ok(int(_p1[_t6[0]].stake_ct) == 600 and int(_p1[_t6[1]].stake_ct) == 200,
       "…split by percentage: 75/25 of 8 tokens",
       f"{_p1[_t6[0]].stake_ct} / {_p1[_t6[1]].stake_ct}")
    _db.close()
    r = c.put(f"/missions/{_mid6}/p1/votes", headers=H6,
              json={"mission_id": _mid6, "shares": {_t6[0]: 1.0}, "ebx": 3})
    _wal = c.get("/wallet", headers=H6).json()["wallet"]
    ok(_wal["free_ct"] == 7 * T,
       "lowering the amount hands the difference back — an ME allocation is soft",
       f'{_wal["free_ct"]} ct')
    ok(_wal["committed_ct"] == 3 * T, "…and the committed segment follows it down")
    r = c.put(f"/missions/{_mid6}/p1/votes", headers=H6,
              json={"mission_id": _mid6,
                    "shares": {t: 1 for t in [_t6[0], _t6[1]]}, "ebx": 3})
    ok(r.status_code == 200, "a 2-way split is fine")
    r = c.put(f"/missions/{_mid6}/p1/votes", headers=H6,
              json={"mission_id": _mid6,
                    "shares": {f"ghost-{i}": 1 for i in range(11)}, "ebx": 3})
    ok(r.status_code == 400, "an 11-way split is refused", f"HTTP {r.status_code}")
    ok("10" in r.json().get("detail", ""),
       "…and the refusal names the cap", r.json().get("detail", "")[:60])
    if _other and _other_tivs:
        r = c.put(f"/missions/{_other}/p1/votes", headers=H6,
                  json={"mission_id": _other, "shares": {_other_tivs[0]: 1.0},
                        "ebx": 5})
        _wal2 = c.get("/wallet", headers=H6).json()["wallet"]
        _db = SessionLocal()
        _spent = sum(int(v.stake_ct or 0) for v in _db.query(_m.VoteP1).filter(
            _m.VoteP1.ben_id == _b6.id, _m.VoteP1.mission_id == _other).all())
        _db.close()
        ok(_spent == 0,
           "a granted token cannot enter ANOTHER cause's initiative election",
           f"{_spent} ct landed")
    else:
        ok(True, "(no second open initiative election to test the door with)")

# ---------------------------------------------------------------------------
section("one benefactor cannot see or spend another's money")
H5 = signup("walletcheck5")
w7 = c.get("/wallet", headers=H5).json()
ok(w7["wallet"]["free_ct"] == 10 * T, "a fresh account gets its own 10")
ok(all(r["my_stake_ct"] == 0 for r in w7["rows"]),
   "…and sees none of anybody else's commitments")

section("closed races refuse money")
_db = SessionLocal()
_closed = _db.query(_m.Mission).filter(_m.Mission.winning_org_id.is_not(None)).first()
_closed_id = _closed.id if _closed else None
_db.close()
if _closed_id:
    r = c.post("/wallet/commit", headers=H5,
               json={"mission_id": _closed_id, "target_ct": T})
    ok(r.status_code == 400, "a decided philanthropy election takes nothing new",
       f"HTTP {r.status_code}")
else:
    ok(True, "(no decided organization election in this database)")

# ---------------------------------------------------------------------------
section("the initiative election: early EBX for the winner's backers, a mark for the rest")
from app import crud as _crud                    # noqa: E402
_db = SessionLocal()
_open_p1 = _db.query(_m.Mission).filter(_m.Mission.winning_tiv_id.is_(None)).all()
_target = next((mm for mm in _open_p1
                if len(_db.query(_m.Initiative).filter(
                    _m.Initiative.mission_id == mm.id).all()) >= 2), None)
if _target is None:
    ok(True, "(no phase-1 mission with two initiatives in this database)")
else:
    _all_tivs = _db.query(_m.Initiative).filter(
        _m.Initiative.mission_id == _target.id).all()
    # Back the initiative that is ALREADY leading, so this benefactor is
    # guaranteed to be on the winning side and the early-EBX path is actually
    # exercised. Picking two arbitrary initiatives and hoping is how the old
    # harness ended up asserting nothing on a database where a third one led.
    _lead = _crud.p1_tally(_db, _target.id)["entries"]
    _lead_id = _lead[0]["tiv_id"] if _lead else _all_tivs[0].id
    _tivs = ([t for t in _all_tivs if t.id == _lead_id]
             + [t for t in _all_tivs if t.id != _lead_id])[:2]
    _bA = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == "walletcheck1").first()
    _bB = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == "walletcheck2").first()
    if _bB is None:
        signup("walletcheck2")
        _bB = _db.query(_m.BenefactorAccount).filter(
            _m.BenefactorAccount.handle == "walletcheck2").first()
    for _b, _tiv, _ct in ((_bA, _tivs[0], 600), (_bB, _tivs[1], 200)):
        _db.add(_m.VoteP1(ben_id=_b.id, mission_id=_target.id, tiv_id=_tiv.id,
                          share=1.0, ebx_committed=_ct / T, stake_ct=_ct,
                          valence="helpful", committed=True))
    _db.commit()
    _mid_p1, _cause_p1 = _target.id, _target.cause_id
    _tiv_a, _tiv_b = _tivs[0].id, _tivs[1].id
    _bA_id, _bB_id = _bA.id, _bB.id
    _db.close()

    _db = SessionLocal()
    _winner = _crud.finalize_p1(_db, _mid_p1)
    ok(_winner is not None, "a race with commitments in it elects an initiative",
       str(_winner))
    _stakes = {v.ben_id: v for v in _db.query(_m.VoteP2).filter(
        _m.VoteP2.mission_id == _mid_p1).all()}
    ok(set(_stakes) >= {_bA_id, _bB_id},
       "BOTH backers are carried into the organization election — including the loser's")
    ok(_stakes[_bA_id].stake_ct == 600 and _stakes[_bB_id].stake_ct == 200,
       "…whole: the initiative election is a routing step, and it skims nothing",
       f"{_stakes[_bA_id].stake_ct} / {_stakes[_bB_id].stake_ct}")
    # Which initiative wins depends on what was already committed in this
    # mission, so who backed the winner is not ours to assume — and on the
    # pilot data it can be NEITHER. Assert the rule per benefactor instead of
    # picking a winner in advance.
    _backed = {_bA_id: _tiv_a, _bB_id: _tiv_b}
    _won_ids = [b for b, t in _backed.items() if t == _winner]
    _lost_ids = [b for b, t in _backed.items() if t != _winner]
    for _bid in _won_ids:
        _v = _stakes[_bid]
        ok(_v.minted_ct == _v.stake_ct,
           f"ben {_bid} backed the winner and is minted ON THE SPOT — the early EBX",
           f"{_v.minted_ct} of {_v.stake_ct} ct")
        ok(_v.marked_tiv_id is None, "…and carries no mark, because nothing of theirs lost")
        ok(not _w.is_movable(_v, _w.current_week()),
           "…and the early EBX is locked in this race until it finalizes")
    for _bid in _lost_ids:
        _v = _stakes[_bid]
        ok(_v.minted_ct == 0, f"ben {_bid} backed a loser and mints nothing yet")
        ok(_v.marked_tiv_id == _backed[_bid],
           "…and holds a token MARKED with the initiative it voted for",
           str(_v.marked_tiv_id))
        ok(_w.is_movable(_v, _w.current_week()),
           "…which is still movable, to any open organization election")
    ok(bool(_won_ids) or bool(_lost_ids), "every backer landed on one side or the other")
    _won_id = (_won_ids or _lost_ids)[0]
    _won = _stakes[_won_id]
    _lost = _stakes[_lost_ids[0]] if _lost_ids else _won
    _el = [e for e in (_lost.provenance or []) if e.get("kind") == "settle_me"]
    ok(len(_el) == 1, "coin element 1 is written once")
    ok(_el[0]["cause_id"] == _cause_p1,
       "…carrying the cause this benefactor voted in")
    ok(_el[0]["winner_id"] == _winner and _el[0]["outcome"] == "lost",
       "…and the initiative that WON, so a losing coin still knows the argument")
    _before = len(_won.provenance or [])
    _crud.finalize_p1(_db, _mid_p1)
    _again = _db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1,
                                         _m.VoteP2.ben_id == _won_id).first()
    ok(len(_again.provenance or []) == _before,
       "finalizing twice does not write the elements twice")
    ok(_again.stake_ct == _won.stake_ct, "…or double the stake")

    # ---------------------------------------------------------------------
    section("the organization election: a clean 10%, and the rest is EBX")
    _org2 = _db.query(_m.Organization).first()
    _cand = _m.MissionCandidacy(mission_id=_mid_p1, org_id=_org2.id,
                                status="nominated",
                                mission_statement="check harness candidacy")
    _db.add(_cand)
    for _v in _db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1).all():
        _v.org_id = _org2.id
        _v.votes = 1
    _db.commit()
    _won_org = _crud.finalize_p2(_db, _mid_p1)
    ok(_won_org is not None, "a race with votes in it elects a philanthropy",
       str(_won_org))
    _after = {v.ben_id: v for v in _db.query(_m.VoteP2).filter(
        _m.VoteP2.mission_id == _mid_p1).all()}
    for _bid, _v in _after.items():
        if int(_v.stake_ct or 0) <= 0:
            continue
        ok(_v.minted_ct == _v.stake_ct,
           f"ben {_bid}: everything still a token became EBX at the close",
           f"{_v.minted_ct} of {_v.stake_ct}")
        ok(_v.donated_ct == tm.settle_oe(int(_v.stake_ct)).donated_ct,
           f"ben {_bid}: a clean 10% crossed as the first donation tranche",
           f"{_v.donated_ct} ct")
        ok(_v.marked_tiv_id is None, f"ben {_bid}: the mark is spent")
    _rates = {int(v.donated_ct) * 10 == int(v.stake_ct) for v in _after.values()
              if int(v.stake_ct or 0) > 0}
    ok(_rates == {True},
       "…and it is the SAME 10% for the winner's backer and the loser's")
    _tranches = [e for e in (_after[_won_id].provenance or [])
                 if e.get("kind") == "donate"]
    ok(len(_tranches) == 1, "one tranche is booked, dated for the deduction")
    ok(all(v.org_id is not None for v in _after.values()
           if int(v.stake_ct or 0) > 0),
       "every stake ends the race naming a philanthropy — including EARLY EBX, "
       "which minted before there was one to name")
    _crud.finalize_p2(_db, _mid_p1)
    _twice = _db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1,
                                         _m.VoteP2.ben_id == _won_id).first()
    ok(int(_twice.donated_ct) == tm.settle_oe(int(_twice.stake_ct)).donated_ct,
       "…and settling twice does not skim twice")
    _db.close()

# ---------------------------------------------------------------------------
section("final conservation sweep")
_db = SessionLocal()
for _handle in ("walletcheck1", "walletcheck3", "walletcheck4", "walletcheck5"):
    _b = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == _handle).first()
    ok(int(_b.purchased_ct or 0) <= int(_b.free_ct or 0),
       f"{_handle}: the purchased slice never exceeds the balance holding it",
       f"{_b.purchased_ct} of {_b.free_ct}")
    _wal = _w.read_wallet(_db, _b.id)
    ok(_wal.free_ct >= 0 and _wal.committed_ct >= 0 and _wal.minted_ct >= 0
       and _wal.donated_ct >= 0,
       f"{_handle}: no segment is negative")
    ok(_wal.tokens_ct == _wal.free_ct + _wal.committed_ct,
       f"{_handle}: the token bin is unallocated + committed, and nothing else")
_db.close()

shutil.rmtree(_tmp.parent, ignore_errors=True)
print(f"\n{N} assertions · " + (f"PROBLEMS: {BAD}" if BAD else "WALLET CLEAN"))
sys.exit(1 if BAD else 0)
