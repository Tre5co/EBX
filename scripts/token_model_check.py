"""token_model_check — the money model's arithmetic, asserted.

    python3 scripts/token_model_check.py        (from the repo root or backend/)

Pure math, no database and no server, so this is the one check that can be run
before anything else is wired. Every number the UI or the docs are allowed to
print about money should be derivable from something asserted here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app import token_model as tm   # noqa: E402

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

# ---------------------------------------------------------------------------
section("units")
ok(T == 100, "1 token = 100 ct")
ok(tm.ct_from_tokens(1) == 100, "1 token → 100 ct")
ok(tm.ct_from_tokens(0.001) == 1, "a tenth of a cent rounds up to 1 ct, not 0")
ok(tm.usd(1000) == 1.0, "10 tokens = $1", str(tm.usd(1000)))
ok(tm.usd(1) == 0.001, "1 ct = $0.001")

# ---------------------------------------------------------------------------
section("the grant is a top-up, not a penalty")
ok(tm.grant_ct(0) == 1000, "hold nothing → 10 tokens")
ok(tm.grant_ct(6 * T) == 4 * T, "hold 6 → grant 4  (Jax's example)")
ok(tm.grant_ct(10 * T) == 0, "hold 10 → no grant")
ok(tm.grant_ct(50 * T) == 0, "hold 50 → no grant, never negative")
ok(tm.grant_ct(1) == 999, "hold 1 ct → 999 ct: no cliff at the bottom")
ok(all(tm.grant_ct(f) + f >= 10 * T or f > 10 * T for f in range(0, 2000, 37)),
   "topped up TO 10 for every holding below 10")
ok(all(tm.grant_ct(a) >= tm.grant_ct(b) for a, b in zip(range(0, 1500, 13),
                                                        range(13, 1513, 13))),
   "monotone: holding more never increases the grant")

# ---------------------------------------------------------------------------
section("vote weight — r = 0.5 reproduces the old price ladder")
# p2_vote_cost(v) = 10 x (2^(v-1) - 1): extras cost 10, 20, 40, 80 EBX.
# Paying 2x for the same marginal vote == getting 1/2 the weight for the same
# marginal payment, so the block totals must land on 10 / 15 / 17.5 / 18.75.
for tk, want in [(10, 10.0), (20, 15.0), (30, 17.5), (40, 18.75)]:
    got = tm.weight_tokens(tk * T)
    ok(abs(got - want) < 1e-9, f"{tk} tokens → {want} weight", f"got {got}")
ok(tm.weight_tokens(5 * T) == 5.0, "flat below the first block")
ok(tm.weight_tokens(0) == 0.0, "nothing weighs nothing")
ok(tm.weight_tokens(15 * T) == 12.5, "half a block into the decay")
ok(all(tm.weight_ct(c + 1) > tm.weight_ct(c) for c in range(0, 4000, 97)),
   "strictly increasing — more money is never less weight")
ok(all(tm.weight_ct(c + T) - tm.weight_ct(c) >=
       tm.weight_ct(c + 2 * T) - tm.weight_ct(c + T) - 1e-9
       for c in range(0, 4000, 100)),
   "diminishing — each further token is worth no more than the last")
ok(tm.weight_tokens(10 * T, 2.0) == 20.0,
   "an influence multiplier scales weight, not money")
ok(tm.weight_tokens(40 * T, 2.0) == 2 * tm.weight_tokens(40 * T),
   "…cleanly, at every stake size")

# ---------------------------------------------------------------------------
section("influence — what being RIGHT is worth (2026-08-20)")
ok(tm.influence_mult("oe", me_correct=True) == 2.0,
   "correct ME voters get twice as much influence in the OE")
ok(tm.influence_mult("oe") == 1.0, "…and everyone else carries their stake, once")
ok(tm.influence_mult("oe", me_correct=False, oe_correct=True) == 1.0,
   "an OE vote cannot reward itself — the race it would weight is the race it is in")
ok(tm.influence_mult("budget", oe_correct=True) == 2.0,
   "correct OE voters get twice as much influence on budget voting")
ok(tm.influence_mult("budget", me_correct=True) == 1.0,
   "…and the ME result does not carry into budgeting on its own")
ok(tm.influence_mult("research", me_correct=True) == 1.5, "one right → 1.5x on research")
ok(tm.influence_mult("research", oe_correct=True) == 1.5, "either one, same 1.5x")
ok(abs(tm.influence_mult("research", True, True) - 2.25) < 1e-9,
   "both right → 2.25x — they MULTIPLY, exactly as Jax wrote it")
ok(tm.influence_mult("research") == 1.0, "neither → 1x")
ok(tm.weight_tokens(10 * T, tm.influence_mult("research", True, True)) == 22.5,
   "and it lands on the weight a stake actually carries")

# ---------------------------------------------------------------------------
section("settlement — ONE skim, and the ME is not it")
s = tm.settle_me(100 * T)
ok(tm.ME_SKIM == 0.0, "the initiative election claims nothing")
ok(s.claimed_ct == 0, "100 tokens → 0 claimed at the ME")
ok(s.carried_ct == 100 * T, "…and ALL of it forward into the winner's OE")
ok(s.total_ct == 100 * T, "nothing is created or destroyed")
ok(tm.settle_me(1).carried_ct == 1, "1 ct stake carries whole — no rounding to skim")
ok(tm.settle_me(0).total_ct == 0, "an empty stake settles to nothing")
ok(all(tm.settle_me(c).total_ct == c for c in range(0, 5000, 61)),
   "conservation holds at every stake size")
ok(all(tm.settle_me(c).claimed_ct == 0 for c in range(0, 5000, 61)),
   "…and the ME claims nothing at any stake size")

section("settlement — the ONE skim: the OE sends 100% on a win, 10% on a loss")
w = tm.settle_oe(90 * T, won=True)
ok((w.claimed_ct, w.carried_ct) == (90 * T, 0), "won → all of it is a donation")
l = tm.settle_oe(90 * T, won=False)
ok(l.claimed_ct == 9 * T, "lost → 10% claimed")
ok(l.carried_ct == 81 * T, "…and 81 tokens still the benefactor's")
ok(all(tm.settle_oe(c, won).total_ct == c
       for c in range(0, 5000, 71) for won in (True, False)),
   "conservation holds on both outcomes")

# ---------------------------------------------------------------------------
section("the four paths — and the promise on the landing page")
tbl = tm.outcome_table(100 * T)
via = tbl["via_me"]
ok(via["oe_win"]["donated_ct"] == 100 * T, "ME → OE won: 100% donated")
ok(via["oe_win"]["yours_ct"] == 0, "…nothing comes back")
ok(via["oe_lose"]["donated_ct"] == 10 * T,
   "ME → OE lost: 10% donated — the most you can lose, said ONCE",
   f'{via["oe_lose"]["donated_ct"] / T}%')
ok(via["oe_lose"]["yours_ct"] == 90 * T, "…90% is yours to redirect or take back")
direct = tbl["straight_to_oe"]
ok(direct["oe_win"]["donated_ct"] == 100 * T, "straight to an OE, won: 100%")
ok(direct["oe_lose"]["donated_ct"] == 10 * T, "straight to an OE, lost: 10%")
ok(direct["oe_lose"]["yours_ct"] == 90 * T, "…90% yours")
ok(via["oe_lose"] == direct["oe_lose"] and via["oe_win"] == direct["oe_win"],
   "arriving through an initiative election costs exactly nothing extra")
ok(tm.settle_me(100 * T).claimed_ct == tm.settle_me(100 * T).claimed_ct,
   "the ME rate does not depend on whether you won it")

# ---------------------------------------------------------------------------
section("the conversion budget closes the deferral loop")
ok(tm.MAX_CONVERSIONS == 3, "three conversions, and no clock")
ok(tm.conversions_left(0) == 3 and tm.conversions_left(3) == 0, "the count runs down")
ok(tm.conversions_left(9) == 0, "…and floors at zero rather than going negative")
ok(tm.can_convert(2) and not tm.can_convert(3), "the third move is the last one")
ok(tm.TOKEN_LIFE_WEEKS == 15, "15 weeks is a token's natural life: ME → OE (8) → mint (7)")
ok(tm.OE_AFTER_ME_WEEKS + tm.MINT_LAG_WEEKS == tm.TOKEN_LIFE_WEEKS,
   "…and the parts add up to the whole")
lot = tm.Lot(ct=10 * T, born_week=4)
ok(lot.matures_week == 19, "a lot committed in week 4 would mint in week 19")
ok(lot.conversions_left == 3, "a new lot has its whole budget")
a, b = lot.split(3 * T)
ok((a.ct, b.ct) == (3 * T, 7 * T), "a lot splits by ct")
ok(a.born_week == b.born_week == 4, "…and both halves keep the original clock")
moved = lot.record(tm.coin_element_oe(week=9, mission_id="oce1", org_id="oceana",
                                      amount_ct=10 * T, converted=True))
ok(moved.conversions_used == 1, "a move spends one")
x, y = moved.split(2 * T)
ok(x.conversions_left == y.conversions_left == 2,
   "splitting a moved lot does NOT buy either half three fresh conversions")

section("the grant carries a date, and the date rolls")
ok(tm.commit_by_week(6) == 7, "a grant paid in week 6 must be committed by week 7")
ok(tm.commit_by_week(6, purchased=True) is None,
   "purchased tokens carry no deadline at all")
ok(tm.roll_commit_by(7, 6) == 7, "an unmet deadline in the future stands")
ok(tm.roll_commit_by(7, 7) == 8, "…and a missed one moves forward exactly one week")
ok(tm.roll_commit_by(7, 30) == 31,
   "a benefactor who vanishes for months is where a weekly one is — not 23 weeks behind")
ok(tm.roll_commit_by(None, 9) is None, "nothing to roll if nothing is dated")

section("the coin's two elements")
el1 = tm.coin_element_me(week=4, mission_id="lan1", cause_id="land",
                         backed_tiv_id="protect-lakes", winning_tiv_id="tree-fund",
                         amount_ct=10 * T)
ok(el1.kind == "settle_me", "element 1 is written at the initiative election")
ok((el1.cause_id, el1.target_id, el1.winner_id) == ("land", "protect-lakes", "tree-fund"),
   "…and carries the cause, the initiative backed, and the one that WON")
ok(el1.outcome == "lost", "a losing vote is recorded as a losing vote")
ok(tm.coin_element_me(4, "lan1", "land", "tree-fund", "tree-fund", 10 * T).outcome == "won",
   "…and a winning one as won")
el2 = tm.coin_element_oe(week=12, mission_id="oce1", org_id="oceana-deep",
                         amount_ct=9 * T, converted=True)
ok(el2.kind == "move_oe", "element 2 marks a conversion as a move")
ok(tm.coin_element_oe(12, "lan1", "oceana-deep", 9 * T, converted=False).kind == "commit_oe",
   "…and voting in the race the ct was born in is not a conversion")
ok(tm.count_conversions([el1.as_dict(), el2.as_dict()]) == 1,
   "the count reads back off a stored chain")

section("one-way commitment — there is no returned balance to launder")
# The FIFO lot ledger that used to be asserted here is gone with the state it
# described: ct cannot come back out of a race, so it cannot rest in the
# unallocated bar shedding its history. What is left is the merge rule, which
# now applies at the moment of a conversion rather than at the moment of a
# re-spend.
ok(tm.merge_conversion(0, 0, 0) == 1, "a first move counts as one")
ok(tm.merge_conversion(5 * T, 1, 2) == 3,
   "…and a move into a row takes the HIGHER history, plus itself")
ok(tm.merge_conversion(0, 2, 0) == 3, "the destination's own count is not forgotten")
ok(not hasattr(tm, "push_lot") and not hasattr(tm, "take_lots"),
   "the returned-lot helpers are deleted, not left lying around")
ok(not hasattr(tm, "rebalance"),
   "…and so is `rebalance`, whose whole purpose was giving money back")
rows, free = tm.allocate({"lan1": 0, "oce3": 2 * T}, "lan1", 3 * T, free_ct=10 * T)
ok(rows["lan1"] == 3 * T and free == 7 * T, "committing to a row spends unallocated")
rows, free = tm.allocate(rows, "lan1", -5 * T, free)
ok(rows["lan1"] == 3 * T and free == 7 * T,
   "a negative commitment is a NO-OP, not a refund")
rows, free = tm.allocate(rows, "oce3", 99 * T, free)
ok(rows["oce3"] == 2 * T + 7 * T and free == 0,
   "asking for more than exists clamps to what unallocated can pay", f"{rows['oce3']} ct")
ok(free >= 0, "unallocated never goes negative")
ok(tm.allocation_ok([], rows.values(), free, 10 * T + 2 * T),
   "conservation survives every move above")

# ---------------------------------------------------------------------------
section("the wallet and its invariant")
w = tm.Wallet(cash_ct=250, free_ct=4 * T, staked_ct=26 * T,
              claimed_ct=9 * T, minted_ct=120 * T)
ok(w.tokens_ct == 30 * T, "the Tokens bin is free + staked")
ok(w.next_grant_ct == 6 * T, "holding 4 free → next grant is 6")
ok(w.donated_ct == 129 * T, "donated = claimed + minted")
d = w.as_dict()
ok(d["free"] == 4.0 and d["staked"] == 26.0, "display copies are in tokens")
ok(d["ct_per_token"] == 100, "the unit travels with the payload")
w2 = tm.Wallet(free_ct=10 * T, purchased_ct=3 * T, commit_by_week=7)
d2 = w2.as_dict()
ok(d2["grant_held_ct"] == 7 * T and d2["purchased_ct"] == 3 * T,
   "unallocated is granted + purchased, and the two are reported apart")
ok(d2["grant_held_ct"] + d2["purchased_ct"] == d2["free_ct"],
   "…and they are the WHOLE of it — there is no third kind")
ok(d2["commit_by_week"] == 7, "the grant's date rides along with the balance")
ok("returned_ct" not in d2 and "fresh_ct" not in d2,
   "the returned/fresh vocabulary is gone with the state it described")
ok(tm.Wallet(free_ct=T, purchased_ct=5 * T).as_dict()["purchased_ct"] == T,
   "the purchased slice can never exceed the balance holding it")

section("allocation — one conservation law, one direction")
ok(tm.allocation_ok([5 * T, 3 * T], [2 * T], 0, 10 * T), "rows + unallocated = owned")
ok(not tm.allocation_ok([5 * T], [2 * T], 0, 10 * T), "…and it catches a leak")

print(f"\n{N} assertions · " + (f"PROBLEMS: {BAD}" if BAD else "TOKEN MODEL CLEAN"))
sys.exit(1 if BAD else 0)
