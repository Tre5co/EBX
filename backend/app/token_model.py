"""The money model — one file, pure functions, no database.

Rewritten 2026-08-27c for the finalized ME/OE model
(`docs/ME_OE_FINALIZATION.md`, answered by Jax the same day). Everything about
what a token IS, what it is worth as a vote, and what happens to it when an
election closes lives HERE, so that `crud.py`, the routers and the front end
cannot each carry their own slightly different arithmetic. `post_config.py` is
the same idea for the discussion model.

TWO UNITS, NOT TWO NAMES FOR ONE UNIT
-------------------------------------
**Tokens are convertible; EBX is not.** That one sentence is the model.

    $ CASH ──buy──▶ ◇ TOKEN ──commit──▶ ◇ committed ──week roll──▶ ● EBX ──tranche──▶ ✓ DONATED
                        ▲                    │                        │
                        └── purchased ct ────┘                        └─ 10% at OE close,
                           may still move                                more as the mission runs
                           until it enters
                           this week's race

    unallocated  →  committed  →  minted  →  donated
    free tokens     to a tiv       to a      consumed by the org
                    (or a phl)     mission   or by Earthbux

A token becomes EBX only when its **mission identity is final** — which is why
an allocation sitting in an initiative election is still a token however long it
sits there: the initiative it backs may never become a mission. `claimed` is NOT
a wallet state; it is the word for an organization claiming a mission, and the
wallet gave it back on 2026-08-27c.

WHAT CHANGED, IN FIVE SENTENCES
-------------------------------
* The **week change** is the ratchet. Inside a week an allocation is a draft;
  at the roll every standing OE allocation hardens into EBX. This retires both
  `MAX_CONVERSIONS = 3` and one-way commitment — the two mechanisms that were
  doing this job badly between 2026-08-20 and today.
* The grant **does not exist until its week**. Ten tokens appear against the
  week's cause, cannot be transferred or withdrawn (there is no moment at which
  they exist and are free), and if unspent they wait for that cause's next
  window. Purchase is the only mobile money in the model.
* A **vote is a split; the commit is an amount.** Up to `MAX_SPLIT_TIVS`
  percentages, and one number for the whole election. A vote can therefore
  stand before the tokens that will back it — it is a preference with no
  funding yet, not a state of anything.
* **One flat skim.** 10% of every stake, winners and losers alike. Being right
  pays in early EBX, in an upgraded mission membership, and in influence — never
  in money.
* **The other 90% becomes the benefactor's EBX for that mission**, and is
  donated in tranches as the mission runs. Each tranche is deductible when it
  crosses; the 10% at OE close is simply the first one.

WHY CENTITOKENS
---------------
Every quantity in this module is an **integer count of centitokens**. The live
database holds values like `123.7142858`; a skim booked with `int(round())`
silently writes 0 for a 0.5 skim; and one balance is split across a slate and a
field of races. Floats lose exactly this shape of problem. So:

    1 token = 100 ct = 10c          1 ct = 0.1c

Rounding is always **up, to the nearest centitoken**, and always against the
benefactor (the donated share is what gets rounded up). At ct granularity that
is a 0.1c bias; the same rule at whole-token granularity would round a 0.1-token
skim up to a full token — a 10x overcharge — which is why the unit matters more
than the direction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Iterable, Literal, Mapping, Optional

# ===========================================================================
# Units
# ===========================================================================
CT_PER_TOKEN = 100                 # 1 token = 100 centitokens
CENTS_PER_TOKEN = 10               # 1 token = 10c  -> 1 ct = 0.1c
USD_PER_CT = CENTS_PER_TOKEN / 100 / CT_PER_TOKEN     # 0.001 USD


def tokens(ct: int) -> float:
    """ct -> tokens, for display only. Never feed this back into the math."""
    return ct / CT_PER_TOKEN


def usd(ct: int) -> float:
    return round(ct * USD_PER_CT, 4)


def ct_from_tokens(t: float) -> int:
    """tokens -> ct, rounding UP. Entry point for anything a human typed."""
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
# "10 tokens appear in your account each week. These tokens can only be used in
# this weeks elections." And, when asked what happens to an unspent one:
#
#   "If there are <= 10 total tokens, 10 tokens will be available in the next
#    election for that cause or its replacement. If there are >= 10 total
#    tokens, that amount of tokens is available in the next election."
#
# Which is a FLOOR, not a ration: hold six and four arrive, hold twenty and
# twenty are votable. `grant_ct` and `available_ct` are the same rule read from
# opposite ends, and both are here so neither the wallet nor the UI has to
# derive one from the other and get the direction wrong.
WEEKLY_GRANT_CT = 10 * CT_PER_TOKEN          # 1000 ct = 10 tokens = $1

# THE GRANT DOES NOT EXIST UNTIL ITS WEEK (2026-08-27c). "Tokens aren't granted
# until election week when it's too late to transfer or withdraw. You can vote
# beforehand, but the tokens aren't there yet." So there is no commit-by date to
# roll and no window in which granted ct is both real and free — the fence and
# the payment are the same event. `GRANT_COMMIT_BY_WEEKS`, `commit_by_week` and
# `roll_commit_by` are gone with the rule they enforced; a granted token carries
# its CAUSE instead, which is a fact a benefactor can act on.


def grant_ct(free_ct: int) -> int:
    """This week's grant, given what the benefactor is already holding free."""
    return max(0, WEEKLY_GRANT_CT - max(0, int(free_ct)))


