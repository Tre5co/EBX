"""The money model — one file, pure functions, no database.

Settled 2026-08-19 with Jax over three conceptual passes (see
`docs/token_model.md`). Everything about what a token IS, what it is worth as a
vote, and what happens to it when an election closes lives HERE, so that
`crud.py`, the routers and the front end cannot each carry their own slightly
different arithmetic. `post_config.py` is the same idea for the discussion
model.

    $ CASH ──buy (only inside a commit)──▶ ◇ TOKENS ──stake──▶ ◇ staked
                                                                  │
                                              ME closes ──────────┤
                                              nothing claimed; ALL of it forward
                                              into the WINNING initiative's OE
                                              (coin element 1 written here)
                                                                  │
                                              OE closes ──────────┤   ← the one skim
                                              phl won  → 100% claimed
                                              phl lost →  10% claimed, 90% still committed
                                                                  │
                                              + 7 weeks ──────────▶ ● MINT → COIN
                                                                    (mission-tied, deductible)

Revised 2026-08-20 (build-seq §1). Two rules changed and one arrived:
  * ONE skim, and it falls after the organization election. The initiative
    election is a routing step now, not a settlement.
  * Being RIGHT pays in influence, not in a cheaper skim — 2x in the OE, 2x on
    budgeting, 1.5x each on research (2.25x for both).
  * A token's life is bounded by a CONVERSION COUNT (3), not by a 15-week fuse.

Four states, three bins, one wallet bar: **free │ staked │ claimed │ minted**.
Refunds land in CASH, never in TOKENS — which is what keeps `grant = 10 −
free` honest: nobody is ever billed a grant for money handed back to them.

WHY CENTITOKENS
---------------
Every quantity in this module is an **integer count of centitokens**. The live
database currently holds values like `123.7142858`, the loser-carryover skim
books `int(round(skim))` — which silently writes **0** for a 0.5 skim — and the
new model splits one balance across eight sliders, which is exactly the shape
of problem floats lose. So:

    1 token = 100 ct = 10¢          1 ct = 0.1¢

Rounding is always **up, to the nearest centitoken**, and always against the
benefactor (the claimed share is what gets rounded up). At ct granularity that
is a 0.1¢ bias; the same rule applied at whole-token granularity would round a
0.1-token skim up to a full token — a 10× overcharge — which is why the unit
matters more than the direction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Iterable, Literal, Optional

# ===========================================================================
# Units
# ===========================================================================
CT_PER_TOKEN = 100                 # 1 token = 100 centitokens
CENTS_PER_TOKEN = 10               # 1 token = 10¢  → 1 ct = 0.1¢
USD_PER_CT = CENTS_PER_TOKEN / 100 / CT_PER_TOKEN     # 0.001 USD


def tokens(ct: int) -> float:
    """ct → tokens, for display only. Never feed this back into the math."""
    return ct / CT_PER_TOKEN


def usd(ct: int) -> float:
    return round(ct * USD_PER_CT, 4)


def ct_from_tokens(t: float) -> int:
    """tokens → ct, rounding UP. Entry point for anything a human typed."""
    return int(ceil(round(t * CT_PER_TOKEN, 6)))


def _ceil_ct(x: float) -> int:
    """Round a ct quantity up to a whole ct.

    `round(x, 6)` first so that 0.1*300 = 30.000000000000004 does not become 31.
    That float-noise-then-ceil is the failure mode this whole module exists to
    avoid, and it would be funny to reintroduce it in the rounding helper.
    """
    return int(ceil(round(x, 6)))


# ===========================================================================
# The weekly grant
# ===========================================================================
# "Your uncommitted balance is topped up to 10 every week." A TOP-UP, not a
# reward and not a forfeiture: hold 6 free tokens and the grant is 4; hold 10 or
# more and it is 0. Nothing is ever taken away. What stops voting power piling
# up is the CAP, not a penalty — which is why the sentence above is the honest
# way to say it and "uncommitted tokens = less grant" is not.
WEEKLY_GRANT_CT = 10 * CT_PER_TOKEN          # 1000 ct = 10 tokens = $1

# The grant comes with a date on it (2026-08-20): "these granted tokens are
# marked with the date that they must be committed by (or expire). If they are
# not committed to one of these 2 missions by that date, the date changes 1 week
# forward." So the deadline is real on the face of the token and soft in effect —
# it is the end of the week it was granted in, and an uncommitted grant simply
# gets next week's date. Nothing is confiscated; what caps a hoard is the top-up
# formula (grant = 10 − free), which was always the mechanism.
#
# PURCHASED tokens carry no date at all — "purchased tokens are the same as
# granted tokens except they do not have a deadline to commit" — and no
# two-door restriction either. `commit_by_week(...)` returns None for them.
GRANT_COMMIT_BY_WEEKS = 1


def grant_ct(free_ct: int) -> int:
    """This week's grant, given what the benefactor is already holding free."""
    return max(0, WEEKLY_GRANT_CT - max(0, int(free_ct)))


