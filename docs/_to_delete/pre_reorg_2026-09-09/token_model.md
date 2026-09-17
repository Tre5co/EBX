# The money model

**Contents**
1. The evolution of the funds and description of how they all end up donated
2. The 3 tiers
- 10%, then 5/16, then 100%
- rest withdrawable as cash.
- once converted to ebx, it's a fully deductable donation.
- *new* fourth tier has been introduced
3. The DEX
- There are some open questions here. I'll get to them.
...


*new*
If you get the right initiative, and the wrong organization, you can move your money during the 7 week framing phase to any of the 13 possible other missions and your money is treated as if you committed it in the oe for that election. It doesn't count as a conversion. - this is the same logic that allows you to change the mission if you get the ME vote wrong.

Ok. I'm going to have to write this myself. AI content below is to help me do that.








*Rewritten **2026-09-04**, when Jax replaced the settlement model with a market.
It supersedes the 2026-08-27c version wholesale. That version's decision record,
`docs/ME_OE_FINALIZATION.md`, is now **historical** — read it to understand why
the skim and the ratchet were built, not to learn what is true.
`backend/app/token_model.py` is the executable version of the **old** model and
is the stale half of this pair; where the two disagree, **this file is the
intent and the code is the backlog** (§12). `scripts/token_model_check.py` and
`scripts/wallet_check.py` assert the old arithmetic.*

*Amended **2026-09-08** (build-seq §4) from four notes Jax added to the build
queue. They do not replace the DEX — the market, the per-mission position and the
no-cash-leg rule all stand — but they **put back three things the 2026-09-04
rewrite retired**, and one of them moves the sentence this file called its most
consequential. Read §0 before anything below it; every section it contradicts
carries a pointer back to it.*

**The sentence the whole model turns on: cash buys a position in a mission, and
the only way out of a position is into another mission.**




---

## 0. Amendment 2026-09-08 — finality is a ladder

Jax's four notes, verbatim:

> - Before the OE, the **field is 14 missions** rule still applies. The 10% skim
>   does happen at the ME, and users can only change their committment once or
>   remove it after the mission has been elected.
> - The org is guaranteed **1/4**, earthbux is guaranteed **1/16**. **3/32** is
>   given in research prizes, and the rest is retained by the benefactors.
> - A benefactor has **7 weeks after the organization election** to withdraw
>   money before the donation becomes final. **5/16** is already final upon org
>   election. **10%** is final upon mission election.
> - The payout works like this: first money paid out to orgs (not including
>   initial 5/16) is any money **converted** to the mission. Next is ordinary
>   money from the **org election**. Last is the money from those who won the
>   **mission election**. That is the advantage of winning the election — you
>   have the power to convert the money for the longest.

### 0a. The one that changes everything: the gift is no longer complete at commit

§6 says *"the receipt is valid at commit"* and calls it "the single most
consequential sentence in the rewrite". **It is no longer true**, and not by a
detail: a benefactor who can withdraw money seven weeks after the organization
election has not given up control of it, and a completed gift requires exactly
that. Deductibility now attaches in **three steps**, and the amount deductible on
a given date is the amount that has become irreversible by that date:

| Event | When | Cumulative share FINAL | Still withdrawable |
|---|---|---:|---:|
| commit | any time in the race | 0 | 100% |
| **initiative elected** | T | **10%** | 90% |
| **organization elected** | T+8wk | **5/16 = 31.25%** | 68.75% |
| **budget set** | T+15wk (`BUDGET_SET_WEEKS = 7` after the OE) | **100%** | 0 |

Two things follow immediately.

1. **The 5/16 is not a fourth number.** `1/4 + 1/16 = 8/32 + 2/32 = 10/32 = 5/16`
   — the organization's guarantee plus Earthbux's guarantee, exactly. The ladder
   and the split are the same arithmetic seen from two ends: what becomes final
   at the organization election is precisely what is guaranteed to the two
   counterparties, because that is the moment there IS an organization to
   guarantee it to. The 10% at the initiative election is the first rung of the
   same climb, not a separate charge.
2. **"Non-withdrawable" survives, but it describes EBX, not a commitment.** §1's
   defining word still holds for every unit that has been *issued*: no EBX can
   ever be redeemed for cash. What the ladder adds is that a commitment does not
   become EBX all at once. Until the budget is set, part of a commitment is a
   **pledge** rather than a position — irrevocable in the fraction that has
   ratcheted, withdrawable in the fraction that has not.