def available_ct(held_ct: int) -> int:
    """What is votable in the next election: `max(10, held)`. The same
    arithmetic as `grant_ct`, said the way Jax said it."""
    return max(WEEKLY_GRANT_CT, max(0, int(held_ct)))


# ===========================================================================
# The vote and the amount — two quantities, one election
# ===========================================================================
# "Since the maximum amount of tivs you can split your vote into is 10, we can
# have the vote commit be the total amount committed to that election, and the
# weight be the percentage given to each tiv within it."
#
#   the vote    a split across up to MAX_SPLIT_TIVS initiatives, in percentages.
#               Settable ANY TIME — it needs no tokens.
#   the commit  ONE number: total tokens committed to that election. Settable
#               when the tokens exist.
#
# A tiv's weight is `commit x that tiv's percentage`. A vote standing with no
# commit behind it is not a promissory note or a third state of anything — it is
# a preference with no funding yet, and when the grant lands it flows through
# whatever split is standing.
#
# NOTE, because it is exactly the kind of thing a later reader derives a rule
# from: MAX_SPLIT_TIVS and WEEKLY_GRANT_CT are both ten BY COINCIDENCE (Jax,
# 2026-08-27c). They are independent numbers. A grant of 12 would not widen the
# slate and an 8-way cap would not shrink the grant, so neither is defined in
# terms of the other here.
MAX_SPLIT_TIVS = 10


def normalize_shares(shares: Mapping[str, float]) -> dict[str, float]:
    """Clean a slate into percentages that sum to 1.0.

    Drops non-positive entries, refuses more than `MAX_SPLIT_TIVS`, and scales
    what is left. Normalizing here rather than at the door means the stored
    slate is always a percentage split, whatever the UI sent — the amount is a
    separate number and multiplying by it is the only place the two meet.
    """
    clean = {k: float(v) for k, v in (shares or {}).items() if float(v or 0) > 0}
    if len(clean) > MAX_SPLIT_TIVS:
        raise ValueError(f"A vote may be split across at most {MAX_SPLIT_TIVS} "
                         f"initiatives ({len(clean)} given)")
    total = sum(clean.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in clean.items()}


def split_ct(commit_ct: int, shares: Mapping[str, float]) -> dict[str, int]:
    """Apply an amount to a normalized split, in whole ct, losing nothing.

    Largest-remainder: floor every share, then hand the leftover ct out to the
    biggest remainders. `sum(split_ct(n, s).values()) == n` exactly, which is
    the property the conservation law downstream depends on.
    """
    norm = normalize_shares(shares)
    total = max(0, int(commit_ct or 0))
    if not norm or total <= 0:
        return {k: 0 for k in norm}
    raw = {k: total * v for k, v in norm.items()}
    out = {k: int(x) for k, x in raw.items()}
    short = total - sum(out.values())
    for k, _r in sorted(raw.items(), key=lambda kv: (kv[1] - int(kv[1])), reverse=True):
        if short <= 0:
            break
        out[k] += 1
        short -= 1
    return out


