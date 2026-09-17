# ME & OE — the finalized model, staged for the doc overhaul

> ## ⚠ SUPERSEDED 2026-09-04 — read this as history, not as the model
>
> The money model was overhauled on 2026-09-04. **EBX is now a tradeable
> position in a mission's remaining charitable capital**, exchanged for other
> missions' EBX on the Earthbux DEX; the donation completes at commit. The
> decisions recorded below that are now **retired**: the clean 10% OE skim, the
> week-roll ratchet, early EBX, marked tokens, the eight-open/fourteen-lifetime
> field, and donation-by-tranche. What survives: centitokens and the rounding
> rule, the grant (ten as a floor, tied to its cause), split-vs-commit, the
> vote-weight curve and the influence multipliers.
>
> This file is still worth reading — it is the record of *why* the retired
> machinery was built, which is exactly the context needed to judge whether the
> DEX really replaces it. `docs/token_model.md` is the model itself.

*Status: **historical.** The model in §A was BUILT and the docs in §B were
rewritten (2026-08-27c); both have since been superseded — see the banner above.
This file is the dated RECORD of what was asked and answered.*

*Written 2026-08-27c from the ME & OE Finalization block at the head of
`docs/INSTRUCTIONS.md`. This file is STAGING: it exists so the model can be
read in one piece and corrected in one place before it is folded into
`docs/token_model.md`, `README.md` §5–§6 and `docs/structure.md`. Nothing here
is built. Eight forks in the block were put to Jax the same day and answered; §C
is the record of what was asked and what came back, and §D is the write plan.*

---

## A. The model, in ten rules

### 0. Two units, not two names for one unit

| | what it is | movable | converts | tied to |
|---|---|---|---|---|
| **Token** | the voting unit | yes, within the week | → EBX, once | nothing |
| **EBX** | a token that has been committed to a mission | **no** | never | one mission |

**EBX cannot exist before its mission does.** A token becomes EBX only when its
**mission identity is finalized** — which is why an allocation sitting in an
initiative election is still a token however long it sits there: the initiative
it backs may never become a mission. (Jax, 2026-08-27c.)

This is the sentence that dissolves the confusion: **tokens are convertible,
EBX is not.** Everything else follows from it. The docs currently treat the two
as one asset under two labels — `structure.md` › Backend says "the unit is
TOKENS on the voting surface, EBX elsewhere", and `structure.md` › profile.html
says "EBX stays the unit (1 EBX = 1 token = 10¢)". Both are now wrong in kind,
not in wording: EBX is a *state*, reached by a one-way conversion, and it is the
thing a benefactor is trying to acquire.

### 1. Ten tokens a week, spendable in that week's elections

> "10 tokens appear in your account each week. These tokens can only be used in
> this weeks elections."

What a benefactor holds free is votable in the races running now — the
initiative election and the organization election of the current window — and
nowhere else.