**Flagged, not answered:** the receipt. The old model dated the deduction at the
OE skim; the DEX rewrite dated it at commit; this dates it three times. A donor
who commits in October and withdraws the remainder in March has made a gift of
31.25% of what they committed, in the tax year the ratchet reached it. That is
answerable — donations with a revocation window are ordinary — but it is a
question for the same review bucket as §6's other two, and it is now the
**largest** of the three because it governs what every receipt says.

### 0b. The ME skim returns, one gate earlier

```
ME_SKIM  = 0.10     the initiative election makes the first tenth final   ← was 0.0
OE_SKIM  = 0.0      the organization election takes nothing new
```

The old (2026-08-27c) model skimmed **10% at the organization election**; the DEX
rewrite set both gates to zero; Jax's note puts 10% back at the **initiative
election**. The move earlier is the substance of it: the first tenth becomes
irreversible at the moment the mission acquires its identity, which is the first
moment there is anything for it to be irreversible *toward*. It is not a fee —
nothing is deducted from the benefactor's position for Earthbux's benefit — it is
the first rung of the finality ladder in §0a, and the code that books it
(`_settle_oe_stakes`) has to move from `finalize_p2` to `finalize_p1`.

### 0c. One change, then it is stuck

> "users can only change their committment once or remove it after the mission
> has been elected"

Before the initiative election, an allocation is a draft and may be dialled
freely (§5 is unchanged). **After** it: **one** change, or a removal, and that is
the end of it. This is neither the old week-roll ratchet (a fresh window every
week) nor `MAX_CONVERSIONS = 3` (a budget of three): it is a single move. The
DEX, which is the general answer to changing your mind, opens on the far side of
this — a position that has ratcheted is traded, not amended.

### 0d. The field is fourteen again, before the OE

§2 retired "eight-open / fourteen-over-a-lifetime" along with marked tokens,
because a DEX makes any position reachable from any other. The note reinstates it
**with a scope it did not have before**: *before the OE*. So the two mechanisms
divide by phase rather than compete —

* **before the organization election**, a benefactor's reachable field is the
  **14 missions** of the lifetime rule, and moving inside it is the one change of
  §0c;
* **after it**, the position is EBX and the DEX is how it moves, with no field
  limit at all, because a swap is not a re-allocation.

`OE_LIFETIME_RACES = 14` and `OE_TABLE_ROWS = 8` therefore stay in
`token_model.py` rather than being deleted with the rest of the retired
machinery.

### 0e. The payout order — and the real prize for being right

> "First money paid out to orgs (not including initial 5/16) is any money
> converted to the mission. Next is ordinary money from the org election. Last is
> the money from those who won the mission election."

**This replaces "consumption burns pro rata" (§7).** Deployment consumes capital
in provenance order, oldest claim last:

```
    deployed first  ┌──────────────────────────────────────┐
                    │ 1. CONVERTED IN — capital moved here │
                    │    from another mission              │
                    ├──────────────────────────────────────┤
                    │ 2. ORG-ELECTION money — committed    │
                    │    during the organization race      │
                    ├──────────────────────────────────────┤
                    │ 3. ME-WINNER money — committed by    │
                    │    backers of the winning initiative │
    deployed last   └──────────────────────────────────────┘
             (the initial 5/16 is outside this order — it is
              guaranteed and goes out first, from everywhere)
```

Jax names the point himself: *"That is the advantage of winning the election. You
have the power to convert the money for the longest."* Being right at the
initiative election buys **duration** — your capital is the last to be consumed,
so your position stays alive, tradeable and re-directable longer than anyone
else's. `docs/PLAN_2026-09-02.md` §A flagged the missing "third reward for being
right" and guessed it would be a price *basis*. It is not: it is a **queue
position**, which is better, because it costs the model nothing (no unit is worth
a different amount depending on how it was acquired — §1's fungibility survives
intact) and it is legible in one sentence.

**What it costs:** fungibility of *timing*. Every Mission A EBX is still worth
the same as every other and still trades one-for-one, but two holders of
identical EBX now have different expected lifetimes, and a DEX price cannot see
that. Whoever builds the DEX surface has to decide whether provenance is visible
in a quote. It belongs beside §7's maturity confound; it is the same class of
problem one level down.

### 0f. The split, restated

Jax's second note gives four numbers where §8 gives eight rows. They reconcile
like this:

| Slice | Amendment | §8 as written (2026-09-04) |
|---|---:|---:|
| Organization, **guaranteed** | **1/4 = 8/32** | 10/32 (8 mission-side + 2 advance) |
| Earthbux, **guaranteed** | **1/16 = 2/32** | 10/32 (8 mission-side + 2 advance) |
| Research prizes | **3/32** | 3/32 ✓ |
| **Retained by benefactors** | **19/32** | 9/32 ("flexible remainder") |

