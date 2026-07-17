## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- (c) **Inconsistencies**
- (d) **Not blocking** Acknowledge but do not attempt to fix yet.

## CONVERSATION
Hello.
We need to work out all this posting chaos because it's driving me insane.
- No writing-in from the cause page. Posts here are view-only. 

- As soon as the initiative is elected, people can start suggesting budget items. 
Table expanded columns need to be filtered by tiv (or by org). Currently its just filtered by cause.
Add helpful, hurtful, or neutral to these posts and option to reply, which takes us to the landing page discussion threads, where replies are displayed inside the posts. Landing page design pending.
Comments are just posts with a parent post.

Landing- All posts -> Stays on landing, users can continue discussion threads
home table- tiv-filtered -> onclick leads to landing
phase areas - cause-filtered -> onclick leads to home table expanded row
profile- user-filtered -> onclick leads to cause page

On the profile page ui, the choices table toggles the discussion area. If a user hasn't made any posts about that mission, display the leading posts from that mission.

Images - users should be able to attach images with their post - backlog this step but we will need it soon.

a. Posts EVERYWHERE need to display the date when they were posted and the initiative/organization which they regard, they should be colored based on what cause they are.

Refined model: it's the best context (cause-specific) post which wins the ebx reward from the p1 postvotes, and the best analysis (initiative-specific) which gets the second reward, who wins the p2 postvotes. The best evaluation/investigation wins it in p3. This changes the timings of some of the releases.

The best case gets an upgraded membership with their organization which includes privelidges like (I'm spitballing) veto rights, communication lines, early information from earthbux, etc. No cash reward for a case.

## BACKLOG (for backlog management - ignore this section during build task)
*The single backlog. Absorbed `docs/backlog.md` + prior loose items on 2026-07-17.*
*Ordered by the current plan: **master the posting + newsfeed experience for phases
1–2 first**; everything from the end of phase 2 onward is **parked** until that
lands. Page specs live in `docs/structure.md`; the model in `README.md` §5.*

### ▶ NOW — posting & newsfeed (phases 1–2, the focus)
- [ ] Landing/newsfeed (`main.html`): all-posts stream + discussion threads; replies render *inside* the parent post; this is the write surface (cause page is view-only).
- [ ] Post composer + reactions **Helpful / Neutral / Harmful** + **Reply**; category routing by phase & scope (Context/Case → P1; Analysis/Suggestion/Org-review → P2; Evaluation → P3).
- [ ] Four filtered post surfaces wired: landing (all) · context-page table (tiv/org) · cause page (cause, view-only) · profile (user). Click-throughs per `structure.md`.
- [ ] Post metadata everywhere: **date** + the **initiative/org it regards**; **cause-colored**.
- [ ] Comments = posts with `parent_post_id`.
- [ ] **Choices table** — toggle **phase1/phase2** (not initiatives/orgs). Show the p1 election choices in phase 1; at the election, clear the user's choices and make the winning initiative the p2 row label.
- [ ] Context-page table: expanded columns filter by **tiv (or org)**, not just cause.
- [ ] Profile: choices table toggles a discussion area; when the user has no posts on a mission, show that mission's **leading posts**.
- [ ] Post rewards: EBX for most-helpful (Context@P1, Analysis@P2, Evaluation@P3); **Case → upgraded org membership, no cash**. Visibility tied to donation size.
- [ ] Rename "home" → **context page** across nav/copy.
- [ ] EN feed layout + parallel progress reports; resolve `main.html`/`en.html` feed overlap.
- [ ] Post category routing enforced server-side in `create_post` (lanes per README §5).
- [ ] Image attachments on posts (needed soon).

### Bugs (clear these for a clean phase-1/2 experience)
- [ ] `cause.html` p2-area date renders ~6 weeks late; should equal the annulus-center date (correct) and the active-phase-corner date.
- [ ] `cause.html` phase header shows "<leading tiv> phase 1 …" instead of "<cause_name cycle_num> phase 1 …". In P1 no tiv has won, but the rhs top card looks like the tiv already won — it should read **leading**.
- [ ] Oceans `cause.html`: "Exception in ASGI application" when committing a p1 vote.

### ▶ NEXT — cause / election UI (phases 1–2)
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