def commit_by_week(granted_week: Optional[int], purchased: bool = False) -> Optional[int]:
    """The cycle week by which a grant must be committed. None if purchased."""
    if purchased or granted_week is None:
        return None
    return int(granted_week) + GRANT_COMMIT_BY_WEEKS


def roll_commit_by(deadline_week: Optional[int], now_week: int) -> Optional[int]:
    """Move a missed deadline forward one week, as many times as it is missed.

    Expressed as arithmetic rather than a loop so that a benefactor who does not
    open the page for a month is treated exactly like one who opened it weekly:
    the date on their uncommitted grant is the end of the CURRENT week either
    way. A loop here would make the answer depend on how often the code ran.
    """
    if deadline_week is None:
        return None
    if int(now_week) < int(deadline_week):
        return int(deadline_week)
    return int(now_week) + GRANT_COMMIT_BY_WEEKS


# ===========================================================================
# Vote weight — the diminishing curve that replaces the price ladder
# ===========================================================================
# The old phase-2 model priced extra votes on a doubling ladder:
#
#     p2_vote_cost(v) = 10 × (2^(v−1) − 1)      # extras cost 10, 20, 40, 80 …
#
# Paying 2× for the same marginal vote is arithmetically identical to receiving
# ½ the weight for the same marginal payment, so the ladder becomes a WEIGHT
# curve with no change to the underlying economics:
#
#     weight is 1:1 for the first block of 10 tokens,
#     then each further block of 10 counts for r× the block before it.
#
#     r = 0.5 → 10 tk = 10.00 · 20 tk = 15.00 · 30 tk = 17.50 · 40 tk = 18.75
#
# `r` is the one tunable knob: 0.5 reproduces today's economics exactly, higher
# is gentler, r = 1 is linear. Weight is returned in ct so callers never have to
# think about two units.
WEIGHT_BLOCK_CT = 10 * CT_PER_TOKEN          # the flat block: first 10 tokens
WEIGHT_R = 0.5                               # per-block decay


# ---------------------------------------------------------------------------
# Influence — what being RIGHT is worth (2026-08-20)
# ---------------------------------------------------------------------------
# "The result of the ME is that 'correct' voters get twice as much influence in
# the OE. 'Correct' OE voters get twice as much influence on budget voting. Both
# get 1.5x as much influence on research voting (so if you got both right, you
# get 2.25x)."
#
# This REPLACES the money reward that used to be here. Yesterday's model paid
# for being right by skimming winners and losers at different rates; today there
# is one skim and it falls on everyone equally (see Settlement below), so the
# entire reward for having voted correctly is influence in the NEXT decision.
# That is a better shape: it compounds into the thing a benefactor came for
# (deciding where the money goes) instead of into their own balance.
#
# Three arenas, and the multipliers do not all stack the same way, so they get
# named separately rather than folded into one number:
#
#   OE       — decided by ME voters. Correct ME vote ⇒ 2x.
#   BUDGET   — decided by OE voters. Correct OE vote ⇒ 2x.
#   RESEARCH — decided by everyone. Each correctness ⇒ 1.5x, and they MULTIPLY:
#              1.5 × 1.5 = 2.25 for a benefactor who got both right.
ME_CORRECT_OE_MULT = 2.0            # backed the winning initiative → 2x in its OE
OE_CORRECT_BUDGET_MULT = 2.0        # backed the winning philanthropy → 2x on budget
RESEARCH_MULT_EACH = 1.5            # each correctness → 1.5x on research (2.25 both)

