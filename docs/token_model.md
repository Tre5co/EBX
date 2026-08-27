# The money model

*Settled 2026-08-19 over three passes; **revised 2026-08-20** when Jax resolved
the confusion that had been driving the model in two directions at once
(build-seq §1). `backend/app/token_model.py` is the executable version of this
file — if the two ever disagree, the code is right and this is stale.
`scripts/token_model_check.py` asserts every number below.*

**What changed on 2026-08-20, in four sentences.** There is **one skim** and it
falls after the organization election — the initiative election takes nothing.
The reward for voting correctly is **influence, not a discount**: 2× in the
organization election, 2× on budgeting, 1.5× each on research (2.25× for both).
A token's life is bounded by a **conversion count (3)** rather than a 15-week
fuse. And — the second pass of the same day — **committing is one way**:
"users can no longer move tokens from an OE to unallocated", so ct leaves a race
only by converting into another one, and the sliders went with the rule.

---

## 1. One asset, four states, three bins

```
$ CASH ──buy (only inside a commit)──▶ ◇ TOKENS ──stake──▶ ◇ staked
                                                              │
                          initiative election closes ─────────┤
                          nothing claimed · 100% forward into
                          the WINNING initiative's organization
                          election (arriving with no philanthropy
                          named, carrying coin element 1)
                                                              │
                       organization election closes ──────────┤   ← the one skim
                          phl won  → 100% claimed
                          phl lost →  10% claimed, 90% still committed
                                                              │
                                  + 7 weeks (budget set) ─────▶ ● MINT → COIN
                                                                mission-tied,
                                                                deductible
       committed & undecided ──▶ resolved as budget items roll through
       committed & refunded  ──▶ back to $ CASH   (never to ◇ TOKENS)
```

One wallet bar, four segments: **unallocated │ committed │ claimed │ minted**.

| Bin | State | Movable? | Donation? | Deductible? |
|---|---|---|---|---|
| **Cash** $ | at the door | yes | no | no |
| **Tokens** ◇ | **unallocated** — granted or purchased; topped up to 10 weekly | into a race, one way | no | no |
| **Tokens** ◇ | **committed** to an open race | only by conversion (3 max) | no | no |
| — | **claimed** — the settled share | no | yes | not yet |
| **Coins** ● | **minted** at OE + 7 weeks | convert only | yes | yes |

Refunds land in **Cash**, never in Tokens. That is what keeps `grant = 10 −
free` honest: nobody is ever billed a grant for money handed back to them — and
since 2026-08-20b it is the ONLY way money leaves a race early, because the
route back to the unallocated bar is closed. `crud.withdraw_p1` is a named
refusal now rather than a live endpoint.

---

## 2. Centitokens

```
1 token = 100 ct = 10¢        1 ct = 0.1¢
```

Every stored quantity is an **integer count of ct**. The pilot database holds
values like `123.7142858`; the loser-carryover skim booked `int(round(skim))`,
which writes **0** for a 0.5 skim; and the new OE table splits one balance
across eight races. Floats lose exactly this shape of problem.

Rounding is always **up, to the nearest ct**, and always against the benefactor
— the *claimed* share is what gets rounded up. At ct granularity that is a 0.1¢
bias. The same rule applied at whole-token granularity would round a 0.1-token
skim up to a full token: a 10× overcharge. The unit matters more than the
direction.

---

## 3. The grant

> **Your uncommitted balance is topped up to 10 every week.**

`grant = max(0, 10 − free)`. Hold 6 and the grant is 4; hold 10 or more and it
is 0. Nothing is ever taken away — what stops voting power piling up is the
**cap**, not a penalty, which is why the sentence above is the honest way to say
it and "uncommitted tokens = less grant" is not.

Paid on `GET /wallet` — opening the page is what tops you up — and idempotent
per cycle week, so a refresh cannot pay one twice.

**The grant carries a date** (2026-08-20).

> "These granted tokens are marked with the date that they must be committed by
> (or expire). If they are not committed to one of these 2 missions by that
> date, the date changes 1 week forward."

So the deadline is real on the face of the token and soft in effect: it is the
end of the week the grant was paid in, and an uncommitted grant simply takes
next week's date (`roll_commit_by`). Nothing is confiscated, because what caps a
hoard is the top-up formula, not a punishment — and a benefactor who thinks for
a week has not done anything wrong. The date is stored on the account
(`grant_commit_by_week`), sent to the client as a **date** rather than a week
index, and printed under the honey segment of the unallocated strip.

The arithmetic is stated once so a benefactor who opens the page monthly is
treated exactly like one who opens it weekly: the date on their uncommitted
grant is the end of the *current* week either way. A loop would have made the
answer depend on how often the code ran.