# ===========================================================================
# Vote weight — the diminishing curve that replaces the price ladder
# ===========================================================================
# The old phase-2 model priced extra votes on a doubling ladder:
#
#     p2_vote_cost(v) = 10 x (2^(v-1) - 1)      # extras cost 10, 20, 40, 80 ...
#
# Paying 2x for the same marginal vote is arithmetically identical to receiving
# 1/2 the weight for the same marginal payment, so the ladder becomes a WEIGHT
# curve with no change to the underlying economics:
#
#     weight is 1:1 for the first block of 10 tokens,
#     then each further block of 10 counts for r x the block before it.
#
#     r = 0.5 -> 10 tk = 10.00 . 20 tk = 15.00 . 30 tk = 17.50 . 40 tk = 18.75
WEIGHT_BLOCK_CT = 10 * CT_PER_TOKEN          # the flat block: first 10 tokens
WEIGHT_R = 0.5                               # per-block decay


# ---------------------------------------------------------------------------
# Influence — what being RIGHT is worth
# ---------------------------------------------------------------------------
# "The result of the ME is that 'correct' voters get twice as much influence in
# the OE. 'Correct' OE voters get twice as much influence on budget voting. Both
# get 1.5x as much influence on research voting (so if you got both right, you
# get 2.25x)."
#
# CONFIRMED 2026-08-27c: these survive the flat skim, and they are joined by the
# two rewards the finalized model names — EARLY EBX for backing the winning
# initiative (rule 4a: the stake mints the moment the initiative election
# closes, a week ahead of everyone else's) and an UPGRADED MISSION MEMBERSHIP
# for backing the winning philanthropy. None of the three is money. That is the
# point: one skim falls on everyone at the same rate, so the prize for being
# right compounds into the next decision rather than into a balance.
ME_CORRECT_OE_MULT = 2.0            # backed the winning initiative -> 2x in its OE
OE_CORRECT_BUDGET_MULT = 2.0        # backed the winning philanthropy -> 2x on budget
RESEARCH_MULT_EACH = 1.5            # each correctness -> 1.5x on research (2.25 both)

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
# The week change — the ratchet
# ===========================================================================
# "The conversion only happens at a week-change. Users will be able to convert
# as many times as they want within the same week." And, asked WHICH
# allocations harden: "All OE allocations."
#
# So inside a week an allocation is a DRAFT — move it between eligible races as
# often as you like, at no cost, with nothing to buy back. At the roll, every
# standing organization-election allocation hardens: those ct become EBX for
# that mission and stop moving.
#
# ME allocations do NOT harden at the roll. The mission identity is not final
# until the initiative election is, and EBX cannot predate its mission — a slate
# can be redrawn week after week and what ends that is `finalize_p1`, not the
# calendar. The roll is the ratchet on the ORGANIZATION side only, which is the
# side where the money picks a recipient.
#
# This is a better instrument than either mechanism it replaces. A conversion
# COUNT priced the hop and made a benefactor's freedom a private number nobody
# else could see; one-way commitment priced deliberation itself. A week boundary
# prices nothing, punishes nothing, and gives everybody the same deadline.


def hardens_at_week(committed_week: int) -> int:
    """The week in which an OE allocation made in `committed_week` becomes EBX."""
    return int(committed_week) + 1


def is_soft(committed_week: Optional[int], now_week: int) -> bool:
    """True while an allocation can still be moved for free — i.e. the week it
    was made in is the week we are in. `None` (a row from before the column
    existed) is treated as hardened, because it certainly is by now."""
    if committed_week is None:
        return False
    return int(now_week) <= int(committed_week)


# ===========================================================================
# Settlement — one flat skim, and what the rest becomes
# ===========================================================================
# "It's a clean 10% across the board, winners and losers pay the same, the
# difference comes after (special ebx for ME, special mission membership for
# OE)." — Jax, 2026-08-27c
#
# The four-path table is gone, and with it `OE_SEND_WIN`, `OE_SEND_LOSE` and the
# buyer's sentence that needed a clause for each path. What is left is one rate
# and one destination for the rest:
#
#   10% of whatever you commit is the skim.
#   The other 90% becomes your EBX for that mission.
#
# The initiative election still takes nothing — it is a routing step, not a
# settlement — so `ME_SKIM` stays at 0 and stays named, because a rate that
# lives in one place can be changed in one place.
ME_SKIM = 0.0                      # the initiative election claims nothing
OE_SKIM = 0.10                     # the one skim, paid by everyone