Arena = Literal["oe", "budget", "research"]


def influence_mult(arena: Arena, me_correct: bool = False,
                   oe_correct: bool = False) -> float:
    """The multiplier a benefactor's weight carries into `arena`.

    Only the correctness that is KNOWN by the time the arena opens can count. A
    benefactor's OE vote is not settled while the OE is the thing being voted
    in, which is why `oe_correct` is ignored for the OE itself rather than
    silently rewarding a vote by its own outcome.
    """
    if arena == "oe":
        return ME_CORRECT_OE_MULT if me_correct else 1.0
    if arena == "budget":
        return OE_CORRECT_BUDGET_MULT if oe_correct else 1.0
    if arena == "research":
        return (RESEARCH_MULT_EACH ** (int(bool(me_correct)) + int(bool(oe_correct))))
    raise ValueError(f"unknown arena {arena!r}")


def weight_ct(stake_ct: int, mult: float = 1.0) -> float:
    """Vote weight of a stake, in ct-equivalent.

    Flat for the first block, then geometric decay per further block, times the
    influence multiplier the benefactor has earned. Returned as a float on
    purpose: weight is a ranking quantity, never money, and never settles into
    anyone's balance.

    `mult` used to be a `backed_winner` boolean. It is a number now because
    there are three arenas and one of them (research) is 2.25 — a flag cannot
    express that, and two flags in a weight function would be two chances to
    pass the wrong one.
    """
    s = max(0, int(stake_ct))
    total = 0.0
    block = 0
    while s > 0:
        take = min(s, WEIGHT_BLOCK_CT)
        total += take * (WEIGHT_R ** block)
        s -= take
        block += 1
    return total * float(mult if mult else 1.0)


def weight_tokens(stake_ct: int, mult: float = 1.0) -> float:
    return weight_ct(stake_ct, mult) / CT_PER_TOKEN


# ===========================================================================
# Settlement — what an election does to a stake
# ===========================================================================
# ONE SKIM, AND IT FALLS AFTER THE ORGANIZATION ELECTION (2026-08-20, Jax:
# "There will only be 1 'skim' after the OE").
#
# The initiative election takes NOTHING. It is not a settlement at all any more,
# it is a routing step: every backer's stake — the winner's and the losers'
# alike — moves whole into the winning initiative's organization election. Two
# reasons this is the right shape:
#
#   * A benefactor who is talked out of their first choice has still funded the
#     cause. Charging them on the way past the ME made the initiative vote feel
#     like a toll booth, and it double-counted the loss for anyone who then
#     backed a losing philanthropy too.
#   * With one skim, the promise finally reads in one clause — "the most you can
#     lose is 10%" — and it is TRUE, not "10% twice = 19%" with an asterisk.
#
# The reward for having been right is no longer a discount on the skim; it is
# the influence multiplier above.
ME_SKIM = 0.0                      # the initiative election claims nothing

# The one skim. Your philanthropy won and all of it is a donation; it lost and
# 10% is, with the rest yours to redirect to another race or take back as cash.
OE_SKIM_LOSE = 0.10
OE_SEND_WIN = 1.00
OE_SEND_LOSE = OE_SKIM_LOSE