**Purchased tokens carry no date, and no door.** "Users can commit purchased
tokens anywhere. Purchased tokens are the same as granted tokens except they do
not have a deadline to commit." They may enter any race, and
`purchased_ct` exists so the strip can say which uncommitted tokens are on a
clock and which are not.

**Two doors for new money.** Granted ct may go to the initiative slate **or** to
the one active-cause organization election. Not to all nine races: "2 options,
not 9". **Purchased** ct carries no such restriction and may enter any of the
eight rows. Same tokens, different permissions — which is why the wallet tracks
`purchased_ct` and the unallocated bar draws two colours. On the active race the
grant is spent first, so a benefactor never loses the wider permission by
accident; on any other row only purchased ct can go at all.

There is no third kind. Unallocated is granted + purchased, full stop —
`grant_held_ct = free_ct − purchased_ct` — because nothing comes back out of a
race to sit there. The `fresh_ct` column and the `returned_lots` ledger that
tracked the third kind were dropped the same day they were added (migration
`a3b81d42c7e9`).

---

## 4. Vote weight

The old model priced extra organization votes on a doubling ladder,
`p2_vote_cost(v) = 10 × (2^(v−1) − 1)`. Paying 2× for the same marginal vote is
arithmetically identical to receiving ½ the weight for the same marginal
payment, so the ladder becomes a **weight curve** with no change to the
economics:

```
flat 1:1 for the first block of 10 tokens,
then each further block of 10 counts for r × the block before it,   r = 0.5

10 tk → 10.00      20 tk → 15.00      30 tk → 17.50      40 tk → 18.75
```

`r` is the one knob: 0.5 reproduces today's economics exactly, higher is
gentler, 1 is linear.

### Influence — what being right is worth

> "The result of the ME is that 'correct' voters get twice as much influence in
> the OE. 'Correct' OE voters get twice as much influence on budget voting. Both
> get 1.5x as much influence on research voting (so if you got both right, you
> get 2.25x)."

| you were right in… | organization election | budget voting | research voting |
|---|---|---|---|
| nothing | 1× | 1× | 1× |
| the initiative election | **2×** | 1× | **1.5×** |
| the organization election | — | **2×** | **1.5×** |
| both | **2×** | **2×** | **2.25×** |

The research column **multiplies** (1.5 × 1.5 = 2.25); the other two do not
stack, because each names one earlier decision. An organization-election vote
cannot reward itself — the race it would weight is the race it is in — which is
why `influence_mult("oe", …)` ignores `oe_correct` rather than quietly counting
it.

This is the whole reward for being right, and it is deliberately **not money**.
Yesterday's model paid for correctness with a cheaper skim; today one skim falls
on everyone at the same rate, and the prize compounds into the thing a
benefactor actually came for — the next decision — instead of into their own
balance.

> ⚠️ The curve is *implemented* (`token_model.weight_ct`) — worth saying,
> because the previous weight formula, `1 + b/(pool−b × size_factor)`, existed
> only in `p1_tally`'s docstring and in `config.size_factor`. The body of
> `p1_tally` is plain linear. Wiring the new curve into the two tallies is the
> next pass; today it drives the per-row weight the wallet reports.

---

## 5. Settlement — one skim, and the ME is not it

```
ME_SKIM      = 0.0      the initiative election claims nothing
OE_SEND_WIN  = 1.00
OE_SKIM_LOSE = 0.10     ← the one skim
```

> "There will only be 1 'skim' after the OE." — Jax, 2026-08-20

**The initiative election is a routing step, not a settlement.** Every backer's
stake — the winner's and the losers' alike — moves whole into the winning
initiative's organization election. Two reasons this is the right shape:

* A benefactor who is talked out of their first choice has still funded the
  cause. Charging them on the way past made the initiative vote feel like a toll
  booth, and it double-counted the loss for anyone who then backed a losing
  philanthropy too.
* The promise reads in one clause. "The most you can lose is 10%" is now simply
  **true**, rather than "10% twice = 19%" with an asterisk.

The four paths, per token staked in an initiative election:

| initiative | organization | donated | yours |
|---|---|---|---|
| won | won | **100%** | 0% |
| lost | won | **100%** | 0% |
| won | lost | **10%** | 90% |
| lost | lost | **10%** | 90% |

Money committed **straight to an organization election** settles identically —
there is no longer any toll for arriving through an initiative election, and
`token_model_check` asserts the two are equal rather than assuming it.

> The buyer's sentence, final. **"If your philanthropy wins, 100% of what you
> spent is donated. If it loses, 10% is donated and 90% is yours — to redirect
> to another mission or take back as cash."** It now reads the same whichever
> door the money came in through.

**Two consequences worth naming**, because a benefactor can see both:

* `crud.P1_SEND_WIN` and `P1_SEND_LOSE` are **0**, so the phase-1 "send floor"
  is 0 and a withdrawal during phase 2 returns everything. That is what one
  skim, after the OE, has to mean.