Two real changes and one clarification:

1. **Earthbux's guarantee falls from 10/32 to 2/32.** Under §8, Earthbux was
   guaranteed as much as the organization; here it is guaranteed a quarter of
   what the organization gets. Everything above 1/16 that Earthbux ends up
   spending has to be *earned out of the 19/32*, on the same footing as anything
   else the benefactors' remainder funds. This is a much sharper version of "you
   donate, we follow" — the news operation is funded like a line item that has to
   be justified, not like a partner's cut.
2. **The remainder more than doubles, and it has an owner.** 9/32 "flexible,
   released in the credit phase → org, or back into the pool" becomes 19/32
   **retained by the benefactors**. That is 59% of every mission sitting behind
   the community's own decisions, which is what makes the budgeting phase the
   centre of the product rather than a formality.
3. The **advance** rows do not vanish; they are no longer *guaranteed*. An
   advance released with the case-post reward is a draw against the remainder,
   which is the same money it always was, now with a decision attached.

**Open:** §8's guarantee is what an organization is promised for winning; the
ladder in §0a says 5/16 is final at the organization election, and 5/16 is
exactly `1/4 + 1/16`. So the guarantee and the finality point agree by
construction — but only if the 19/32 remainder is understood as **not yet
deployed**, and therefore as the part a benefactor may still withdraw during the
seven weeks. Sequencing the withdrawal window against the deployment schedule is
the one piece of arithmetic this amendment does not close.

---

## 1. What EBX is

> **EBX is a non-withdrawable digital unit representing a holder's position in a
> mission's remaining charitable capital.** Each mission creates its own fungible
> EBX pool. EBX may be traded on the Earthbux DEX for EBX associated with other
> missions, allowing benefactors to reallocate their charitable exposure as
> mission performance and confidence change. EBX is progressively consumed as its
> associated mission's capital is deployed to organizations, Earthbux operations,
> and authorized citizen-research rewards.

And the single unit, precisely:

> A **Mission A EBX** is a transferable, mission-specific claim on a portion of
> charitable capital that is scheduled to be deployed through Mission A, with the
> holder retaining the ability to exchange that claim for exposure to another
> mission before it is consumed.

Read those two paragraphs slowly, because four words in them are doing all the
work:

- **non-withdrawable** — there is no path from EBX back to cash, for anybody, at
  any price. ⚠ **Amended 2026-09-08 (§0a):** this still describes EBX exactly,
  but it no longer makes the commit a completed gift, because a commitment does
  not become EBX all at once — 10% is final at the initiative election, 5/16 at
  the organization election, and the remainder only when the budget is set seven
  weeks later. Until then part of a commitment is a withdrawable pledge.
- **position** — not a balance, not a token, not a receipt. It is exposure to
  what a specific mission will do with money that is already charity's.
- **fungible, per mission** — every Mission A EBX is identical to every other.
  The pool is the unit of identity; the holder is not.
- **consumed** — the terminal state is deployment, not redemption. Every EBX
  ever issued ends by being burned against a dollar going out the door.

### The benefactor's loop

```
Choose mission
   ↓
Commit capital ─────────────────► donation receipt is valid HERE
   ↓
Receive Mission EBX position
   ↓
Watch researchers / organization / budget / resolutions
   ↓
Gain or lose confidence
   ↓
Hold  /  sell  /  buy another mission     ◄──┐
   ↓                                          │
Continue participating ───────────────────────┘
   ↓
Eventually all capital is deployed
```

There is no exit to cash anywhere on that loop, and that absence is the whole
design. Everything after the second step is about **direction**, never about
ownership.

---

## 2. Three states

```
$ CASH ──buy──▶ ◇ TOKEN ──commit──▶ ● MISSION EBX ──deploy──▶ ✓ CONSUMED
                   │                   ▲        │
                   │ withdrawable      │        │
                   │ until committed   └── DEX ─┘
                   ▼                    swap for another
                ✓ CASH BACK             mission's EBX
                                        (never for cash)
```

| | what it is | movable | withdrawable | tied to |
|---|---|---|---|---|
| **Token** ◇ | the pre-commit unit — the weekly grant, or cash bought in | anywhere | **yes**, if purchased and uncommitted | nothing (a grant is tied to its cause) |
| **EBX** ● | a position in one mission's remaining capital | **on the DEX**, into any other mission's EBX | **never** | one mission, until traded |
| **Consumed** ✓ | capital deployed; the EBX that represented it is burned | — | — | the deployment that burned it |