# The field a marked token can reach. Eight races are open at any instant (a
# mission enters phase 2 every week and leaves eight weeks later); wait six
# weeks and six more have opened under it, which is the 14 the model names —
# "7 elected before, the current one, and 6 elected later". Fourteen is a
# LIFETIME, not a screen: the table is always the eight.
OE_TABLE_ROWS = 8
OE_LIFETIME_RACES = 14
OE_AFTER_ME_WEEKS = 8              # phl elected at T + 8wk

# Seven weeks after the organization election the budget is set. That is what
# `MINT_LAG_WEEKS` was really measuring, and it is NOT the mint: EBX exists at
# mission identity, and the deduction rides each donation tranche rather than a
# date. Renamed for what it is, and nothing now expires on it.
BUDGET_SET_WEEKS = 7


@dataclass(frozen=True)
class Settlement:
    """What an election left behind. donated + held == the stake, exactly."""
    donated_ct: int                # gone, deductible, split between org and Earthbux
    held_ct: int                   # the benefactor's EBX for this mission

    @property
    def total_ct(self) -> int:
        return self.donated_ct + self.held_ct


def settle_me(stake_ct: int) -> Settlement:
    """Initiative election closes — and claims nothing.

    Kept as a function rather than deleted because the ROUTING is still a step
    the ledger has to record (it is the first element on the credit coin).
    """
    s = max(0, int(stake_ct))
    donated = min(s, _ceil_ct(s * ME_SKIM)) if ME_SKIM else 0
    return Settlement(donated_ct=donated, held_ct=s - donated)


def settle_oe(stake_ct: int) -> Settlement:
    """Organization election closes. 10% is donated — whoever you backed — and
    the rest becomes EBX for this mission.

    There is deliberately no `won` argument any more. Being right is worth early
    EBX, a mission membership and influence; it has not been worth money since
    2026-08-27c, and a boolean here would be the place that quietly re-invented
    it.
    """
    s = max(0, int(stake_ct))
    donated = min(s, _ceil_ct(s * OE_SKIM))
    return Settlement(donated_ct=donated, held_ct=s - donated)


def tranche_ct(held_ct: int, fraction: float) -> int:
    """One donation tranche out of a benefactor's remaining EBX.

    Donation is an EVENT and it happens more than once: "the tax deduction
    happens when the ebx is donated (included in the skim). Throughout the
    mission, more ebx will be donated." The 10% at the organization election is
    simply the first tranche, which is what "included in the skim" means — the
    skim is not a separate charge outside the donation flow, it is the opening
    instalment of it.

    What TRIGGERS each later tranche, and how each is divided between the
    organization and Earthbux, belongs to the resolutions phase and is not
    modelled here. This function is the arithmetic those rules will call, and
    nothing more.
    """
    h = max(0, int(held_ct))
    return min(h, _ceil_ct(h * max(0.0, float(fraction))))


def outcome_table(stake_ct: int = 100 * CT_PER_TOKEN) -> dict:
    """What a commitment settles into, so the docs, the landing copy and the UI
    cannot drift from the arithmetic.

    One row now, where there used to be four. That is the point of the flat
    skim: the promise no longer needs to know how you voted.
    """
    oe = settle_oe(stake_ct)
    return {
        "stake_ct": stake_ct,
        "skim_rate": OE_SKIM,
        "donated_ct": oe.donated_ct,
        "ebx_ct": oe.held_ct,
        "donated": tokens(oe.donated_ct),
        "ebx": tokens(oe.held_ct),
        "usd_donated": usd(oe.donated_ct),
    }