* `COMMITMENT_FUND_SKIM` is **0** and nothing rolls to a cause's next election.
  `finalize_p1` carries the money into this mission's organization election
  (`_open_oe_stakes`) and re-lists losing initiatives as next-cycle candidates
  (`_relist_losers`) — the idea moves, the money stays with the mission it
  funded. The phase-2 pool is bigger and more honest for it: it used to
  under-report itself by everything the losing initiatives held.

---

## 6. Conversions — three, and no clock

> "The token can now be converted to any OE. There is no time limit on the
> token, but there is a limit to the amount of times it can be converted (3),
> which puts a de facto limit on the time."

This **replaces the 15-week fuse**. The problem both mechanisms solve is the
same: a new mission enters phase 2 every week, so there is always a farther race
to hop to, and a benefactor could stay permanently committed — never donating,
collecting the full grant throughout, carrying weight in whichever race has the
least scrutiny. A count is the better instrument. A deadline punishes a
benefactor for deliberating; a conversion budget prices the hop itself, which is
the thing that needed pricing. Three conversions at eight weeks a race is a de
facto life of about thirty weeks.

**A conversion is the only way ct leaves a race** (2026-08-20b), and it is a
single transaction: `POST /wallet/convert` carries the amount, the destination
race and the philanthropy together. It never passes through the unallocated
balance, so there is no moment at which a thrice-moved token looks like a fresh
one — which is what the FIFO lot ledger existed to prevent, and why that ledger
could be deleted.

**A conversion is spent by VOTING, not by parking.**

> "In order for the user to convert their token to a different OE, they need to
> vote on a phl for it. If they don't, the token defaults to the OE from the tiv
> it was created within."

`POST /wallet/convert` REQUIRES an `org_id`: moving ct between races without
saying who it now backs is exactly what the rule forbids. After the move the
destination is home — an unvoted stake there would follow ITS winner, not the
race it left.

`votes_p2.conversions` holds the count and `origin_mission_id` the race these ct
were created in. `merge_conversion` takes the HIGHER count of the two rows plus
the move itself, so splitting a stake across races cannot buy extra moves.

`TOKEN_LIFE_WEEKS` (15) survives as the natural life of one ct from commitment
to mint — the date on the tax receipt — but it is a projection now, not an
expiry.

---

## 7. Provenance

> "Every token maintains a record of its transactions."

A balance cannot carry a history, so the unit that does is the **lot**: ct that
have always moved together. Split a lot and both halves inherit the whole
record — and so the whole conversion count. The chain survives the mint: a
credit coin still knows which initiative and which philanthropy its ct backed on
the way there.

**The coin has two elements**, and Jax's naming of them is the specification.

*Element 1* is written when the initiative election hits: "they become marked
with the cause, initiative and date it was converted, as well as the winning
initiative." One `settle_me` event per initiative the benefactor backed, each
carrying the cause, the amount, the date, and the initiative that **won** — so a
losing coin still remembers the argument that made the mission, instead of being
retconned into having always backed the winner. Written by `_open_oe_stakes` at
`finalize_p1`, and idempotent: finalizing twice does not write it twice.

*Element 2* is the conversions — a `commit_oe` for a philanthropy voted for in
the race the ct was born in, a `move_oe` for each of the (at most three) moves
elsewhere.

Only a **registered** vote is recorded. Typing an amount and changing it before
pressing Commit leaves nothing behind: a benefactor's second thoughts are not
part of the public record of what their money supported.

---

## 8. Unassigned stakes

When an initiative election closes, every backer's remainder moves into the
winning initiative's organization election **automatically**, and arrives with
no philanthropy named. Such a stake:

- **funds** the mission (it is in the pool);
- carries **no vote weight** — silence must not be able to change a result;
- **defaults to the winner** of the race it was born in, so it is never
  orphaned — silence is not a losing vote, and reading it as one (which the code
  did until 2026-08-20, against this section) charged silence a 10% penalty;
- **goes home** if it is sitting in a race that is not its origin and no
  philanthropy was voted for there. Unreachable by design since 2026-08-20b —
  a conversion carries its vote, so ct cannot arrive in a foreign race silently
  — but `wallet.settles_as_won` keeps the rule for rows written before that.

`VoteP2.org_id` is nullable for exactly this state. Inventing an org id instead
is how the orphaned-initiative 500 happened in August.

---

## 9. The OE surface

Three things stacked, in the order the decision has: **what I have** → **which
race** → **the eight deadlines**.

### The action row (2026-08-20b)

> "Discuss, register/nominate, and mission page should all be in the row with
> the unallocated slider, which should be above the cause-toggled OE race area."
> "Commit should be all-encompassing, not race-specific."

