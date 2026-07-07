# Mission Lifecycle & System Model

> Canonical model of how an Earthbux mission moves from idea to resolution.
> The page-by-page UI spec lives in `structure.md`; open ideas live in `backlog.md`.
> Status: working draft — reflects decisions through the phase-2 design pass.

## Goals

Streamline and publicize charity missions. Pool donations to avoid redundant or
competing efforts, expose wasteful or fraudulent actors, and reorient attention
toward the cause rather than the sponsor. Democratize *which* idea and *which*
organization gets funded, and report on the work independently through Earthbux
News (EN).

## The 7-cause rotation

Seven causes rotate, one decision per week:

`Atmosphere · Oceans · Land · Forests · Wildlife · Human Rights · Human Progress`

Each cause runs a staggered 7-week window. Each week, one cause's window opens and
a new mission is created (`atm0, oce0, … hpr0`, then `atm1, …`). A mission's
`started_at` is the day its window opens; every phase boundary is measured from there.

## Mission phases

| # | Phase | Window (from start) | What happens |
|---|-------|--------------------|--------------|
| 1 | Pre-Initiative / Initiative election | weeks < 1 → ends ~week 7 | Benefactors propose and vote on initiatives |
| 2 | Organization election | ends on the cause's final active day (~week 8) | Benefactors nominate/vote on organizations |
| 3 | Budget | weeks 9–16 | Elected org budgets & plans; **EN verifies the org**; advance released |
| 4 | Credit-Release | weeks 17–32 | Credits released in stages; progress reports |
| 5 | Resolution | weeks 33+ | Final distribution, impact summary |

The **organization election (phase 2) happens before budgeting and planning** — the
org is chosen on credentials and a short statement, not a detailed plan.

---

## Phase 1 — Initiative election

- Anyone can propose an initiative (an idea; no owner, no legal identity).
- Split-vote economy: a benefactor may spread vote share across several initiatives.
- Vote weight is amplified by contribution amount.
- Settlement: **20% of your commit is sent to the pool if your initiative wins, 10% if not.**
- Tallied on the first day of the cause's active period.

### How commits carry into phase 2

1. Benefactors vote in phase 1. The losers' 10% and winners' 20% become part of the **pool**.
2. Anyone with a contribution in the pool now holds **credit coins** (locked until the end of phase 3).
3. The **rest of your commit stays in the pool for phase 2** unless you withdraw it.
4. If you don't vote in phase 2, your money simply flows to the winning org. (Most are expected to vote.)

---

## Phase 2 — Organization election

An initiative is a proposition; an organization is a **counterparty** that must
receive funds and do the work. So phase 2 is three steps, not one:
**nominate → (register/claim) → elect.**

### Nomination & registration (both open, no gate)

- **Organizations can self-register at any time** — no candidacy required.
- **Benefactors can nominate any organization as a candidate for any phase-2 mission.**
- Minimum candidacy requirement: **a name and a mission statement.**
- An org is a single entity: it can run multiple missions but is **never nominated
  twice** and never has separate pages. On nomination, warn on near-duplicate names
  and prompt "did you mean an existing org?" (matching tunable).
- Nominating and voting are **free**. The only gate is the claim (below).

### Claiming a mission (the gate)

- A real representative **claims** the mission → their account gains authority over
  the **budget and mission sequence**. This is the key trust moment.
- A nominated (not self-registered) org has **until the start of phase 4 to claim**.
- Claiming requires a **click-through legal agreement** (representative attestation;
  see `mission.html`). This establishes the basis to litigate fraud.