**Nothing expires, and nothing above ten is clawed back.** (Jax, 2026-08-27c:
*"If there are <= 10 total tokens, 10 tokens will be available in the next
election for that cause or its replacement. If there are >= 10 total tokens,
that amount of tokens is available in the next election."*)

```
available next election = max(10, tokens held)
```

Which is the formula already in the code — `grant_ct(free) = max(0, 1000 − free)`
— said from the other end. Ten is a **floor**, not a ration: hold six and four
arrive, hold twenty and twenty are votable. That is what makes "these tokens can
only be used in this weeks elections" a statement about *reach* rather than a
fuse: an unspent token is not burned at the roll, it waits for the next race it
is allowed into — and the paragraph below says which race that is.

**A granted token does not exist until its week.** (Jax, 2026-08-27c: *"Tokens
aren't granted until election week when it's too late to transfer or withdraw.
You can vote beforehand, but the tokens aren't there yet."*) The ten are not paid
into an account and then fenced — they **appear in the week their cause's races
run**, which is the same thing as the fence and needs no rule to enforce it. A
granted token is therefore never transferable and never withdrawable: there is no
moment at which it exists and is free.

That is also the honest answer to "can I withdraw my grant": there is nothing to
withdraw, because nothing was paid for it and it is not there yet.

**You can vote before the tokens arrive, and it is not a special kind of vote.**
(Jax, 2026-08-27c, correcting the first draft of this file: *"It's still a vote,
it just doesn't have any tokens committed to it yet."*) See rule 1b — the vote
and the amount were always two things, and the docs have been writing them as
one.

**Unspent, they wait for their cause.** A granted token that its week did not
spend is available at **that cause's next window** — seven weeks on, or its
replacement's window if the cause election swapped it out. It cannot be moved
anywhere else in the meantime. The cause is not a tag on a mobile token; it is
the only place that token was ever able to go.

Three mobilities, then, and the docs should name them as three:

| token | exists from | transfer | withdraw | how it commits |
|---|---|---|---|---|
| **granted** | its cause's election week | **no** | **no** | votes in its cause's race; unspent, waits for that cause's next window |
| **purchased** | the moment it is bought | yes, until it enters this week's election | yes, until it enters this week's election | votes in any race it may enter |
| **marked** (lost an ME) | `finalize_p1` | **no** | **no** | a philanthropy vote, or rule 7 |

Purchase is the only mobile money in the model, and rule 2 is where it stops
being mobile. The **rolling commit-by date** (`GRANT_COMMIT_BY_WEEKS`, printed
under the honey segment) has nothing left to do under any of this: a deadline
that rolls forever, on tokens that cannot expire and cannot move, is a sentence
the interface has to explain and the model never enforces.

### 1b. A vote is a split; the commit is an amount

> "Since the maximum amount of tivs you can split your vote into is 10, we can
> have the vote commit be the total amount committed to that election, and the
> weight be the percentage given to each tiv within it." — Jax, 2026-08-27c

Two quantities, and every confusion in this area comes from printing them as one:

| | what it is | when it can be set |
|---|---|---|
| **the vote** | a split across **up to 10** initiatives, in percentages | any time — it needs no tokens |
| **the commit** | **one** number: total tokens committed to that election | when the tokens exist |

A tiv's weight is `commit × that tiv's percentage`. So a vote standing with no
commit behind it is not a promissory note or a pledge or a third state of
anything — it is a **preference with no funding yet**, and when the grant lands
it flows through whatever split is standing. Nothing about the vote changes when
the money arrives; only the multiplier in front of it does.

This is also the shape the ME surface has been missing. `replace_p1_shares`
already normalizes a slate to shares — the percentages are built. What is not
built is the **single amount for the election** beside them: the ME table still
spends a per-row client-side budget, which is why the backlog has carried *"make
the ME table one-way too"* since 2026-08-20. That item is now better described as
**one amount, one slate**, and it is the same shape the OE side already took when
Commit became all-encompassing rather than race-specific.

> **The two tens are a coincidence.** (Jax, 2026-08-27c, correcting this file:
> *"the 10-token grant and the 10-way split are coincidentally the same
> (possibly because my human brain likes the number 10)".*) The cap on a split
> and the size of the grant are **independent numbers**. The docs must not
> explain either with the other, and neither should move because the other did —
> a grant of 12 would not widen the slate, and an 8-way cap would not shrink the
> grant. Written down because the coincidence is exactly the kind a later reader
> derives a rule from.

### 2. Purchased tokens are the same tokens, until they vote

Tokens can be bought in any ME, and unlike the grant they exist the moment they
are bought. While they sit outside this week's election they may be **converted
or withdrawn** — the whole of the model's mobility lives here. The moment they enter this week's election
they behave "exactly the same as granted tokens": same lock, same rules, no
withdrawal. Purchase therefore buys *reach and reversibility*, not weight, and
`purchased_ct` stops being a permanent property of a token — it is a property of
a token that has not voted yet.

> "Purchased ME tokens (except the ones that become this weeks) can still be
> moved, although they don't become ebx until their mission identity is
> finalized." — Jax, 2026-08-27c

So a purchased token parked in a **future** initiative election is a live,
movable token for as long as that election is unresolved. It is spending it in
**this week's** race that ends the movement, not the act of pointing it at one.

### 3. Conversion happens at the week change

> "the conversion only happens at a week-change. Users will be able to convert
> as many times as they want within the same week."

Inside a week, an allocation is a **draft**: move tokens between eligible races
as often as you like, at no cost. At the week roll, **every standing OE
allocation hardens** — tokens pointed at a philanthropy become EBX for that
mission and stop moving. (Jax, 2026-08-27c: *"All OE allocations."*)

**ME allocations do not harden at the roll**, and rule 0 says why: the mission
identity is not final until the initiative election is. A slate can be redrawn
week after week; what ends that is `finalize_p1`, not the calendar. The roll is
the ratchet on the **organization** side only — which is the side where the
money picks a recipient.

This retires two rules at once: **`MAX_CONVERSIONS = 3`** (the conversion budget
that replaced the 15-week fuse on 2026-08-20) and **one-way commitment** (2026-
08-20b, "ct leaves the unallocated bar for a race and only a conversion moves
it"). The week boundary is the ratchet now, and it is a better one: it prices
nothing, it punishes no deliberation, and it gives every benefactor the same
deadline instead of a private counter.

### 4. When the initiative election closes, backers split two ways

**You backed the winning initiative.** Your tokens are **locked in that
mission's OE** until it finalizes. You receive that mission's **EBX
preemptively** — early EBX, which carries benefits to be specified — and for the
purposes of the OE the early EBX counts exactly as tokens.

**You backed a loser.** Your tokens **stay tokens**, marked with the initiative
they voted for. They may move to a different OE, and **the move is spent by
voting**: you vote for a philanthropy in the destination race, and that vote is
the commitment. Committed tokens become **EBX for that mission and stop moving**.

So the losing backer is not punished and not stranded; they are handed a live
token with a mark on it. The winning backer is paid early instead — which is the
incentive the block is careful to name ("they may do this because they are
trying to get the early ebx, which will have benefits").

### 5. The field is fourteen missions

> "7 elected before, the current one, and 6 elected later."

A marked token may be committed to any of **14** organization elections: the
seven missions elected before this one, this one, and the six elected after.

**Fourteen is a lifetime, not a screen.** (Jax, 2026-08-27c: *"8 options at the
beginning, if the user waits 6 weeks 6 new options will appear. 8 at any given
moment."*) A mission enters phase 2 every week and leaves eight weeks later, so
**exactly eight races are open at any instant** — that is the eight-row table,
unchanged. What grows is the token's cumulative reach: wait a week and the
oldest race closes while a new one opens. Six weeks of waiting is six new
options, and 8 + 6 = 14 distinct races a marked token could ever have reached.
The six-week horizon is not a separate rule either — it is rule 7 arriving: by
the token's own OE week it must go back to the ME or be committed to that
race's winner, so the field stops growing there.

The table therefore stays **eight rows, sorted by deadline** — and the honest
way to print the fourteen is on the *token*, not on the table: how many races
this one has left before its horizon closes.

### 6. A split ME vote makes different tokens — and then it doesn't

Splitting a slate leaves a benefactor holding tokens with different marks. Once
those tokens are committed to an OE and converted to EBX, **the mark is
forgotten**: EBX knows its mission, and the argument that got it there lives in
the coin's provenance, not in the balance.

### 7. There is one way back — and it is a conscious act

If a marked token is **still a token** when its OE week arrives, it may be
**transferred back to the ME and added to that week's grant**, still locked to
the initiative it originally voted for. The benefactor has to choose this
deliberately; there is no automatic sweep.

**The default is the opposite**: a token left in an OE is committed to whichever
philanthropy wins it. Silence is not a withdrawal.

### 8. What finalizing the OE does

- the **10% skim** is added to the pool;
- **correct OE voters get upgraded mission memberships**;
- the organization's **posting ability is expanded**;
- other consequences, out of scope here.

**A clean 10%, across the board.** (Jax, 2026-08-27c: *"It's a clean 10% across
the board, winners and losers pay the same, the difference comes after (special
ebx for ME, special mission membership for OE)."*) Every ct that entered the race
pays the same rate at finalization, and **being right is worth nothing in money**:

| you backed | the skim | what being right pays |
|---|---|---|
| the winning initiative | **10%** | **early EBX** — the preemptive holding of rule 4 |
| a losing initiative | **10%** | — |
| the winning philanthropy | **10%** | an **upgraded mission membership** |
| a losing philanthropy | **10%** | — |

This deletes the four-path settlement table in `token_model.md` §5 and the two
constants under it: `OE_SEND_WIN = 1.00` is gone, and `OE_SKIM_LOSE = 0.10`
becomes **`OE_SKIM = 0.10`**, paid by everyone. The buyer's sentence — *"if your
philanthropy wins, 100% of what you spent is donated; if it loses, 10% is
donated and 90% is yours"* — is retired with them. It is a simpler promise now,
and a much easier one to print on a card: **whatever you commit, 10% of it is
the skim. What you win is standing, not a rebate.**

**And the other 90% becomes the benefactor's EBX for that mission.** (Jax,
2026-08-27c.) It is not refunded and it is not kept back from the mission — it
changes *form*. The ct stop being a balance and become **mission-tied credit**:
the coin of `models.CreditCoin`, the donation receipt, the thing whose worth
tracks how well the organization runs what it was elected to run. The mission
spends against it (`README` §5, *EBX-coin holding actions* — a mission spends its
allocation, the holder may convert or withdraw at a sacrifice); the benefactor
holds the record of having funded it.

So the sentence a benefactor reads is:

> **10% of whatever you commit is the skim. The other 90% becomes your EBX for
> that mission — money you can no longer move, in a mission you helped choose.**

Two consequences the rewrite has to carry:

* **The wallet bar's four segments were mislabelled, and one of them was a pun.**
  (Jax, 2026-08-27c: *"'Claimed' refers to the org claiming the mission, not
  directly to a form of the ebx."*) The bar reads:

  ```
  unallocated ─▶ committed ─▶ minted ─────────▶ donated
   free tokens   to a tiv     to a mission       consumed by the org,
                 (or a phl)   = committed to     or by Earthbux
                              an org — this is
                              where it is EBX
  ```

  Which fixes a genuine collision in the code, not just on the page: `claimed` is
  a wallet segment AND the word for an organization taking authority over a
  mission (`Org claim flow`, *guaranteed-to-pool rate: bump on claim*). One of
  the two had to give it up, and the wallet was using it for something that
  already had a better name.

  **Donated and spent are different metrics, and each applies to both parties.**
  (Jax, 2026-08-27c.) The bar's last segment is the benefactor's side of a line
  that has two sides:

  - **Donate** — the benefactor's act, and each EBX crosses this line **once**.
    What is donated is split by percentage: **Earthbux gets its share, the
    organization gets its share.** This is the deductible moment (below).
  - **Spend** — what a recipient does afterwards, **incrementally**, over the
    life of the mission. Earthbux spends its share on supervision, publication
    and organizing; the organization spends its share on the mission itself.
    Two ledgers, same shape, neither of them the donation.

  So there are four numbers where the old bar had one word, and README's running
  tally already asks for them: *money donated* (the benefactor's, once per EBX)
  against *spent by Earthbux* and *spent by the org* (both continuous). A
  benefactor can watch their donation being used without their donation changing
  size — which is the whole point of a receipt whose worth tracks how well the
  money was spent.

* **README §5's donation split is rebuilt, not patched** (Jax, 2026-08-27c). The
  $2 researchers / $0–6 Earthbux / $6–18 mission table was built when a
  commitment was *spent* — one contribution divided three ways at the door. Under
  this model a commitment is 10% donated and 90% **held**, and what the two
  recipients do with their shares is a *spending* ledger that runs for the life
  of the mission. The old table conflates the two, which is why no amount of
  re-arithmetic saves it: it answers "where did my $20 go" with a split that now
  happens at three different times. The researcher slice needs re-deriving from
  the donation side, not the door.

**When does the mint happen, and when is it deductible?** Two different
questions, and `MINT_LAG_WEEKS = 7` was answering neither. The corrected flow
says *minted = committed to a mission*, and rule 0 says EBX exists exactly when
the mission identity is final — so the **mint is that moment**, not a date seven
weeks later.

The deduction is the other question, and it has a cleaner answer than a lag:

> "the tax deduction happens when the ebx is donated (included in the skim).
> Throughout the mission, more ebx will be donated." — Jax, 2026-08-27c

**Donation is an event, and it happens more than once.** A benefactor's EBX is
not donated in a lump at some week-number; it crosses the line **in tranches as
the mission runs**, and each tranche is deductible when it crosses. The 10% at
organization-election finalization is simply **the first one** — which is what
"included in the skim" means: the skim is not a separate charge sitting outside
the donation flow, it is the opening instalment of it.

This is the piece that makes the credit coin worth holding rather than a polite
fiction. Undonated EBX is still the benefactor's, still tied to the mission, and
still withdrawable at a sacrifice; donated EBX is gone, deductible, and being
spent by two parties on two ledgers. The mission's progress is legible in a
benefactor's own wallet as the balance moves from one to the other.

`MINT_LAG_WEEKS = 7` therefore does not survive as a mint or as a deduction
date. If seven weeks still names something real — the point at which the budget
is set and the first substantial tranche can be released — it should be renamed
for that and nothing else.

> **Two things this leaves for the resolutions work, named so they are not
> assumed:** what *triggers* each donation tranche after the first (a budget
> release? a resolved step? the org drawing funds?), and whether every tranche
> carries the same Earthbux/organization percentage the first one does. Both
> belong to phase 3, which is parked — the docs will say the shape and stop.

The sequencing of the skim follows from all of it. A benefactor who backed the
winning initiative is minted **early** (rule 4a — that is what early EBX *is*), while the
10% is not taken until the organization election finalizes. So the skim comes out
of a holding that already exists, rather than off the top of a stake on its way
in. Same 10%, but the order matters for the ledger: it is a **deduction from
minted EBX**, not a toll at the door.

**And being right still pays in influence.** (Jax, 2026-08-27c: both.) The
multipliers in `token_model.influence_mult` — 2× in the OE for backing the
winning initiative, 2× on budgeting for backing the winning philanthropy, 1.5×
each on research and 2.25× for both — **survive intact**, and the upgraded
mission membership and expanded posting reach are added beside them. Influence
compounds into the next decision; the membership is the part a benefactor can
see. Wiring the multipliers into `p1_tally` / `p2_tally` stays on the backlog
where it has been since 2026-08-20 — this answer keeps that item alive rather
than retiring it.

---

## B. What this contradicts, doc by doc

### `docs/token_model.md` — the heaviest rewrite

| § | claim on the page | status |
|---|---|---|
| §1 | state table: committed ct "only by conversion (3 max)" | **replaced** by rule 3 |
| §1 | the wallet bar *unallocated · committed · claimed · minted* | **relabelled and reordered**: unallocated → committed → minted → donated (rule 8) |
| §1 | "Refunds land in **Cash**, never in Tokens" | **contradicted** by rule 7; and the 90% now lands in **EBX**, not cash (rule 8) |
| §3 | `grant = max(0, 10 − free)`, deadline that rolls | formula **survives**; the grant now *appears in its week* and the rolling deadline goes (rule 1) |
| §3 | "Two doors": granted ct → slate or the one active OE; purchased ct → anywhere | **restated**: rule 1 is the same fence in better words; rule 2 changes what purchase buys |
| §4 | influence multipliers 2× / 2× / 1.5× | **survives**, joined by the membership and posting perks (rule 8) |
| §5 | four-path settlement table, `OE_SEND_WIN`, the buyer's sentence | **deleted**: one flat 10% for everyone, 90% held as EBX (rule 8) |
| §6 | *Conversions — three, and no clock* | **deleted whole**, replaced by rule 3 |
| §7 | provenance, the lot, the two coin elements | **survives**; rule 6 is exactly why element 1 must be kept |
| §6/§10 | `MINT_LAG_WEEKS = 7` as the mint | **retired**: EBX at mission identity; the deduction rides each **donation tranche** (rule 8) |
| §8 | unassigned stake defaults to the winner of its race | **survives**, and is now rule 7's default |
| §9 | eight-row OE table, "conversions left" per row | table **survives at eight**; the conversions column goes |
| §10 | built/not-built ledger | rewrite last, once the rest lands |

### `README.md`

- **§5 *At a glance*** is two model-generations stale: 20%/10% send rates and
  "loser commitments roll forward to the cause's next-cycle initiative". Nothing
  has rolled since 2026-08-20 and the initiative election has claimed nothing
  since then either. Same fault in the **§5 *Votes by phase*** table.
- **§4 *ME and OE*** — the definitions still hold; they need the token/EBX line
  and the two-outcome split (rule 4) added under them.
- **§6 *What happens to a commitment once phase 1 closes*** — rewrite around
  rule 4. This is the section the new model changes most in README.
- **§5 *Where a donation goes*** — the $2 / $0–6 / $6–18 split assumes a spent
  commitment. Under rule 8 a commitment is 10% spent and 90% held, so this table
  is a model of the old machine. Rebuild or mark superseded; do not leave it.

### `docs/structure.md`

- **profile.html › Wallet** already carries the seed of this model in three
  lines (*Cash / Tokens / EBX*). Promote it to the top of the section and make
  it agree with rule 0. Delete "**EBX stays the unit**" — it is the opposite of
  the finalized model.
- **main.html › OE table** — eight rows (Q3), the "n of three conversions left"
  cell (gone), "Committing is one way" (gone), the THIS WEEK tint that marks
  "the only row granted ct may enter" (survives as rule 1).
- **Backend** — `POST /wallet/convert` is documented as a one-of-three move that
  requires a philanthropy. Under rule 3 the free-move-inside-the-week is a
  different endpoint shape, and the week roll is a scheduler job.

### `docs/INSTRUCTIONS.md` backlog

- **"Make the ME table one-way too"** — moot. The rule it was copying is gone;
  the ME table needs to be *wallet-backed*, which was the real half of it.
- **"Buying tokens"** grows a second half: rule 2 gives purchased tokens a
  **withdraw** path, which nothing has today.
- **"Retire the phase-1 carryover machinery"** — still valid, still pending.

### Code the docs describe and this model breaks

`token_model.MAX_CONVERSIONS` · `conversions_left` · `can_convert` ·
`wallet.merge_conversion` · `GRANT_COMMIT_BY_WEEKS` / `roll_commit_by` (rule 1
removes the rolling deadline outright) · the one-way guard in
`wallet.commit_stake` · `POST /wallet/convert`'s required `org_id` ·
`wallet.claimed_ct`, which needs a new name now that *claimed* goes back to
meaning an organization claiming a mission · `OE_SEND_WIN` / `OE_SKIM_LOSE`,
which collapse to one `OE_SKIM`.

---

## C. The forks — all answered 2026-08-27c

| | question | answer |
|---|---|---|
| **Q1** | unspent weekly token at the roll | `available = max(10, held)`. Ten is a floor; nothing expires, nothing above ten is clawed back. |
| **Q1c** | can a granted token be withdrawn? | No, and not transferred either — it does not exist until the week when it is too late to do either. A vote may stand ahead of it (**the pledge**). |
| **Q1b** | is it tied to its cause? | Yes, absolutely — a granted token appears in its cause's election week and waits for that cause's next window if unspent. It can never be moved. |
| **Q2** | what hardens at the roll | **All OE allocations.** ME allocations stay soft until `finalize_p1`, because EBX cannot predate its mission. |
| **Q3** | fourteen missions or eight | **Eight open at any moment.** Fourteen is one token's cumulative reach as the field rotates under it. |
| **Q4** | influence multipliers | **Both** — the multipliers survive, the membership and posting perks are added. |
| **Q5** | the 10% skim | **A clean 10%, everyone, into the pool.** Being right pays in early EBX and mission membership, not in money. |
| **Q6** | where the other 90% goes | **It becomes the benefactor's EBX for that mission** — held, not refunded, not movable. The skim is the only thing that leaves. |

**Every fork is answered.** Two of this file's own inventions were corrected by
Jax the same day and are recorded here so the next reader does not re-derive
them: the **pledge** (there is no such thing — a vote simply has no amount behind
it yet, rule 1b) and the reading of **claimed** as a state of EBX (it is the word
for an organization claiming a mission, rule 8).

A third invention was corrected too: the **10-initiative cap and the 10-token
grant are a coincidence**, not one number expressed twice (rule 1b). Nothing in
the file now rests on an inference of mine.

What Q6 costs the existing docs is worth naming here as well as in §B: `README`
§5's *At a glance* (money in = money out), its **donation split** table, and
`token_model.md`'s four-segment wallet bar were all built around a commitment
being *spent*. Under a flat 10% a commitment is 10% spent and 90% **held**, and
those three passages are the ones that have to be rebuilt rather than edited.

---

## D. The write plan

In this order, because each one is the ground the next stands on:

1. **`docs/token_model.md`** — the heaviest. §1 (the state diagram gains the
   token→EBX conversion and the three mobilities), §3 (the grant appears in its
   week, the rolling deadline goes, the pledge gets its name), **§6 deleted and
   rewritten** as *the week change*, **§5 rewritten to one flat rate**, §8 folded into rule 7's default, §9's conversions column struck, §10
   rebuilt last.
2. **`README.md` §5–§6 — rebuilt, and deliberately shorter.** (Jax: *"yes,
   rebuild it. This new model is fleshed out and makes more sense, therefore it
   can probably be explained more concisely."*) That is the test the rewrite has
   to pass: one flat rate and one flow of four states should take fewer words
   than four settlement paths, two skims and a carryover did. Kill the 20%/10%
   send rates and the loser-carryover language, rebuild *At a glance* and the
   **donation split** around 10% skimmed / 90% held, rewrite *What happens to a
   commitment once phase 1 closes* around rule 4, and add the token/EBX line
   under §4's ME/OE definitions. If a section is not shorter afterwards, the
   model is not as settled as it looks — that is worth reporting back, not
   papering over.
3. **`docs/structure.md`** — promote the three-line Cash/Tokens/EBX sketch on
   profile.html to the model's own words, delete "EBX stays the unit", and strike
   the one-way and conversions-left language from the main.html OE table.
4. **`docs/INSTRUCTIONS.md`** — retire *Make the ME table one-way too*, grow
   *Buying tokens* to include the withdraw path, and write the new queue.
5. **This file** — KEPT, as the dated record of what was asked and answered.
   The model itself lives in `docs/token_model.md`; this is the why.

The code named in §B is untouched by any of that. The docs will say plainly what
is model and what is built, the way they do now.