# The claimed share is not minted at the election. It waits out the mission's
# 7-week budgeting phase and mints when the budget is set — the donation
# crystallises at the moment the mission knows what it is buying.
MINT_LAG_WEEKS = 7
OE_AFTER_ME_WEEKS = 8              # phl elected at T + 8wk
# A token used to carry a 15-week fuse: without one, a benefactor could hop to
# the newest organization election every week forever — always committed, never
# donating, collecting the full grant throughout. 2026-08-20 replaces the fuse
# with a COUNT: "there is no time limit on the token, but there is a limit to
# the amount of times it can be converted (3), which puts a de facto limit on
# the time." Same bound, better mechanic — a deadline punishes a benefactor for
# deliberating, a conversion budget prices the hop itself. Three conversions at
# eight weeks a race is a de facto ~32-week life.
MAX_CONVERSIONS = 3
# Kept as the natural life of ONE ct from commitment to mint (ME → OE → budget),
# which is still what the tax receipt is dated by. It is no longer an expiry.
TOKEN_LIFE_WEEKS = OE_AFTER_ME_WEEKS + MINT_LAG_WEEKS       # 15


def conversions_left(used: int) -> int:
    """How many more times this lot may be moved to a different race."""
    return max(0, MAX_CONVERSIONS - max(0, int(used or 0)))


def can_convert(used: int) -> bool:
    return conversions_left(used) > 0


@dataclass(frozen=True)
class Settlement:
    """What an election left behind. claimed + carried == the stake, exactly."""
    claimed_ct: int                # irrevocable; mints at OE close + 7 weeks
    carried_ct: int                # moves on (ME) or stays withdrawable (OE)

    @property
    def total_ct(self) -> int:
        return self.claimed_ct + self.carried_ct


def settle_me(stake_ct: int) -> Settlement:
    """Initiative election closes — and claims nothing.

    The whole stake carries into the winning initiative's organization election,
    whether this benefactor backed the winner or not. Kept as a function rather
    than deleted because the ROUTING is still a step the ledger has to record
    (it is the first element on the credit coin), and because a rate that lives
    in one named place can be changed in one named place.
    """
    s = max(0, int(stake_ct))
    claimed = min(s, _ceil_ct(s * ME_SKIM)) if ME_SKIM else 0
    return Settlement(claimed_ct=claimed, carried_ct=s - claimed)


def settle_oe(stake_ct: int, won: bool) -> Settlement:
    """Organization election closes. Won: all of it is a donation. Lost: 10% is,
    and `carried_ct` is the benefactor's to redirect to another mission or take
    back as cash — after the mission's 7-week budgeting phase."""
    s = max(0, int(stake_ct))
    if won:
        return Settlement(claimed_ct=s, carried_ct=0)
    claimed = min(s, _ceil_ct(s * OE_SEND_LOSE))
    return Settlement(claimed_ct=claimed, carried_ct=s - claimed)


def outcome_table(stake_ct: int = 100 * CT_PER_TOKEN) -> dict:
    """The four paths a staked token can take, as settled ct.

    One function so the docs, the landing copy and the UI cannot drift from the
    arithmetic. Two entry points are still reported, but since 2026-08-20 they
    settle to the SAME numbers: the initiative election takes nothing, so
    arriving at a philanthropy election through one costs no more than being
    committed to it directly. That equality is worth asserting rather than
    assuming, which is why both halves survive.
    """
    via_me = settle_me(stake_ct)
    return {
        "stake_ct": stake_ct,
        "via_me": {
            "me_claimed_ct": via_me.claimed_ct,
            "oe_win": {
                "donated_ct": via_me.claimed_ct + settle_oe(via_me.carried_ct, True).claimed_ct,
                "yours_ct": settle_oe(via_me.carried_ct, True).carried_ct,
            },
            "oe_lose": {
                "donated_ct": via_me.claimed_ct + settle_oe(via_me.carried_ct, False).claimed_ct,
                "yours_ct": settle_oe(via_me.carried_ct, False).carried_ct,
            },
        },
        "straight_to_oe": {
            "oe_win": {"donated_ct": settle_oe(stake_ct, True).claimed_ct,
                       "yours_ct": settle_oe(stake_ct, True).carried_ct},
            "oe_lose": {"donated_ct": settle_oe(stake_ct, False).claimed_ct,
                        "yours_ct": settle_oe(stake_ct, False).carried_ct},
        },
    }