**`minted` is gone as a state.** In the old model commit and mint were separate
events because *EBX could not predate its mission*: an allocation sitting in an
initiative election was still a token, since the initiative it backed might never
become a mission. That constraint dissolves once the unit of commitment is the
**mission** rather than the initiative — and the mission spine exists from the
cycle's start (`current_phase='pre'`), before any initiative is elected. So:

    OLD:  unallocated → committed → minted → donated
    NEW:  unallocated → committed (donated, EBX issued) → consumed
                              ↑______ DEX ______↓

**`claimed` is still not a wallet state** (that was settled 2026-08-27c and
survives): it is the word for an organization *claiming* a mission.

### What this retires

The old model spent most of its complexity answering one question: *how does a
benefactor move a stake between races before its mission identity is final?* The
DEX answers it permanently, so all of the following go at once:

| Retired | What it was for |
|---|---|
| **the week-roll ratchet** (`wallet.harden_due`) | a free window to change your mind, closed by the calendar — still retired, but ⚠ **§0c puts ONE change (or removal) in its place** after the initiative is elected |
| **`MAX_CONVERSIONS = 3`** (already retired 2026-08-20) | a budget of mind-changes |
| **soft-until-close ME allocations** | the same freedom, on the initiative side |
| **early EBX** | paying winners in timing |
| **marked tokens** (`VoteP2.marked_tiv_id`) | somewhere for a losing backer to stand |
| ~~**eight-open / fourteen-over-a-lifetime**~~ | the field a marked token could reach — ⚠ **BACK, scoped, 2026-09-08 (§0d): the field is 14 missions BEFORE the organization election.** The DEX governs after it. |
| **the rule-8 way back to the ME** | returning a marked token to an initiative election |
| ~~**the 10% OE skim**~~ (`P2_SKIM`) | making a donation event happen at a fixed point — ⚠ **BACK one gate EARLIER, 2026-09-08 (§0b): 10% at the INITIATIVE election.** |
| **donation tranches** (`tranche_ct`) | spreading deductibility across the mission |

A market prices deliberation continuously. A calendar prices it once a week, and
badly.

---

## 3. Centitokens

Unchanged, and still the least glamorous load-bearing decision in the model.

```
1 token = 100 ct = 10¢        1 ct = 0.1¢
```

Every stored quantity is an **integer count of ct**. Rounding is always **up, to
the nearest ct**, and always against the benefactor. At ct granularity that is a
0.1¢ bias; the same rule at whole-token granularity would round a 0.1-token
remainder up to a full token, a 10× overcharge. The unit matters more than the
direction.

**The DEX inherits this and needs more of it.** An AMM produces a real-valued
price, and the swap has to land on an integer ct on both legs. The rule stays
the same — round against the trader, never in a direction that mints EBX out of
nothing — and the invariant to assert is that **a swap never increases total EBX
outstanding across the two pools**. Rounding dust goes to the pool, not to the
trader.

---

## 4. The grant

> **10 tokens appear in your account each week. These tokens can only be used in
> this week's elections.**

**Ten is a floor, not a ration.** `grant = max(0, 10 − free)`, the same rule as
`available = max(10, held)` read from the other end. Hold six and four arrive;
hold twenty and twenty are votable and none are taken away.

**The grant does not exist until its week**, so there is no window in which
granted ct is both real and free, and therefore nothing for a deadline to
threaten. What a granted token carries is the **cause** it was granted against
(`BenefactorAccount.grant_cause_id`). A granted token can be neither transferred
nor withdrawn.

**Purchased tokens are the only mobile money before commitment.** They exist the
moment they are bought, may enter any mission, and may be transferred or
withdrawn right up until they are committed. Withdrawal returns face value to
**Cash**, never to the token bin, which keeps the grant arithmetic honest: nobody
is ever billed a grant for money handed back to them.

### Granted tokens mint ordinary EBX

**Decided 2026-09-04.** A grant committed to a mission produces the same EBX as a
purchased token does — one class, no asterisk, tradeable on the DEX like any
other unit.

The consequence has to be stated rather than discovered later: **EBX outstanding
for a mission exceeds the cash committed to it**, by whatever the grants added.
So a unit of EBX is a **share of direction, not a dollar**:

```
your share of what remains  =  your EBX  /  that mission's EBX outstanding
```

**Grants dilute direction, not money.** No unit can ever be redeemed, so a
diluted claim claims a slightly smaller *say* — never a smaller pile. At ten
tokens (\$1) per benefactor per week the effect is small, and one EBX class is
worth the small dilution.