# ===========================================================================
# Provenance — "every token maintains a record of its transactions"
# ===========================================================================
# A benefactor's tokens are a balance, not a hundred little objects, so the unit
# that can carry a history is the **lot**: ct that have always moved together.
# Split a lot and both halves inherit the history. The chain survives the mint —
# a credit coin still knows which initiative and which philanthropy its ct
# backed on the way here.
#
# ONLY A REGISTERED VOTE IS RECORDED, and under the week-change rule that has a
# sharper meaning than it used to: what is registered is what STANDS AT THE
# ROLL. A benefactor who moves an allocation three times on a Thursday leaves
# one event behind, not three, because the first two were drafts. Second
# thoughts are not part of the public record of what someone's money supported.
#
# THE COIN HAS TWO ELEMENTS, and Jax's naming of them is the specification:
#
#   element 1 — written when the initiative election hits. "They become marked
#     with the cause, initiative and date it was converted, as well as the
#     winning initiative." One event per initiative this benefactor backed,
#     carrying both what they backed and what won: on a losing vote those
#     differ, and a coin that only remembered the winner would erase the
#     argument that made the mission.
#
#   element 2 — the philanthropy these ct stand behind, written when the
#     allocation hardens. A split ME vote leaves a benefactor holding tokens
#     with different marks; once they are committed to an OE and minted, the
#     mark is FORGOTTEN in the balance and lives only here.
ProvenanceKind = Literal["commit_me", "settle_me", "mint_ebx", "donate", "refund"]


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


def coin_element_oe(week: int, mission_id: str, org_id: Optional[str],
                    amount_ct: int) -> ProvenanceEvent:
    """Element 2: the philanthropy these ct minted behind, at the week roll.

    `org_id` is Optional for one real case: EARLY EBX. A benefactor who backed
    the winning initiative mints the moment the initiative election closes — a
    week ahead of everyone else, which is what the reward IS — and at that
    moment the mission is known but its organization has not been elected yet.
    The philanthropy is named on the ROW when the race decides, rather than
    rewritten into this event: the chain records what was true when it happened.
    """
    return ProvenanceEvent(week=week, kind="mint_ebx", mission_id=mission_id,
                           amount_ct=int(amount_ct), target_id=org_id)


def coin_donation(week: int, mission_id: str, amount_ct: int,
                  note: Optional[str] = None) -> ProvenanceEvent:
    """A donation tranche crossing out of held EBX. Deductible at this date."""
    return ProvenanceEvent(week=week, kind="donate", mission_id=mission_id,
                           amount_ct=int(amount_ct), outcome=note)


def minted_ct_of(history: Iterable[dict]) -> int:
    """How much of a chain has hardened into EBX."""
    return sum(int((e or {}).get("amount_ct") or 0)
               for e in (history or []) if (e or {}).get("kind") == "mint_ebx")


def donated_ct_of(history: Iterable[dict]) -> int:
    """How much of a chain has been donated, across every tranche."""
    return sum(int((e or {}).get("amount_ct") or 0)
               for e in (history or []) if (e or {}).get("kind") == "donate")


@dataclass(frozen=True)
class Lot:
    """ct that have always moved together, plus everything they have supported."""
    ct: int
    born_week: int                  # the week this lot's clock started
    history: tuple[ProvenanceEvent, ...] = field(default_factory=tuple)

    def record(self, event: ProvenanceEvent) -> "Lot":
        return Lot(self.ct, self.born_week, self.history + (event,))

    def split(self, take_ct: int) -> tuple["Lot", "Lot"]:
        """Split off `take_ct`. Both halves keep the whole history."""
        take = max(0, min(int(take_ct), self.ct))
        return (Lot(take, self.born_week, self.history),
                Lot(self.ct - take, self.born_week, self.history))


def lots_total_ct(lots: Iterable[Lot]) -> int:
    return sum(l.ct for l in lots)