The unallocated balance used to be a row INSIDE the table, which made a
benefactor's whole wallet look like a property of one race's leaderboard; Commit
and the three links lived in the race dialog's foot, which made all four look
race-specific — and Commit actually was, so a benefactor who had dialled three
races had to press three buttons for one decision.

One row, above the dialog: the balance (one bar, two colours — honey granted
with its commit-by date, moss purchased with none), **one Commit** that writes
every pending amount across every race, and Discuss · Register an Organization ·
Mission page.

### The dialog

The nominated philanthropies, the pool, and — since the sliders went — **the
amount**: a number field beside the choice, because one-way money should be
typed deliberately rather than dragged past. Its ceiling is the server's, so a
benefactor cannot dial ct the two-door rule forbids.

### The table

Eight rows, one per mission with an open organization election — a mission
enters phase 2 every week and leaves eight weeks later. Two of them share a
cause, because the rotation is seven weeks and the window is eight, which is why
a row is titled by its **initiative** and merely coloured by its cause.

| column | |
|---|---|
| ☆ | watch |
| **My commitment** | read-only: "*4.5 committed to CarbonBridge Foundation*", plus anything dialled and any conversions left |
| **Initiative** | title · cause · `THIS WEEK` on the active race |
| **Total pool** | the race's phase-2 pool and vote count |
| **Vote date** | the day this race is decided — replaces "Week 0" |

Five rules the table obeys, all of them from 2026-08-20:

- **No Vote column.** "Clicking on the row is sufficient" — a column whose
  button repeats the row's own behaviour is a column of noise.
- **Rows do not expand.** A panel unfolding under one row pushes the other seven
  down the page, destroying the comparison the table exists to make.
- **No scrollbar.** "It should be a consistent size to fit the 8 races." The
  count is fixed by the calendar, so the shape is fixed too.
- **Sorted by deadline, soonest first**, on entry to the mode. The headers still
  re-sort once you are there.
- **No filter and no search.** On a table of exactly eight rows a filter can only
  hide races a benefactor still has money in — which is what pressing Vote on a
  card used to do, so that button is gone from the OE cards.

The conservation law both tables share:

```
Σ(ME rows) + Σ(OE rows) + unallocated = tokens owned
```

Unallocated is the only cell either table spends, and since 2026-08-20b it only
ever goes DOWN (the weekly top-up aside). Neither table can reach into the
other's committed rows, and neither can reach back into its own.

---

## 10. What is built, and what is not

**Built and asserted** (`token_model_check` 101 · `wallet_check` 118 ·
`oe_check` 58):

- the arithmetic, end to end, in `backend/app/token_model.py`;
- `free_ct` / `fresh_ct` / `cash_ct` / `last_grant_week` on the account, and
  `stake_ct` / `origin_mission_id` / `born_week` / `provenance` / nullable
  `org_id` on `votes_p2` (migration `d4e7b91c3a52`);
- `purchased_ct` / `grant_commit_by_week` on the account and `conversions` on
  `votes_p2` (migrations `f2c6a80d91b4` and `a3b81d42c7e9`, 2026-08-20);
- `GET /wallet` · `GET /wallet/rows` · `POST /wallet/commit` ·
  `POST /wallet/convert` · `PUT /wallet/org`. `PUT /wallet/stake` is gone: it
  set a position, and positions are what one-way commitment removes;
- the organization-election surface: action row, dialog with an amount, and a
  fixed eight-row table with no sliders, no scroll, no filter, no Vote column;
- **the ME half of settlement is booked** — `finalize_p1` carries every backer
  into the organization election and writes coin element 1.

**Not built yet** — named here so nobody assumes otherwise:

- **The OE half of settlement is still derived.** `finalize_p2` books nothing
  per benefactor, so `claimed` is recomputed from closed races on every read
  rather than written once. Correct number, wrong place.
- **Nothing sweeps a stake home at close.** `settles_as_won` returns `None` for
  an unassigned stake in a foreign race, so the read treats it as still
  committed — right answer, but no row is actually moved back to its origin.
  Unreachable for anything committed under the current rules, since a conversion
  cannot happen without a vote.
- **Buying tokens is still the localStorage simulation.** `purchased_ct` is the
  column the real thing will write; nothing writes it yet but the checks.
- **The influence multipliers are not wired into the tallies.** `p1_tally` is
  linear and `p2_tally` counts integer votes; today the multipliers drive the
  per-row weight the wallet reports (`my_influence` · `my_weight`). Budget and
  research voting do not read them yet, because neither surface tallies weight.
- **The mint does not exist.** Nothing yet moves a claimed stake into a credit
  coin at OE + 7 weeks.
- **The ME table's fresh-token door.** The initiative table still spends the old
  client-side `10 + localStorage.ebx_purchased_ebx` budget; only the OE side
  reads the wallet.
- **Buying tokens inside a commit.** `buyVoteEbx` is still the localStorage
  simulation.