> **Named exposure, not decided.** At scale — many accounts, thin committed cash
> — grant-minted EBX could come to outweigh committed capital, and free units
> would be voting real money around the DEX with real price impact. The obvious
> lever is a **cap on grant-minted EBX as a fraction of a mission's
> outstanding**; a second is to let grants mint only against missions the grant's
> cause owns (which they already do at the election level). Decide this **before**
> grants and the DEX are live simultaneously.

---

## 5. The vote is a split; the commit is an amount

Unchanged in shape, changed in consequence.

| | what it is | when it can be set |
|---|---|---|
| **the vote** | a split across up to `MAX_SPLIT_TIVS` initiatives, in percentages | any time — it needs no tokens |
| **the commit** | one number: total ct committed to that mission | when the tokens exist |

A tiv's weight is `commit × that tiv's percentage`. A vote standing with no
commit behind it is **a preference with no funding yet**. `split_ct` applies the
amount by largest remainder, so a mission's rows sum to the commit exactly.

**What changed: the commit is no longer revisable downward.** Committing issues
EBX and completes the donation, so the slate is a percentage split of an amount
that has already been given. Raising the commit spends more unallocated ct and
issues more EBX; **lowering it is not a refund**, because there is nothing to
refund from. A benefactor who wants less exposure to this mission sells on the
DEX.

The split itself stays freely editable until `finalize_p1` — it directs money
that is already committed, and directing it differently costs nothing.

> `MAX_SPLIT_TIVS` and the weekly grant are both **ten by coincidence** (Jax,
> 2026-08-27c). They are independent numbers and the docs must not explain one
> with the other.

---

## 6. Settlement — there isn't one

```
ME_SKIM  = 0.10     the initiative election makes the first tenth FINAL  ← §0b
OE_SKIM  = 0.0      the organization election takes nothing NEW          ← §0a
```

⚠ **Amended 2026-09-08.** The block below is the 2026-09-04 position and is kept
because its *reasoning* about fees is still right — there is no toll for entering
a race, and Earthbux is funded from the deployment schedule rather than from a
charge at a gate. What it gets wrong is the **timing of finality**: §0a replaces
"all of it, at commit" with a three-rung ladder (10% at T, 5/16 at T+8wk, the
rest at T+15wk), and §0b is where the 10% went.

**100% of a commitment becomes the mission's charitable capital, at commit.**
There is no toll at any gate. Earthbux is funded from its **10/32 of the
deployment schedule** (§8), on the same footing as the organization and the
research rewards — a line item inside the mission, not a charge for entering it.

> "The 10% skim might not even be necessary. It might just all go into the
> liquidity pool… So the cash in the pool is the only money that can be a real
> donation." — Jax, 2026-09-04

### ~~The receipt is valid at commit~~ — SUPERSEDED 2026-09-08 (§0a)

> ⚠ **This section is the one the amendment overturns.** A benefactor has seven
> weeks after the organization election to withdraw, so control is not
> surrendered at commit and the gift is not complete there. Deductibility
> ratchets: 10% at the initiative election, 31.25% at the organization election,
> 100% when the budget is set. Everything below is the superseded argument, kept
> because the *reasoning* — that non-withdrawability is what completes a gift —
> is exactly what makes the ladder work; it is the date that moved, not the
> principle.

This is the single most consequential sentence in the rewrite, and it follows
from non-withdrawability rather than from a policy choice. A completed gift
requires the donor to give up control and give up any path back to value. A
benefactor who commits has done both: **no unit can be redeemed for cash, by
anyone, ever.** Trading afterwards does not create a second deduction, does not
reverse the first, and does not change its size. Deduction is fixed **at commit,
by amount**.

`MINT_LAG_WEEKS` does not survive as a mint date or as a deduction date. Seven
weeks names the point at which the **budget is set** (`BUDGET_SET_WEEKS`).
`TOKEN_LIFE_WEEKS` is gone. `tranche_ct` computes an arithmetic nobody calls any
more.

### Donate and spend, now further apart than ever

The benefactor **donates once**, at commit, for the whole amount. Earthbux and
the organization then **spend** their shares incrementally over the life of the
mission. A benefactor watches their donation being *used* without their donation
changing size — which was always the point of a receipt whose worth tracks how
well the money was spent. What changed is that the donation is complete before
the watching starts.

### The two legal questions, flagged not answered

Neither should be assumed from the fact that the mechanism is clean, and nobody
on this project is a lawyer:

1. **Does a DEX trade constitute receiving value?** A donor swapping A for B
   receives something with an observable market price. The intended answer is
   that both legs are non-withdrawable charitable claims, so no value leaves
   charity — an argument, not a ruling. It is also the strongest reason to keep a
   cash leg off the DEX **permanently**, including "just for liquidity".
2. **Whose donation is it after a trade?** If a buyer's capital is deployed
   through a mission the seller chose, the deduction and the deployment have come
   apart. Deduction is fixed at commit by amount, and a receipt must be able to
   say so plainly.

Same review bucket as the kids-accounts COPPA/GDPR-K item.

---

## 7. The DEX

The Earthbux DEX trades **EBX for EBX**, never EBX for cash. It is where a
benefactor changes their mind, and it replaces every mechanism the old model had
for the same purpose.

```
        Mission facts
             │
             ▼
     Performance metrics
             │
             │ informs
             ▼