# ===========================================================================
# The wallet
# ===========================================================================
# FOUR STATES, and the third one used to be a pun. `claimed` is the word for an
# organization CLAIMING a mission (the claim flow, the guaranteed-to-pool rate
# that bumps on claim); the wallet was borrowing it for something that already
# had a better name. It gave it back on 2026-08-27c.
#
#     unallocated -> committed -> minted -> donated
#
# DONATED AND SPENT ARE DIFFERENT METRICS, and each applies to both parties:
# a benefactor DONATES, once per EBX, and what is donated is split by percentage
# between Earthbux and the organization; each of those two then SPENDS its share
# incrementally over the life of the mission. This wallet counts the donation.
# The two spending ledgers are theirs, not the benefactor's, and a benefactor
# can watch their donation being used without their donation changing size.
@dataclass(frozen=True)
class Wallet:
    """The four states, in ct. One bar, four segments, one invariant."""
    cash_ct: int = 0                # bought back or never spent; not a donation
    free_ct: int = 0                # UNALLOCATED — granted or purchased
    # The part of free that was BOUGHT rather than granted, and the only mobile
    # money in the model. A GRANTED token appears in its cause's election week,
    # cannot be transferred or withdrawn (there is no moment at which it exists
    # and is free), and if unspent waits for that cause's next window. A
    # PURCHASED token exists the moment it is bought and may be transferred or
    # withdrawn right up until it enters this week's election, at which point it
    # behaves exactly like a granted one.
    purchased_ct: int = 0
    committed_ct: int = 0           # in an election, still a token, still soft
    minted_ct: int = 0              # EBX: mission-tied, immovable
    donated_ct: int = 0             # crossed over, deductible, being spent
    # The cause this week's grant was issued against. Not a deadline and not a
    # tag on mobile money — it is the only place a granted token was ever able
    # to go.
    grant_cause_id: Optional[str] = None

    @property
    def grant_held_ct(self) -> int:
        """Unallocated ct that came from a grant: cause-bound, immobile."""
        return max(0, self.free_ct - max(0, self.purchased_ct))

    @property
    def tokens_ct(self) -> int:
        """The Tokens bin: free + committed. Minted ct are EBX, not tokens."""
        return self.free_ct + self.committed_ct

    @property
    def ebx_ct(self) -> int:
        """Held EBX — minted and not yet donated."""
        return self.minted_ct

    @property
    def next_grant_ct(self) -> int:
        return grant_ct(self.free_ct)

    def as_dict(self) -> dict:
        purchased = min(max(0, self.purchased_ct), self.free_ct)
        return {
            "cash_ct": self.cash_ct,
            "free_ct": self.free_ct,
            "grant_held_ct": self.grant_held_ct,
            "purchased_ct": purchased,
            "grant_cause_id": self.grant_cause_id,
            "committed_ct": self.committed_ct,
            "minted_ct": self.minted_ct,
            "donated_ct": self.donated_ct,
            "tokens_ct": self.tokens_ct,
            "next_grant_ct": self.next_grant_ct,
            "available_ct": available_ct(self.tokens_ct),
            # display copies — the front end should never divide by 100 itself
            "cash": tokens(self.cash_ct),
            "free": tokens(self.free_ct),
            "grant_held": tokens(self.grant_held_ct),
            "purchased": tokens(purchased),
            "committed": tokens(self.committed_ct),
            "minted": tokens(self.minted_ct),
            "donated": tokens(self.donated_ct),
            "next_grant": tokens(self.next_grant_ct),
            "usd_donated": usd(self.donated_ct),
            "ct_per_token": CT_PER_TOKEN,
            "weekly_grant_ct": WEEKLY_GRANT_CT,
            "max_split_tivs": MAX_SPLIT_TIVS,
            "oe_skim": OE_SKIM,
        }


# ===========================================================================
# Allocation — the conservation law, and the week it runs in
# ===========================================================================
# The ME slate and the OE field both spend ONE cell: `free_ct`.
#
#     sum(ME rows) + sum(OE rows) + free = tokens owned
#
# Minted EBX is NOT in that sum — it has left the token bin for a mission, which
# is exactly what minting means.
#
# Inside the week the allocation is a POSITION, revisable at no cost, which is
# why `set_allocation` sets rather than adds. At the roll the OE side of it
# hardens and stops being an allocation at all. The one-way `allocate` that
# lived here from 2026-08-20b to 2026-08-27c is gone with the rule it enforced.
def allocation_ok(me_rows_ct: Iterable[int], oe_rows_ct: Iterable[int],
                  free_ct: int, owned_ct: int) -> bool:
    return sum(me_rows_ct) + sum(oe_rows_ct) + int(free_ct) == int(owned_ct)


def set_allocation(rows_ct: Mapping[str, int], key: str, target_ct: int,
                   free_ct: int) -> tuple[dict[str, int], int]:
    """Set one row to `target_ct`, funding it from (or returning it to) free.

    Returns the new rows and the new free balance. Clamped, never rejected: a
    target above what free can pay lands at the ceiling, and a negative target
    lands at zero. This is a draft being revised, and a draft that throws is a
    draft that loses work.
    """
    rows = dict(rows_ct)
    have = max(0, int(rows.get(key, 0)))
    free = max(0, int(free_ct))
    want = max(0, int(target_ct or 0))
    delta = min(want - have, free)          # cannot spend more than free holds
    rows[key] = have + delta
    return rows, free - delta