# ===========================================================================
# Provenance — "every token maintains a record of its transactions"
# ===========================================================================
# A benefactor's tokens are a balance, not a hundred little objects, so the unit
# that can actually carry a history is the **lot**: ct that have always moved
# together. Split a lot and both halves inherit the history; merge two and you
# keep two lots rather than losing one's past. The chain survives the mint — a
# credit coin still knows which initiative and which philanthropy its ct backed
# on the way here.
#
# Only a REGISTERED vote is recorded. Dragging a slider up and down before
# committing leaves nothing behind: a benefactor's second thoughts are not part
# of the public record of what their money supported.
#
# THE COIN HAS TWO ELEMENTS (2026-08-20). Jax names them, and the naming is the
# specification:
#
#   element 1 — written when the initiative election hits. "They become marked
#     with the cause, initiative and date it was converted, as well as the
#     winning initiative." One event, `settle_me`, carrying both the initiative
#     this benefactor backed and the one that won: on a losing vote those differ,
#     and a coin that only remembered the winner would erase the argument that
#     made the mission.
#
#   element 2 — the conversions. Each move to a different organization election
#     is a `move_oe`, and there are at most MAX_CONVERSIONS of them.
ProvenanceKind = Literal["commit_me", "commit_oe", "move_oe", "settle_me",
                         "settle_oe", "mint", "refund"]


@dataclass(frozen=True)
class ProvenanceEvent:
    week: int                       # cycle week index — never a wall clock
    kind: ProvenanceKind
    mission_id: str
    amount_ct: int
    target_id: Optional[str] = None       # tiv id (ME) or org id (OE)
    outcome: Optional[str] = None         # 'won' | 'lost' | None while open
    cause_id: Optional[str] = None        # element 1: the cause it was cast in
    winner_id: Optional[str] = None       # element 1: the initiative that WON

    def as_dict(self) -> dict:
        return {"week": self.week, "kind": self.kind, "mission_id": self.mission_id,
                "amount_ct": self.amount_ct, "target_id": self.target_id,
                "outcome": self.outcome, "cause_id": self.cause_id,
                "winner_id": self.winner_id}


def coin_element_me(week: int, mission_id: str, cause_id: str, backed_tiv_id: str,
                    winning_tiv_id: str, amount_ct: int) -> ProvenanceEvent:
    """Element 1: what the initiative election made of these ct."""
    return ProvenanceEvent(
        week=week, kind="settle_me", mission_id=mission_id, amount_ct=int(amount_ct),
        target_id=backed_tiv_id, cause_id=cause_id, winner_id=winning_tiv_id,
        outcome=("won" if backed_tiv_id == winning_tiv_id else "lost"),
    )


def coin_element_oe(week: int, mission_id: str, org_id: str, amount_ct: int,
                    converted: bool) -> ProvenanceEvent:
    """Element 2: a philanthropy this stake stood behind. `converted` marks the
    ones that spent a conversion — i.e. moved to a race other than the one the
    initiative election put these ct in."""
    return ProvenanceEvent(
        week=week, kind=("move_oe" if converted else "commit_oe"),
        mission_id=mission_id, amount_ct=int(amount_ct), target_id=org_id,
    )


def count_conversions(history: Iterable[dict]) -> int:
    """Conversions spent, read back off a stored chain."""
    return sum(1 for e in (history or []) if (e or {}).get("kind") == "move_oe")


