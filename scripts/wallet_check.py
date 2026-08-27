"""wallet_check — the wallet and OE-stake endpoints, end to end.

    python3 scripts/wallet_check.py

Runs the real FastAPI app against a **throwaway copy** of `earthbucks.db`, so it
signs up accounts, moves money and never touches the pilot data. Nothing here
mocks the routers: every assertion goes through HTTP the way the page does.

What it is really guarding is the conservation law. Two tables share one cell
(`free`), a stake can move between eight rows, and the failure mode is money
that quietly appears or vanishes on a drag — the ratchet bug, one level up.
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

from fastapi.testclient import TestClient        # noqa: E402
from app.main import app                          # noqa: E402
from app import token_model as tm                 # noqa: E402

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

# ---------------------------------------------------------------------------
section("the OE table")
rows = c.get("/wallet/rows").json()
ok(len(rows) <= 8, "at most 8 rows — one per mission in phase 2", f"{len(rows)} rows")
ok(len(rows) > 0, "and not zero on the pilot data")
dates = [r["vote_date"][:10] for r in rows]
ok(dates == sorted(dates), "ordered by the philanthropy-election date")
ok(len(set(dates)) == len(dates), "one race closes per week — no two share a date")
causes = [r["cause_id"] for r in rows]
ok(len(set(causes)) < len(causes) or len(rows) < 8,
   "at 8 rows two share a cause (7-week rotation, 8-week phase 2)",
   " · ".join(causes))
ok(all(r["tiv_title"] for r in rows), "every row is labelled by its INITIATIVE")
ok(all(r["my_stake_ct"] == 0 and r["my_org_id"] is None for r in rows),
   "signed out, nobody has a commitment")

# ---------------------------------------------------------------------------
section("the grant tops up to 10, once per week")
w = c.get("/wallet", headers=H).json()
ok(w["granted_this_week_ct"] == 10 * T, "a new account is granted 10 tokens")
ok(w["wallet"]["free_ct"] == 10 * T, "…and holds them free")
ok(w["wallet"]["next_grant_ct"] == 0, "holding 10 → next grant is 0")
again = c.get("/wallet", headers=H).json()
ok(again["granted_this_week_ct"] == 0, "a refresh does NOT pay a second grant")
ok(again["wallet"]["free_ct"] == 10 * T, "…and the balance is unchanged")
ok(again["rules"]["ct_per_token"] == 100, "the unit rides along in the payload")
ok(again["rules"]["weight_r"] == 0.5, "so does the curve's knob")

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
section("committing is ONE WAY")
# Every assertion in this section used to read the other way round: the old
# `PUT /wallet/stake` set a POSITION, so dragging a row down returned ct to the
# unallocated balance and the check called that "a position, not a ratchet".
# 2026-08-20b inverts it — "users can no longer move tokens from an OE to
# unallocated" — so what is guarded now is that the door only opens outward.
mid = rows[0]["mission_id"]           # the race finalizing soonest = active


def wallet():
    return c.get("/wallet", headers=H).json()


def total_ct(payload):
    """Every ct this benefactor holds as a token, wherever it sits."""
    return payload["wallet"]["free_ct"] + sum(r["my_stake_ct"] for r in payload["rows"])


before = total_ct(wallet())
r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "add_ct": 4 * T}).json()
ok(r["stake_ct"] == 4 * T, "commit 4 tokens to a race")
ok(r["committed_ct"] == 4 * T, "…and that is what left the bar")
ok(r["free_ct"] == 6 * T, "…unallocated drops to 6")
ok(total_ct(wallet()) == before, "conservation: nothing created", str(total_ct(wallet())))

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "add_ct": 2 * T}).json()
ok(r["stake_ct"] == 6 * T, "committing again ADDS rather than replacing")
ok(r["free_ct"] == 4 * T, "…and takes the difference from the bar")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "add_ct": -3 * T})
ok(r.status_code == 422, "a negative commitment is refused by the schema",
   f"HTTP {r.status_code}")
ok(next(x for x in wallet()["rows"] if x["mission_id"] == mid)["my_stake_ct"] == 6 * T,
   "…and the stake is untouched by the attempt")
ok(wallet()["wallet"]["free_ct"] == 4 * T, "…as is the balance")

r = c.post("/wallet/commit", headers=H, json={"mission_id": mid, "add_ct": 999 * T}).json()
ok(r["committed_ct"] == 4 * T, "asking for more than exists commits what there is",
   f'{r["committed_ct"]} ct')
ok(r["free_ct"] == 0, "…and the bar floors at zero, never negative")
ok(total_ct(wallet()) == before, "conservation holds at the clamp")

w2 = wallet()
ok(w2["wallet"]["staked_ct"] == before, "everything is committed — segments agree with rows")
ok(w2["wallet"]["free_ct"] == 0, "…and unallocated is empty")
ok(w2["wallet"]["tokens_ct"] == before, "the Tokens bin is unallocated + committed")
ok("returned_ct" not in w2["wallet"],
   "there is no 'returned' segment any more — nothing comes back")
STAKE = next(x for x in w2["rows"] if x["mission_id"] == mid)["my_stake_ct"]

# ---------------------------------------------------------------------------
section("a stake with no philanthropy named is legal, and weighs nothing")
row = next(r for r in wallet()["rows"] if r["mission_id"] == mid)
ok(row["my_stake_ct"] == STAKE, "the row carries the stake", f'{row["my_stake_ct"]} ct')
ok(row["my_org_id"] is None, "…with no organization — the state the ME default creates")
ok(row["born_week"] is not None, "and the lot's clock has started")
ok(row["conversions_left"] == tm.MAX_CONVERSIONS,
   "…with its whole conversion budget unspent")
ok(row["is_origin_race"], "ct committed straight to a row is native to that race")

orgs = c.get("/organizations").json()
oid = orgs[0]["id"]
oid2 = orgs[1]["id"] if len(orgs) > 1 else orgs[0]["id"]
r = c.put("/wallet/org", headers=H, json={"mission_id": mid, "org_id": oid}).json()
ok(r["org_id"] == oid, "naming a philanthropy is a separate call from the money")
ok(r["stake_ct"] == STAKE, "…and does not move the stake")
ok(r["conversions_used"] == 0, "…and costs no conversion in the race it was born in")
row = next(r for r in wallet()["rows"] if r["mission_id"] == mid)
ok(row["my_org_id"] == oid, "the row now reads 'committed to <phl>'")

# ---------------------------------------------------------------------------
section("the amount and the philanthropy can arrive in one transaction")
H5 = signup("walletcheck5")
w9 = c.get("/wallet", headers=H5).json()
act5 = next(x for x in w9["rows"] if x["is_active_race"])
r = c.post("/wallet/commit", headers=H5,
           json={"mission_id": act5["mission_id"], "add_ct": 3 * T, "org_id": oid}).json()
ok(r["stake_ct"] == 3 * T and r["org_id"] == oid,
   "one call carries the amount and the choice — the gesture the dialog asks for")
prov = None
_db0 = None
row5 = next(x for x in c.get("/wallet", headers=H5).json()["rows"]
            if x["mission_id"] == act5["mission_id"])
ok(row5["my_org_id"] == oid, "…and the row reads it back")
ok(row5["my_stake_ct"] == 3 * T, "…with the money where it was sent")

# ---------------------------------------------------------------------------
section("the clock does not restart when more is committed")
row = next(r for r in wallet()["rows"] if r["mission_id"] == mid)
born = row["born_week"]
c.post("/wallet/commit", headers=H, json={"mission_id": mid, "add_ct": 0})
row = next(r for r in wallet()["rows"] if r["mission_id"] == mid)
ok(row["born_week"] == born, "a second commitment does not restart the clock")

# ---------------------------------------------------------------------------
section("weight follows the curve, and being right in the ME doubles it")
row = next(r for r in wallet()["rows"] if r["mission_id"] == mid)
expected = tm.weight_tokens(row["my_stake_ct"],
                            tm.influence_mult("oe", me_correct=row["backed_winner"]))
ok(abs(row["my_weight"] - expected) < 1e-9, "the row reports token_model's weight",
   f'{row["my_weight"]} vs {expected}')
ok(row["my_influence"] == (2.0 if row["backed_winner"] else 1.0),
   "…and says which multiplier it applied")
ok(tm.weight_tokens(20 * T) == 15.0, "…and that curve is the old price ladder")

# ---------------------------------------------------------------------------
section("one skim, and it is not the initiative election")
rules = wallet()["rules"]
ok(rules["me_skim"] == 0.0, "the API reports a zero initiative-election skim")
ok(rules["oe_send_lose"] == 0.10, "…and the one skim, 10%, at the philanthropy election")
ok(rules["oe_send_win"] == 1.0, "a won race donates all of it")
ok(rules["max_conversions"] == 3, "three conversions per lot")
ok(rules["me_correct_oe_mult"] == 2.0 and rules["oe_correct_budget_mult"] == 2.0,
   "the two doublings are published to the client")
ok(abs(rules["research_mult_both"] - 2.25) < 1e-9, "…and the 2.25x compound")
ok(rules["oe_table_rows"] == 8, "the table is eight rows")

# ---------------------------------------------------------------------------
section("the grant carries a date to commit by")
w7 = wallet()
ok(w7["commit_by_week"] == w7["week"] + 1,
   "this week's grant is marked to be committed by the end of the week",
   f'{w7["commit_by_week"]} vs week {w7["week"]}')
ok(w7["commit_by"] is not None, "…and the date is sent as a date",
   str(w7["commit_by"]))
ok(w7["wallet"]["commit_by_week"] == w7["commit_by_week"],
   "the wallet payload and the envelope agree")
ok(w7["wallet"]["purchased_ct"] == 0, "nothing has been purchased, so nothing is undated")
ok(w7["wallet"]["grant_held_ct"] == w7["wallet"]["free_ct"] - w7["wallet"]["purchased_ct"],
   "unallocated is granted + purchased, and nothing else")

# ---------------------------------------------------------------------------
section("conversion: the only way ct leaves a race, and it costs one of three")
from app.database import SessionLocal            # noqa: E402
from app import models as _m                     # noqa: E402

H4 = signup("walletcheck4")
w8 = c.get("/wallet", headers=H4).json()
act = next(r for r in w8["rows"] if r["is_active_race"])
oth = next(r for r in w8["rows"] if not r["is_active_race"])
c.post("/wallet/commit", headers=H4,
       json={"mission_id": act["mission_id"], "add_ct": 8 * T, "org_id": oid})
r = c.post("/wallet/convert", headers=H4,
           json={"from_mission_id": act["mission_id"],
                 "to_mission_id": oth["mission_id"], "ct": 5 * T, "org_id": oid2}).json()
ok(r["moved_ct"] == 5 * T, "5 tokens move straight from one race to the other")
ok(r["from_stake_ct"] == 3 * T, "…leaving 3 behind")
ok(r["to_stake_ct"] == 5 * T, "…and arriving whole")
ok(r["conversions_used"] == 1 and r["conversions_left"] == 2, "one of three spent")
w8b = c.get("/wallet", headers=H4).json()
ok(w8b["wallet"]["free_ct"] == 2 * T,
   "the unallocated balance is UNTOUCHED — a conversion never passes through it",
   f'{w8b["wallet"]["free_ct"]} ct')
dest = next(x for x in w8b["rows"] if x["mission_id"] == oth["mission_id"])
ok(dest["my_org_id"] == oid2, "the destination carries the philanthropy it was voted for")
ok(dest["is_origin_race"], "…and is home now: an unvoted stake here would follow ITS winner")

r = c.post("/wallet/convert", headers=H4,
           json={"from_mission_id": act["mission_id"],
                 "to_mission_id": oth["mission_id"], "ct": 5 * T, "org_id": ""})
ok(r.status_code == 400, "a conversion with no philanthropy is refused — it IS a vote",
   f"HTTP {r.status_code}")
r = c.post("/wallet/convert", headers=H4,
           json={"from_mission_id": act["mission_id"],
                 "to_mission_id": act["mission_id"], "ct": T, "org_id": oid})
ok(r.status_code == 400, "converting a race into itself is refused")
r = c.post("/wallet/convert", headers=H4,
           json={"from_mission_id": oth["mission_id"],
                 "to_mission_id": act["mission_id"], "ct": 99 * T, "org_id": oid}).json()
ok(r["moved_ct"] == 5 * T, "asking to convert more than is there moves what is there",
   f'{r["moved_ct"]} ct')
ok(r["conversions_used"] == 2, "…and spends the second conversion")

# Exhaust the budget and confirm the ceiling holds.
_db = SessionLocal()
_row = _db.query(_m.VoteP2).filter(
    _m.VoteP2.mission_id == act["mission_id"]).order_by(_m.VoteP2.id.desc()).first()
_row.conversions = tm.MAX_CONVERSIONS
_db.commit()
_db.close()
r = c.post("/wallet/convert", headers=H4,
           json={"from_mission_id": act["mission_id"],
                 "to_mission_id": oth["mission_id"], "ct": T, "org_id": oid2})
ok(r.status_code == 400, "a lot with no conversions left cannot move again",
   f"HTTP {r.status_code}")
spent = next(x for x in c.get("/wallet", headers=H4).json()["rows"]
             if x["mission_id"] == act["mission_id"])
ok(spent["conversions_left"] == 0, "…and the row says so")

# ---------------------------------------------------------------------------
section("there is no way back to unallocated")
free_before = c.get("/wallet", headers=H4).json()["wallet"]["free_ct"]
ok(c.put("/wallet/stake", headers=H4,
         json={"mission_id": act["mission_id"], "stake_ct": 0}).status_code in (404, 405),
   "the old position-setting endpoint is GONE, not quietly still working")
ok(c.get("/wallet", headers=H4).json()["wallet"]["free_ct"] == free_before,
   "…and nothing came back to the bar")
# ---------------------------------------------------------------------------
section("a second benefactor cannot see or spend the first's money")
H2 = signup("walletcheck2")
w3 = c.get("/wallet", headers=H2).json()
ok(w3["wallet"]["staked_ct"] == 0, "a fresh account starts with nothing staked")
ok(all(r["my_stake_ct"] == 0 for r in w3["rows"]), "…and no commitments on any row")
ok(w3["wallet"]["free_ct"] == 10 * T, "…but does get its own grant")
mine_before = next(x for x in wallet()["rows"] if x["mission_id"] == mid)["my_stake_ct"]
r = c.post("/wallet/commit", headers=H2,
           json={"mission_id": mid, "add_ct": 3 * T}).json()
ok(r["stake_ct"] == 3 * T, "it commits its own to the same race")
ok(next(x for x in wallet()["rows"] if x["mission_id"] == mid)["my_stake_ct"] == mine_before,
   "…and the first benefactor's stake on the same row is untouched",
   f"{mine_before} ct")

# ---------------------------------------------------------------------------
section("closed races refuse money")
closed = c.get("/missions").json()
done = [m for m in closed if m.get("winning_org_id")]
if done:
    r = c.post("/wallet/commit", headers=H,
               json={"mission_id": done[0]["id"], "add_ct": T})
    ok(r.status_code == 400, "committing into a decided philanthropy election is rejected",
       f"HTTP {r.status_code}")
    r = c.put("/wallet/org", headers=H, json={"mission_id": done[0]["id"], "org_id": oid})
    ok(r.status_code == 400, "…and so is voting in one")
else:
    ok(True, "(no decided race in this database to test against)")
r = c.post("/wallet/commit", headers=H,
           json={"mission_id": "no-such-mission", "add_ct": T})
ok(r.status_code == 400, "an unknown mission is rejected, not created")

# ---------------------------------------------------------------------------
section("two doors: granted ct enters this week's race, purchased ct enters any")
H3 = signup("walletcheck3")
w5 = c.get("/wallet", headers=H3).json()
ok(w5["wallet"]["grant_held_ct"] == 10 * T, "the whole balance starts granted")
ok(w5["wallet"]["purchased_ct"] == 0, "…and nothing is purchased yet")
active = [r for r in w5["rows"] if r["is_active_race"]]
ok(len(active) == 1, "exactly one row is the active-cause race", str(len(active)))
ok(active[0]["vote_date"] == min(r["vote_date"] for r in w5["rows"]),
   "…and it is the race that finalizes soonest")
other = next(r for r in w5["rows"] if not r["is_active_race"])
ok(other["max_stake_ct"] == 0,
   "a non-active row will not take granted money", f'{other["max_stake_ct"]} ct')
ok(active[0]["max_stake_ct"] == 10 * T, "the active row will take all of it")

r = c.post("/wallet/commit", headers=H3,
           json={"mission_id": other["mission_id"], "add_ct": 5 * T}).json()
ok(r["committed_ct"] == 0, "…and asking anyway commits nothing, rather than spending")
ok(r["free_ct"] == 10 * T, "the balance is untouched")

r = c.post("/wallet/commit", headers=H3,
           json={"mission_id": active[0]["mission_id"], "add_ct": 6 * T}).json()
ok(r["committed_ct"] == 6 * T, "the active race accepts granted ct")
ok(r["grant_held_ct"] == 4 * T, "…leaving 4 granted")

# Buying is still the localStorage simulation on the client, so the purchase is
# made here the way the eventual endpoint will: ct into the bar, marked bought.
_db = SessionLocal()
_b3 = _db.query(_m.BenefactorAccount).filter(
    _m.BenefactorAccount.handle == "walletcheck3").first()
_b3.free_ct = int(_b3.free_ct or 0) + 5 * T
_b3.purchased_ct = int(_b3.purchased_ct or 0) + 5 * T
_db.commit()
_db.close()
w6 = c.get("/wallet", headers=H3).json()
ok(w6["wallet"]["purchased_ct"] == 5 * T, "5 purchased tokens are in the bar")
ok(w6["wallet"]["grant_held_ct"] == 4 * T, "…alongside the 4 still granted")
other = next(r for r in w6["rows"] if not r["is_active_race"])
ok(other["max_stake_ct"] == 5 * T,
   "…and THOSE can go to any of the other seven rows", f'{other["max_stake_ct"]} ct')
r = c.post("/wallet/commit", headers=H3,
           json={"mission_id": other["mission_id"], "add_ct": 99 * T}).json()
ok(r["committed_ct"] == 5 * T, "a non-active row clamps to the purchased balance")
ok(r["free_ct"] == 4 * T, "…leaving the granted ct where it was")
ok(r["grant_held_ct"] == 4 * T, "…still granted, still for this week's two doors")
ok(r["purchased_ct"] == 0, "…and the purchased slice is spent")

r = c.post("/wallet/commit", headers=H3,
           json={"mission_id": active[0]["mission_id"], "add_ct": 4 * T}).json()
ok(r["grant_held_ct"] == 0 and r["free_ct"] == 0,
   "granted ct is spent FIRST, so the wider permission is never burned by accident")

section("final conservation sweep")
ok(total_ct(wallet()) == 10 * T, "benefactor 1 still holds exactly its 10 tokens")
w4 = wallet()["wallet"]
ok(w4["free_ct"] + w4["staked_ct"] == 10 * T, "free + staked = the Tokens bin")
ok(w4["claimed_ct"] >= 0 and w4["minted_ct"] >= 0, "the other two segments are sane")
# Unallocated is granted + purchased and nothing else, for every account that
# moved money in this run. The old lot ledger that used to be checked here went
# with the balance it described: nothing comes back out of a race.
_db = SessionLocal()
for _handle in ("walletcheck1", "walletcheck3", "walletcheck4", "walletcheck5"):
    _b = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == _handle).first()
    ok(int(_b.purchased_ct or 0) <= int(_b.free_ct or 0),
       f"{_handle}: the purchased slice never exceeds the balance holding it",
       f"{_b.purchased_ct} of {_b.free_ct}")
_db.close()

# ---------------------------------------------------------------------------
section("the initiative election carries EVERY backer, and skims nothing")
# Run a real finalize on the throwaway copy: two benefactors back different
# initiatives in the same phase-1 mission, one wins, and both stakes have to
# arrive whole in that mission's organization election.
from app import crud as _crud                    # noqa: E402
_db = SessionLocal()
_open_p1 = _db.query(_m.Mission).filter(_m.Mission.winning_tiv_id.is_(None)).all()
_target = next((mm for mm in _open_p1
                if len(_db.query(_m.Initiative).filter(
                    _m.Initiative.mission_id == mm.id).all()) >= 2), None)
if _target is None:
    ok(True, "(no phase-1 mission with two initiatives in this database)")
else:
    _tivs = _db.query(_m.Initiative).filter(_m.Initiative.mission_id == _target.id).all()[:2]
    _b1 = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == "walletcheck1").first()
    _b2 = _db.query(_m.BenefactorAccount).filter(
        _m.BenefactorAccount.handle == "walletcheck2").first()
    for _b, _tiv, _ebx in ((_b1, _tivs[0], 6.0), (_b2, _tivs[1], 2.0)):
        _db.add(_m.VoteP1(ben_id=_b.id, mission_id=_target.id, tiv_id=_tiv.id,
                          share=1.0, ebx_committed=_ebx, valence="helpful",
                          committed=True))
    _db.commit()
    # Pull the plain values out before the session closes — these ORM objects
    # go detached and every later attribute read would be a lazy load.
    _mid_p1, _cause_p1 = _target.id, _target.cause_id
    _tiv_win, _tiv_lose = _tivs[0].id, _tivs[1].id
    _b1_id, _b2_id = _b1.id, _b2.id
    _db.close()

    _db = SessionLocal()
    _winner = _crud.finalize_p1(_db, _mid_p1)
    # Which initiative wins depends on what was already committed in this
    # mission, so the assertion is that a race with votes in it DECIDES — the
    # point of the section is where the money goes afterwards, and the
    # interesting case (a backer of a losing initiative) is guaranteed either
    # way: at most one of these two benefactors can have backed the winner.
    ok(_winner is not None, "a race with commitments in it elects an initiative",
       str(_winner))
    _stakes = {v.ben_id: v for v in _db.query(_m.VoteP2).filter(
        _m.VoteP2.mission_id == _mid_p1).all()}
    ok(set(_stakes) >= {_b1_id, _b2_id},
       "BOTH backers are carried into the organization election — including the loser's")
    ok(_stakes[_b1_id].stake_ct == 600,
       "the winner's backer arrives with all 6 tokens, not 5.4",
       f"{_stakes[_b1_id].stake_ct} ct")
    ok(_stakes[_b2_id].stake_ct == 200,
       "…and the loser's with all 2 — one skim, and this is not it",
       f"{_stakes[_b2_id].stake_ct} ct")
    ok(all(v.org_id is None for v in _stakes.values()),
       "they arrive with no philanthropy named")
    ok(all(v.origin_mission_id == _mid_p1 for v in _stakes.values()),
       "…native to the race they were created in")
    _el = [e for e in (_stakes[_b2_id].provenance or []) if e.get("kind") == "settle_me"]
    ok(len(_el) == 1, "coin element 1 is written once")
    ok(_el[0]["cause_id"] == _cause_p1 and _el[0]["target_id"] == _tiv_lose,
       "…carrying the cause and the initiative this benefactor backed")
    ok(_el[0]["winner_id"] == _winner
       and _el[0]["outcome"] == ("won" if _tiv_lose == _winner else "lost"),
       "…and the initiative that WON, so a losing coin still knows the argument",
       str(_el[0]["outcome"]))
    _before = len(_stakes[_b1_id].provenance or [])
    _crud.finalize_p1(_db, _mid_p1)
    _again = _db.query(_m.VoteP2).filter(_m.VoteP2.mission_id == _mid_p1,
                                         _m.VoteP2.ben_id == _b1_id).first()
    ok(len(_again.provenance or []) == _before,
       "finalizing twice does not write the element twice")
    ok(_again.stake_ct == 600, "…or double the stake")
    _skims = _db.query(_m.Transaction).filter(
        _m.Transaction.bucket == "commitment_fund",
        _m.Transaction.mission_id == _mid_p1).all()
    ok(not _skims, "and no commitment-fund skim is booked at all")
    _db.close()

shutil.rmtree(_tmp.parent, ignore_errors=True)
print(f"\n{N} assertions · " + (f"PROBLEMS: {BAD}" if BAD else "WALLET CLEAN"))
sys.exit(1 if BAD else 0)