- **Identity verification is EN's responsibility, performed during phase 3** — so EN
  only verifies one organization per week (the week's single elected mission).

### If no org claims

The mission is **not cancelled**. The advances are still sent; the **community
executes the mission** as best it can (e.g. donating the pool onward), and EN still
reports on it. These cases tend to end with significantly smaller pools.

> Earthbux does **not** create its own organizations. Instead the community
> determines the best existing organization for the elected initiative and votes.

### Guaranteed-to-pool rate

- An unclaimed/nominated mission has a **set guaranteed-to-pool rate**.
- That rate is **bumped when the organization claims the mission** — rewarding orgs
  for showing up, and protecting benefactors when no one does.

### Voting

- **One vote per benefactor; no split** (contrast with phase 1).
- Additional votes are **bought** on a steep curve: 1st free, 2nd $10, 3rd $20,
  4th $40 … i.e. `price(votes_held) = 10 × 2^(votes_held − 1)` EBX. Spent outright,
  never committed.
- Eligibility: tied to having a stake in this mission (committed in phase 1 / holds
  the credit coin) — credits = membership.
- Settlement: **100% of your commit is sent if your org wins, 20% if not.**
- Tallied on the final day of the cause's active period.

### Election content

Benefactor-authored, pre-vote due diligence drives the election:

- **Evaluation** — my verdict on this org (trustworthy? effective? transparent?).
- **Context** — neutral background / track record.
- **Analysis** — data or expert take.

Org-authored: a **Pitch / mission statement** plus **Responses** to questions, kept
visually distinct from benefactor evaluations.

> "Feedback" is reserved for the *post-mission* performance phases (4–5), not the
> election. Evaluation = pre-vote; feedback = post-hoc performance.

### Fraud handling

The advance lands at the **start of phase 3**, but EN verifies *during* phase 3 — so
a fraudulent group could in theory win the advance. Mitigations: the click-through
legal agreement (litigation basis), EN verification before the **full** pool unlocks,
and recovery of fraudulently obtained funds through litigation.

---

## Phases 3–5 (summary)

- **Phase 3 — Budget:** committed money locks; the org learns how to earn the full
  pool and builds a budget. EN verifies the org. Initial advance released.
- **Phase 4 — Credit-Release:** credits released in stages to the best contributors,
  then to a mix of org and benefactors; 7–12 step progress reports (org report vs.
  EN parallel report, benefactor-moderated).
- **Phase 5 — Resolution:** final distribution and impact summary.

---

## Credits, EBX & the pool

- 1 credit = 1 EBX ≈ $1; EBX hold $1 value for 7 weeks post-mint.
- Credit coins represent a benefactor's stake in a mission; **holding one = membership**.
- EN takes a 5/16 cut only when the pool clears $100 (1/16 to evaluation, ¼ to EN's
  side of the mission). Minted credits become tax-deductible after they are committed
  to a charity and converted.

## Membership roles

Every org account is a set of members:

- **Contributor** — a benefactor who voted for the org / holds credits for the mission. Community.
- **Representative** — may edit the mission page.
- **Executive** — highest org permission.
- **Beneficiary** — represents the recipients of the charity effort; has a **unique
  profile page** and gets a **voice at the start of phase 2**.

Earthbux retains override authority (e.g. to revoke a claim from a fraudulent or
inactive rep).

## Page map (see structure.md for detail)

- `index.html` — discovery + voting entry (annulus, elections, propose/nominate).
- `cause.html` — the cause's rotation + live elections (phase 1 & 2 voting).
- `mission.html` — per-mission operational hub (budget, plan, progress, member
  channel); phases 3–5 live here. **Spawned** by the cause page on election.
- `en.html` — Earthbux News editorial/reporting layer, across missions.
- `profile.html` — identity + holdings for benefactor / org / beneficiary / admin.
- `admin.html` — internal data console.

## The cause-page phase blocks ("Middle Cause")

The center column of `cause.html` reads top-to-bottom as the mission's story; each
phase fills its block as the mission progresses. The spec below is the **target
content** per block (UI not yet built — documented here as the framework).

| Block | Header line | Body / sub-line |
|---|---|---|
| **P1** | `<Cause_name> Decision:` | `tiv_election_date` |
| **P2** | Initiative logo *(default: an acronym of the tiv title)* | `org_election_date` |
| **P3 · Budget** | nothing yet `*` | `credit_release_date` *(default: week 16 for now)* |
| **P4 · Credit** | `**` | — |
| **P5 · Resolution** | `***` | — |

Footnotes (the framework for the phases we haven't built):

- `*` The **budgeting phase** is where it gets interesting. Users investigate the
  price to do certain things — a game of *"How much does it cost?"*. This is when
  the annuli start to **spin faster**.
- `**` This is when the **commentary-based awards** are released, and benefactors
  can **convert their credits**.
- `***` **Success or failure.** Missions may take **many years** to reach
  resolution.

> Dates referenced above are derived from the mission anchor: `tiv_election_date`
> is the first day of the cause's active period (= `started_at`); `org_election_date`
> is its final day; `credit_release_date` defaults to week 16. See README §6.

---

## Loser carryover & the commitment fund

When `finalize_p1` elects a winner, the **losing initiatives are not discarded** —
they re-enter the cause's **next-cycle** election automatically:

- Each loser is **re-listed** under the cause's `cycle+1` mission (created on
  demand), status reset to `suggested`, so it competes again with momentum intact.
- Every backer's phase-1 commitment **carries forward at 90%** (`1 −
  COMMITMENT_FUND_SKIM`); the **10% skim** is booked to a single global
  `commitment_fund` ledger bucket (`transactions.bucket = 'commitment_fund'`).
- The **80%** locked behind a *winning* vote stays in the won mission's pool and is
  untouched by this path.
- Rates (`COMMITMENT_FUND_SKIM = 0.10`) are **placeholders** — tune later. The fund
  is a global bucket for now; reallocation rules are a future decision.

Implementation: `crud._carry_losers_forward`, called from `finalize_p1`. See README
§6 for the full vote/election algorithm.

---

## Withdrawals

- **Initiative status** is now just `suggested | active | resolved`. A losing tiv
  stays `suggested` (and rolls into next cycle); the elected tiv becomes `active`
  for the life of the mission and `resolved` at distribution. The phase a mission
  is in (1-5) is read from `mission.current_phase` + its winners, **not** the tiv
  status.
- **Phase-2 withdrawal (implemented):** during phase 2 — after the initiative is
  elected but before budgeting locks the pool — a benefactor may withdraw their
  phase-1 commitment **minus the send** (20% if they backed the winning tiv, 10%
  otherwise). Endpoint `POST /missions/{id}/p1/withdraw` → `crud.withdraw_p1`; the
  refund is booked to the `refund` ledger bucket and the send stays in the pool.
- **Phase-3 org-loss withdrawal (deferred — tune after phase 2):** once
  organizations are decided, a benefactor whose org **loses** should have their
  **80% immediately withdrawable**, but only after **acknowledging they don't trust
  the winning organization** (exact wording/flow TBD). This lives in phase 3 and is
  intentionally **not implemented yet** — it can be tuned once phase 2 settles.

## Admin mode

`profile.html` doubles as the admin surface: a staff account (`role` =
`employee`/`admin`) sees a **"Switch to admin mode"** toggle that re-renders the
profile page **as the admin data console** (the same staff-gated `/admin/query/*`
endpoints `admin.html` uses). The toggle is hidden for non-staff and every call is
server-gated, so it's safe to ship on the shared profile page.

---

## Open questions / to settle

- Exact guaranteed-to-pool rates (unclaimed vs claimed) **and** the loser-carryover
  skim / commitment-fund reallocation rates.
- Verification method specifics (domain, registration number, manual EN review).
- Where each discussion category renders at each phase (cause vs mission vs EN).
