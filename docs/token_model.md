# The money model

*Rewritten **2026-08-27c** when Jax finalized the ME/OE experience. The eight
questions the model left open were put and answered the same day; the record of
what was asked and what came back is `docs/ME_OE_FINALIZATION.md`, and this file
is the model those answers make. `backend/app/token_model.py` is the executable
version — if the two ever disagree, the code is right and this is stale.
`scripts/token_model_check.py` asserts every number below.*

**The sentence the whole model turns on: tokens are convertible, EBX is not.**

---

## 1. Two units, four states

| | what it is | movable | tied to |
|---|---|---|---|
| **Token** ◇ | the voting unit | inside its own week | nothing |
| **EBX** ● | a token committed to a mission | **no** | one mission |

```
$ CASH ──buy──▶ ◇ TOKEN ──commit──▶ ◇ committed ──week roll──▶ ● EBX ──tranche──▶ ✓ DONATED
                   ▲                     │                        │
                   └── purchased ct, ────┘                        └─ 10% at the OE close,
                      movable and                                    more as the mission runs
                      withdrawable until
                      it enters a race
```

    unallocated  →  committed  →  minted  →  donated
    free tokens     to a tiv       to a       consumed by the
                    or a phl       mission    org, or by Earthbux

**EBX cannot exist before its mission does.** A token becomes EBX only when its
**mission identity is final**, which is why an allocation sitting in an
initiative election is still a token however long it sits there: the initiative
it backs may never become a mission.

**`claimed` is not a wallet state.** It is the word for an organization
*claiming* a mission, and the wallet gave it back on 2026-08-27c. What follows
`committed` is `minted`, and what follows that is `donated`.

**Donated and spent are different metrics, and each applies to both parties.** A
benefactor DONATES, once per EBX, and what is donated is split by percentage
between Earthbux and the organization. Each of those two then SPENDS its share
incrementally over the life of the mission. This wallet counts the donation; the
two spending ledgers are theirs. A benefactor can watch their donation being
used without their donation changing size.

---

## 2. Centitokens

```
1 token = 100 ct = 10¢        1 ct = 0.1¢
```

Every stored quantity is an **integer count of ct**. Rounding is always **up, to
the nearest ct**, and always against the benefactor — the donated share is what
gets rounded up. At ct granularity that is a 0.1¢ bias; the same rule at
whole-token granularity would round a 0.1-token skim up to a full token, a 10×
overcharge. The unit matters more than the direction.

---

## 3. The grant

> **10 tokens appear in your account each week. These tokens can only be used in
> this week's elections.**

**Ten is a floor, not a ration.** `grant = max(0, 10 − free)`, which is the same
rule as `available = max(10, held)` read from the other end. Hold six and four
arrive; hold twenty and twenty are votable and none are taken away. Both
functions are in the code so neither the wallet nor the UI has to derive one
from the other and get the direction wrong.

**The grant does not exist until its week.**

> "Tokens aren't granted until election week when it's too late to transfer or
> withdraw. You can vote beforehand, but the tokens aren't there yet."

So there is no window in which granted ct is both real and free, and therefore
nothing for a deadline to threaten. `GRANT_COMMIT_BY_WEEKS`, `commit_by_week`
and `roll_commit_by` are gone with the rule they enforced. What a granted token
carries instead is the **cause** it was granted against
(`BenefactorAccount.grant_cause_id`) — its races this week, and if it goes
unspent, that cause's next window seven weeks on. A granted token can be neither
transferred nor withdrawn.

**Purchased tokens are the only mobile money in the model.** They exist the
moment they are bought, may enter any race, and may be transferred or withdrawn
right up until they enter this week's election — at which point they behave
exactly like granted ones. Withdrawal returns face value to **Cash**, never to
the token bin, which is what keeps the grant arithmetic honest: nobody is ever
billed a grant for money handed back to them.

---

## 4. The vote is a split; the commit is an amount

> "The vote commit is the total amount committed to that election, and the weight
> is the percentage given to each tiv within it."

| | what it is | when it can be set |
|---|---|---|
| **the vote** | a split across up to `MAX_SPLIT_TIVS` initiatives, in percentages | any time — it needs no tokens |
| **the commit** | one number: total ct committed to that election | when the tokens exist |