People's confidence ──────► DEX price
```

### Price is an exchange rate of preference, not a return

Nobody ever gets paid. A benefactor pays more Mission B EBX for Mission A EBX
because they would rather their remaining capital go through A — that is the
entire content of the number. A premium means the community wants to fund more of
that mission; a discount means people are quietly exiting it. It is a confidence
reading that costs nothing to produce and that a survey cannot fake.

### Pricing is a constant-product pool

Buy a mission's EBX and less of it is left in the pool, so the next unit costs
more. Sell into the pool and there is more of it, so the next unit costs less.

```
x · y = k
```

No order book, no counterparty to find, no listing committee. The trade-size
question that always follows — how much slippage a benefactor should be allowed
to eat in one swap — is a UI decision (quote first, confirm second), not a model
one.

### ~~Consumption burns pro rata~~ — SUPERSEDED 2026-09-08 (§0e)

> ⚠ **Deployment consumes in PROVENANCE ORDER now**, not in proportion:
> converted-in capital first, then organization-election money, then the backers
> of the winning initiative last. "You have the power to convert the money for
> the longest" is the prize for being right, and a pro-rata burn cannot pay it.
> The paragraph below is what the DEX rewrite assumed; keep it in view because
> its claim — that "position in remaining capital" stays literally true — is the
> thing an ordered burn has to be checked against.

When capital is deployed, EBX is consumed across **every** holder in proportion,
including whatever inventory sits in the liquidity pool. Nobody's position is
singled out, and holding to the end pays nothing extra: the terminal state of
every EBX is consumption. This is what keeps "position in remaining capital"
literally true as the mission runs.

### A mission delists when its capital is fully deployed

Supply walks to zero as the mission runs, and the last EBX is **consumed, not
sold**. Trading must therefore close before the pool empties. When — at final
resolution, at an outstanding floor, or on a schedule — is open (§11).

### The maturity confound

EBX of a mission about to deploy heavily is shorter-lived than EBX of a mission
that just opened, so a holder who wants to keep options open rotates out of
late-stage missions **on timing alone**. That is a systematic discount on
maturity with nothing to do with performance, contaminating the one signal the
DEX exists to produce.

Candidates: normalize the displayed price by remaining-capital fraction; quote
confidence as price *per unit of remaining capital*; or accept the drift and
label it in the UI. **Not decided.** It should be decided before any price is
shown to a benefactor as a quality signal, because the first thing people will do
is compare two missions at different stages.

---

## 8. Deployment — where the capital actually goes

*Formerly "the resolution split". Same 32nds, different meaning: not a carve-up
at resolution, but the schedule by which a mission's capital is deployed. Each
deployment consumes EBX pro rata (§7).*

```
$100,000 committed to Mission A
│
├── Organization allocation ─────────→ eventually spent by the organization
├── Earthbux allocation ─────────────→ eventually spent by Earthbux
│                                         └── some seeds DEX liquidity (§11)
└── Benefactor allocation ───────────→ represented by Mission A EBX
                                          │
                                          ├── held
                                          ├── traded
                                          ├── converted to other mission EBX
                                          └── eventually consumed
