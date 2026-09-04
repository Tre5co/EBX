"""token_model_check — the money model's arithmetic, asserted.

    python3 scripts/token_model_check.py        (from the repo root or backend/)

Pure math, no database and no server, so this is the one check that can be run
before anything else is wired. Every number the UI or the docs are allowed to
print about money should be derivable from something asserted here.

Rewritten 2026-08-27c with the model (`docs/ME_OE_FINALIZATION.md`): one flat
skim, the week change as the ratchet, the vote/amount split, and the four states
`unallocated -> committed -> minted -> donated`.
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
ok(tm.ct_from_tokens(1) == 100, "1 token -> 100 ct")
ok(tm.ct_from_tokens(0.001) == 1, "a tenth of a cent rounds up to 1 ct, not 0")
ok(tm.usd(1000) == 1.0, "10 tokens = $1", str(tm.usd(1000)))
ok(tm.usd(1) == 0.001, "1 ct = $0.001")

# ---------------------------------------------------------------------------
section("the grant — ten is a FLOOR, said from both ends")
ok(tm.grant_ct(0) == 1000, "hold nothing -> 10 tokens")
ok(tm.grant_ct(6 * T) == 4 * T, "hold 6 -> grant 4  (Jax's example)")
ok(tm.grant_ct(10 * T) == 0, "hold 10 -> no grant")
ok(tm.grant_ct(50 * T) == 0, "hold 50 -> no grant, never negative")
ok(tm.grant_ct(1) == 999, "hold 1 ct -> 999 ct: no cliff at the bottom")
ok(tm.available_ct(6 * T) == 10 * T,
   "<= 10 held -> 10 available in the next election")
ok(tm.available_ct(20 * T) == 20 * T,
   ">= 10 held -> that amount is available: nothing above ten is clawed back")
ok(all(tm.available_ct(h) == max(10 * T, h) for h in range(0, 4000, 53)),
   "available = max(10, held), at every holding")
ok(all(tm.grant_ct(f) + f == tm.available_ct(f) for f in range(0, 4000, 53)),
   "grant_ct and available_ct are the SAME rule read from opposite ends")
ok(not hasattr(tm, "commit_by_week") and not hasattr(tm, "roll_commit_by"),
   "the rolling commit-by date is gone: a granted token cannot expire or move")
ok(not hasattr(tm, "GRANT_COMMIT_BY_WEEKS"),
   "...and so is the constant behind it")

# ---------------------------------------------------------------------------
section("the vote is a split; the commit is an amount")
ok(tm.MAX_SPLIT_TIVS == 10, "a vote splits across at most 10 initiatives")
ok(tm.MAX_SPLIT_TIVS == 10 and tm.WEEKLY_GRANT_CT == 10 * T,
   "...and the grant is also ten, BY COINCIDENCE — neither defines the other")
n = tm.normalize_shares({"a": 1, "b": 3})
ok(abs(sum(n.values()) - 1.0) < 1e-9, "a slate normalizes to 1.0")
ok(abs(n["b"] - 0.75) < 1e-9, "...proportionally")
ok(tm.normalize_shares({"a": 5, "b": 0, "c": -2}) == {"a": 1.0},
   "non-positive shares are dropped, not counted")
ok(tm.normalize_shares({}) == {}, "an empty slate is empty, not an error")
try:
    tm.normalize_shares({str(i): 1 for i in range(11)})
    over = False
except ValueError:
    over = True
ok(over, "an 11-way split is refused")
sp = tm.split_ct(1000, {"a": 1, "b": 2})
ok(sum(sp.values()) == 1000, "an amount applied to a split loses no ct")
ok(sp == {"a": 333, "b": 667}, "...largest-remainder, not floor-and-lose", str(sp))
ok(all(sum(tm.split_ct(c, {"a": 1, "b": 1, "c": 1}).values()) == c
       for c in range(0, 3000, 37)),
   "conservation holds at every amount")
ok(tm.split_ct(0, {"a": 1}) == {"a": 0}, "no amount is no ct, not an error")
ok(tm.split_ct(500, {}) == {}, "no slate is no rows")

# ---------------------------------------------------------------------------
section("vote weight — r = 0.5 reproduces the old price ladder")
for tk, want in [(10, 10.0), (20, 15.0), (30, 17.5), (40, 18.75)]:
    got = tm.weight_tokens(tk * T)
    ok(abs(got - want) < 1e-9, f"{tk} tokens -> {want} weight", f"got {got}")
ok(tm.weight_tokens(5 * T) == 5.0, "flat below the first block")
ok(tm.weight_tokens(0) == 0.0, "nothing weighs nothing")
ok(tm.weight_tokens(15 * T) == 12.5, "half a block into the decay")
ok(all(tm.weight_ct(c + 1) > tm.weight_ct(c) for c in range(0, 4000, 97)),
   "strictly increasing — more money is never less weight")
ok(tm.weight_tokens(10 * T, 2.0) == 20.0,
   "an influence multiplier scales weight, not money")

# ---------------------------------------------------------------------------
section("influence — one of the three things being right is worth")
ok(tm.influence_mult("oe", me_correct=True) == 2.0,
   "correct ME voters get twice as much influence in the OE")
ok(tm.influence_mult("oe") == 1.0, "...and everyone else carries their stake, once")
ok(tm.influence_mult("oe", me_correct=False, oe_correct=True) == 1.0,
   "an OE vote cannot reward itself — the race it would weight is the race it is in")
ok(tm.influence_mult("budget", oe_correct=True) == 2.0,
   "correct OE voters get twice as much influence on budget voting")
ok(tm.influence_mult("research", me_correct=True) == 1.5, "one right -> 1.5x on research")
ok(abs(tm.influence_mult("research", True, True) - 2.25) < 1e-9,
   "both right -> 2.25x — they MULTIPLY, exactly as Jax wrote it")
ok(tm.influence_mult("research") == 1.0, "neither -> 1x")
ok(tm.weight_tokens(10 * T, tm.influence_mult("research", True, True)) == 22.5,
   "and it lands on the weight a stake actually carries")

# ---------------------------------------------------------------------------
section("the week change is the ratchet")
ok(tm.hardens_at_week(6) == 7, "an allocation made in week 6 hardens in week 7")
ok(tm.is_soft(6, 6), "inside its own week it is a draft — move it as often as you like")
ok(not tm.is_soft(6, 7), "at the roll it is EBX and it stops moving")
ok(not tm.is_soft(None, 7), "a row from before the column existed is long hardened")
ok(not hasattr(tm, "MAX_CONVERSIONS"), "the conversion budget is gone")
ok(not hasattr(tm, "conversions_left") and not hasattr(tm, "can_convert"),
   "...and so are the functions that counted it down")
ok(not hasattr(tm, "merge_conversion"),
   "...and the merge rule that stopped a split from buying extra moves")
ok(not hasattr(tm, "allocate"),
   "one-way `allocate` is gone: inside the week an allocation is a position")

# ---------------------------------------------------------------------------
section("settlement — the initiative election is a routing step")
s = tm.settle_me(100 * T)
ok(tm.ME_SKIM == 0.0, "the initiative election claims nothing")
ok(s.donated_ct == 0, "100 tokens -> 0 donated at the ME")
ok(s.held_ct == 100 * T, "...and ALL of it forward into the winner's OE")
ok(all(tm.settle_me(c).total_ct == c for c in range(0, 5000, 61)),
   "conservation holds at every stake size")

section("settlement — A CLEAN 10%, ACROSS THE BOARD")
ok(tm.OE_SKIM == 0.10, "one rate")
ok(not hasattr(tm, "OE_SEND_WIN") and not hasattr(tm, "OE_SKIM_LOSE"),
   "the win/lose rates are gone — being right is not worth money")
r = tm.settle_oe(100 * T)
ok(r.donated_ct == 10 * T, "10% of every stake is donated")
ok(r.held_ct == 90 * T, "...and the other 90% becomes EBX for that mission")
ok(all(tm.settle_oe(c).total_ct == c for c in range(0, 5000, 71)),
   "conservation holds at every stake size")
ok(tm.settle_oe(1).donated_ct == 1,
   "a 1 ct stake rounds the donation UP — against the benefactor, at 0.1c")
try:
    tm.settle_oe(100 * T, True)
    took_won = True
except TypeError:
    took_won = False
ok(not took_won, "settle_oe takes no `won` argument to quietly re-invent the fork")
tbl = tm.outcome_table(100 * T)
ok(tbl["donated_ct"] == 10 * T and tbl["ebx_ct"] == 90 * T,
   "the outcome table is ONE row now, not four")
ok(tbl["skim_rate"] == 0.10, "...and it prints the rate it used")

section("donation is an event, and it happens more than once")
ok(tm.tranche_ct(90 * T, 0.10) == 9 * T, "a tranche is a fraction of what is held")
ok(tm.tranche_ct(90 * T, 1.0) == 90 * T, "the last tranche can be all of it")
ok(tm.tranche_ct(90 * T, 5.0) == 90 * T, "...and never more than is there")
ok(tm.tranche_ct(0, 0.5) == 0, "nothing held, nothing donated")
ok(not hasattr(tm, "MINT_LAG_WEEKS"),
   "the mint is not a lag: EBX exists at mission identity")
ok(tm.BUDGET_SET_WEEKS == 7,
   "seven weeks names the budget being set, which is what it always measured")
ok(not hasattr(tm, "TOKEN_LIFE_WEEKS"), "nothing expires on a clock any more")

# ---------------------------------------------------------------------------
section("the field: eight open, fourteen over a token's life")
ok(tm.OE_TABLE_ROWS == 8, "eight races are open at any instant")
ok(tm.OE_LIFETIME_RACES == 14,
   "...and fourteen is what one token can reach as the field rotates under it")
ok(tm.OE_TABLE_ROWS + 6 == tm.OE_LIFETIME_RACES,
   "8 at the beginning + 6 that open while it waits = 14")

# ---------------------------------------------------------------------------
section("the coin's two elements")
el1 = tm.coin_element_me(week=4, mission_id="lan1", cause_id="land",
                         backed_tiv_id="protect-lakes", winning_tiv_id="tree-fund",
                         amount_ct=10 * T)
ok(el1.kind == "settle_me", "element 1 is written at the initiative election")
ok((el1.cause_id, el1.target_id, el1.winner_id) == ("land", "protect-lakes", "tree-fund"),
   "...and carries the cause, the initiative backed, and the one that WON")
ok(el1.outcome == "lost", "a losing vote is recorded as a losing vote")
el2 = tm.coin_element_oe(week=12, mission_id="oce1", org_id="oceana-deep",
                         amount_ct=9 * T)
ok(el2.kind == "mint_ebx", "element 2 is the philanthropy these ct minted behind")
ok(not hasattr(tm, "count_conversions"), "there are no conversions to count")
don = tm.coin_donation(week=20, mission_id="oce1", amount_ct=T)
ok(don.kind == "donate", "a tranche is its own event, dated for the deduction")
chain = [el1.as_dict(), el2.as_dict(), don.as_dict()]
ok(tm.minted_ct_of(chain) == 9 * T, "a chain says how much has hardened")
ok(tm.donated_ct_of(chain) == T, "...and how much has crossed over")
lot = tm.Lot(ct=10 * T, born_week=4)
a, b = lot.split(3 * T)
ok((a.ct, b.ct) == (3 * T, 7 * T), "a lot splits by ct")
ok(a.born_week == b.born_week == 4, "...and both halves keep the original clock")
ok(not hasattr(lot, "matures_week"), "a lot has no maturity date to print")

# ---------------------------------------------------------------------------
section("the wallet: unallocated -> committed -> minted -> donated")
w = tm.Wallet(cash_ct=250, free_ct=4 * T, committed_ct=26 * T,
              minted_ct=120 * T, donated_ct=9 * T)
ok(w.tokens_ct == 30 * T, "the Tokens bin is free + committed")
ok(w.ebx_ct == 120 * T, "EBX is what has minted and not yet been donated")
ok(w.next_grant_ct == 6 * T, "holding 4 free -> next grant is 6")
d = w.as_dict()
ok("claimed_ct" not in d and "staked_ct" not in d,
   "`claimed` goes back to meaning an ORG claiming a mission; `staked` is `committed`")
ok(d["free"] == 4.0 and d["committed"] == 26.0, "display copies are in tokens")
ok(d["ct_per_token"] == 100, "the unit travels with the payload")
ok(d["oe_skim"] == 0.10, "...and so does the one rate a benefactor is charged")
ok("max_conversions" not in d, "the wallet no longer advertises a conversion budget")
w2 = tm.Wallet(free_ct=10 * T, purchased_ct=3 * T, grant_cause_id="forests")
d2 = w2.as_dict()
ok(d2["grant_held_ct"] == 7 * T and d2["purchased_ct"] == 3 * T,
   "unallocated is granted + purchased, and the two are reported apart")
ok(d2["grant_held_ct"] + d2["purchased_ct"] == d2["free_ct"],
   "...and they are the WHOLE of it — there is no third kind")
ok(d2["grant_cause_id"] == "forests",
   "a granted token carries its cause where the deadline used to be")
ok("commit_by_week" not in d2, "...and the deadline is not there any more")
ok(d2["available_ct"] == 10 * T, "the wallet says what is votable next")
ok(tm.Wallet(free_ct=T, purchased_ct=5 * T).as_dict()["purchased_ct"] == T,
   "the purchased slice can never exceed the balance holding it")

section("allocation — a position inside the week, and one conservation law")
ok(tm.allocation_ok([5 * T, 3 * T], [2 * T], 0, 10 * T), "rows + unallocated = owned")
ok(not tm.allocation_ok([5 * T], [2 * T], 0, 10 * T), "...and it catches a leak")
rows, free = tm.set_allocation({"lan1": 0, "oce3": 2 * T}, "lan1", 3 * T, free_ct=10 * T)
ok(rows["lan1"] == 3 * T and free == 7 * T, "committing to a row spends unallocated")
rows, free = tm.set_allocation(rows, "lan1", T, free)
ok(rows["lan1"] == T and free == 9 * T,
   "and dialling it back DOWN returns the difference — inside the week it is a draft")
rows, free = tm.set_allocation(rows, "oce3", 99 * T, free)
ok(rows["oce3"] == 11 * T and free == 0,
   "asking for more than exists clamps to what unallocated can pay", f"{rows['oce3']} ct")
rows, free = tm.set_allocation(rows, "oce3", -5 * T, free)
ok(rows["oce3"] == 0 and free == 11 * T, "a negative target is zero, not a debt")
ok(tm.allocation_ok([], rows.values(), free, 12 * T),
   "conservation survives every move above")

print(f"\n{N} assertions · " + (f"PROBLEMS: {BAD}" if BAD else "TOKEN MODEL CLEAN"))
sys.exit(1 if BAD else 0)