@dataclass(frozen=True)
class Lot:
    """ct that have always moved together, plus everything they have supported."""
    ct: int
    born_week: int                  # the week this lot's clock started
    history: tuple[ProvenanceEvent, ...] = field(default_factory=tuple)

    @property
    def conversions_used(self) -> int:
        return sum(1 for e in self.history if e.kind == "move_oe")

    @property
    def conversions_left(self) -> int:
        return conversions_left(self.conversions_used)

    @property
    def matures_week(self) -> int:
        """When ct committed at `born_week` would mint if it never converted.
        A projection, not a deadline — nothing expires any more."""
        return self.born_week + TOKEN_LIFE_WEEKS

    def record(self, event: ProvenanceEvent) -> "Lot":
        return Lot(self.ct, self.born_week, self.history + (event,))

    def split(self, take_ct: int) -> tuple["Lot", "Lot"]:
        """Split off `take_ct`. Both halves keep the whole history — and so the
        whole conversion count: splitting a lot must not buy three more moves."""
        take = max(0, min(int(take_ct), self.ct))
        return (Lot(take, self.born_week, self.history),
                Lot(self.ct - take, self.born_week, self.history))


def lots_total_ct(lots: Iterable[Lot]) -> int:
    return sum(l.ct for l in lots)


# ---------------------------------------------------------------------------
# Moving a stake — the only way ct leaves a race
# ---------------------------------------------------------------------------
# 2026-08-20, second pass. **Committed ct cannot come back.** Jax: "Users can no
# longer move tokens from an OE to unallocated. Unallocated is just the tokens
# they have either purchased or been granted and not yet allocated."
#
# That deletes a whole category of state. There is no returned balance, no lot
# ledger sitting in the wallet waiting to be re-spent, and no way for a stake to
# launder its history by resting in the bar for a week — because it cannot rest
# there at all. A committed token has exactly two futures: it stays where it is
# and settles, or it CONVERTS directly into another organization election,
# which is one transaction, requires a philanthropy vote at the destination, and
# spends one of three conversions.
#
# The two-way slider went with it. A slider says "this is a position you can
# revise"; one-way commitment is a decision, and it should cost a deliberate
# act — an amount, a philanthropy, and a button.
def merge_conversion(dest_ct: int, dest_conversions: int,
                     src_conversions: int) -> int:
    """The conversion count a destination row carries after ct arrives from
    another race.

    The HIGHER of the two, plus the move itself. Conservative on purpose:
    merging a thrice-moved stake into a fresh one must not buy back moves, and
    the count is a property of the ct, not of the row it happens to sit in.
    """
    return max(0, int(dest_conversions or 0), int(src_conversions or 0)) + 1