A tiv's weight is `commit × that tiv's percentage`. A vote standing with no
commit behind it is **a preference with no funding yet** — not a pledge, not a
promissory note, not a third state of anything. When the grant lands it flows
through whatever split is standing.

`split_ct` applies the amount by largest remainder, so a mission's rows sum to
the commit exactly.

> `MAX_SPLIT_TIVS` and the weekly grant are both **ten by coincidence** (Jax,
> 2026-08-27c). They are independent numbers: a grant of 12 would not widen the
> slate, and an 8-way cap would not shrink the grant. Neither is defined in
> terms of the other, and the docs must not explain one with the other.

---

## 5. The week change is the ratchet

> "The conversion only happens at a week-change. Users will be able to convert as
> many times as they want within the same week." … "All OE allocations."

Inside a week an allocation is a **draft**: set it, unset it, move it between
races as often as you like, at no cost. At the roll, **every standing
organization-election allocation hardens** — those ct become EBX for that
mission and stop moving.

**ME allocations do not harden at the roll.** The mission identity is not final
until the initiative election is, so a slate stays revisable right up to the
close; what ends it is `finalize_p1`, not the calendar.

Two rows are also left alone by the roll:

* one that **names no philanthropy** — there is nothing to harden into. An
  unvoted stake is a token sitting in a race, and it commits to that race's
  winner when the race finalizes.
* one that is **marked** (§7) — it hardens when its benefactor votes for a
  philanthropy and the next roll comes.

**This retires two mechanisms at once**, and it is better than either. The
`MAX_CONVERSIONS = 3` budget (2026-08-20) priced the hop and made a
benefactor's remaining freedom a private number nobody else could see. One-way
commitment (2026-08-20b) priced deliberation itself. A week boundary prices
nothing, punishes nothing, and gives everybody the same deadline.

---

## 6. Settlement — a clean 10%, across the board

```
ME_SKIM  = 0.0      the initiative election claims nothing
OE_SKIM  = 0.10     the one skim, paid by everyone
```

> "It's a clean 10% across the board, winners and losers pay the same, the
> difference comes after (special ebx for ME, special mission membership for
> OE)." — Jax, 2026-08-27c

| you backed | the skim | what being right pays |
|---|---|---|
| the winning initiative | **10%** | **early EBX** (§7) |
| a losing initiative | **10%** | — |
| the winning philanthropy | **10%** | an **upgraded mission membership** |
| a losing philanthropy | **10%** | — |

The four-path table is gone, and with it `OE_SEND_WIN`, `OE_SEND_LOSE`, and the
buyer's sentence that needed a clause for each path. What replaces it fits on a
card:

> **10% of whatever you commit is the skim. The other 90% becomes your EBX for
> that mission. What you win is standing, not a rebate.**

**And the 90% is not withheld from the mission — it changes form.** The ct stop
being a balance and become mission-tied credit: the coin of `models.CreditCoin`,
the donation receipt, the thing whose worth tracks how well the organization
runs what it was elected to run. The mission spends against it; the benefactor
holds the record of having funded it.

### Donation is an event, and it happens more than once

> "The tax deduction happens when the ebx is donated (included in the skim).
> Throughout the mission, more ebx will be donated."

EBX is not donated in a lump at some week-number. It crosses **in tranches as
the mission runs**, and each tranche is deductible when it crosses. The 10% at
the organization election is simply **the first one** — which is what "included
in the skim" means: the skim is not a separate charge outside the donation flow,
it is the opening instalment of it.

`MINT_LAG_WEEKS` therefore does not survive as a mint or as a deduction date.
Seven weeks names the point at which the **budget is set**, and it is called
`BUDGET_SET_WEEKS` now. Nothing expires on a clock any more; `TOKEN_LIFE_WEEKS`
is gone.

> **Out of scope, and named rather than assumed:** what *triggers* each donation
> tranche after the first (a budget release? a resolved step? the org drawing
> funds?), and whether every tranche carries the same Earthbux/organization
> percentage the first one does. Both belong to the resolutions phase, which is
> parked. `tranche_ct` is the arithmetic those rules will call, and nothing more.

---

## 7. When the initiative election closes, backers split two ways

**Backed the winning initiative → early EBX.** Those ct mint on the spot, into
this mission, a week ahead of everybody else's. They are locked in this
organization election until it finalizes, and for the purposes of voting in it
they count exactly as tokens. This is the reward for having been right, and it
is not money: it is the same money, sooner, in a mission the benefactor chose.

**Backed a loser → a marked token.** Still a token, still movable, carrying the
initiative it voted for (`VoteP2.marked_tiv_id`). It may go to any open
organization election **by voting for a philanthropy there** — the vote is the
commitment — or come back to its cause's initiative election (§8). If it does
neither, it commits to whoever wins the race it is sitting in.

So the losing backer is not punished and not stranded; they are handed a live
token with a mark on it. The winning backer is paid early instead.

**A split ME vote makes different tokens — and then it doesn't.** Splitting a
slate leaves a benefactor holding tokens with different marks. Once those are
committed to an OE and minted, **the mark is forgotten in the balance** and
lives only in the provenance chain.

### The field: eight open, fourteen over a token's life

> "8 options at the beginning, if the user waits 6 weeks 6 new options will
> appear. 8 at any given moment."

A mission enters phase 2 every week and leaves eight weeks later, so **exactly
eight races are open at any instant** — that is the eight-row table. What grows
is a marked token's cumulative reach: wait a week and the oldest race closes
while a new one opens. Six weeks of waiting is six new options, and 8 + 6 = 14,
which is the model's "7 elected before, the current one, and 6 elected later."
**Fourteen is a lifetime, not a screen.**

---

## 8. The way back, and the default

If a marked token is **still a token** when its OE week arrives, it may be
transferred back to the initiative election and added to that week's grant,
still locked to the initiative it originally voted for. The benefactor has to
choose this deliberately; there is no automatic sweep.

**The default is the opposite**: a token left in an OE is committed to whichever
philanthropy wins it. Silence is not a withdrawal, and it is not a losing vote
either — an unassigned stake funds the mission, carries no vote weight, and
follows the winner of the race it is sitting in.

`VoteP2.org_id` is nullable for exactly this state. Inventing an org id instead
is how the orphaned-initiative 500 happened in August.

---

## 9. Vote weight, and what being right is worth

Weight is 1:1 for the first block of 10 tokens, then each further block of 10
counts for `r ×` the block before it, `r = 0.5`:

```
10 tk → 10.00      20 tk → 15.00      30 tk → 17.50      40 tk → 18.75
```

That reproduces the old doubling price ladder exactly — paying 2× for the same
marginal vote is arithmetically identical to receiving ½ the weight for the same
marginal payment — with `r` as the one knob.

| you were right in… | organization election | budget voting | research voting |
|---|---|---|---|
| nothing | 1× | 1× | 1× |
| the initiative election | **2×** | 1× | **1.5×** |
| the organization election | — | **2×** | **1.5×** |
| both | **2×** | **2×** | **2.25×** |

The research column multiplies (1.5 × 1.5 = 2.25); the other two do not stack,
because each names one earlier decision. An organization-election vote cannot
reward itself — the race it would weight is the race it is in.

**These survive the flat skim** (Jax, 2026-08-27c: both), and they are joined by
the two rewards §6 names. None of the three is money, which is the point: one
skim falls on everyone at the same rate, so the prize for being right compounds
into the next decision rather than into a balance.

---

## 10. Provenance

> "Every token maintains a record of its transactions."

A balance cannot carry a history, so the unit that does is the **lot**: ct that
have always moved together. Split a lot and both halves inherit the record. The
chain survives the mint — a credit coin still knows which initiative and which
philanthropy its ct backed on the way there.

**Only a registered vote is recorded, and the week change sharpens what that
means:** what is registered is what **stands at the roll**. A benefactor who
moves an allocation three times on a Thursday leaves one event behind, not
three, because the first two were drafts.

**The coin has two elements.**

*Element 1* (`settle_me`) is written when the initiative election hits: the
cause, the amount, the date, the initiative this benefactor backed, and the one
that **won** — so a losing coin still remembers the argument that made the
mission instead of being retconned into having always backed the winner.

*Element 2* (`mint_ebx`) is the philanthropy these ct minted behind, written at
the roll. It carries **no org id in one real case**: early EBX mints the moment
the initiative election closes, when the mission is known and its organization
has not been elected yet. That is what early means.

A donation tranche (`donate`) is its own event, dated for the deduction.

---

## 11. The surfaces

### The allocations panel — three sets of two

**Unallocated** (granted · purchased) → **Committed** (initiatives ·
organizations) → **EBX** (held · donated). The bar carries the whole of what a
benefactor holds, and the pairs are pairs because the two halves of each are not
interchangeable: granted ct is bound to its cause, purchased ct goes anywhere;
an initiative allocation is soft to the close, an organization allocation
hardens at the roll; held EBX is still theirs, donated EBX is gone and
deductible.

The granted segment prints the **cause** it was granted for, where the commit-by
date used to be.

### The initiative election — one amount, one slate

The ME table spends the **wallet** now, not `10 + localStorage`. Raising the
election's amount spends unallocated ct; lowering it hands the difference back,
because an initiative allocation is soft until the close. The rows are
percentages of that one amount.

### The organization election — eight rows, and a position

Eight rows, one per mission with an open philanthropy election, sorted by
deadline, no scrollbar and no filter: the count is fixed by the calendar, so the
shape is fixed too. A row is titled by its **initiative** and merely coloured by
its cause — two missions of the same cause are open at once.

The dialog's number is **this race's total**, not an amount to add, with a floor
of whatever has already minted. What the row reports is which state its money is
in: EBX and staying, marked and movable to any open race, or movable until the
week changes.

The conservation law both tables share:

```
Σ(ME rows) + Σ(OE rows) + unallocated = tokens owned
```

Minted EBX is deliberately outside that sum — it has left the token bin, which
is what minting means.

---

## 12. What is built, and what is not

**Built and asserted** (`token_model_check` **108** · `wallet_check` **123**):

- the arithmetic end to end in `backend/app/token_model.py`;
- `grant_cause_id` on the account; `stake_ct` on `votes_p1`; `committed_week`,
  `minted_ct`, `donated_ct` and `marked_tiv_id` on `votes_p2` (migration
  `c5d8f2a91e67`);
- `GET /wallet` · `GET /wallet/rows` · `POST /wallet/commit` (a position) ·
  `POST /wallet/move` · `POST /wallet/withdraw` · `PUT /wallet/org`.
  `POST /wallet/convert` is gone with the budget it spent;
- the week roll, `wallet.harden_due`, applied by the scheduler and lazily on
  `GET /wallet`;
- **both halves of settlement are booked.** `finalize_p1` mints the winner's
  backers and marks the rest; `finalize_p2` mints what is left and books the
  first donation tranche. The OE half used to be recomputed on every read — the
  right number in the wrong place — and `minted_ct` / `donated_ct` ended that;
- the ME table on the wallet: one amount, one slate, refunded when lowered.

**Not built yet** — named here so nobody assumes otherwise:

- **The later donation tranches.** Only the first one is booked; what triggers
  the rest is the parked resolutions work.
- **The Earthbux/organization split of a donation.** The model says each gets a
  percentage and each spends its share incrementally; the percentages are not
  set, so nothing divides a tranche yet.
- **Buying tokens.** `purchased_ct` is the column the real thing will write, and
  the localStorage simulation on main.html was retired rather than left to
  invent a budget the account does not hold.
- **The rule-8 way back to the ME.** A marked token can move between
  organization elections and can wait; nothing yet transfers it back into an
  initiative election with its mark intact.
- **The influence multipliers are not wired into the tallies.** `p1_tally` is
  linear and `p2_tally` counts integer votes; today the multipliers drive the
  per-row weight the wallet reports.
- **The coin's issuance timing.** `mint_mission_coins` still runs at
  `finalize_p2`; the model says EBX at mission identity, **coin at budget**.
- **The phase-1 carryover machinery** still exists and describes a world that
  ended on 2026-08-20.
