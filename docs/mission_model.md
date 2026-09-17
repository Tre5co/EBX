# THE MISSION MODEL

*What a mission IS, from the week its initiative is elected to the week its
resolutions close: the phases, who owes what on which date, the discussion
incentives, the vetting gates, the agreement an organization signs (§7), and —
in §10 — what `mission.html` has to show as a result. §3 of
[`README.md`](../README.md) is the summarized version; this file is the spec the
mission page is built from.*

**Jax's plan for this document** — the shape he is writing it into, kept above
the generated contents because it is the intent, not the index:
1. Overview
- Cause -> initiative -> organization -> framing -> release
- The clock
2. The discussion
- List of post types, when they will be posted, and templates for each. 
- The rewards
- Science and accreditability
3. ME
- bens, orgs, ebx, money
- Budgeting opens but without voting
- Org nomination
4. OE
- Mission Statements, timeline estimations, credentials
- bens, orgs, ebx, money
5. Framing
- bens, orgs, ebx, money
- Membership roles
- link and messages to send to winning org
- org verification
- contracts
- Phase is the end if org doesn't pass.
6. release
- Budgeting voting live
- the dex stimulates research.

*The process a mission runs, end to end, from the week its cause window opens to
the last resolution years later. Written 2026-09-02 from Jax's skeleton and the
build-sequence entry that asked for it:*

> "The discussion I created is a rudimentary version of what the mission will
> become. I need to expand this into a rich program to guarantee success. This
> needs to include Discussion incentives (C, I, A + B), Organization Requirements
> (Mission statement, binding agreements, budgeting), and earthbux plans (travel,
> purchases, deadlines, etc.)."

**Where this sits.** `README.md` §3 is the lifecycle as the code runs it and
`docs/money_model.md` is the money. Neither is restated here except where a
phase needs it in one line. What this file adds is the part no other doc holds:
**who owes what to whom in each phase, and what happens if they don't deliver.**

<!-- TOC -->
## Contents

