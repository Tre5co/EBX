## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- Right now in cause.html: org decisions: Human rights: sep 8 (correct) human progress: nov 3 (wrong) atmosphere: sep 22 (wrong). The dates are all correct on main.html.
- (c) **Inconsistencies**
- (d) **Not blocking** Acknowledge but only fix if trivial.
- Main.html profile batch has spilled onto the second line even when my screen is big enough. This is incorrect.

### 1. Mission.html
- Each initiative has a unique mission page. The design is in in jax notes 2
### 2. index.html
- We're going to extreme simplify. Restructure according to jax notes 2
### 3. Cause.html
- Resolve the issue from blockers.
- There is a bug I believe is caused by a tie as described in jax notes 2. Analyze it but do not change anything.
- There are only 3 phases. P1 and P2 can be unchanged for now (although p2 needs a strong resedign)
- Each phase area splits into a discussion thread, which can be navigated by checkboxing which types of posts you want to see. Users can page through posts, and sort by relevance, popularity, or recency. 
### 4. Main.html
- Remove all post dialog from main.html. The expanded rows only contain the description, and the ststus (current votes, age, if_active, winning case, posts that WON (if applicable), org running it, key dates.). Just frame this out for now. We will execute it later. 
## CONVERSATION
- Absorb amd modify backlog items as you see fit.

## BACKLOG (for backlog management - ignore this section during build task)
*The single backlog. Absorbed `docs/backlog.md` + prior loose items on 2026-07-17.*
*Ordered by the current plan: **master the posting + newsfeed experience for phases
1–2 first**; everything from the end of phase 2 onward is **parked** until that
lands. Page specs live in `docs/structure.md`; the model in `README.md` §5.*

