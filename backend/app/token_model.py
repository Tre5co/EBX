"""The money model — one file, pure functions, no database.

Amended 2026-09-16 (money_model.md): the finality ladder, grants carry a week,
no correctness multipliers, the 32nds.

Rewritten 2026-08-27c for the finalized ME/OE model
(`docs/_to_delete/ME_OE_FINALIZATION.md`, answered by Jax the same day). Everything about
what a token IS, what it is worth as a vote, and what happens to it when an
election closes lives HERE, so that `crud.py`, the routers and the front end
cannot each carry their own slightly different arithmetic. `post_config.py` is
the same idea for the discussion model.

TWO UNITS, NOT TWO NAMES FOR ONE UNIT
-------------------------------------
**Tokens are convertible; EBX is not.** That one sentence is the model.

    $ CASH ──buy──▶ ◇ TOKEN ──commit──▶ ◇ committed ──week roll──▶ ● EBX ──tranche──▶ ✓ DONATED
                        ▲                    │                        │
                        └── purchased ct ────┘                        └─ 10% at ME, +10% at OE,
                           may still move                                100% final on budget day
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
* The grant **does not exist until its week**, and carries that WEEK, never a
  cause (2026-09-16). It cannot be transferred or withdrawn. Purchase is the
  only mobile money in the model.
* A **vote is a split; the commit is an amount.** Up to `MAX_SPLIT_TIVS`
  percentages, and one number for the whole election. A vote can therefore
  stand before the tokens that will back it — it is a preference with no
  funding yet, not a state of anything.
* **The finality ladder** (2026-09-16). 10% of every stake is final at the
  initiative election, another 10% at the organization election, and ALL of it
  on budget day (T+15). Winners and losers pay the same. Being right is rewarded
  by the deployment order — never by a rate or a multiplier.
* **A skim only marks finality.** Nothing leaves the benefactor's position; after
  budget day all of it is final and still held as EBX, consumed only as the
  mission deploys it. The organization claims 5/16 of the pool on budget day
  (money_model.md §8).

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
# `roll_commit_by` are gone with the rule they enforced.
#
# A GRANT CARRIES ITS WEEK, NOT A CAUSE (Jax, 2026-09-16): "Grants do not have a
# cause id, only a weekly id ... the active week's cause is different between
# the 2 elections." A granted token may enter the initiative election or the
# organization election that closes on its grant week. The week is
# `BenefactorAccount.last_grant_week`; `grant_cause_id` was dropped by migration
# e1a7c3b95d20.


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
# Influence — being RIGHT is not a multiplier (2026-09-16)
# ---------------------------------------------------------------------------
# "Being right is rewarded by the deployment order. Only other benefit is
# bragging rights ... Budget voting is influenced by ebx holdings, but not being
# right." — Jax, 2026-09-16.
#
# So `ME_CORRECT_OE_MULT`, `OE_CORRECT_BUDGET_MULT`, `RESEARCH_MULT_EACH` and
# `influence_mult` are gone. Weight is the stake (or, in budget voting, the EBX
# held) through the block curve below, and nothing else. What being right buys
# is WHEN your capital is deployed: last (money_model.md §7).

def weight_ct(stake_ct: int, mult: float = 1.0) -> float:
    """Vote weight of a stake, in ct-equivalent.

    Flat for the first block, then geometric decay per further block. `mult`
    survives as a plain scale factor for callers; no rule sets it above 1. Returned as a float on
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
# Settlement — the finality ladder (2026-09-16)
# ===========================================================================
# "The code needs to be fixed to 10% at ME. The 5/16 applies to the guaranteed
# org reward, not the skim from benefactors. Let's add an additional 10% skim at
# OE, and 100% at budget day." — Jax, 2026-09-16.
#
#     T        initiative election closes    10% of every ME stake is final
#     T+8wk    organization election closes  another 10% of every OE stake
#     T+15wk   budget day                    100% of every stake is final
#
# "ALL donations are final at T + 15. Some may be finalized beforehand." A skim
# ONLY MARKS FINALITY (Jax, 2026-09-16): the skimmed ct become deductible and can
# no longer be withdrawn as cash, but they do not leave the benefactor's
# position and fund nothing yet. Until budget day the non-final rest may be
# withdrawn as cash (not built — money_model.md §12). From budget day on,
# everything is final and stays EBX in the benefactor's account, consumed only
# as the mission deploys it; the organization claims its 5/16
# (`ORG_BUDGET_DAY_32NDS`) from the whole pool that day.
#
# `votes_p2.donated_ct` is where the skims are booked, so in the database
# "donated" means FINAL-SO-FAR — an overlay on the stake, never a segment beside
# it. Winners and losers pay the same rates. Money that enters only at the OE
# pays only the OE skim; money carried from the ME pays both.
ME_SKIM = 0.10                     # final at the initiative election (T)
OE_SKIM = 0.10                     # ADDITIONAL, final at the organization election (T+8)

# The field a marked token can reach. Eight races are open at any instant (a
# mission enters phase 2 every week and leaves eight weeks later); wait six
# weeks and six more have opened under it, which is the 14 the model names —
# "7 elected before, the current one, and 6 elected later". Fourteen is a
# LIFETIME, not a screen: the table is always the eight.
# build-seq §3 (2026-09-16): "You must donate at least $1 to vote in the
# organization election. So the only way to allocate your grant there is if it
# is the full grant, or if you already participated in the ME, or if you add
# more money." A stake in an organization race is 0 or at least this — unless
# the benefactor carried money in from that mission's initiative election.
OE_MIN_STAKE_CT = 10 * CT_PER_TOKEN          # $1

