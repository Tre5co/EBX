"""wallet_check — the wallet and OE-stake endpoints, end to end.

    python3 scripts/wallet_check.py

Runs the real FastAPI app against a **throwaway copy** of `earthbucks.db`, so it
signs up accounts, moves money and never touches the pilot data. Nothing here
mocks the routers: every assertion goes through HTTP the way the page does.

What it is really guarding is the conservation law. The slate and the field
share one cell (`free`), an allocation can move between eight races, and the
failure mode is money that quietly appears or vanishes on a change of mind.

Rewritten 2026-08-27c for the finalized model
(`docs/_to_delete/ME_OE_FINALIZATION.md`): an allocation is a POSITION inside its own week
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
section("the grant: ten tokens in EVERY initiative election (ruling 19, 2026-10-09)")
w = wallet()
ok(w["granted_this_week_ct"] == 0 and w["wallet"]["free_ct"] == 0,
   "nothing is paid into the wallet: the grant belongs to the elections", str(w["wallet"]["free_ct"]))
_g0 = w["grant"]
ok(_g0["per_election_ct"] == 10 * T and w["rules"]["me_grant_ct"] == 10 * T,
   "each initiative election carries ten granted tokens")
ok(_g0["open"] >= 1 and len(_g0["elections"]) == _g0["open"],
   "…and the wallet lists every open initiative election", f'{_g0["open"]} open')
ok(all(e["left_ct"] == 10 * T and e["used_ct"] == 0 for e in _g0["elections"]),
   "…with all ten unused in each, for a new account")
ok(_g0["left_ct"] == 10 * T * _g0["open"], "…so the grant left is ten per open election")
ok(w["wallet"]["next_grant_ct"] == 10 * T, "the grant is 10, whatever is held")
ok(w["wallet"]["available_ct"] == 10 * T, "…and 10 is what one election takes before any purchased token")
ok(w["grant_week"] == w["week"] and "grant_cause_id" not in w,
   "the grant carries no cause (2026-09-16)", str(w.get("grant_week")))
ok("commit_by" not in w and "commit_by_week" not in w,
   "…and no deadline, because a granted token is never both real and free")
again = wallet()
ok(again["granted_this_week_ct"] == 0, "a refresh does NOT pay anything")
ok(again["wallet"]["free_ct"] == 0, "…and the balance is unchanged")
ok(again["rules"]["ct_per_token"] == 100, "the unit rides along in the payload")
ok(again["rules"]["me_skim"] == 0.10 and again["rules"]["oe_skim"] == 0.10,
   "so do the two skim rates")
ok(again["rules"]["oe_table_rows"] == 8, "the table is eight rows")
ok(again["rules"]["oe_lifetime_races"] == 14,
   "…and fourteen is the lifetime, not the screen")
ok("max_conversions" not in again["rules"],
   "…and the conversion budget is not advertised, because it does not exist")

# ---------------------------------------------------------------------------
section("inside its week an allocation is a POSITION — up, and down")
mid = rows[0]["mission_id"]           # the race finalizing soonest = active


def voted_in_me(handle, mission_id):
    """Ruling 20 (2026-10-09): only someone who voted in a mission's initiative
    election may put tokens into its organization election. The races in the
    table are already past their initiative election, so the check records the
    vote the way a 0-token ballot leaves it: a share, no stake."""
    _d = SessionLocal()
    _b = _d.query(_m.BenefactorAccount).filter(_m.BenefactorAccount.handle == handle).first()
    _mm = _d.get(_m.Mission, mission_id)
    _t = _mm.winning_tiv_id or _d.query(_m.Initiative).filter(_m.Initiative.mission_id == mission_id).first().id
    if not _d.query(_m.VoteP1).filter(_m.VoteP1.ben_id == _b.id, _m.VoteP1.mission_id == mission_id).first():
        _d.add(_m.VoteP1(ben_id=_b.id, mission_id=mission_id, tiv_id=_t, share=1.0,
                         ebx_committed=0, stake_ct=0, valence="helpful", committed=True))
        _d.commit()
    _d.close()


voted_in_me("walletcheck1", mid)
# 2026-09-16: an organization-election stake is 0 or at least $1 (10 tokens).
# 2026-10-07 (D31): only PURCHASED tokens enter an organization election, so this
# account adds $2 of funds through the real endpoint — 20 tokens — and the grant
# stays behind for the week's initiative election.
r = c.post("/wallet/add-funds", headers=H, json={"usd_cents": 200}).json()
ok(r["added_ct"] == 20 * T and r["mode"] == "test", "add funds: $2 -> 20 purchased tokens (test mode)", str(r))
ok(r["purchased_ct"] == 20 * T and r["free_ct"] == 20 * T, "…and they are the whole bar: no grant sits in it (ruling 19)")
_db = SessionLocal()
_dep = _db.query(_m.Transaction).filter(_m.Transaction.bucket == "deposit").all()
ok(any(int(t.amount_ebx) == 20 * T and "TEST" in (t.note or "") for t in _dep),
   "…and the deposit is in the ledger, marked TEST")
_db.close()
r = c.post("/wallet/add-funds", headers=H, json={"usd_cents": 99999})
ok(r.status_code == 400, "a deposit over the per-deposit cap is refused", f"HTTP {r.status_code}")
before = total_ct(wallet())
r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 4 * T})
ok(r.status_code == 400 and "$1" in r.json().get("detail", ""),
   "4 tokens is refused: it takes at least $1 to vote in an organization election",
   r.json().get("detail", "")[:70])
r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 12 * T}).json()
ok(r["stake_ct"] == 12 * T, "set 12 tokens on a race")
ok(r["free_ct"] == 8 * T and r["purchased_ct"] == 8 * T, "…unallocated drops to 8, all of it purchased")
ok(total_ct(wallet()) == before, "conservation: nothing created", str(total_ct(wallet())))

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 16 * T}).json()
ok(r["stake_ct"] == 16 * T, "setting it again REPLACES rather than adding")
ok(r["free_ct"] == 4 * T, "…and takes the difference from the bar")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 11 * T}).json()
ok(r["stake_ct"] == 11 * T, "and it can go DOWN — this is a draft, not a ratchet")
ok(r["free_ct"] == 9 * T and r["purchased_ct"] == 9 * T, "…with the difference handed back to unallocated, as PURCHASED")
ok(total_ct(wallet()) == before, "conservation holds on the way down too")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": -3 * T})
ok(r.status_code == 422, "a negative target is refused by the schema",
   f"HTTP {r.status_code}")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "target_ct": 999 * T}).json()
ok(r["stake_ct"] == 20 * T, "asking for more than exists lands on what there is",
   f'{r["stake_ct"]} ct')
ok(r["free_ct"] == 0 and r["grant_held_ct"] == 0, "…and the bar is empty: no grant waits in it, and none enters an organization election")
ok(total_ct(wallet()) == before, "conservation holds at the clamp")
w2 = wallet()
ok(w2["wallet"]["committed_ct"] == 20 * T,
   "everything purchased is committed — segments agree with rows")
ok(w2["wallet"]["minted_ct"] == 0, "and none of it is EBX yet: the week has not rolled")
ok("staked_ct" not in w2["wallet"] and "claimed_ct" not in w2["wallet"],
   "`staked` is `committed`, and `claimed` went back to meaning an org claim")

# ---------------------------------------------------------------------------
section("a stake with no philanthropy named is legal, and weighs nothing")
row = next(x for x in wallet()["rows"] if x["mission_id"] == mid)
ok(row["my_org_id"] is None, "ct can sit in a race with no philanthropy named")
ok(row["my_stake_ct"] == 20 * T, "…funding it in full")
ok(row["movable"], "…and it stays movable: there is nothing to harden into")

# ---------------------------------------------------------------------------
section("the amount and the philanthropy arrive in one transaction")
_db = SessionLocal()
_org = _db.query(_m.Organization).first()
_org_id = _org.id if _org else None
_db.close()
if _org_id:
    r = c.post("/wallet/commit", headers=H,
               json={"mission_id": mid, "target_ct": 20 * T, "org_id": _org_id}).json()
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
ok(w3["wallet"]["minted_ct"] == 20 * T, "the allocation minted into EBX",
   f'{w3["wallet"]["minted_ct"]} ct')
ok(w3["wallet"]["committed_ct"] == 0, "…and left the committed segment")
ok(w3["wallet"]["tokens_ct"] == 0, "…and the token bin entirely")
_row = next(x for x in w3["rows"] if x["mission_id"] == mid)
ok(not _row["movable"], "hardened ct is not movable")
ok(_row["my_minted_ct"] == 20 * T, "…and the row says so")
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
_db = SessionLocal()
_b3 = _db.query(_m.BenefactorAccount).filter(_m.BenefactorAccount.handle == "walletcheck3").first()
_b3.free_ct = int(_b3.free_ct or 0) + 50 * T
_b3.purchased_ct = 50 * T
_db.commit(); _db.close()
voted_in_me("walletcheck3", _a)
c.post("/wallet/commit", headers=H3, json={"mission_id": _a, "target_ct": 50 * T})
r = c.post("/wallet/move", headers=H3,
           json={"from_mission_id": _a, "to_mission_id": _b, "ct": 10 * T, "org_id": _org_id})
ok(r.status_code == 400 and "initiative election" in r.json().get("detail", ""),
   "(ruling 20) nothing moves INTO a race whose initiative election this benefactor skipped",
   f"HTTP {r.status_code}")
voted_in_me("walletcheck3", _b)
c.post("/wallet/commit", headers=H3, json={"mission_id": _a, "target_ct": 50 * T})
r = c.post("/wallet/move", headers=H3,
           json={"from_mission_id": _a, "to_mission_id": _b, "ct": 1 * T, "org_id": _org_id})
ok(r.status_code == 400, "a move that would leave under $1 in the destination is refused",
   f"HTTP {r.status_code}")
moved = 0
for _ in range(5):
    r = c.post("/wallet/move", headers=H3,
               json={"from_mission_id": _a, "to_mission_id": _b, "ct": 10 * T,
                     "org_id": _org_id})
    if r.status_code == 200:
        moved += 1
ok(moved == 5, "five moves in one week, and none of them refused", f"{moved} of 5")
w5 = c.get("/wallet", headers=H3).json()
ok(sum(r["my_stake_ct"] for r in w5["rows"]) == 50 * T,
   "…and the money is conserved across every one")
_dest = next(r for r in w5["rows"] if r["mission_id"] == _b)
ok(_dest["my_org_id"] == _org_id, "a move carries its philanthropy vote with it")
ok(_dest["my_stake_ct"] == 50 * T, "…and lands the ct it moved", f'{_dest["my_stake_ct"]}')
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
_b4.free_ct = int(_b4.free_ct or 0) + 15 * T
_b4.purchased_ct = 15 * T                    # as a purchase would write it
_db.commit()
_db.close()
w6 = c.get("/wallet", headers=H4).json()["wallet"]
ok(w6["purchased_ct"] == 15 * T and w6["grant_held_ct"] == 0,
   "the bar holds purchased tokens and nothing else (ruling 19)")
r = c.post("/wallet/withdraw", headers=H4, json={"ct": 2 * T}).json()
ok(r["withdrawn_ct"] == 2 * T, "purchased ct withdraws")
ok(r["cash_ct"] == 2 * T, "…into CASH, never back into tokens")
ok(r["purchased_ct"] == 13 * T and r["free_ct"] == 13 * T,
   "…and both balances drop by exactly what left")
r = c.post("/wallet/withdraw", headers=H4, json={"ct": 99 * T})
ok(r.status_code == 400, "…and you cannot withdraw more purchased ct than you hold",
   f"HTTP {r.status_code}")

# ---------------------------------------------------------------------------
section("one vote everywhere; tokens only for initiative-election voters (ruling 20, 2026-10-09)")
_rows4 = c.get("/wallet", headers=H4).json()["rows"]
_active = _rows4[0]["mission_id"]
_far = _rows4[-1]["mission_id"]
ok(_rows4[0]["is_active_race"], "the race closing soonest is this week's")
ok(not _rows4[-1]["is_active_race"], "…and the last row is not")
ok(all(x["can_take_part"] for x in _rows4), "every open race takes this benefactor's one vote")
ok(not any(x["can_commit"] for x in _rows4) and all(x["max_stake_ct"] == 0 for x in _rows4),
   "…but none takes their tokens: they voted in none of these initiative elections")
r = c.post("/wallet/commit", headers=H4,
           json={"mission_id": _far, "target_ct": 99 * T})
ok(r.status_code == 400 and "initiative election" in r.json().get("detail", ""),
   "a far race refuses tokens from a benefactor who did not vote in its initiative election",
   f"HTTP {r.status_code}")
r = c.post("/wallet/commit", headers=H4,
           json={"mission_id": _active, "target_ct": 99 * T})
ok(r.status_code == 400, "…and so does this week's race — the old open door is gone", f"HTTP {r.status_code}")
r = c.put("/wallet/org", headers=H4, json={"mission_id": _far, "org_id": "earthbux"})
ok(r.status_code == 200, "…while the nominal vote is open in the far race", f"HTTP {r.status_code}")
_rf = next(x for x in c.get("/wallet", headers=H4).json()["rows"] if x["mission_id"] == _far)
ok(_rf["my_org_id"] == "earthbux" and _rf["my_votes"] == 1 and _rf["my_stake_ct"] == 0,
   "…and counts once: 0 tokens = 1 vote", str((_rf["my_org_id"], _rf["my_votes"])))
voted_in_me("walletcheck4", _far)
_rf = next(x for x in c.get("/wallet", headers=H4).json()["rows"] if x["mission_id"] == _far)
ok(_rf["can_commit"] and _rf["max_stake_ct"] == 13 * T,
   "once they voted in its initiative election, the race takes their purchased tokens", str(_rf["max_stake_ct"]))
r = c.post("/wallet/commit", headers=H4,
           json={"mission_id": _far, "target_ct": 99 * T}).json()
ok(r["stake_ct"] == 13 * T, "…every PURCHASED token", f'{r["stake_ct"]} ct')
ok(r["free_ct"] == 0, "…leaving the bar empty")


# ---------------------------------------------------------------------------
section("the initiative election: one amount, one slate, and the WALLET pays")
# The ME table spent `10 + localStorage.ebx_purchased_ebx` until 2026-08-27c —
# a budget invented in the browser, which is why the allocations panel could
# report the same tokens twice. `replace_p1_shares` reconciles against the
# account now, and the slate is percentages of the one amount.
H6 = signup("walletcheck6")
_w6 = c.get("/wallet", headers=H6).json()
_open_ids6 = [e["mission_id"] for e in _w6["grant"]["elections"]]
_db = SessionLocal()
_target6 = None
for _mid in _open_ids6:
    _t = _db.query(_m.Initiative).filter(_m.Initiative.mission_id == _mid).all()
    if len(_t) >= 2:
        _target6 = (_mid, [x.id for x in _t[:2]])
        break
_other = next((x for x in _open_ids6 if not _target6 or x != _target6[0]), None)
_other_tivs = ([x.id for x in _db.query(_m.Initiative).filter(
    _m.Initiative.mission_id == _other).all()[:1]] if _other else [])
_db.close()
if _target6 is None:
    ok(True, "(no open initiative election with two candidates)")
else:
    _mid6, _t6 = _target6
    r = c.put(f"/missions/{_mid6}/p1/votes", headers=H6,
              json={"mission_id": _mid6, "shares": {_t6[0]: 0.75, _t6[1]: 0.25},
                    "ebx": 8})
    ok(r.status_code == 200, "a slate with an amount is accepted", f"HTTP {r.status_code}")
    _x6 = c.get("/wallet", headers=H6).json()
    _wal = _x6["wallet"]
    ok(_wal["free_ct"] == 0, "the GRANT paid for it — the bar never held it", f'{_wal["free_ct"]} ct')
    ok(_wal["committed_ct"] == 8 * T,
       "…and the committed segment holds them, ME and OE in one number")
    _e6 = next(e for e in _x6["grant"]["elections"] if e["mission_id"] == _mid6)
    ok(_e6["used_ct"] == 8 * T and _e6["left_ct"] == 2 * T,
       "…and that election shows 8 of its 10 granted tokens used")
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
    _x6 = c.get("/wallet", headers=H6).json()
    _wal = _x6["wallet"]
    ok(_wal["committed_ct"] == 3 * T,
       "lowering the amount is allowed — an ME allocation is soft", f'{_wal["committed_ct"]} ct')
    ok(_wal["free_ct"] == 0 and next(e for e in _x6["grant"]["elections"] if e["mission_id"] == _mid6)["left_ct"] == 7 * T,
       "…and the grant it frees stays with its election; the wallet gains nothing")
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
        ok(_spent == 5 * T,
           "ANOTHER initiative election takes its own grant — no door any more (ruling 19)",
           f"{_spent} ct landed")
        ok(_wal2["free_ct"] == 0 and _wal2["committed_ct"] == 8 * T,
           "…and still nothing came out of the wallet", f'{_wal2["committed_ct"]} ct committed')
    else:
        ok(True, "(no second open initiative election to test with)")

# ---------------------------------------------------------------------------
section("one benefactor cannot see or spend another's money")
H5 = signup("walletcheck5")
w7 = c.get("/wallet", headers=H5).json()
ok(w7["grant"]["left_ct"] == 10 * T * w7["grant"]["open"], "a fresh account gets its own ten in every election")
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
        ok(_v.donated_ct == tm.settle_me(int(_v.stake_ct)).donated_ct,
           "…and 10% of it is final at the initiative election",
           f"{_v.donated_ct} of {_v.stake_ct} ct")
        ok(_v.marked_tiv_id is None, "…and carries no mark, because nothing of theirs lost")
        ok(not _w.is_movable(_v, _w.current_week()),
           "…and the early EBX is locked in this race until it finalizes")
    for _bid in _lost_ids:
        _v = _stakes[_bid]
        ok(_v.minted_ct == 0, f"ben {_bid} backed a loser and mints nothing yet")
        ok(_v.donated_ct == tm.settle_me(int(_v.stake_ct)).donated_ct,
           "…but 10% of the stake is FINAL all the same — a skim marks finality",
           f"final {_v.donated_ct} of {_v.stake_ct}")
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
    section("the organization election: ANOTHER 10%, and the rest is EBX")
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
        _me_part = sum(int(e.get("amount_ct") or 0) for e in (_v.provenance or [])
                       if e.get("kind") == "donate" and e.get("outcome") == "me_close")
        ok(_v.donated_ct == _me_part + tm.settle_oe(int(_v.stake_ct)).donated_ct,
           f"ben {_bid}: the OE skim is ADDITIONAL to the ME skim",
           f"{_v.donated_ct} ct (me {_me_part})")
        ok(_v.marked_tiv_id is None, f"ben {_bid}: the mark is spent")
    _rates = {abs(int(v.donated_ct) * 5 - int(v.stake_ct)) <= 10 for v in _after.values()
              if int(v.stake_ct or 0) > 0}
    ok(_rates == {True},
       "…and it is the SAME 20% for the winner's backer and the loser's (to the ct)")
    _tranches = [e for e in (_after[_won_id].provenance or [])
                 if e.get("kind") == "donate"]
    ok(len(_tranches) == 2, "two tranches are booked (ME close, OE close), dated for the deduction")
    ok(all(v.org_id is not None for v in _after.values()
           if int(v.stake_ct or 0) > 0),
       "every stake ends the race naming a philanthropy — including EARLY EBX, "
       "which minted before there was one to name")
    _crud.finalize_p2(_db, _mid_p1)
    _twice = _db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1,
                                         _m.VoteP2.ben_id == _won_id).first()
    ok(int(_twice.donated_ct) == int(_after[_won_id].donated_ct),
       "…and settling twice does not skim twice")
    _fw = _w.final_ct_of(_db, _twice)
    ok(_fw == int(_twice.donated_ct) or _fw == int(_twice.stake_ct),
       "final ct is the skims before budget day, the whole stake after")

    section("withdrawing the non-final part as cash, until budget day (2026-09-16)")
    _wv = _db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1,
                                      _m.VoteP2.ben_id == _won_id).first()
    _wb = _db.get(_m.BenefactorAccount, _won_id)
    _stake0, _final0, _cash0 = int(_wv.stake_ct), int(_wv.donated_ct), int(_wb.cash_ct or 0)
    _mis = _db.get(_m.Mission, _mid_p1)
    _before_bd = _w.budget_day(_mis) - __import__("datetime").timedelta(days=1)
    _open = _stake0 - _final0
    if _open > 0:
        _res = _w.withdraw_stake(_db, _won_id, _mid_p1, 1, now=_before_bd)
        ok(_res["withdrawn_ct"] == 1 and int(_db.get(_m.BenefactorAccount, _won_id).cash_ct) == _cash0 + 1,
           "1 ct of the non-final part comes back as CASH")
        try:
            _w.withdraw_stake(_db, _won_id, _mid_p1, 10 ** 9, now=_before_bd)
            _left = int(_db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1,
                                                   _m.VoteP2.ben_id == _won_id).first().stake_ct)
            ok(_left == _final0, "asking for everything stops at the final part", f"{_left} vs {_final0}")
        except ValueError as _e:
            ok(False, "a large withdrawal is clamped, not refused", str(_e))
    try:
        _w.withdraw_stake(_db, _won_id, _mid_p1, 1, now=_before_bd)
        ok(False, "nothing more can be withdrawn once only final ct is left")
    except ValueError:
        ok(True, "nothing more can be withdrawn once only final ct is left")
    try:
        _w.withdraw_stake(_db, _won_id, _mid_p1, 1,
                          now=_w.budget_day(_mis) + __import__("datetime").timedelta(days=1))
        ok(False, "from budget day on, nothing is withdrawable")
    except ValueError:
        ok(True, "from budget day on, nothing is withdrawable")
    _db.close()

# ---------------------------------------------------------------------------
section("ruling 19 (2026-10-09): grant first, purchased on top, last in first out")
c.get("/missions")                                 # let the scheduler open the week's mission
_db = SessionLocal()
_door = _w.door_mission(_db)                       # the soonest-closing initiative election
_door_id = _door.id if _door else None
_door_cause = _door.cause_id if _door else None
if _door_id:
    for _i in range(2):
        if _db.get(_m.Initiative, f"d31-{_i}") is None:
            _db.add(_m.Initiative(id=f"d31-{_i}", title=f"D31 check {_i}", cause_id=_door_cause,
                                  mission_id=_door_id, status="suggested", approved=True))
    _db.commit()
_db.close()
if _door_id is None:
    ok(True, "(no initiative election open)")
else:
    HD = signup("walletcheckd31")
    c.post("/wallet/add-funds", headers=HD, json={"usd_cents": 100})
    def _wd():
        x = c.get("/wallet", headers=HD).json()
        return x["wallet"], next(e for e in x["grant"]["elections"] if e["mission_id"] == _door_id), x
    _wal, _e, _x = _wd()
    ok(_e["left_ct"] == 10 * T and _wal["free_ct"] == 10 * T and _wal["purchased_ct"] == 10 * T,
       "ten granted in the election, ten purchased in the bar", str(_e)[:90])
    c.put(f"/missions/{_door_id}/p1/votes", headers=HD,
          json={"mission_id": _door_id, "shares": {"d31-0": 1.0}, "ebx": 15})
    _wal, _e, _x = _wd()
    ok(_e["left_ct"] == 0 and _wal["purchased_ct"] == 5 * T,
       "15 tokens in: the 10 granted go first, then 5 purchased")
    c.put(f"/missions/{_door_id}/p1/votes", headers=HD,
          json={"mission_id": _door_id, "shares": {"d31-0": 1.0}, "ebx": 10})
    _wal, _e, _x = _wd()
    ok(_wal["purchased_ct"] == 10 * T and _e["left_ct"] == 0,
       "lowering to 10 hands the PURCHASED 5 back first")
    c.put(f"/missions/{_door_id}/p1/votes", headers=HD,
          json={"mission_id": _door_id, "shares": {"d31-0": 1.0}, "ebx": 4})
    _wal, _e, _x = _wd()
    ok(_e["left_ct"] == 6 * T and _wal["purchased_ct"] == 10 * T and _wal["free_ct"] == 10 * T,
       "…and only then frees the grant — inside its election, never into the wallet")
    _db = SessionLocal()
    _bd = _db.query(_m.BenefactorAccount).filter(_m.BenefactorAccount.handle == "walletcheckd31").first()
    _bd.last_grant_week = _w.current_week() - 1    # pretend the week changed
    _bd.free_ct = int(_bd.free_ct or 0) + 7 * T    # …and a D31 weekly pile is still in the bar
    _db.commit(); _bd_id = _bd.id; _db.close()
    _wal, _e, _x = _wd()
    ok(_wal["free_ct"] == 10 * T and _wal["purchased_ct"] == 10 * T and _x["expired_this_week_ct"] == 7 * T,
       "the switch retires a weekly pile left in the bar; purchased tokens are untouched")
    ok(_e["left_ct"] == 6 * T, "…and nothing about the week changes what the election still offers")

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