- [0. Overview](#0-overview)
  - [The clock](#the-clock)
  - [Reading the legend](#reading-the-legend)
- [1. Phase 1 — Initiative Election](#1-phase-1--initiative-election)
  - [Earthbux Responsibilities](#earthbux-responsibilities)
  - [Organization Responsibilities](#organization-responsibilities)
  - [Benefactor Impact](#benefactor-impact)
  - [Money Dynamics](#money-dynamics)
- [2. Phase 2 — Organization Election](#2-phase-2--organization-election)
  - [Earthbux Responsibilities](#earthbux-responsibilities-1)
  - [Organization Responsibilities](#organization-responsibilities-1)
  - [Benefactor Impact](#benefactor-impact-1)
  - [Money Dynamics](#money-dynamics-1)
- [3. Phase 3 — Resolutions](#3-phase-3--resolutions)
  - [Stage 3a — Mission Framing (7 weeks)](#stage-3a--mission-framing-7-weeks)
  - [Stage 3b — Budgeting and onward](#stage-3b--budgeting-and-onward)
  - [Stage 3c — Release](#stage-3c--release)
  - [Stage 3d — Resolve](#stage-3d--resolve)
- [4. Discussion incentives — C, I, A + B](#4-discussion-incentives--c-i-a--b)
- [5. Organization communication — the four automatic messages](#5-organization-communication--the-four-automatic-messages)
- [6. Vetting — the gap between electable and payable](#6-vetting--the-gap-between-electable-and-payable)
  - [6a. The per-recipient checklist — what "payable" is measured against](#6a-the-per-recipient-checklist--what-payable-is-measured-against)
- [7. The mission agreement — the contract behind the claim gate](#7-the-mission-agreement--the-contract-behind-the-claim-gate)
  - [7.0 Parties & scope](#70-parties--scope)
  - [7.1 Representative attestation](#71-representative-attestation)
  - [7.2 Reporting consent](#72-reporting-consent)
  - [7.3 Money routing](#73-money-routing)
  - [7.4 Communication clause (both directions)](#74-communication-clause-both-directions)
  - [7.5 Resolutions & value](#75-resolutions--value)
  - [7.6 Nonprofit status](#76-nonprofit-status)
  - [7.7 Enforcement & override](#77-enforcement--override)
- [8. How the money physically moves](#8-how-the-money-physically-moves)
- [9. Open questions for Jax](#9-open-questions-for-jax)
- [10. What mission.html has to show, from all of the above](#10-what-missionhtml-has-to-show-from-all-of-the-above)

<!-- /TOC -->

---
## 0. Overview
Each mission follows the same structureal model.

```
Phase 1              Phase 2                  Phase 3           Phase 4
Initiative election  Organization election    Framing           Exchange
```

Organization → proposes
Scientists → investigate/explain
Public → chooses
Earthbux → executes and audits

### The clock
**T** is the initiative-election close
(`finalize_p1`); **T+8wk** is the organization-election close (`finalize_p2`, `OE_AFTER_ME_WEEKS = 8`).

| | Stage | Window | Ends when | Code |
|---|---|---|---|---|
| **P1** | initiative election | W0 → **T** (7 weeks) | an initiative is elected | `finalize_p1` |
| **P2** | organization election | T → **T+8wk** | an organization is elected | `finalize_p2` |
| **P3** | **mission framing** | T+8 → **T+15** (7 weeks) | the budget is set | `BUDGET_SET_WEEKS = 7` |
- P4 is after this.

### Reading the legend
**✅ built** · **◑ partial** · **[ ] not built** · **⚠ PROPOSED — needs Jax**.

## 1. Phase 1 — Initiative Election

**W0 → T (7 weeks). The mission does not exist yet; the cause window does.**
What is being decided is *what should be done*, deliberately before *who does
it*. Nothing in this phase is an entity, and that is the point — the initiative
election is conceptual, so an organization cannot win it by being popular.

### Earthbux Responsibilities

- ✅ **Open the window on time.** `bootstrap.ensure_due()` creates the mission as
  its cause's week arrives; the scheduler advances it. One cause per week, seven
  causes, staggered.
- ✅ **Seed the field.** The cause's catalogue initiatives are attached as
  phase-1 candidates so the race is never empty on day one.
- ✅ **Run the parallel cause election.** A challenger must take seven consecutive
  weeks; otherwise the interface confirms the incumbent by name.
- ◑ **Rate every post on the way in.** `classify_flag` is a stub returning green.
  Until it is real, Phase 1 is unmoderated in fact while claiming to be moderated
  in shape.
- [ ] **Publish the Winner Update**, 24 hours after finalize, drafted
  automatically and editable until it posts (§5).
- **Scientist + Site Auditor** (`roles.md`) own the phase: the initiatives on the
  ballot have to be real, achievable, and honestly described.

### Organization Responsibilities

**None, on purpose — and they may still show up.** An organization has no standing
in Phase 1 and cannot be voted for. But
- [ ] **Self-registration is always open**, unattached to any mission. An org may build its page at any time.
- [ ] **Be nominated** When proposing an initiative, benefactors may suggest orgs. This triggers a message "join our site".

### Benefactor Impact

- ✅ **Ten tokens land each week, stamped with the WEEK** (never a cause —
  money_model §0.7), spendable in the ME or OE closing that week. Ten is a floor:
  hold six and four arrive.
- ✅ **The vote is a split, the commit is an amount** — percentages across up to
  ten initiatives, one number behind them. A slate can stand before the tokens
  that will fund it exist.
- ✅ **Posting:** *research → context* and *review → case* are the Phase-1 types.
  Case argues the initiative; context gives neutral background.
- ✅ **Backers of the winning initiative mint early EBX** on the spot. Being right
  carries **no multiplier** (retired 2026-09-16): it is rewarded by the deployment
  order — their capital is deployed last — and by bragging rights.

### Money Dynamics

- ✅ `ME_SKIM = 0.10` (2026-09-16). **10% of every ME stake is final at T**,
  winners and losers alike. A skim only marks finality: the ct become deductible
  and stop being withdrawable as cash, but stay in the benefactor's position.
- ◑ **The non-final 90% is withdrawable as cash until T+15** —
  `POST /wallet/withdraw-stake` (2026-09-16); no page offers it yet.
- ✅ **Allocations stay soft to the close.** EBX cannot predate its mission, so an
  initiative allocation is revisable until `finalize_p1` — the week roll does not
  harden it.
- ✅ **At the close the field splits two ways.** Winner's backers → early EBX,
  locked into the organization election. Everyone else → a **marked token**,
  carrying the initiative it backed.
- ◑ **Losers move during framing (T+8 → T+15)** (money_model §0.10), exchanging
  into another mission and becoming EBX there. The code still lets a marked token
  move to any open OE race during the OE instead — framing build item 1.

---

## 2. Phase 2 — Organization Election

**T → T+8wk. Eight races open at any instant.** What is being decided is *who is
trusted to do it*. The mission now has an identity; it does not yet have a
counterparty.

### Earthbux Responsibilities

- ✅ **Nomination and registration are both open, with no gate.** Anyone may
  nominate any org; any org may self-register. Neither costs anything and neither
  requires a claim.
- ✅ **One entity, one page.** Near-duplicate names get a "did you mean?"
  (`org_dup_threshold = 0.82`). An org is never nominated twice.
- ✅ **Hold the claim gate.** Claiming requires the click-through representative
  attestation (§7 below), recorded with version, timestamp and
  account. That record is the litigation basis.
- [ ] **Warn the leaders at week 5** (§5 M2) — the top three orgs in a live race
  are told they might win and what winning will require.
- [ ] **The vetting pass** (§6). Before an org can be *elected* it needs a name
  and a mission statement; before it can be *paid* it needs far more. Today
  nothing enforces the gap.
- **Organization Relations Manager** owns the phase. This is the first human
  contact Earthbux has with a counterparty, and it sets the tone for the seven
  weeks that follow.

### Organization Responsibilities

- ◑ **Exist, verifiably, and say what you would do.** The election is decided on
  credentials and a short statement — **not a plan**. The plan is Phase 3, and
  that ordering is deliberate: no organization should have to write a budget for
  money it has a one-in-eight chance of receiving.
- [ ] **Answer the thread.** Org-authored *pitch* and *responses* are visually
  distinct from benefactor posts. An org that never posts is electable and
  usually shouldn't be.
- ⚠ **PROPOSED — silence is a public fact.** The org card shows *last responded*.
  Not a penalty, just the truth, visible before the vote rather than after.

### Benefactor Impact

- ✅ **One philanthropy per benefactor per mission.** Weight follows the block
  curve (`r = 0.5`): 10 tokens → 10.00, 20 → 15.00, 40 → 18.75. Buying more
  votes gets steadily worse value, which is the anti-capture mechanism.
- ✅ **Posting:** *research → analysis* and *review → evaluation*. Evaluation is
  pre-vote due diligence on the org; it is not the post-mission verdict.
- [ ] **The new-account rule** (CONVERSATION): a first-time account may vote in
  any election, but **may not buy extra votes** until it has been a member long
  enough. This is what stops someone registering accounts to elect their own org.
  Nothing enforces it yet.
- ✅ **Budget voting is weighted by EBX holdings**, not by having backed the
  winner (2026-09-16). Backing the winner is worth bragging rights, which can be
  shown as a membership benefit. ⚠ Open: what else an "upgraded membership"
  carries (§9 Q6).

### Money Dynamics

- ✅ **The week change is the ratchet.** Inside a week an allocation is a draft.
  At the roll, every standing organization-election allocation **hardens into
  EBX** for that mission and stops moving.
- ✅ **Two rows survive the roll:** one naming no philanthropy (there is nothing
  to harden into — it will follow the race's winner), and a marked one (it
  hardens once its benefactor votes for a philanthropy).
- ✅ **Another 10% is final at the close** (`OE_SKIM`, additional to the ME's),
  winners and losers alike — so money carried from the ME is 20% final at T+8.
  Nothing moves: a skim only marks finality.
- ◑ **Losing-organization backers keep tokens through framing** and exchange into
  another mission, becoming EBX on exchange. The code still mints them behind the
  winner at T+8 — framing build item 1.
- ✅ **Claiming raises the guaranteed pool rate** from `0.20` to `0.35`. The org
  is paid for showing up; the benefactor is protected when nobody does.

---

## 3. Phase 3 — Resolutions
a moment when a decision is made to allocate a specific amount of money to a specific mission objective. - a budget item

Budget posting starts at T. Budget voting starts at T + 8
**T+8wk onward.** One phase, four stages. The elections are over; from here the
mission is a relationship, and every mechanism below exists to keep that
relationship honest without making it adversarial.

---

### Stage 3a — Mission Framing (7 weeks)
We should remove budgeting from the phase vocabulary. Budgeting isn't really a phase, it's just something that happens, and it starts before this time period. We can call it "Orientation".

> "This is the step where the organization has 7 weeks to claim and submit things
> like a mission statement and an estimation of when they will be able to start.
> This is the time for Earthbux and the Organization to establish a
> relationship." — Jax

**The seven weeks are `BUDGET_SET_WEEKS`.** This stage is not an addition to the
clock; it is the name for a window the code already keeps. It ends when the
budget is set, and nothing about the money moves until it does.

#### Earthbux Responsibilities

- [ ] **Send the win notice within 24 hours** (§5 M3), with the claim link and
  the countdown stated in weeks remaining, not a date buried in a paragraph.
- ⚠ **PROPOSED — deliver the spiel, by a named human.** Not a form letter. The
  Relations Manager's opening, built on Jax's line:

  > "We're here to work with you to help the cause. Either we report on the
  > cause, or we report on you — and the goal is to report on the cause. If you
  > do a good job, we'll be able to tell interesting stories about the cause.
  > Some number of people have already committed their own money to this mission
  > and chose you to run it. Here is what they said about you, here is what they
  > asked for, and here are the six things we need from you in the next seven
  > weeks."

  The honesty is the pitch. An organization that hears "either we report on the
  cause or we report on you" at week one cannot say later that it was ambushed.
- [ ] **Verify identity — EN, one organization per week** (`roles.md`, Site
  Auditor + Relations Manager). One per week is the whole capacity, and it is
  exactly one elected mission per week, so the rate works only if verification
  never falls behind.
- ⚠ **PROPOSED — publish the framing checklist as a public progress bar** on
  `mission.html`. Six items (§6), each ✓ or ✗, visible to every benefactor from
  day one. The org is not being graded in private, and benefactors watching their
  money can see exactly what is outstanding.
- [ ] **Open S/S/S suggestion posting.** Per CONVERSATION: *items can be suggested
  any time, but they cannot be voted on until budgeting opens.* Framing collects;
  budgeting selects.
- [ ] **Begin the nonprofit-status application** with the org (contract §6).
  **Donations cannot flow until it is achieved** — which makes this the single
  longest-lead item in the model and the one most likely to blow the seven weeks.
  ⚠ **PROPOSED:** start it at week 5 of the *organization election*, for all
  three leaders, not at the win.

#### Organization Responsibilities

**The six framing artifacts** (⚠ PROPOSED as a set; the individual items come
from the contract draft and the build sequence):

1. **Claim the mission** — the click-through attestation, by a named
   representative. Everything else is gated on this.
2. **A mission statement for *this* mission** — not the org's boilerplate. What
   this initiative means when they do it.
3. **A start estimate** — the date they can begin, and what has to be true first.
4. **Identity verification** — registration documents, address, the
   representative's authority to bind the org.
5. **A payee for the check** (§7) — the legal name funds are made out to, matched
   against the verified identity.
6. **An executive and a representative named**, with the difference understood:
   the representative edits the mission, the executive holds the org account.

- [ ] **Respond to the top three benefactor threads** before budgeting opens.
  ⚠ PROPOSED — the cheapest possible obligation, and the one that tells everyone
  whether this relationship is going to work.
- ✅ **Accept being reported on** (contract §2). Supervision, publicity, and an
  EN progress report running parallel to their own.

#### Benefactor Impact

- ✅ **Membership is the coin**, and holding one is what makes a benefactor a
  member of this mission. Model says the coin issues **at budget**; the code
  still mints it at `finalize_p2` — a named backlog item, and this stage is
  exactly where the difference shows.
- [ ] **Suggest, don't yet vote.** S/S/S posting opens; upvoting waits.
- [ ] **The three research posts**, editable, on the card for the mission they
  target (profile + mission page).
- ⚠ **PROPOSED — roles are earned here.** From `jax notes 2.md`: *"You elevate
  yourself to higher roles in the organization through participation — valid
  posts, budget item approval, donation threshold."* Framing is when a
  contributor becomes visible enough to become something more.
- ⚠ **PROPOSED — carry it forward.** *"Benefactors should be encouraged to carry
  their earthbux through successive phases."* The mission page should make the
  next window's decision visible from inside this one.

#### Money Dynamics

- ◑ **Framing is when money is still settling.** Losers of both elections
  exchange into other missions (becoming EBX there), and anyone may withdraw the
  non-final part of a stake as cash. **Donations can always be received**
  (`jax notes 2.md`). [ ] The framing exchange is not built; the cash withdrawal
  exists as an endpoint (`POST /wallet/withdraw-stake`) with no page yet.
- ✅ **Budget day (T+15) makes 100% final** (`wallet.final_ct_of`).
- ◑ **The floor is known, the ceiling is not.** The organization's guaranteed
  **10/32 (5/16)** — its 8/32 framing release plus its 2/32 advance — is claimed
  from the whole pool **on budget day, at the end of framing**, before the
  exchange begins, so nothing on the DEX can undermine it. Its maximum adds its
  share of the **17/32** flexible. [ ] The claim itself is not booked.
- ✅ **Claimed or not changes the rate**, 0.20 → 0.35.
- ⚠ **PROPOSED — what "a small donation" means when nobody claims.** The build
  sequence promises an unclaimed org "only a small donation (which we will still
  investigate)". Concretely: the unclaimed rate (0.20) of the pool, sent to the
  organization *by check, after EN verification*, with EN reporting on the cause
  rather than the org. The mission is **not cancelled** — the community executes
  it as best it can.
- ◑ **The organization's advance (2/32) releases on budget day** with its framing
  release. Framing itself is unpaid, deliberately: the first money moves after the
  first obligations are met.

---

### Stage 3b — Budgeting and onward

#### Earthbux Responsibilities

- [ ] **Open S/S/S voting.** Suggestions collected during framing become votable;
  upvote-only, one open item per type per benefactor, rolling — a slot frees only
  when the item is **paid out**, never by revocation.
- ✅ **Hold the range.** `mission_budget_range` gives the org its concrete floor
  and its uncapped max.
- [ ] **Lock the step plan.** 7–12 steps, each with a guaranteed and a potential
  pool, no maximums, finalized by the end of budgeting. Step creation locks when
  the mission leaves `budget`.
- [ ] **Set `projected_end_at`.** One strategy named in the README: end right
  before that cause's next phase-1, so the org can bid for the next pool.
- ⚠ **PROPOSED — the Earthbux operational plan lands here.** Jax's "travel,
  purchases, deadlines" are not org line items; they are **support** items (the
  third S), and they are Earthbux's own budget for supervising this mission:
  who travels to see the work, what EN buys to document it, and the dates both
  are due. They are budgeted in the same stream and disclosed in the same place,
  because the whole model turns on Earthbux being audited by the same people it
  audits.

#### Organization Responsibilities

- [ ] **Draft budgets between the floor and the max**, publicly, more than once.
  Hypothetical budgets are the expected artifact, not a single final number.
- [ ] **Route against the socially selected picks** (contract §3) — the money
  follows the S/S/S items the community upvoted, not the org's preferences.
- ✅ **Some fields lock once adopted** — the committed cost line cannot be edited
  after it becomes a budget line.

#### Benefactor Impact

- [ ] **Budget voting is weighted by EBX holdings** in the mission (2026-09-16).
  A negative vote only counts from someone who holds that EBX. The 2× for backing
  the winning organization is retired.
- [ ] **Supply is the benefactor's column.** Service is what orgs do, supply is
  what they need, support is how Earthbux keeps it honest.

#### Money Dynamics

- ✅ **The 32nds** (2026-09-16, money_model §8). Research rewards **3/32** (1 each:
  situation · investigation · analysis) · advances **4/32** (2 Earthbux, 2
  organization) · framing release to the organization **8/32** · flexible **17/32**
  between Earthbux (max 8), the organization, and benefactor exchange. Constants
  in `token_model.py`.
- ✅ **EN takes nothing until the pool clears `POOL_THRESHOLD` ($100).**
- [ ] **No deployment is booked yet.** The skims (10% at the ME, +10% at the OE)
  are booked, but they only mark finality. The organization's 5/16 on budget day,
  the advances, the research rewards and every flexible tranche are unbuilt. Named
  here so nobody assumes the budget stage can pay anything out today.

---

### Stage 3c — Release

- [ ] **Steps release in stages**, each against its guaranteed and potential pool.
- [ ] **Two progress reports per step, in parallel**: the organization's and EN's,
  **moderated by benefactors**. The parallel report is the product — a single
  self-report from a funded party is not evidence.
- ◑ **The communication clause runs both ways** (contract §4). Missed reports
  reduce the releasable pool on a published schedule; **Earthbux forfeits value
  on the same schedule** if it fails its own obligations. ⚠ The schedule itself
  is TBD and is the most important unwritten number in the contract.
- [ ] **The weekly digest to every philanthropy** — threads flagged green (useful)
  / orange (critical but helpful) / red (spam, scam, unsupported slander, with our
  apology). Built as a surface on `mission.html`; **blocked on a mail transport**.

### Stage 3d — Resolve

- [ ] **Many small resolutions, possibly over years.** A resolution is a
  mission-tied outcome we can reasonably assume happened; each grants its
  evaluation point and bumps `mission.credit_value` (`resolution_value_bump`
  0.02).
- [ ] **Early resolution pays more** (rate TBD).
- ⚠ **PROPOSED — a mission is never marked "complete".** It goes **quiet**: no
  open steps, no unpaid guaranteed pool, EN's closing report published. Anything
  that arrives later still resolves. "Design for failure" cuts both ways —
  missions that fail need an ending that isn't a lie, and missions that succeed
  slowly need one that isn't a deadline.

---

## 4. Discussion incentives — C, I, A + B

*Jax: "Discussion incentives (C, I, A + B)." C/I/A are the three rewarded
research types; B is budgeting. Review sits alongside, paid in access.*

| Category | Type | Opens | Judged by | Wins | Paid |
|---|---|---|---|---|---|
| **Research** | **Context** | P1 | most helpful | **1/32** | with the advances |
| | **Investigation** | P3a | most helpful | **1/32** | end of Phase 3 |
| | **Analysis** | P2 | most helpful | **1/32** | later (post-P3) |
| **Review** | **Case** (initiative) | P1 | most **fair** | direct line to Earthbux + the org | at the ME close |
| | **Evaluation** (org) | P2 | most **fair** | direct line to Earthbux + the org | at the OE close |
| **Budgeting** | **Service · Supply · Support** | suggest any time · vote at 3b | **upvote only** | becomes a budget line | when the item is paid |

- ✅ **Membership gates winning, not posting.** Anyone in scope may post; only a
  mission member can take a reward or a comm line. A winner is a member by
  construction.
- ✅ **Neutral is a real signal** on research posts — people read it and felt no
  commitment either way. It is not a downvote and it is not nothing.
- ✅ **Review is fair/unfair, both counts shown.** No neutral.
- ✅ **Budgeting is upvote-only** — there is no way to vote *against* someone
  else's supply request, because that is a budget negotiation, not a debate.
- ✅ **Edits are versioned**; replying to your own post is an allowed alternative.
- ⚠ **PROPOSED — one incentive is missing and should exist: the org's own
  reward.** Every prize above pays a benefactor. An organization that reports
  well, early, and honestly gains only the absence of punishment. The early-step
  bonus (3d) is the hook to hang this on; it should be the *loudest* number in
  the contract, not a TBD at the bottom.

---

## 5. Organization communication — the four automatic messages

*Jax: "We are also going to need a level of automation in communication with
orgs."* All four are ⚠ **PROPOSED** as copy and **blocked on a mail transport**,
the same blocker as the weekly digest and self-serve password reset. Each is
drafted and editable before it sends, like the Winner Update.

**M1 · Registered.** *Trigger: an org is registered or nominated, any phase.*
> "Someone on Earthbux wants to donate to you. You've been added as a candidate
> organization — you didn't sign up for this and you don't owe us anything yet.
> Verify a few things now and you'll receive the maximum donation if the
> community elects you."

**M2 · You might win.** *Trigger: week 5 of an organization election, top three.*
> "You're currently in the top three for [initiative]. Here's what's being said
> about you, here's how to respond to it, and here's exactly what you'd need to
> do in the seven weeks after winning."

**M3 · You won.** *Trigger: within 24h of `finalize_p2`.*
> "The community elected you to run [initiative]. **You have seven weeks to claim
> this mission.** Claiming is a legal attestation that you're an authorized
> representative — it gives your account authority over the budget, and it raises
> the guaranteed donation. If nobody claims by [date], the mission still runs and
> you'll receive a smaller donation, which we'll still investigate and report on."

**M4 · Weekly digest.** *Trigger: weekly, for every live mission.* Threads about
you, grouped green / orange / red, with our apology attached to the red ones.

- [ ] **The claim link lands on the org registration page** — "kind of like
  Spotify for creators: you need to get verified, because we will be paying you."
- [ ] **Earthbux needs its own email address** before any of this can send.
  Currently the first blocker in the chain.

---

## 6. Vetting — the gap between electable and payable

*Jax: "I need to hammer down the vetting process."* ⚠ **The whole of this section
is PROPOSED.** Three gates, deliberately separated, because they protect
different things:

| Gate | Requires | Protects | When |
|---|---|---|---|
| **Nominable** | a name | nothing — it's free | any time |
| **Electable** | name + mission statement | the ballot from placeholders | before the OE close |
| **Payable** | claim + identity + payee + nonprofit status + EN verification | **the money** | before any funds move |

- **Fraud's window is real and named.** The advance lands at the start of
  budgeting; EN verifies *during* it. A fraudulent claimant could take an advance.
  Mitigations today: the attestation (litigation basis), verification before the
  full pool unlocks, recovery through litigation.
- ⚠ **PROPOSED — close the window instead of mitigating it.** Hold the advance
  until identity verification passes. Framing is seven weeks and verification is
  one org per week; if verification cannot happen inside seven weeks, the rate is
  the problem, not the gate.
- ⚠ **PROPOSED — publish a refusal.** An org that fails verification is removed
  and the reason is published. The alternative is a quiet removal, which looks
  identical to a corrupt one.
- **Until there's a security budget, exposure is limited on purpose** (Jax:
  *"Until I make enough to hire security, I need to hide earthbux from corrupt
  organizations"*). That is a real constraint on how loudly M1 and M2 go out, and
  it argues for keeping outbound contact human and narrow this year.


### 6a. The per-recipient checklist — what "payable" is measured against

*Moved here from `RESEARCH.md` on 2026-09-09 (build-seq: "add the vetting
checklist from research into…"). It was written as evidence and it is actually a
**gate**: this is the procedure that decides whether an elected organization is
payable, and everything in it is public record an unpaid person can run. Tier 1
is automated and disqualifying; Tier 2 is the twenty-minute human read of the
990 for a finalist; Tier 3 fires on any recipient whose revenue is more than 30%
noncash. The three gates in the table above say WHEN; this says WHAT.*

**Tier 1 — automated, under 60 seconds, disqualifying. Run on every candidate before it reaches a ballot.**

1. EIN resolves in **IRS Tax Exempt Organization Search** and appears in **Pub 78 data** (contributions actually deductible). *Fail = off the ballot.*
2. EIN **not** on the **IRS Automatic Revocation List** (monthly file — three consecutive years of non-filing triggers automatic loss of status). **A revoked org can still have a live website and a working donate button.** *Fail = off the ballot.*
3. No name or officer match on the **OFAC SDN list**. *Fail = off the ballot, and stop.*
4. **ProPublica Nonprofit Explorer API** (free, no key) returns at least one filing in the last 24 months. *Fail = manual review.*
5. Pull revenue, expenses, program expenses, net assets, officer compensation. Compute program %; flag below 65% (the BBB floor).

**Tier 2 — human, 20–30 minutes, per finalist.**

6. Open the most recent **Form 990 PDF** and confirm the API numbers match. They sometimes don't.
7. **Part VIII line 1g** — what fraction of revenue is noncash? **If >30%, escalate to Tier 3 and never publish a program ratio without a cash-only version beside it.**
8. **Schedule G Part I** — professional fundraisers: gross raised vs. **amount retained by the fundraiser**. This is where Kids Wish Network's $12.8M of $14.4M shows up.
9. **Schedule L** — related-party transactions (Part I excess benefit, Part II loans, Part III grants to interested persons, Part IV business transactions). **Name the counterparty and amount in the published writeup, always, even when innocuous.** GiveDirectly's ~$560,000 in 2023 fees to TTS, a payment platform formed by its co-founders, is a live example of a clean disclosure of an awkward fact.
10. **Part IX line 26** — joint costs allocated to program? Recompute with the whole joint cost moved to fundraising and **publish both numbers**.
11. **Part VI** — independent board majority; conflict-of-interest policy *monitored and enforced*; whistleblower policy; CEO compensation process.
12. **Part VII / Schedule J** — top compensation against **cash** program spend, never total.
13. **Part XII lines 3a–b** — Single Audit required? If yes, get and read the actual report; the 990 only tells you it exists.
14. Cross-check ratings on **at least two** of CharityWatch, Charity Navigator, BBB give.org. **Never Charity Navigator alone for a GIK-heavy org.**

**Tier 3 — GIK escalation, any recipient over 30% noncash revenue.**

15. **Schedule M column (d) — "Method of determining noncash contribution amounts."** *This is the single most important box on the entire form.* "Donor's estimate" and "third-party published price file" are not the same answer. Direct Relief and Good360 would fill this box differently. **Publish that sentence verbatim.**
16. **Schedule M Part II line 32b** — third party used to solicit, process or sell noncash contributions? A yes plus a big number is a pass-through structure.
17. **Part V line 7 / Form 8282** — if donated property was disposed of within three years, the charity must report what it actually got. **Mismatch between the donor's claimed Form 8283 value and the 8282 sale price is the classic overvaluation detection route.**
18. Ask the organization in writing: *what price source, at what granularity, refreshed how often, and what discount for used or near-expiry goods?* **Publish the answer or publish the refusal.**
19. Run a **physical-unit sanity check** — dollars per pound, per dose, per unit shipped — and publish it.
20. Compute and publish a **cash-only program ratio** beside the headline.

**What EN publishes.** Every number this checklist recomputes — the cash-only
program ratio, the fundraiser retention, the joint-cost split, the Schedule M
valuation sentence verbatim — goes in the organization's writeup, alongside the
headline figure it corrects. Publishing both numbers is the point: a benefactor
voting in an organization election is being asked to trust a stranger with a
pool, and the correction is the evidence that someone looked.

---

## 7. The mission agreement — the contract behind the claim gate

*Folded in from `docs/CONTRACT_DRAFT.md` on 2026-09-09 (build-seq:
"Contract_draft.md should be added to mission_model.md"). It sits here because
it is the artifact §6's **payable** gate actually collects: the representative
attestation an organization signs at claim, plus the reporting, routing,
communication and override terms that the rest of this document assumes exist.
⚠ **DRAFT — not legal advice and not reviewed by counsel.** The version and
timestamp of whatever text is live at claim time is what gets recorded against
the claim.*

> Working draft of the claim-gate contract. This document describes Earthbux's
> relationship to the organization and to the mission. The click-through
> representative attestation on mission.html is the acceptance mechanism; each
> acceptance is recorded server-side (attestation version + timestamp + account,
> table `org_claims`). NOT LEGAL LANGUAGE YET — structure and substance first,
> counsel later.

### 7.0 Parties & scope

- **Earthbux** — the platform and pool administrator; **Earthbux News (EN)** —
  its in-house media agency, funded by a fixed cut of each pool.
- **The Organization** — the entity whose authorized representative passes the
  claim gate for one specific **Mission** (one cause, one cycle).
- The agreement binds per-mission. An organization running several missions
  accepts once per mission.

### 7.1 Representative attestation

(As presented at the claim gate — v. `draft-2026-07`.)

1. The signer is an authorized representative of the organization, and the
   information provided about it is truthful and accurate.
2. EN will verify the organization's identity during the budgeting phase;
   misrepresentation is grounds for removal, public disclosure, and legal action.
3. The initial advance is released at the start of the budgeting phase; the full
   charity pool unlocks only after verification and against agreed budget and
   reporting obligations.
4. The organization will operate the mission in good faith — publish a budget,
   report progress honestly, and direct funds to the stated cause and beneficiary.
5. Accepting authority over the budget and mission sequence is a binding
   commitment; funds obtained through fraud may be recovered through litigation.

### 7.2 Reporting consent

By passing the claim gate, **the organization agrees to be reported on by
Earthbux** (EN): supervision, publicity, progress coverage, and a parallel EN
progress report alongside the organization's own, moderated by benefactors.

### 7.3 Money routing

- Earthbux agrees to **route untaxed money to the organization based on the
  socially selected service/supply suggestions** (the community-approved S/S/S
  picks recorded on the mission).
- Routing follows the mission's **step plan**: each release-phase STEP carries a
  **guaranteed** and a **potential** pool (no maximums), finalized by the end of
  the budgeting phase.
- Donations are routed through Earthbux to the organization or the community;
  most value remains in benefactor wallets as EBX. What benefactors keep as EBX
  (rather than converting/withdrawing) determines the pool available to budget.
- The guaranteed-to-pool rate rises when the mission is claimed (currently
  20% unclaimed → 35% claimed; config-driven placeholders).

### 7.4 Communication clause (both directions)

- **The available money declines if the organization fails to communicate with
  Earthbux** — missed progress reports, unanswered benefactor questions, or
  unreachable representatives reduce the releasable pool on a published
  schedule (schedule TBD).
- **Earthbux is bound symmetrically**: if Earthbux fails to meet its own
  communication and reporting obligations to the organization, Earthbux forfeits
  value on the same schedule. Both directions are part of this contract.

### 7.5 Resolutions & value

- The mission closes through **many small resolutions** (achieved suggestions
  and resolved steps), not a single resolution event. Each landed resolution
  grants its evaluation point and moves the mission's credit-coin value.
- Resolving steps **ahead of schedule earns a higher cash reward** (rate TBD).
- Realistically, missions can fail (bad-actor claims or extreme costs). Failure
  handling: unresolved steps' guaranteed pools, refund/return rules, and EN's
  closing report — TBD.

### 7.6 Nonprofit status

Earthbux works with the organization to apply for legal nonprofit status; the
application begins when the election is won, and **donations cannot flow to the
organization until nonprofit status is achieved**.

### 7.7 Enforcement & override

- Earthbux retains override authority (e.g. revoking a claim from a fraudulent
  or inactive representative).
- The recorded acceptance (version, timestamp, account) is the litigation basis.

---
*Open items: decline schedules (§4), early-resolution bonus rate (§5), failure
handling (§5), jurisdiction/governing law, beneficiary standing.*

*(End of the folded contract draft. When this goes to counsel, it goes as this
section, and the redline comes back into it.)*

---

## 8. How the money physically moves

*Jax: "How does the money transfer happen? I'd prefer if it was a check."*

⚠ **PROPOSED, and check is the right default.** A check is slow, which is a
feature here: it is auditable, it names a payee that must match the verified
identity, it clears against a real bank account, and it produces an artifact EN
can photograph. Constraints already in the model:

- ✅ **Nonprofit status first** (contract §6) — nothing flows before it.
- ⚠ **One payee per mission**, fixed at framing, changeable only by re-verifying.
- ⚠ **Every transfer is a post.** The check is a *mission-update* with the amount
  and the step it pays. Benefactors watching their EBX get used should see the
  instrument, not just a number changing.
- [ ] **Where the money lives between donation and check is undecided** (Jax:
  *"Need to start thinking about where the money lives"*). This is a bank and
  custody question, not a code question, and it gates real donation intake more
  firmly than any feature does.
- [ ] **Kids' accounts (12–17) need a linked adult account to authorize any
  transaction.**

---

## 9. Open questions for Jax

1. **The communication decline schedule** (contract §4) — how fast does the
   releasable pool fall when an org goes quiet, and does Earthbux forfeit at the
   same rate? Symmetry is promised; the number isn't.
2. **The early-resolution bonus rate** (§4) — the only reward pointed at the
   organization, currently TBD.
3. **Hold the advance until verification, or keep mitigating** (§6)?
4. **Does an unclaimed mission's "small donation" equal the 0.20 unclaimed rate**,
   or is it a separate smaller number?
5. **"Philanthropy" as the word for an organization** (CONVERSATION) — the model
   already uses *organization* everywhere the contract binds. Recommend retiring
   *philanthropy* from user-facing copy and keeping it only in `phl` identifiers.
6. **Membership tiers** — what exactly does an "upgraded mission membership" get?
   Since 2026-09-16 being right carries no voting multiplier (budget voting is
   weighted by EBX holdings), so the membership benefit is bragging rights unless
   something else is named.
7. **When does the coin issue** — the model says at budget, the code says at
   `finalize_p2`. Framing is where the difference becomes visible.

---

## 10. What mission.html has to show, from all of the above

*Mapped onto the ASCII layout in `jax notes 2.md` so the page build starts from
the process rather than from the boxes.*

| Box | Carries | From |
|---|---|---|
| **a** | 3 previous missions in this cause, pager above | continuity |
| **b** | globe + 7-sector annulus | the clock (§0) |
| **c** | membership, allocations, my votes, activity, inbox | benefactor impact, every phase |
| **d** | about · reviews · status graph · mission statement · org overview | framing artifacts (3a) |
| **e** | credit coin | money dynamics |
| **f** | **IN PROGRESS** — all input to the page | open steps + open S/S/S |
| **g** | **DONE** | resolutions, accumulating |
| **h** | 7-cause selection | the rotation |
| **i** | discussion, calmer than cause.html | §4 |

**The framing checklist (3a) has no box yet** and needs one — it is the only
surface that shows a benefactor what their money is waiting on. ⚠ PROPOSED: it
belongs at the top of **f**, above the steps, and it empties into **g** as items
land.
