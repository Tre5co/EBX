# THE MISSION MODEL

**Contents**
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

Hi Claude, Let's improve this because I think this should be a permanent document- possibly something available to investors. I'm going to write a review on each section. Please edit each according to my review. This one is good. Just make it more concise. We'll edit the readme soon.

*The process a mission runs, end to end, from the week its cause window opens to
the last resolution years later. Written 2026-09-02 from Jax's skeleton and the
build-sequence entry that asked for it:*

> "The discussion I created is a rudimentary version of what the mission will
> become. I need to expand this into a rich program to guarantee success. This
> needs to include Discussion incentives (C, I, A + B), Organization Requirements
> (Mission statement, binding agreements, budgeting), and earthbux plans (travel,
> purchases, deadlines, etc.)."

*And from `jax notes 2.md`: **"Before designing the page, I need to design the
process of a mission."** This file is that design. `mission.html` is built from
it, not the other way round.*

**Where this sits.** `README.md` §3 is the lifecycle as the code runs it and
`docs/token_model.md` is the money. Neither is restated here except where a
phase needs it in one line. What this file adds is the part no other doc holds:
**who owes what to whom in each phase, and what happens if they don't deliver.**

---

## 0. Phase numbering, settled

It would be helpful if we built like this: Every phase before the one currently in progress is confirmed, but everything afterwards is not. So I know that phases 1 and 2 are locked in, and phase 3 is this 7 week period where the mission gets oriented between earthbux, the organization, the beneficiaries, and the benefactors. I don't really know much about what happens afterwards, because I haven't built it yet. I like the classification of ending a class of reversability. 

**Three phases, not four.** The skeleton called Mission Framing a fourth phase;
it is a **stage inside Phase 3**, the first one, and everything after the
organization election stays inside Resolutions:

```
Phase 1              Phase 2                  Phase 3 · RESOLUTIONS
Initiative election  Organization election    framing → budgeting → release → resolve
```

That keeps one phase model across `README.md` §3, `current_phase` in the code,
and this file. **Framing is not a small stage** — it is seven weeks and it is
where the counterparty relationship is either built or lost — but it is a stage,
because nothing about the money changes when it opens or closes. The elections
are phases because each one *ends a class of reversibility*.

### The clock
Yes. I will need to edit the readme. I already begain editing it. I'll start a "Readme" section in structure.md. Phase map looks good. One note. P3c & P3d overlap. Credit stage begins when the ebx becomes tradeable. each resolution isn't really a phase, rather a moment when a decision is made to allocate a specific amount of money to a specific mission objective. Also, budgeting technically starts at T. Framing is a better word for what I put as budgeting originally. Framing isn't even the best word. This is the 7 week period where the mission gets oriented between earthbux, the organization, the beneficiaries, and the benefactors.

Two anchors, both already in the code. **T** is the initiative-election close
(`finalize_p1`); **T+8wk** is the organization-election close (`finalize_p2`,
`OE_AFTER_ME_WEEKS = 8`).

| | Stage | Window | Ends when | Code |
|---|---|---|---|---|
| **P1** | initiative election | W0 → **T** (7 weeks) | an initiative is elected | `finalize_p1` |
| **P2** | organization election | T → **T+8wk** | an organization is elected | `finalize_p2` |
| **P3a** | **mission framing** | T+8 → **T+15** (7 weeks) | the budget is set | `BUDGET_SET_WEEKS = 7` |
| **P3b** | budgeting | T+15 → step plan final | steps lock | `budget` |
| **P3c** | release | step plan → last step | the last step reports | `credit` |
| **P3d** | resolve | continuous, may run years | never, formally | `resolution` |

> ⚠ **Inconsistency to fix:** `README.md` §3's "Full phase map" still numbers the
> budget window as weeks 9–16 (eight weeks) from `started_at`. `BUDGET_SET_WEEKS`
> is **7**. The table above is right; the README table is stale.

### Reading the legend

**✅ built** · **◑ partial** · **[ ] not built** · **⚠ PROPOSED — needs Jax**.
Everything marked ⚠ is an invention of this file. It is written as a concrete
mechanism so it can be argued with, not so it can be assumed. Nothing ⚠ may be
cited by another doc until it loses the mark.

---

## Phase 1: Initiative Election

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
in Phase 1 and cannot be voted for. But per `jax notes 2.md`:

> "Users need to be able to suggest organizations even before the initiative has
> been decided. In this case, they do not need to be associated with any
> particular initiative or cause."

- [ ] **Self-registration is always open**, unattached to any mission. An org
  that registers early builds its page before it is under election pressure —
  "without being forced to make commitments they don't yet understand."