### ▶ NOW — posting & newsfeed (phases 1–2, the focus)
- [x] **Page roles** — REVISED 2026-08-01 (build-seq §2): `index.html` = **Landing, extreme-simplified** per jax notes 2 (founding blurb + "The System — 3 Phases" with p1→main / p2→cause / p3→mission links). The 2026-07-31 all-posts stream was REMOVED from index; the newsfeed lives on Context/Mission surfaces (this also resolves the index-vs-`en.html` overlap: index carries no feed). `main.html` = **Context** (topbar tag). EBX corner mark → `main.html` everywhere.
- [x] **Mission page rebuilt** — 2026-08-01 (build-seq §1), jax-notes-2 layout: a mission toggle + initiative search · b profile/membership status · c 3-category post stream (budgeting / mission_support / review tabs) · d dated progress log · e 3-phase circle (future 3D globe) · f pool (in-pool / committed / withdrawn) · g name + core info. Claim/register agreement gate kept verbatim; competing-orgs card kept below the grid (slot TBD).
- [x] **Cause phase areas** — 2026-08-01 (build-seq §3): recap stack collapsed **5 → 3 phases** (back half = one "Budgeting & Resolution" area, S/S/S folded in; annulus center now reads "Phase 3 · Budgeting & Resolution" for enum 3/4/5). Each active phase area splits into a **discussion thread**: checkbox post-type filters (P1 context·case / P2 analysis·investigation·evaluation / P3 service·supply·support·evaluation), sort by relevance / popularity / recency, 5-per-page pager; read-only, click-through → Context (P1/P2) or Mission (P3).
- [x] **Main.html expanded rows** — 2026-08-01 (build-seq §4): post dialog REMOVED from main.html. Expanded row = description + STATUS frame (current votes, age, if_active, winning case, posts that WON, org running it, key dates) — winning-case/winning-posts fields are framed "—" until the per-row discussion wiring lands. Execution later.
- [ ] **Five surfaces wired** (per `structure.md`): ✅ Landing `index.html` (all) · ◑ Context `main.html` (tiv/org row) · Election `cause.html` (top-few, view-only) · Mission `mission.html` (full convo, P3+) · Profile `profile.html` (user activity).
- [ ] **Origination** — new discussions start on the **Context** or **Mission** page only. Replies allowed from **Landing, Profile, Context, Mission**; a reply/comment opens **Context** (P1/P2) or **Mission** (P3+) by phase.
- [ ] **Context table** — expanded columns filter posts by **tiv (or org)**, not just cause; each row owns its discussion.
- [ ] **In-mission row type** — initiatives/orgs currently in a mission get a distinct context-table row: mission id, current phase, start date, current votes; links to Mission or Election page.
- [ ] **Post-type location** — org reviews/investigations/testimonials postable on **any org anytime**; analysis/comparisons/justifications only **inside an active mission**.
- [ ] **P1 recap** shows only two categories — **context** and **case**.
- [ ] **Resolutions area links to the Mission page.**
- [ ] Post composer + reactions + **Reply**; **category → type** picker; reactions are **per type** from `backend/app/post_config.py` (Budgeting = upvote-only · Mission Support = Helpful/Neutral/Harmful · Review = Fair/Unfair); routing by phase & scope. *(Landing reply composer shipped 2026-07-31; full composer + per-type reaction buttons still open.)*
- [ ] Post metadata everywhere: **date** + the **initiative/org it regards**; **cause-colored**.
- [x] Comments = posts with `parent_id` — backend enforced; Landing renders replies inside their parent (2026-07-31).
- [ ] **Choices table** — toggle **phase1/phase2** (not initiatives/orgs). Show p1 choices in phase 1; at the election, clear the user's choices and make the winning initiative the p2 row label.
- [ ] Profile: choices table toggles a discussion area; when the user has no posts on a mission, show that mission's **leading posts**. Mission-member pages carry a deeper messageboard/console **separate from posts**.
- [ ] Post rewards: EBX for most-helpful (Context@P1, Analysis@P2, Evaluation@P3); **Case → upgraded org membership, no cash**. Visibility tied to donation size.
- [ ] EN feed layout + parallel progress reports; resolve Landing (`index.html`) all-posts vs. `en.html` curated feed overlap.
- [x] Post routing/limits enforced server-side in `create_post` — two-tier (category → type) taxonomy from `backend/app/post_config.py`; membership gate, one post per type per mission (replies exempt), per-type reactions. Shipped 2026-07-19 (migration `a1b2c3d4e5f6`, **applied to the live db 2026-07-31**; backup `earthbucks.db.bak_jul31`).
- [ ] Image attachments on posts (needed soon).

### Cause framework (absorbed from `jax notes 2.txt`, 2026-07-31)
- [ ] Causes must be ubiquitously essential human experiences, corruption-resistant ("thick skin" — resources allocated to resilience), with a prospect of change.
- [ ] **Cause replacement rule** — if the SAME cause is voted on by >50% of people for the whole 6-week period, it replaces the cause that would have come next.
- [ ] Annulus: main glowy marker pointing; colored sectors ray outwards.