# ===========================================================================
# The wallet
# ===========================================================================
@dataclass(frozen=True)
class Wallet:
    """The four states, in ct. One bar, four segments, one invariant."""
    cash_ct: int = 0                # bought back or never spent; not a donation
    free_ct: int = 0               # UNALLOCATED — granted or purchased, not yet
                                   # committed. Topped up to 10 every week.
    # The part of free that was BOUGHT rather than granted. Authoritative, and
    # the grant-held part is derived from it — because after 2026-08-20 those are
    # the ONLY two things unallocated can contain ("unallocated is just the
    # tokens they have either purchased or been granted and not yet allocated"),
    # so tracking both would be tracking one number twice.
    #
    # They differ in exactly two ways: granted ct carries a commit-by date and
    # may only enter this week's two doors (the ME slate or the ONE active-cause
    # OE); purchased ct carries no date and may enter any race.
    purchased_ct: int = 0
    staked_ct: int = 0             # committed to a race — one-way, until it settles
    claimed_ct: int = 0            # irrevocable, awaiting mint at OE + 7 weeks
    minted_ct: int = 0             # credit coins, mission-tied, deductible
    # Cycle week by which the granted part must be committed, or it takes next
    # week's date. Never a forfeiture.
    commit_by_week: Optional[int] = None

    @property
    def grant_held_ct(self) -> int:
        """Unallocated ct that came from a grant: dated, and two doors."""
        return max(0, self.free_ct - max(0, self.purchased_ct))

    @property
    def tokens_ct(self) -> int:
        """The Tokens bin: free + staked. Claimed has left it; minted is a coin."""
        return self.free_ct + self.staked_ct

    @property
    def next_grant_ct(self) -> int:
        return grant_ct(self.free_ct)

    @property
    def donated_ct(self) -> int:
        return self.claimed_ct + self.minted_ct

    def as_dict(self) -> dict:
        purchased = min(max(0, self.purchased_ct), self.free_ct)
        return {
            "cash_ct": self.cash_ct,
            "free_ct": self.free_ct,
            # Unallocated is grant + purchased, and nothing else: ct committed to
            # a race never comes back to it.
            "grant_held_ct": self.grant_held_ct,
            "purchased_ct": purchased,
            "commit_by_week": self.commit_by_week,
            "staked_ct": self.staked_ct,
            "claimed_ct": self.claimed_ct,
            "minted_ct": self.minted_ct,
            "tokens_ct": self.tokens_ct,
            "next_grant_ct": self.next_grant_ct,
            "donated_ct": self.donated_ct,
            # display copies — the front end should never divide by 100 itself
            "cash": tokens(self.cash_ct),
            "free": tokens(self.free_ct),
            "grant_held": tokens(self.grant_held_ct),
            "purchased": tokens(purchased),
            "staked": tokens(self.staked_ct),
            "claimed": tokens(self.claimed_ct),
            "minted": tokens(self.minted_ct),
            "next_grant": tokens(self.next_grant_ct),
            "usd_donated": usd(self.donated_ct),
            "ct_per_token": CT_PER_TOKEN,
            "weekly_grant_ct": WEEKLY_GRANT_CT,
            "max_conversions": MAX_CONVERSIONS,
        }


# ===========================================================================
# Allocation — the conservation law, and the one direction it runs in
# ===========================================================================
# The ME table and the OE table both spend ONE cell: `free_ct`. Neither can
# reach into the other's committed rows, and — since 2026-08-20 — neither can
# reach into its OWN:
#
#     Σ(ME rows) + Σ(OE rows) + free = tokens owned        (still true)
#     free only ever goes DOWN, except when the weekly grant tops it up
#
# "Users can no longer move tokens from an OE to unallocated. Unallocated is
# just the tokens they have either purchased or been granted and not yet
# allocated." So allocation is a one-way door: ct leaves the bar for a race and
# the only way it moves again is a CONVERSION straight into another race.
#
# New tokens still have two doors — this week's grant may enter the ME slate or
# the ONE active-cause OE, per "2 options, not 9" — while PURCHASED ct may enter
# any race, which is why the unallocated bar still draws two colours. They are
# grant and purchase now, not grant and returned; there is no returned.
def allocation_ok(me_rows_ct: Iterable[int], oe_rows_ct: Iterable[int],
                  free_ct: int, owned_ct: int) -> bool:
    return sum(me_rows_ct) + sum(oe_rows_ct) + int(free_ct) == int(owned_ct)


def allocate(rows_ct: dict[str, int], key: str, add_ct: int,
             free_ct: int) -> tuple[dict[str, int], int]:
    """Commit `add_ct` more to one row, out of free. One direction only.

    Returns the new rows and the new free balance. The amount is CLAMPED to what
    free can pay rather than rejected, and a negative request is a no-op rather
    than a refund: this replaced `rebalance`, whose whole purpose was to let a
    slider give money back. It cannot, now — committing is a decision, and the
    way out of a race is `merge_conversion` into another one.
    """
    rows = dict(rows_ct)
    add = max(0, min(int(add_ct), max(0, int(free_ct))))
    rows[key] = int(rows.get(key, 0)) + add
    return rows, int(free_ct) - add
