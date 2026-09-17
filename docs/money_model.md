# The money model

*The money in full: what EBX is, the finality ladder, the grant, the DEX, the
32nds, and what the code implements versus what this document says (§12).
§5 of [`README.md`](../README.md) is the summarized version; where the two
differ, this file is the model and the README is the summary that has to catch
up. **Rewritten 2026-09-16** from Jax's edits and answers (INSTRUCTIONS
build-seq §1). §0 lists every ruling in one place; the sections below it are
written to agree with §0, and where they do not, §0 wins.*

**Jax's plan for this document** — the shape he is writing it into, kept above
the generated contents because it is the intent, not the index:
1. The evolution of the funds and description of how they all end up donated
2. The tiers
- 10% at the ME, another 10% at the OE, then 100% on budget day (T+15)
- rest withdrawable as cash until budget day.
- once final, it's a fully deductible donation.
3. The DEX
- There are some open questions here. I'll get to them.
...

*Jax, kept verbatim:* "Ok. I'm going to have to write this myself. AI content is
to help me do that." — so every section below says what was decided and by
whom, and §14 says what was not.

<!-- TOC -->
## Contents

- [0. The rulings of 2026-09-16](#0-the-rulings-of-2026-09-16)
- [1. What EBX is](#1-what-ebx-is)
  - [The benefactor's loop](#the-benefactors-loop)
- [2. The states, and what "commit" means](#2-the-states-and-what-commit-means)
- [3. Centitokens](#3-centitokens)
- [4. The grant](#4-the-grant)
- [5. ME vote split](#5-me-vote-split)
- [6. Finality — the ladder](#6-finality--the-ladder)
  - [Who can move money, and when](#who-can-move-money-and-when)
  - [The two legal notes](#the-two-legal-notes)
- [7. The DEX](#7-the-dex)
  - [Price is an exchange rate of preference, not a return](#price-is-an-exchange-rate-of-preference-not-a-return)
  - [Pricing is a constant-product pool](#pricing-is-a-constant-product-pool)
  - [Deployment consumes in provenance order](#deployment-consumes-in-provenance-order)
  - [Delisting](#delisting)
- [8. Deployment — the 32nds](#8-deployment--the-32nds)
- [9. Vote weight, and what being right is worth](#9-vote-weight-and-what-being-right-is-worth)
- [10. Provenance](#10-provenance)
- [11. Liquidity — decided](#11-liquidity--decided)
- [12. What is built, and what is not](#12-what-is-built-and-what-is-not)
  - [Built 2026-09-16](#built-2026-09-16)
  - [Still true and still built](#still-true-and-still-built)
  - [Not built — the framing and exchange work list](#not-built--the-framing-and-exchange-work-list)
- [13. The surfaces](#13-the-surfaces)
- [14. Open questions](#14-open-questions)

<!-- /TOC -->

---

## 0. The rulings of 2026-09-16

Copy these exactly wherever the docs talk about money. Each one replaces
whatever an older section, doc or code comment said.

1. **All donations are final at T+15 (budget day).** Some are finalized before
   it. T is the initiative-election close; the organization election closes at
   T+8; framing runs T+8 → T+15.
2. **The finality ladder.** 10% of every initiative-election (ME) stake is final
   at T. Another 10% of every organization-election (OE) stake is final at T+8.
   100% is final at T+15. Winners and losers pay the same rates.
3. **A skim only marks finality.** A finalized ct is deductible and can no
   longer be withdrawn as cash. It does not leave the benefactor's position and
   funds nothing by itself.
4. **Until T+15 the non-final part can be withdrawn as cash.**
5. **The 5/16 is the organization's, not a skim.** On budget day the organization
   claims 5/16 (10/32) of the whole pool — its 8/32 framing release plus its
   2/32 advance. The rest stays as EBX in benefactor accounts.
6. **The 32nds.**

   | Slice | 32nds | Goes to |
   |---|---:|---|
   | Research rewards | 3 | 1 each: situation · investigation · analysis |
   | Advances | 4 | 2 to Earthbux · 2 to the organization |
   | Framing release | 8 | the organization, after framing |
   | Flexible | 17 | Earthbux (**max 8**) · the organization · benefactor exchange |
   | **Total** | **32** | |

7. **Grants carry a week id, never a cause id.** The active week's cause differs
   between the two elections, so a cause id cannot say where a granted token may
   go. A granted token may enter the ME or the OE that closes on its grant week.
8. **Being right is rewarded by the deployment order** (§7), and otherwise only
   by bragging rights, which can count as a membership benefit. There are no
   correctness multipliers. **Budget voting is weighted by EBX holdings**, never
   by having been right.
9. **The organization's guaranteed floor is paid at the end of framing**, before
   the exchange begins. Nothing on the DEX can undermine it.
10. **Losers move during framing (T+8 → T+15).** Backers of a losing initiative
    and backers of a losing organization can exchange their tokens into another
    mission during framing, and the tokens become EBX at that mission when they
    do.
11. **Liquidity: per-mission pools plus a common pool** (§11). **Capital follows
    the claim**: converting EBX-A into EBX-B moves the capital to mission B.
12. **Phases:** P1 initiative election · P2 organization election · P3 framing ·
    P4 exchange.

---

## 1. What EBX is

> **EBX is a non-withdrawable digital unit representing a holder's position in a
> mission's remaining charitable capital.** Each mission creates its own fungible
> EBX pool. EBX may be traded on the Earthbux DEX for EBX associated with other
> missions, so benefactors can reallocate their charitable exposure as mission
> performance and confidence change. EBX is consumed as its mission's capital is
> deployed to organizations, Earthbux operations, and authorized citizen-research
> rewards.

*Mission-specific units:*

> **EBX-A** is a transferable, mission-specific claim on a portion of charitable
> capital that is scheduled to be deployed through Mission A. The holder can
> exchange it for a claim on a different mission before it is consumed.

**Cash buys a position in a mission. After budget day the only way out of a
position is into another mission.** Before budget day, the non-final part of a
position can still be withdrawn as cash (§6).

### The benefactor's loop

```
Choose mission (P1 initiative election, P2 organization election)
   ↓
Commit tokens ───────────────────► 10% final at T, +10% at T+8
   ↓                                  (rest withdrawable as cash)
Framing, T+8 → T+15 ─────────────► losers exchange into another mission
   ↓
Budget day, T+15 ────────────────► 100% FINAL — the donation receipt is complete
   ↓                                  the organization claims 5/16 of the pool
Watch researchers / organization / news
   ↓
Gain or lose confidence
   ↓
Hold  /  sell  /  buy another mission     ◄──┐
   ↓                                          │
Continue participating ───────────────────────┘
   ↓
Eventually all capital is deployed
```

After budget day there is no exit to cash anywhere on that loop, and that absence
is the design. Benefactors keep influence and get the full legal benefit of
having made a donation.

---

## 2. The states, and what "commit" means

| State | What it is | Withdrawable as cash? |
|---|---|---|
| **Unallocated** | granted or purchased tokens not in any election | purchased: yes · granted: no |
| **Committed** | tokens backing an initiative, or an organization within a mission, before that election is final | the non-final part, until T+15 |
| **EBX** | a position in a mission whose initiative is elected and whose organization is elected (or that the benefactor exchanged into) | the non-final part, until T+15 |
| **Final** | an overlay, not a separate pile: the part of a stake the ladder has finalized (§6) | never |
| **Consumed** | capital deployed against a position (§8) | never; it is gone |

**"Commit"** is the button a benefactor presses to make a decision (Jax's
definition). Committing to a cause or an initiative is not yet a donation.
Committing to an organization turns tokens into EBX, and that still does not make
all of the money a donation. **100% is a donation only once framing is over
(T+15).**

---

## 3. Centitokens

Every stored quantity is an **integer count of ct**.

```
1 token = 100 ct = 10¢        1 ct = 0.1¢
```

Rounding always goes against the benefactor, to the ct: a skim of a 1 ct stake
finalizes 1 ct. **A swap never increases total EBX outstanding across the two
pools.** An AMM produces a real-valued price, and the swap has to land on an
integer ct on both legs.

---

## 4. The grant

> **10 tokens appear in your account each week. These tokens can only be used in
> this week's elections.**

- **A grant carries its week, never a cause** (§0.7). A granted token may be
  committed to the ME or the OE that closes on its grant week. The code keeps the
  week in `BenefactorAccount.last_grant_week`; `grant_cause_id` was dropped on
  2026-09-16.
- **Ten is a floor, not a ration.** `grant = max(0, 10 − free)`, the same rule as
  `available = max(10, held)` read from the other end. Hold six and four arrive;
  hold twenty and twenty are votable and none are taken away.
- **The grant does not exist until its week**, so there is no window in which
  granted ct is both real and free. A granted token can be neither transferred
  nor withdrawn.
- **Purchased tokens are the mobile money.** They exist the moment they are
  bought, may enter any mission, and may be transferred or withdrawn until they
  are committed. Withdrawal returns face value to **Cash**, never to the token
  bin, so nobody is ever billed a grant for money handed back to them.

**The grant is real money.** Earthbux actually grants $1 per user per week, and
that is what the funding runway measures. It is meant to be sourced from
**program-related investments (PRIs)** from VCs or early investors (a PRI is
essentially a loan with interest). Think of it as Earthbux paying a person $1 to
decide what to donate Earthbux's dollar to, in their name. A granted token
therefore mints ordinary EBX, one class with no asterisk, and it is backed by
cash like any other. The EBX-outstanding-exceeds-cash worry of 2026-09-04 does
not arise.

---

## 5. ME vote split

| | What it is | When it can be set |
|---|---|---|
| **the vote** | a split across up to `MAX_SPLIT_TIVS` (10) initiatives, **in whole percentages** | any time — it needs no tokens |
| **the commit** | one number: the total committed to that election | when the tokens exist |

A tiv's weight is `commit × that tiv's percentage`. `split_ct` applies the amount
by largest remainder, so a mission's rows sum to the commit exactly.

**The sliders are percentages, not tokens** (Jax, build backlog §2). They look the
same however much is committed. They move in 1% steps, so on a $100 commit the
smallest slice any initiative can hold is $1. **Adding money keeps the ratios**:
new tokens spread across the slate in its current proportions, and the
benefactor can re-split at will. The backend already stores the split as
percentages; the main.html sliders still work in tokens (§12).

A vote standing with no commit behind it is **a preference with no funding yet**.
The split stays freely editable until `finalize_p1`.

---

## 6. Finality — the ladder

```
T        initiative election closes     10% of every ME stake     FINAL
T+8wk    organization election closes   +10% of every OE stake    FINAL
T+15wk   budget day                     100% of every stake       FINAL
```

| | At T | At T+8 | At T+15 |
|---|---|---|---|
| Money carried from the ME | 10% final | 20% final | 100% final |
| Money that entered at the OE | — | 10% final | 100% final |
| Withdrawable as cash | the non-final 90% | the non-final rest | nothing |
| Still in the benefactor's position | all of it | all of it | all of it, as EBX |

- **A skim only marks finality** (§0.3). Nothing moves to the pool, to Earthbux or
  to the organization when a skim is taken. What moves money is deployment (§8),
  and the first deployment is the organization's 5/16 claim on budget day.
- **Winners and losers pay the same rates.** There is no `won` argument anywhere
  in the arithmetic.
- **The donation receipt is complete at T+15.** Before that it records a partly
  final donation: the finalized ct and the date each rung was reached.

### Who can move money, and when

| Who | What they hold | What they can do |
|---|---|---|
| Backed the **winning initiative** | early EBX in its organization election | vote for an organization; withdraw the non-final part as cash |
| Backed a **losing initiative** | tokens, marked with the initiative they backed | exchange into another mission **during framing (T+8 → T+15)**, becoming EBX there; withdraw the non-final part as cash |
| Backed the **winning organization** | EBX in the mission | hold; withdraw the non-final part as cash until T+15; trade on the DEX once it exists |
| Backed a **losing organization** | tokens in the mission | exchange into any of the other open missions (13 across the field) **during framing**, becoming EBX on exchange; or commit to the winner. Moving to another mission is treated as if it had been committed in that mission's OE, and it does not count as a DEX conversion. |
| Anyone, **after T+15** | final EBX | hold, or trade on the DEX. No cash exit. |

A loser who does nothing by budget day stays in the mission they are in, as EBX
behind its winner (⚠ assumed, §14).

### The two legal notes

1. **A DEX trade does not constitute receiving value.** A donor swapping A for B
   receives something with an observable market price, but both legs are
   non-withdrawable charitable claims, so no value leaves charity.
2. **The donation is set at budget day.** The receipt verifies the amount and the
   recipient mission, with the stipulation that the position may later be
   redirected to a different mission. Before T+15 a receipt can only certify the
   finalized rungs. ⚠ Both notes need a lawyer (§14).

---

## 7. The DEX

The Earthbux DEX trades **EBX for EBX**. It is where a benefactor changes their
mind after budget day. It opens with the exchange phase (P4).

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
because they would rather their remaining capital go through A. A premium means
the community wants to fund more of that mission; a discount means people are
quietly leaving it. **DEX price** (what people expect) and **coin value** (what
the mission has achieved) are different numbers and must never be drawn as one.

### Pricing is a constant-product pool

Buy a mission's EBX and less of it is left in the pool, so the next unit costs
more. Sell into the pool and the next unit costs less.

```
x · y = k
```

No order book, no counterparty to find, no listing committee. How much slippage a
benefactor may take in one swap is a UI decision (quote first, confirm second),
not a model one.

### Deployment consumes in provenance order

After the organization's guaranteed 5/16, which goes out first and pro rata from
everywhere, a mission's capital is deployed in this order:

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
```

**This is the reward for being right** (§0.8): the backers of the winning
initiative keep the power to convert their money for the longest. It also solves
the maturity confound. A pro-rata burn would make an old mission's EBX look
cheap just because more of it had been consumed; an ordered burn leaves the
last-deployed holders with a full claim until their turn.

### Delisting

Delisting a mission is far out and the process is not yet known. Supply walks to
zero as the mission runs, and the last EBX is **consumed, not sold**, so trading
must close before the pool empties. When — at final resolution, at an
outstanding floor, or on a schedule — is open (§14).

---

## 8. Deployment — the 32nds

*The schedule by which a mission's capital is deployed (§0.6).*

```
$100,000 committed to Mission A
│
├── Organization ────────────────→ 10/32 on budget day (8 framing release + 2 advance)
│                                   + its share of the flexible 17/32
├── Earthbux ────────────────────→ 2/32 advance + up to 8/32 of the flexible
├── Research rewards ────────────→ 3/32, one per rewarded post type
└── Benefactor positions ────────→ everything not yet deployed, held as Mission A EBX
                                      ├── held
                                      ├── traded
                                      ├── converted to other missions' EBX
                                      └── eventually consumed
```

| Slice | Fraction | Destination | Released |
|---|---:|---|---|
| Research reward — situation | 1/32 | authorized citizen-research reward | ⚠ §14 |
| Research reward — investigation | 1/32 | authorized citizen-research reward | ⚠ §14 |
| Research reward — analysis | 1/32 | authorized citizen-research reward | ⚠ §14 |
| Earthbux advance | 2/32 | Earthbux operations | ⚠ §14 |
| Organization advance | 2/32 | the elected organization | budget day (T+15), with the framing release |
| Framing release | 8/32 | the elected organization | budget day (T+15) — the guaranteed floor |
| Flexible | 17/32 | Earthbux (max 8/32) · the organization · benefactor exchange | during the exchange phase |
| **Total** | **32/32** | | |

So the most any mission can pay **Earthbux** is 2 + 8 = **10/32**. The
**organization** gets a guaranteed 10/32 and can reach 10 + 17 = 27/32 if none of
the flexible goes to Earthbux or back to benefactors. **Research rewards** are
always 3/32.

**How the exchange phase releases money** (Jax, kept as the next conceptual leap):

- The organization's releases are triggered when a budget item receives a
  critical amount of community support, especially from those who hold the
  mission's EBX. **A vote is multiplied by the voter's EBX holdings, and a
  negative vote only matters if the voter holds that EBX.** Non-holding voters can
  still trigger a release, as can effective organization activity.
- Each tranche released to the organization is registered as an **exchange**:
  the organization trades actions for money. Its spending of that money is
  tracked, and going over or under affects the mission's value (⚠ coin value or
  DEX price, §14).
- Resolutions and tranche releases are still an important part of the exchange
  phase; they are just not its definition.
- ⚠ The old line "each reward is released when 1/3, 2/3, and all the money has
  been spent" came from the pre-2026-09-16 table. Whether it still sets when the
  research rewards pay is open (§14).

---

## 9. Vote weight, and what being right is worth

Weight is 1:1 for the first block of 10 tokens, then each further block of 10
counts for `r ×` the block before it, `r = 0.5`:

```
10 tk → 10.00      20 tk → 15.00      30 tk → 17.50      40 tk → 18.75
```

- **No correctness multipliers** (§0.8). The 2× in the organization election for
  backing the winning initiative, the 2× in budget voting for backing the winning
  organization, and the 1.5× research multipliers are all retired.
- **Budget voting is weighted by EBX holdings** in that mission.
- **Being right is rewarded by the deployment order** (§7) and by bragging
  rights, which can be shown as a membership benefit.

---

## 10. Provenance

> "Every token maintains a record of its transactions."

**The coin treats each mission like a blockchain: every transaction is tracked.**
The accounting unit is the mission's funds: money in from x, money out to y,
money deployed. Jax is researching what this means for the per-lot record
described below, and suspects the per-lot view may be the wrong one (§14).

The current design: a balance cannot carry a history, so the unit that does is
the **lot**, ct that have always moved together. Split a lot and both halves
inherit the record. When Mission A EBX becomes Mission B EBX, the lot's chain
continues across the swap; it records its own journey (committed here, swapped
there, consumed against this deployment).

**Membership survives consumption.** Once a mission has consumed any donations
(which it has from budget day on), a donor keeps their mission membership
because they hold the coin-receipt of the initial advance. The coins on the
profile page show, per mission, the amount donated and the amount still held.

---

## 11. Liquidity — decided

**Decided (Jax): per-mission pools plus a common pool.** Each mission gets its
own pool, paired against a shared reserve, so prices move on each mission's own
pressure. The **common pool** also funds the grant runway and provides extra
liquidity.

**Capital follows the claim.** If someone converts EBX-A to EBX-B, the value of
that conversion becomes usable by mission B and stops being usable by mission A.
The organization's guaranteed floor is not undermined, because it is paid at the
end of framing, before the exchange (and the DEX) begin (§0.9).

Still open: where each per-mission pool's initial inventory comes from (§14).
Earthbux seeding liquidity with charitable capital needs the same legal review as
§6.

---

## 12. What is built, and what is not

### Built 2026-09-16

| Change | Where |
|---|---|
| `ME_SKIM = 0.10` booked at `finalize_p1` for every backer, winners and losers alike | `token_model.py`, `crud._open_oe_stakes` |
| `OE_SKIM = 0.10`, **additional**, booked once at `finalize_p2` | `crud._settle_oe_stakes` |
| A skim only marks finality: `votes_p2.donated_ct` now means final-so-far, and held EBX is `minted_ct` (no longer minted − donated) | `wallet.held_ebx_ct_of`, main.html + profile.html allocation bars, `stats` |
| 100% final at T+15: `tm.final_ct`, `wallet.budget_day`, `wallet.final_ct_of`; `final_ct` on `GET /wallet` and `my_final_ct` on each row | `token_model.py`, `wallet.py` |
| A moved stake carries its final part with it, in proportion | `wallet.move_stake` |
| An OE allocation cannot be set below its final part | `wallet.set_stake` |
| Withdraw the non-final part as cash until budget day (build-seq §2) | `POST /wallet/withdraw-stake` |
| Grants carry a week: `grant_week` on `GET /wallet`; `grant_cause_id` dropped (migration `e1a7c3b95d20`); the grant door is the week's active cause | `wallet.ensure_grant`, `crud.replace_p1_shares`, main.html, profile.html |
| Correctness multipliers removed (`influence_mult`, `ME_CORRECT_OE_MULT`, `OE_CORRECT_BUDGET_MULT`, `RESEARCH_MULT_EACH`); `my_influence` gone from the rows | `token_model.py`, `wallet.oe_rows`, `routers/wallet.py` |
| The 32nds as constants (`RESEARCH_REWARD_32NDS`, `ADVANCE_32NDS`, `ORG_FRAMING_RELEASE_32NDS`, `FLEXIBLE_32NDS`, `EARTHBUX_FLEX_MAX_32NDS`, `ORG_BUDGET_DAY_32NDS`) | `token_model.py` |
| `token_model_check` (107) and `wallet_check` (130) assert the ladder and the withdrawal | `scripts/` |

### Still true and still built

- centitoken arithmetic and the rounding rule (§3);
- the grant as a floor, granted ct non-transferable (§4);
- the split-and-commit shape of an ME vote, `split_ct` by largest remainder (§5);
- the vote-weight curve (§9);
- `GET /wallet` · `GET /wallet/rows` · `POST /wallet/commit` · `POST /wallet/move` ·
  `PUT /wallet/org`; `POST /wallet/withdraw` for uncommitted purchased ct.

### Not built — the framing and exchange work list

In rough build order. **Framing (P3) first:**

1. **Losers stay tokens through framing.** Today `_settle_oe_stakes` mints a
   losing-organization backer's stake into the winner at T+8, and a
   losing-initiative backer's marked tokens can move to other open OE races
   during the OE. The model: both groups hold tokens through framing and
   exchange into another mission during T+8 → T+15, becoming EBX on exchange.
   That needs a framing-window move endpoint (the current `move_stake` refuses
   decided races).
2. ◑ **Cash withdrawal of the non-final part until T+15.** Endpoint built
   2026-09-16 (build-seq §2): `POST /wallet/withdraw-stake` → `wallet.withdraw_stake`
   (unminted ct first, then minted; final ct never; refused from budget day).
   No page offers it yet, and `crud.withdraw_p1` is still a named refusal.
3. **The organization's 5/16 claim on budget day** — the first deployment, pro
   rata from every position, and the first thing that reduces held EBX.
4. **ME sliders in whole percentages** (main.html; backend already stores shares).
5. **Buying tokens.** `purchased_ct` is the column the real thing will write.
6. **`mint_mission_coins` still runs at `finalize_p2`**; the coin should issue at
   budget day.

**Exchange (P4):**

7. **The DEX**: per-mission pools plus the common pool, pricing curve, swap,
   slippage quoting, delisting.
8. **Deployment in provenance order** — needs provenance on every position.
9. **The flexible 17/32 and the release vote** (holder-weighted, §8).
10. **Budget voting weighted by EBX holdings.**
11. **Research reward payouts** (3/32) and the Earthbux advance.
12. **Membership after a full exit** (§10).
13. **The phase-1 carryover machinery** (`/p1/carryover`, `_withdraw_p1_legacy`),
    which describes a world that ended 2026-08-20 — REMOVAL REGISTER §C.

---

## 13. The surfaces

### The allocations panel

- **Unallocated** — granted · purchased. The granted part says which week's
  elections it may enter. Purchased ct is withdrawable here.
- **Committed** — to initiatives · to organizations.
- **EBX** — held, one figure per mission once positions exist: EBX held, the
  mission's DEX price, and the holder's share of remaining capital. A swap starts
  here.
- **Final** — shown as a figure against the position, never as a segment beside
  it, because finality does not move money. Before T+15 it shows the ladder
  (10% / 20%); after, it shows everything.
- **Consumed** — capital deployed against the holder's positions, with the
  deployment that consumed it. Read-only history.

### The initiative election

One amount, one slate, rows as percentages of that amount. The UI must say at the
point of commit, in plain words, that 10% becomes final when the initiative
election closes and the rest stays withdrawable as cash until budget day.

### The organization election

Eight rows, one per mission with an open organization election, sorted by
deadline. A row is titled by its **initiative** and coloured by its cause. The
commit dialog says another 10% becomes final at the close.

### The DEX surface (unbuilt)

At minimum: a per-mission price; a swap quote that shows slippage *before*
confirmation; the holder's share of remaining capital next to the price; and a
visible separation between **DEX price** and **coin value**.

### The conservation law

```
Σ(unallocated) + Σ(committed) + Σ(EBX held) = tokens owned and not yet consumed
final ⊆ committed + EBX held                     (an overlay, never added)
Σ(EBX held, per mission) + Σ(consumed) = every unit ever issued for that mission
```

---

## 14. Open questions

1. **A loser who never exchanges by T+15.** Assumed: they stay in the mission
   they are in, as EBX behind its winner. Confirm.
2. **What losing-initiative backers do during the OE (T → T+8).** Framing is when
   they move (§0.10). Until then, may they vote in the mission's organization
   election, and does the current "move to any open OE race" stay?
3. **When the research rewards and the Earthbux advance are paid.** The retired
   table said the Earthbux advance went "with the case post reward", and rewards
   at 1/3, 2/3 and all spent.
4. **Over/under spending moves which number** — coin value (what the mission has
   achieved) or DEX price (what people expect)? §13 warns against merging them.
5. **Initial DEX inventory** per mission pool: Earthbux's share, a genesis mint,
   or benefactor LPs.
6. **Delisting**: when trading closes.
7. **Per-lot provenance vs per-mission accounting** (§10) — Jax's research.
8. **Legal**: whether a partly-final donation can be receipted rung by rung,
   whether a DEX swap is receiving value, whether Earthbux can seed liquidity with
   charitable capital, and how PRI-funded grants are receipted (the grant is
   Earthbux's money given in the benefactor's name).