### Bugs (clear these for a clean phase-1/2 experience)
- [x] Org election recap showed "Organization (record missing)" as winner (upcoming cause) — legacy `init.winning_org` field; now resolved from `mission.winning_org_id` (2026-07-31).
- [x] `cause.html` p2-area date rendered a full cause-cycle (7 wks) late — FIXED 2026-08-01 (build-seq §0b). The org decision falls ON the cause's next decision day (org close = its mission's p1 + 7wk, and the cause recurs every 7wk), so the old `decision + 7wk` double-counted the cycle: hpr showed Nov 3 / atm Sep 22 instead of Sep 15 / Aug 4 (hmr's Sep 8 was coincidentally right). Org pill now = the annulus-center date. NOTE: the `missionPhaseDates` (+8wk) path for a SELECTED past mission still disagrees with the weekly cadence by 1 wk — fold into the back-half phase-enum redesign.
- [x] `main.html` profile badge wrapped to a second topbar line — FIXED 2026-08-01 (build-seq §0d): the topbar grid override said `auto 1fr` (2 columns) for 3 children (brand · pagetag · badge); now `auto auto 1fr`.
- [ ] `cause.html` phase header shows "<leading tiv> phase 1 …" instead of "<cause_name cycle_num> phase 1 …". In P1 no tiv has won, but the rhs top card looks like the tiv already won — it should read **leading**.
- [ ] Oceans `cause.html`: "Exception in ASGI application" when committing a p1 vote.

### ▶ NEXT — cause / election UI (phases 1–2)
- [ ] **Org election experience redesign** (jax notes 2: "it's ugly"; build-seq §3: "p2 needs a strong redesign").
- [ ] **Active cause / active mission top card** has many errors (jax notes 2) — audit every stat on the main.html top card.
- [ ] **7-causes bottom row**: space left + right — add a **Help** link (→ `index.html`) on the left; the right-side link is still undecided (jax notes 2 cuts off mid-sentence — ask Jax).
- [ ] Election-card nav buttons: View (jump to table row) · Explore (cause page) · Vote.
- [ ] Move overview into the table; clicking a row expands it and filters discussion.
- [ ] Pool metrics: "guaranteed pool" vs "committed pool".
- [ ] Vote visualization (count + relative commit size per vote).
- [ ] Start dates on every mission card; show future dates after the cause shift.
- [ ] "Log in to vote" gating on the cause page (no phantom voting when signed out).
- [ ] Better active/upcoming indicator: **horizontal, not diagonal** — a 2-row box between the upcoming and active causes naming both.
- [ ] Move show & register/propose into the top "Active mission"/"Active cause" bar (adjust CSS).
- [ ] Various locations need black-on-white Times New Roman.
- [ ] Propose / nominate dialogs shared between context page and cause page.

### Elections / voting model
- [ ] **Tie-break rule** (from the hpr0 analysis, 2026-08-01, build-seq §3 — analyzed, nothing changed): a p1 tie is currently broken by *vote-row insertion order* (`p1_tally` sorts stably; `finalize_p1` takes `entries[0]`). Jax's 5/5 split on GEAG vs Solar Grids → GEAG won only because its vote row (id 26) predates Solar's. The "4.5 committed" is CORRECT behavior, not corruption: the losing tiv rolled to hpr1 via `_carry_losers_forward` with the 10% commitment-fund skim (5 EBX → 4.5 EBX, uncommitted); "total fund 5" = only the winner's 5 EBX remains in hpr0. Decide an explicit tie-break (earliest commit? most voters? sudden-death week?).
- [ ] **Skim ledger rounding bug** (same analysis): `_carry_losers_forward` books the skim as `int(round(skim))` — a 0.5-EBX skim logs a **0-EBX** transaction (tx #322) while the vote row really lost 0.5. Commitment fund undercounts on small commitments; store fractional EBX or round the vote row to match the ledger.
- [ ] Winner-backer perk: cheaper bonus votes in phase 2 — same doubling, but the 1st extra vote costs **$2.50**, so a winner-backer's 3rd extra vote = everyone else's 1st.
- [ ] Negative/block (`harmful`) org votes — schema exists; UI deferred (reputationally sensitive).
- [ ] Beneficiary voice surface at the **start of phase 2**.

### ▶ Proposed model change — collapse the back-half phase enum
- [ ] Redesign so **budget → release = resolutions**: fold `current_phase` values `budget · credit · resolution` into a single `resolutions` phase (keep `pre · initiative` for phases 1–2). Touches `scheduler.py`, `models.py`, the phase map, and any UI reading `current_phase`. Modeled in README §3.

---
## ⏸ PARKED — end of phase 2 onward (do not build until the posting focus lands)

### Phase 2 / organizations (backend)
- [ ] Org claim flow wired to backend (authority transfer + acceptance record).
- [ ] Duplicate-org detection on nominate (fuzzy name match + "did you mean?").
- [ ] Guaranteed-to-pool rate: set unclaimed rate, bump on claim.
- [ ] EN verification queue (one org/week) + revoke-authority control.

### Resolutions (phase 3: budget → release → resolve)
- [ ] **S/S/S vs. context** — reconcile the parked inconsistency: Suggestions is its own post category, *not* a stance on context ("S/S/S is not context"). See README §5 flag.
- [ ] Mission gantt chart / annulus ring widget (deadlines, 7–12 steps).
- [ ] Tune step guaranteed/potential pool ratios + early-resolution bonus size.
- [ ] Tune `resolution_value_bump` and its relation to the global coin value.
- [ ] Suggestion → approval threshold (how many helpful reacts elevate a suggestion to org-resolvable).
- [ ] Progress reports (org report vs. EN parallel report, benefactor-moderated); mission member communication channel.

### Money / credit / donations
- [ ] Benefactor running tally of 3 categories: **wallet value** (across all credit coins), **money donated** (each donation hashed with its send-time value; tax-deductible), **spent by Earthbux** (money consumed).
- [ ] EBX-coin holding actions — a. **spend** (a mission spends its allocation; split between org + Earthbux; per-benefactor + combined mission-page receipts), b. **convert** (passed along), c. **withdraw** (must sacrifice value).
- [ ] Loser-vote choice: benefactors set what % of a losing tiv commitment is sent to the winning tiv vs. rolled to the cause's next p1; changeable until end of p2 (so they can react to the winning tiv).
- [ ] The ledger will be **public**.
- [ ] Resolve the transactional-credit decision framework (README §5): targets, availability state machine, routing precedence, ledger/retarget type, abuse caps.
- [ ] Credit lifecycle (generic → cause → mission → org → live), coin value parameters; exchange + donation/tax-deductibility flow; EN $100 pool threshold.

### Creditcoin front/back + 3D earth (born on `mission.html`)
- [ ] Coin card UI: front = value, initiative, org, election info, key dates; flip to back.
- [ ] Back = 3D earth (three.js), rotate-to-location for: user home, mission location(s), org location(s).
- [ ] Schema: `location_type` + coordinates on missions (site / region / distributed / global); home location on benefactors; location(s) on orgs.
- [ ] Globe rendering per location-type (pin vs. shaded region vs. multi-pin).

### Profiles
- [ ] Benefactor profile buildout around mission-memberships + credit-coin holdings per mission.
- [ ] Organization profile (initiative coins, tasklist, annulus 4, memberships).
- [ ] Beneficiary profile page (unique surface; voice at phase-2 start).
- [ ] Credit-badge colorization perk (participation threshold $10; `vvv` flag).
- [ ] Profile ring sticky to the rhs with badge in the corner (design on backburner).

### Accounts / kids (12–17)
- [ ] Birthdate (or age bracket) on `BenefactorAccount` + guardian link (parent account or verified email).
- [ ] Parental-approval flow gating every money-in action (add EBX, buy votes); voice (vote/post) ungated.
- [ ] Approval UX: per-transaction vs. allowance ("approve up to N EBX/month").
- [ ] Legal review: COPPA/GDPR-K, minimum age 12, regional definitions of minor.

---
## Infra / admin / testing
- [ ] Admin page off `profile.html` — a link to `admin.html` from `profile.html` instead.
- [ ] Admin event log (`vote_events`: CAST/UPDATE/REMOVE) + duplicate/invalid-vote flags + CSV export.
- [ ] Mission Simulator — input votes, commits, budget suggestions/resolutions; step forward in time.
- [ ] `is_test` column + `cyclestart` config endpoint for simulations.
- [ ] v2-compatible seeder (pilot/seed are stale against the current schema).
- [ ] Working-tree corruption: avoid concurrent writers (mount sync vs. `uvicorn --reload`); commit often.
- [ ] Apache stack (Kafka/Flink/Airflow/Cassandra) — future.

## Founding
- [ ] First 100 `BenefactorAccount` signups receive 49 EBX automatically (id < 100).