```

| Slice | Fraction | Destination |
|---|---:|---|
| EN — mission side | 8/32 | Earthbux operations |
| EN — advance | 2/32 | Earthbux operations, released with the case post reward |
| Org — mission side | 8/32 | the elected organization |
| Org — advance | 2/32 | the organization, released with the case post reward |
| Reward — best context | 1/32 | authorized citizen-research reward |
| Reward — best investigation | 1/32 | authorized citizen-research reward |
| Reward — best analysis | 1/32 | authorized citizen-research reward |
| Flexible remainder | 9/32 | released in the credit phase → org, or back into the pool |
| **Total** | **32/32** | |

⚠ **Amended 2026-09-08 (§0f).** Jax's note gives the guarantees directly:
**org 1/4 (8/32)**, **Earthbux 1/16 (2/32)**, **research prizes 3/32**, and
**19/32 retained by the benefactors**. So Earthbux's *guarantee* drops from 10/32
to 2/32 and the flexible remainder more than doubles, from 9/32 to 19/32. The
advance rows survive as draws against that remainder rather than as guaranteed
slices. The table above is the 2026-09-04 shape; §0f is the current one.

The three destinations named in §1 map onto this exactly: the **organization**
(10/32 guaranteed plus most of the flexible 9/32), **Earthbux operations**
(10/32), and **authorized citizen-research rewards** (3/32).

**Open:** what *triggers* each deployment (a budget release? a resolved step? the
org drawing funds?), whether the Earthbux and organization shares deploy on the
same clock, and whether the 9/32 flexible remainder may be steered by DEX price.
All three belong to the parked resolutions work.

---

## 9. Vote weight, and what being right is worth

**Unchanged by the rewrite.** These are influence, not money, which is exactly
why they survive a change that removed every monetary reward.

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
reward itself.

**Being right is now worth *only* this**, plus the upgraded mission membership
for backing the winning philanthropy. Early EBX is gone. That is a feature: the
prize for being right compounds into the next decision instead of into a
balance, and nobody's money moves faster than anybody else's.

**Open, and sharpened by the DEX:** does influence follow the **position** or the
**history**? A benefactor who sells their entire Mission A position — do they
keep the 2× they earned by backing its winning initiative? Following the history
is more honest about who did the work; following the position stops someone
accumulating vote weight across missions they have exited. **Not decided.**

---

## 10. Provenance

> "Every token maintains a record of its transactions."

A balance cannot carry a history, so the unit that does is the **lot**: ct that
have always moved together. Split a lot and both halves inherit the record.

**A swap is the hard case, and it is new.** When Mission A EBX becomes Mission B
EBX, the lot's chain does not end — but the chain now crosses a counterparty. The
model's position: a lot records **its own** journey (committed here, swapped
there, consumed against this deployment) and does not claim custody of the
capital on the other side of a swap. The receipt records the commit; the chain
records the direction; the two are not the same document and should not be drawn
as one.

**The coin has two elements.** *Element 1* (`settle_me`) is written when the
initiative election hits: the cause, the amount, the date, the initiative this
benefactor backed, and the one that **won** — so a losing coin still remembers
the argument that made the mission instead of being retconned into having always
backed the winner. *Element 2* is the philanthropy, written when the organization
election finalizes.

**Under the new model, element 2 is no longer a mint event** — nothing mints
there — and both elements now describe a mission the benefactor may since have
traded out of. Whether a coin (and the **mission membership** it confers, with
its right to win rewards) survives a full exit is **not decided**: membership can
follow the receipt, follow the position, or decay. Pick before the DEX ships.

---

## 11. Open fork — where the liquidity sits

**UNDECIDED as of 2026-09-04.** The choice changes what a price means, so it
gates the UI as much as the backend.

| Shape | How it works | For | Against |
|---|---|---|---|
| **One common pool** | every mission's EBX trades against a single shared reserve; a mission↔mission swap is two hops | deepest liquidity, one price surface, easiest to reason about and display | single point of failure and of manipulation |
| **Per-mission pools + common reserve** | each mission gets its own pool paired against the shared reserve — classic AMM | prices move per mission on that mission's own pressure, which is the signal we want | 8+ pools to seed; thin pools price badly and swing on small trades |
| **Direct mission↔mission pairs** | pools between specific missions | maximum expressiveness — "out of A specifically, into B" | liquidity fragments across 8+ open missions; almost certainly unworkable at this scale |

Two questions ride on the answer:

**Where does the initial inventory come from?** Earthbux seeding the pool out of
its own 10/32 (the "some returned to DEX/liquidity" branch in §8) is the leading
candidate; a genesis inventory minted at mission creation, or benefactors LP-ing
their own EBX, are the alternatives. Note that Earthbux seeding liquidity with
charitable capital needs the same legal look as §6.

**Does capital follow the claim, or only the claim?**

- *Capital follows* — a swap moves real capital between mission reserves.
  Coherent with "a position in remaining capital"; brutal for an organization
  mid-mission whose guaranteed 10/32 floor stops being a floor.
- *Only the claim moves* — per-mission capital is fixed at commit, and the DEX is
  a pure secondary market in direction. **This is the safer default and what the
  rest of this document assumes**, but it is not ratified.

---

## 12. What is built, and what is not

**The model is ahead of the code.** Nothing in §7 or §11 exists. Worse, the parts
of the old model this rewrite retires are still running, so the code is not
merely incomplete — in places it is now **wrong**.

### Disagreements between this document and the build

| The code does | This model says |
|---|---|
| `P2_SKIM = 0.10`, booked at `_settle_oe_stakes` in `finalize_p2` | ⚠ **the rate is right and the GATE is wrong** — 10% is final at the INITIATIVE election, so this booking moves to `finalize_p1` (§0b). This row used to read "no skim"; the amendment brought it back. |
| nothing implements a withdrawal window | 7 weeks after the OE to withdraw the not-yet-final remainder, then 100% is final (§0a) — **the largest unbuilt piece in this file** |
| deployment order is unspecified | converted-in, then org-election money, then the winning initiative's backers (§0e) — needs provenance on every position |
| `OE_LIFETIME_RACES = 14` / `OE_TABLE_ROWS = 8` | **keep them** — the 14-mission field applies before the OE (§0d) |
| `minted_ct` / `donated_ct` on `votes_p2` | one event — commit issues EBX and completes the donation |
| `wallet.harden_due` (the week roll) | retired; the DEX replaces the ratchet (§2) |
| `marked_tiv_id`, early EBX, the loser money paths | retired; every backer holds the mission's EBX (§2) |
| lowering an ME commit refunds the difference | no refund; reduce exposure by trading (§5) |
| `token_model_check` (108) · `wallet_check` (123) | both assert the retired arithmetic — they are the spec of the OLD model until rewritten |

### Still true and still built

- centitoken arithmetic and the rounding rule (§3);
- the grant: `grant_cause_id`, ten-as-a-floor, granted ct non-transferable (§4);
- the split-and-commit shape of an ME vote, `split_ct` by largest remainder (§5);
- the vote-weight curve and the influence multipliers as documented (§9) —
  though the multipliers still are not wired into the tallies; today they drive
  the per-row weight the wallet reports;
- `GET /wallet` · `GET /wallet/rows` · `POST /wallet/commit` · `PUT /wallet/org`;
  `POST /wallet/withdraw` survives but **only** for uncommitted purchased ct.

### Not built, named rather than assumed

- **The DEX**: pool, pricing curve, swap, slippage quoting, delisting.
- **The deployment triggers** after the first, and whether Earthbux and the org
  deploy on one clock.
- **Buying tokens.** `purchased_ct` is the column the real thing will write.
- **The grant-dilution cap** (§4) — the one open item that can go wrong quietly.
- **Membership after a full exit** (§10), and **influence after a full exit**
  (§9).
- **The coin's issuance timing.** `mint_mission_coins` still runs at
  `finalize_p2`; the model says coin at budget.
- **The phase-1 carryover machinery**, which still exists and describes a world
  that ended on 2026-08-20.

---

## 13. The surfaces

### The allocations panel

The old three-pairs bar (**Unallocated** → **Committed** → **EBX**) collapses
along with the states behind it. What a benefactor holds is now:

- **Unallocated** — granted · purchased. The granted segment prints the **cause**
  it was granted for. Purchased ct is withdrawable here and nowhere later.
- **Positions** — one row per mission: EBX held, that mission's current DEX
  price, and the holder's share of remaining capital. This row is where a swap
  starts.
- **Consumed** — capital deployed against the holder's positions, with the
  deployment that burned it. Read-only history.

**Donated is no longer a segment of the bar**, because it is no longer a
fraction of anything: everything committed is donated. The donated *total* is a
figure at the top of the panel — the sum of every commit — and it only ever goes
up.

### The initiative election

One amount, one slate, rows as percentages of that amount. The amount spends the
wallet. What changes: **the amount does not come back down.** The UI must say so
at the point of commit, in plain words, because it is the moment the gift
completes.

### The organization election

Eight rows, one per mission with an open philanthropy election, sorted by
deadline. A row is titled by its **initiative** and coloured by its cause.
Retired from this table: the "which state is this money in" column (EBX vs marked
vs movable), because there is only one state now.

### The DEX surface (unbuilt)

Needs, at minimum: a per-mission price with its **maturity caveat** (§7) legible
rather than buried; a swap quote that shows slippage *before* confirmation; the
holder's share of remaining capital next to the price, since that is what is
actually being traded; and a visible separation between **DEX price** (what
people expect) and **coin value** (what the mission has achieved). Rendering
those two as one number would be the single most misleading thing this product
could do.

### The conservation law

```
Σ(uncommitted tokens) = tokens owned and not yet given
Σ(EBX held, per mission) + Σ(consumed) = every unit ever issued for that mission
```

Two separate sums now, and deliberately so: the token bin and the EBX pools do
not share a total, because the door between them only opens one way.