OE_TABLE_ROWS = 8
OE_LIFETIME_RACES = 14
OE_AFTER_ME_WEEKS = 8              # phl elected at T + 8wk

# Seven weeks after the organization election the budget is set. That is what
# `MINT_LAG_WEEKS` was really measuring, and it is NOT the mint: EBX exists at
# mission identity, and the deduction rides each donation tranche rather than a
# date. Renamed for what it is, and nothing now expires on it.
BUDGET_SET_WEEKS = 7
# Budget day: every donation is final. T + 8 + 7.
BUDGET_DAY_AFTER_ME_WEEKS = OE_AFTER_ME_WEEKS + BUDGET_SET_WEEKS     # 15

# ===========================================================================
# The 32nds — where a mission's capital goes (2026-09-16, money_model.md §8)
# ===========================================================================
RESEARCH_REWARD_32NDS = 1          # each: situation · investigation · analysis  (3/32)
ADVANCE_32NDS = 2                  # each: Earthbux advance · organization advance (4/32)
ORG_FRAMING_RELEASE_32NDS = 8      # to the organization after framing
FLEXIBLE_32NDS = 17                # Earthbux (max 8) · organization · benefactor exchange
EARTHBUX_FLEX_MAX_32NDS = 8
ORG_BUDGET_DAY_32NDS = ORG_FRAMING_RELEASE_32NDS + ADVANCE_32NDS    # 10/32 = 5/16
assert 3 * RESEARCH_REWARD_32NDS + 2 * ADVANCE_32NDS + ORG_FRAMING_RELEASE_32NDS \
    + FLEXIBLE_32NDS == 32


@dataclass(frozen=True)
class Settlement:
    """What an election's skim finalized. donated + held == the stake, exactly.
    Both halves stay in the benefactor's position; `donated` is the final part."""
    donated_ct: int                # final: deductible, no longer withdrawable as cash
    held_ct: int                   # not yet final

    @property
    def total_ct(self) -> int:
        return self.donated_ct + self.held_ct


def settle_me(stake_ct: int) -> Settlement:
    """Initiative election closes: 10% of the stake is final, whoever you backed.
    `held_ct` here is the NOT-YET-FINAL part, not a smaller position."""
    s = max(0, int(stake_ct))
    donated = min(s, _ceil_ct(s * ME_SKIM)) if ME_SKIM else 0
    return Settlement(donated_ct=donated, held_ct=s - donated)


def settle_oe(stake_ct: int) -> Settlement:
    """Organization election closes: ANOTHER 10% of the stake is final.

    There is deliberately no `won` argument. Being right is rewarded by the
    deployment order (money_model.md §7), never by the rate.
    """
    s = max(0, int(stake_ct))
    donated = min(s, _ceil_ct(s * OE_SKIM))
    return Settlement(donated_ct=donated, held_ct=s - donated)


def final_ct(stake_ct: int, donated_ct: int, budget_day_reached: bool) -> int:
    """The deductible, non-withdrawable part of a stake.

    Before budget day: what the skims have finalized. On and after: all of it.
    """
    s = max(0, int(stake_ct))
    if budget_day_reached:
        return s
    return min(s, max(0, int(donated_ct)))


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
    """The finality ladder for one stake carried from the ME through budget day,
    so the docs, the landing copy and the UI cannot drift from the arithmetic."""
    me = settle_me(stake_ct)
    oe = settle_oe(stake_ct)
    skimmed = min(stake_ct, me.donated_ct + oe.donated_ct)
    return {
        "stake_ct": stake_ct,
        "me_skim_rate": ME_SKIM,
        "oe_skim_rate": OE_SKIM,
        "final_at_me_ct": me.donated_ct,
        "final_at_oe_ct": skimmed,
        "final_at_budget_day_ct": stake_ct,
        "ebx_after_budget_day_ct": stake_ct,           # a skim never shrinks the position
        "org_budget_day_32nds": ORG_BUDGET_DAY_32NDS,
        "usd_final_at_budget_day": usd(stake_ct),
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
    donated_ct: int = 0             # FINAL so far (the skims) — an overlay on committed + minted
    # The week this benefactor's grant was issued in (2026-09-16: a grant has a
    # week, not a cause). A granted token may enter either election closing that
    # week.
    grant_week: Optional[int] = None
    # Deductible and non-withdrawable: the skims so far, or everything once a
    # mission reaches budget day (`final_ct`).
    final_ct: int = 0

    @property
    def grant_held_ct(self) -> int:
        """Unallocated ct that came from a grant: week-bound, immobile."""
        return max(0, self.free_ct - max(0, self.purchased_ct))

    @property
    def tokens_ct(self) -> int:
        """The Tokens bin: free + committed. Minted ct are EBX, not tokens."""
        return self.free_ct + self.committed_ct

    @property
    def ebx_ct(self) -> int:
        """Held EBX — minted. Finality does not reduce it (2026-09-16)."""
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
            "grant_week": self.grant_week,
            "final_ct": self.final_ct,
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
            "final": tokens(self.final_ct),
            "next_grant": tokens(self.next_grant_ct),
            "usd_donated": usd(self.donated_ct),
            "ct_per_token": CT_PER_TOKEN,
            "weekly_grant_ct": WEEKLY_GRANT_CT,
            "max_split_tivs": MAX_SPLIT_TIVS,
            "me_skim": ME_SKIM,
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