- ⚠ **PROPOSED — the registration auto-message fires here**, the moment an org is
  registered or nominated, not at election time (§5 M1). The earliest possible
  contact is the cheapest one.

### Benefactor Impact

- ✅ **Ten tokens land against this cause**, spendable only in its elections. Ten
  is a floor: hold six and four arrive.
- ✅ **The vote is a split, the commit is an amount** — percentages across up to
  ten initiatives, one number behind them. A slate can stand before the tokens
  that will fund it exist.
- ✅ **Posting:** *research → context* and *review → case* are the Phase-1 types.
  Case argues the initiative; context gives neutral background.
- ✅ **Being right buys standing, not money:** backers of the winning initiative
  mint **early EBX** on the spot and carry **2×** into the organization election
  and **1.5×** into research voting.

### Money Dynamics

- ✅ `ME_SKIM = 0.0`. **The initiative election claims nothing.**
- ✅ **Allocations stay soft to the close.** EBX cannot predate its mission, so an
  initiative allocation is revisable until `finalize_p1` — the week roll does not
  harden it.
- ✅ **At the close the field splits two ways.** Winner's backers → early EBX,
  locked into the organization election and counting as tokens inside it.
  Everyone else → a **marked token**, still movable, carrying the initiative it
  backed.
- ✅ **Nobody is stranded and nobody is punished.** A marked token has eight open
  races to enter at any instant, fourteen over its life.

---

## Phase 2: Organization Election

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
  attestation (`docs/CONTRACT_DRAFT.md`), recorded with version, timestamp and
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
- ✅ **Backing the winner buys an upgraded mission membership** and **2×** in
  budget voting.

### Money Dynamics

- ✅ **The week change is the ratchet.** Inside a week an allocation is a draft.
  At the roll, every standing organization-election allocation **hardens into
  EBX** for that mission and stops moving.
- ✅ **Two rows survive the roll:** one naming no philanthropy (there is nothing
  to harden into — it will follow the race's winner), and a marked one (it
  hardens once its benefactor votes for a philanthropy).
- ✅ **A clean 10% at the close, winners and losers alike.** That skim is **the
  first donation tranche**, not a charge outside the flow, and it is deductible
  when it crosses.
- ✅ **The other 90% becomes mission-tied EBX** — held by the benefactor, spent
  against by the mission, worth what the organization makes it worth.
- ✅ **Claiming raises the guaranteed pool rate** from `0.20` to `0.35`. The org
  is paid for showing up; the benefactor is protected when nobody does.

---

## Phase 3: Resolutions

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

- ✅ **Nothing new is committed and nothing is refunded.** The pool is what
  hardened at the close, plus whatever arrives later — **donations can always be
  received** (`jax notes 2.md`).
- ✅ **The floor is known, the ceiling is not.** Guaranteed **10/32** of today's
  pool; maximum is that plus the **9/32** flexible remainder, and both grow with
  new donations. The org drafts against a range, not a number.
- ✅ **Claimed or not changes the rate**, 0.20 → 0.35.
- ⚠ **PROPOSED — what "a small donation" means when nobody claims.** The build
  sequence promises an unclaimed org "only a small donation (which we will still
  investigate)". Concretely: the unclaimed rate (0.20) of the pool, sent to the
  organization *by check, after EN verification*, with EN reporting on the cause
  rather than the org. The mission is **not cancelled** — the community executes
  it as best it can.
- [ ] **The advance releases at the start of budgeting**, not here. Framing is
  unpaid, deliberately: the first money moves after the first obligations are met.

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

- ✅ **2× in budget voting** for backing the winning organization; **1×** for
  everyone else. This is the only place the OE reward pays out as influence.
- [ ] **Supply is the benefactor's column.** Service is what orgs do, supply is
  what they need, support is how Earthbux keeps it honest.

#### Money Dynamics

- ✅ **The 32nds.** EN 10/32 · org guaranteed 10/32 · three post rewards 1/32 each
  · **flexible remainder 9/32**, released in the credit stage to the org or back
  to benefactors.
- ✅ **EN takes nothing until the pool clears `POOL_THRESHOLD` ($100).**
- [ ] **Later tranches are unbuilt.** Only the first (the 10% skim) is booked, and
  the Earthbux/organization percentages of a tranche are not set. Named here so
  nobody assumes the budget stage can pay anything out today.

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

---

## 7. How the money physically moves

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

## 8. Open questions for Jax

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
6. **Membership tiers** — what exactly does an "upgraded mission membership" get,
   beyond 2× budget voting? It is promised as one of the two rewards for being
   right and it is currently undefined.
7. **When does the coin issue** — the model says at budget, the code says at
   `finalize_p2`. Framing is where the difference becomes visible.

---

## 9. What mission.html has to show, from all of the above

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
