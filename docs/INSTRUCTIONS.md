## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- (c) **Inconsistencies** 
- (d) **Not blocking** Acknowledge but only fix if trivial.


1. [ ] **Discussion edits**
I made numerous refinements to the discussion experience in the structure.

2. [ ] **Budgeting details**
I detailed the interface for budgeting too.

3. [ ] **main.html**
Various refinements to improve the user experience on main.html.

## CONVERSATION
- Without permission, only execute build sequence.
- Absorb amd modify backlog items and update structure as you see fit.
- note - s/s/s items can be suggested any time, but they can't be voted on until the budgeting opens.
- Until I make enough to hire security, I need to hide earthbux from corrupt organizations.
- Does calling an organization a "philanthropy" make sense?
- Need to start thinking about where the money lives.

- Kids accounts need a dedicated adult account to authorize any transactions.
Security rule: The first time an account signs in, they are told they can't vote in any org elections except the first (most recently electeed tiv) org election. - This prevents from creating accounts just to vote your org in.

## BACKLOG (for backlog management - ignore this section during build task)
*The single backlog. Absorbed `docs/backlog.md` + prior loose items on 2026-07-17.*
*Ordered by the current plan: **master the posting + newsfeed experience for phases
1–2 first**; everything from the end of phase 2 onward is **parked** until that
lands. Page specs live in `docs/structure.md`; the model in `README.md` §5.*

### ▶ NOW — posting & newsfeed (phases 1–2, the focus)
- [x] **§2 DISCUSSION EDITS · BUDGETING DETAIL · main.html (2026-08-12)** —
  build-seq §1, §2 and the EASY half of §3.
  - **§0 The error was mine, and it was the first thing fixed.** "My dialogue is
    deleting every time I try to link something." The box repaints as a whole
    and an `innerHTML` swap discards whatever is in an input, so linking wiped
    the post being written. Every repaint now captures title/body/row fields
    into the cell's draft, re-renders from it and restores the caret; each
    (category, phase, type) cell owns its draft, so leaving and returning finds
    the text intact. Three assertions guard it.
  - **§1 Research links itself.** A context/investigation/analysis post is about
    the mission you are reading, so nothing has to be picked: the mission rides
    on the payload and the composer says which links were made for you. Analysis
    also auto-links the elected initiative and philanthropy. Only reviews still
    require a link. The rails read **Linked Initiatives / Linked Organizations**
    in full, and research carries an *edit it on your profile →* link.
  - **§2 The type toggle moved into k**, beside the result, and now always shows
    every type the category has — the ones this stage has not opened are drawn
    but dead, with the reason on hover. The ladder a benefactor climbs is
    legible from any stage instead of appearing a tab at a time.
  - **§3 Budgeting is a costed LIST, not prose.** Toggling s/s/s swaps a row
    that REPLACES the title — service `|Job|hourly rate|days needed|`, supply
    `|Item|Supplier|Cost|`, support `|Item|` — **+ Add** appends it, and the
    area below prints the three tables across every budgeting post on the
    mission, each row approvable. No link rails, no target/open/reward/rating
    chips, no examples: a budget item is not judged, it is bought.
    - **New column, and it is the right call.** `posts.line_items` (JSON),
      migration `a1f6b3c92d47`, applies at server start — verified applying
      cleanly and round-tripping through `GET /posts`. An hourly rate that only
      exists inside prose cannot be totalled, and the mission page has to sum
      these to build a plan.
    - **The costing rule survives, derived instead of typed.**
      `post_config.estimates_from_line_items`: service = Σ days and
      Σ rate × days × **8h** (`HOURS_PER_DAY` — an assumption, named rather than
      inlined), supply = Σ cost, support = 0. `crud.create_post` fills the
      estimates from the rows and validates each row, so "a suggestion is costed
      or it is not a suggestion" still holds. Legacy budgeting posts render as
      one row from their title + estimates rather than vanishing.
  - **§4 main.html, the EASY three plus the rail.** "Next votes:" deleted —
    markup, renderer and every `.nextvotes*` rule; the hidden duplicate page
    toggle under the annulus deleted with the two `setMainMode` writes that fed
    it; the state toggle names the elections in the **plural** (a card naming
    ONE race stays singular); and the toggle now sits in a full-bleed row with a
    lit rail running from its right edge to the edge of the screen.
  - **§5 Two more from the cause backlog.** The header's phase chip became the
    ACTION — **[Vote]** *to elect an initiative / a philanthropy*, pointed at the
    Context table filtered to this cause — and the right-hand cards order by the
    mission's own anchor, newest first, so two simultaneous elected initiatives
    stop depending on array order.
  - **Not built, and why**: *phl vote onclick* and *OE voting UX* are the same
    mechanism — row selection and the vote bar — and rewriting the selection
    path without a test that drives a real vote would risk the only working
    voting surface. They are the next main.html pass, together. Also open: the
    philanthropy side of a budget thread (an org-authored budgeting post has no
    composer), and the two unwired rails.
  - **Verified**: `posts_box_check.js` extended to 82 assertions — the repaint
    regression, research's auto-links and missing requirement, the type toggle
    showing all three with two dead, budgeting's three titled tables and empty
    meta, the row editor adding/keeping/removing a row across a kind switch, and
    the stage-4 mission where budgeting is actually open. POSTS BOX CLEAN.
    `render_check` re-pointed at the new main.html toggle and clean on all five
    page/states; `date_audit` CONSISTENT; migration applied and read back.
- [x] **§1 THE DISCUSSION BOX (2026-08-12)**
  - **§0 Checks, before anything moved.**
  - **§1 One box replaces four systems.** The four-section accordion
    (2026-08-10), the three-band P3 box (2026-08-08), the dual panels
    (2026-08-02) and the per-phase checkbox threads (2026-08-01) are deleted —
    ~1,000 lines. Each was the same three jobs (explain the post type, take a
    post, show the best one) wired to a different idea of where you were. The
    matrix states both axes explicitly, so the three jobs are written once and
    all twelve cells get them. `renderTimeline`/`renderSections`/`_ctBody1-4`/
    `_ctThread`/`_ctComposer`/`renderP3Bands`/`_p3Band{A,B,C}`/`_bindP3`/
    `_p3Suggest`/`_p3Approve` and the `_CT_HOME` migration table are gone;
    `renderPostsBox` is the entry point.
  - **§2 The second drawing, in order.** k (results, notched onto its tab) · a–d
    (dated stages) · i (composer) · b (type selector) · h (about) · e–g
    (categories) · j (leading post + pager). The tabs sit BELOW h on purpose: h
    is about the post you are writing in i, and e–g switches what j shows under
    it. Detail written up in `docs/structure.md`.
  - **§3 The five link rails are three.** Linked tivs → `posts.tiv_id`, linked
    phls → `posts.org_id`, media → `posts.image_url`; each picker lists real
    entities and attaches a removable chip, and the required one (`*`) blocks the
    send. **Budget items and external links have no column on a post** — drawn,
    disabled, and labelled as such rather than faked. Jax: the links point at a
    specific entity, "I'm talking about THIS"; stub for now.
  - **§4 A cause runs two elections at once, and this page only knew about one.**
    "Phl consistency across pages": the philanthropy race was read off
    `_v2Mission` — the INITIATIVE-election mission, which never has a race — so
    cause.html showed no philanthropies while main.html showed Earthbux ahead of
    River Cleanup Collective on the same cause. Garbage Patch Analysis is
    **oce0**; the page was reading **oce2**. New `_v2OrgMission()` picks the
    selected mission if it has its own result, else the OLDEST open race (the
    same `_finalizingMission` rule main.html's OE card follows), else the newest
    elected one — and the selection re-reads it. Both pages now print the same
    two philanthropies.
  - **§5 A TDZ crash, caught by moving one declaration.** `_v2OrgMission` reads
    `_missionRefId`, which the async bootstrap reached before its `let` ran —
    "Cannot access '_missionRefId' before initialization", the same class of bug
    as mission.html's 2026-08-08 blank page. Declared with the rest of the page
    state instead.
  - **§6 Also cleared from the cause backlog**: the header moved above the
    annulus, "View initiatives →" deleted with **Vote** promoted into the left
    column's header (ME or OE, per the selected mission's race), the eyebrow
    renamed *Leading Philanthropies*, and the box titled **Discussion**.
    `#phase-recap-1` — an id deleted on 2026-08-10 — was still the scroll target
    of three handlers here and five links on main.html; all nine now point at
    `#pb`.
  - **Verified**: new `scripts/posts_box_check.js` (replacing
    `timeline_check.js`) drives all twelve cells in a headless DOM — tab keys
    a–d/e–g, one selection per row, the gray rules, one explanation per cell and
    three for budgeting, the notch tracking the stage and not the browsed tab,
    the five rails with two disabled, a pick→chip→unpick round trip, a shut
    composer that says why, and zero survivors of the four deleted systems —
    then loads oceans and asserts the philanthropy cards match
    `/candidacies?mission_id=oce0`. POSTS BOX CLEAN. `render_check` extended to
    the new selectors and clean on all five page/state combinations;
    `date_audit` still CONSISTENT.
  - **Left for Jax**: the two unwired rails (above), the rhs card ordering (same
    oldest-vs-newest rule), moving the cause suggestor off main.html, and the
    philanthropy-vocabulary rename outside this page.
- [x] **§8 LANDING + CONTEXT REFINEMENTS + CAUSE NAMING (2026-08-10)**
  - **§0 The OE annulus centre named the wrong race.**
    **"{cause} Confirmed for {mission start} Mission"**
- [x] **§7b BLANK PAGE FROM A STALE**
- [x] **§7 EVERY DATE, FROM ONE ANCHOR (2026-08-10)** — build-seq §1, "I'm
  trying to get all dates correct."
- [x] **§7c THE DOUBLE CORRECTION, UNDONE (2026-08-10)**
- [x] **§6 CAUSE PAGE — THE FOUR-SECTION TIMELINE (2026-08-10)**
  - **§1 Four sections, one open.**
  - **§5 Vote stats removed, leaderboard moved.**
- [x] **§5 CONTEXT PAGE DESIGN UPGRADES (2026-08-10)** — **§0 The date that belonged to a different race.**
  - **§4 The vote dialog is above the table keys.**
  - **§5 The leader is marked.**
- [x] **§6 P2 IS REAL: PHASE-2 MONEY, THE CAUSE-VOTE WINDOW, LANDING (2026-08-08)**
  - **§1 One Commit for the organization election.**
  - **§2 The cause vote has dates and display conditions.**
  - **§4 Doc notation.** `orange` <red> [purple]
- [x] **§1 STRUCTURE UPDATE BUILT (2026-08-05)**
**table state 2 = active missions**,- [x] **§5 CAUSE VOTE BACKEND**- **§4 P2 shows leaders and winners.**- **§2 Propose moved into the table**- **§3 Orgs → Mission** on the side card.
- [x] **§4 CARRYOVER + CAUSE BALLOT + LANDING (2026-08-06)**
  - **§1 EBX vote-to-vote carryover.** - *keep here* and *roll to the next election of this cause*. `GET/PUT /missions/{id}/p1/carryover`
  - **§2 New cause vote.** a **funding runway** chart: `weeks = pooled $ ÷ (members × 10 EBX × 10¢)`
- [x] **§3 ME / OE (2026-08-06)**
  - **§0d — annulus centre** 
  - **§1 — ME / OE.** **Mission Election**-**budgeting card** 
  - **§2 — cause logic folded into the README** (§4 *ME and OE*, §4)
  - **§3 — glow logic**
  - **§4 — registered organizations**
  - **Accounts console**`GET /admin/accounts` + `DELETE /admin/accounts/{id}`*Accounts · remove*
- [x] **§2 CARDS + THE REST OF main.html (2026-08-05)**
  - **Side cards**
  - **Top card** - **Upcoming Causes**
  - **Annulus** — Rays
    (`localStorage.ebx_purchased_ebx`).
- [x] **§0a Oceans p1-commit 500 FIXED (2026-08-05)**
- [x] **THE SPLIT (2026-08-02)** — **voting happens on `main.html`, discussing happens on `cause.html`.** This is the organizing rule the two pages below implement; every future surface decision should follow it.
- [x] **`cause.html` = discussion hub** - **top 3** - **Gray rules**
  **Research** 
  **review**
- [x] **`main.html` = voting hub** — **Commit** button (`PUT /missions/{id}/p1/votes` normalized to shares + `POST .../p1/commit`, grouped per mission). **My vote** and **Total EBX** headers are **click-sortable** (▲/▼ indicator). Every initiative row carries a **Mission →** link. Cards' primary button is now **Discuss** (→ cause page), not Vote. **Convert** + **Donate** added to the expanded row (framed — the credit lifecycle is still parked). Bottom row of the 7 causes gained **Help** (left → `index.html`) and **Commit** (right).

### Cause framework (absorbed from `jax notes 2.txt`, 2026-07-31)
- [ ] Causes must be ubiquitously essential human experiences, corruption-resistant ("thick skin" — resources allocated to resilience), with a prospect of change.
- [ ] **Cause replacement rule** — if the SAME cause is voted on by >50% of people for the whole 6-week period, it replaces the cause that would have come next.
- [x] Annulus: main glowy marker pointing; colored sectors ray outwards. — was
  already BUILT 2026-08-05 (§2): `.st-now` (the glowing arrowhead aimed into the
  wheel) and the per-cause `rayGroup` in `resources/js/ebx_shared.js`, which
  `_update()` brightens for the active + upcoming cause. Verified rendering
  2026-08-10 (§5); the line was stale, nothing was rebuilt.

### Model notes absorbed from CONVERSATION (2026-08-06) — documented, not built
- [ ] **Donation split** — a weekly contribution is 100% a donation and lands in
  three places: researchers (**$2** at $20/wk), Earthbux (**$0–6**), the mission
  (**$6–18**). The last two flex against each other — money directed at an org
  election or given under a *specified-must-donate* instruction ends up in **a**
  mission, not necessarily the one it was cast in. Written up in README §5
  *Where a donation goes*. No intake, no split at the door, no researcher payout.
- [ ] **First-sign-in voting rule** — on a new account's first sign-in, tell them
  they can't vote in any organization election except the **first one** (the most
  recently elected tiv's). This is an anti-sockpuppet gate: a fresh account
  can't be spun up to swing an org race that is already half-run. Needs
  `BenefactorAccount.created_at` compared against each mission's phase-2 window
  in `cast_p2`, plus the first-run notice on the client.

### Bugs (clear these for a clean phase-1/2 experience)
- [x] **P2 finalization was a week early everywhere** — FIXED 2026-08-09.
  Jax's rule: *missions in p2 remain in p2 until the end of their ACTIVE CAUSE
  WEEK.* The trap is a misleading name — `EBX.Cycle.nextDecisionDate(idx)`
  returns the **start** of that cause's next active week, not the decision.
  Today (Aug 9, week 14) Atmosphere is active and its `nextDecisionDate` is
  **Aug 4**, already past, because that is when its week opened. So:
  Atmosphere's week is Aug 4 → Aug 11 and Carbon Capture Expansion finalizes
  **Aug 11**; Oceans' is Aug 11 → Aug 18 and Garbage Patch Analysis finalizes
  **Aug 18** — not Aug 11 alongside it, which was the worry, and which any
  surface reading `nextDecisionDate` as "the decision" would have printed.
  One named helper `_phlFinalizeDate(causeIndex)` = `nextDecisionDate + 1 week`
  now owns it, and the OE card, the p2 overview and the vote-bar header all go
  through it. Verified against all seven causes.
  *Open:* `nextDecisionDate` keeps its misleading name and is read directly in
  ~10 other places. Renaming it (`causeWeekStart`?) and auditing those is its
  own pass.
- [x] **atm0 is elected when it should not be.** `winning_org_id = org-001`,
  `current_phase = budget` — but its philanthropy election does not finalize
  until Aug 11. While it looks closed there is only ONE open race for
  atmosphere, so the ME and OE cards collapse onto the same mission and OE
  reads Methane Leak Detection Grid instead of Carbon Capture Expansion.
  **Fix: run `python ../scripts/unelect_atm0.py --apply` from `backend/`.**
  Cannot be applied from the agent sandbox — the mount does not support the
  file locking SQLite needs and every write fails at commit.
  — RESOLVED: verified against the live db 2026-08-10 (§5). `atm0` now reads
  `winning_org_id = None`, `current_phase = initiative`; atm0 and atm1 are both
  open philanthropy races, so `_finalizingMission` (atm0 · Carbon Capture
  Expansion) and `_orgMissionsFor().newest` (atm1 · Methane Leak Detection Grid)
  resolve to different missions and the ME/OE cards no longer collapse. The
  script appears to have been run (`earthbucks.db.bak_premigrate`, Aug 10 09:41).
- [x] Org election recap showed "Organization (record missing)" as winner (upcoming cause) — legacy `init.winning_org` field; now resolved from `mission.winning_org_id` (2026-07-31).
- [x] `cause.html` p2-area date rendered a full cause-cycle (7 wks) late — FIXED 2026-08-01 (build-seq §0b). The org decision falls ON the cause's next decision day (org close = its mission's p1 + 7wk, and the cause recurs every 7wk), so the old `decision + 7wk` double-counted the cycle: hpr showed Nov 3 / atm Sep 22 instead of Sep 15 / Aug 4 (hmr's Sep 8 was coincidentally right). Org pill now = the annulus-center date. NOTE: the `missionPhaseDates` (+8wk) path for a SELECTED past mission still disagrees with the weekly cadence by 1 wk — fold into the back-half phase-enum redesign.
- [x] `main.html` profile badge wrapped to a second topbar line — FIXED 2026-08-01 (build-seq §0d): the topbar grid override said `auto 1fr` (2 columns) for 3 children (brand · pagetag · badge); now `auto auto 1fr`.
- [x] `cause.html` rhs top card looked like the tiv had already won — FIXED
  2026-08-08 (§7 §0b). The card names the top-weighted CANDIDATE; its eyebrow
  and badge now read **leading** ("Phase 1 · leading initiative" ·
  "Leading · election open"). The phase-1 *header* was already correct
  (`{cause.name} {cycle}: Initiative Election`) — the card was the problem.
- [x] `mission.html` rendered nothing at all on any mission that had a
  candidacy — FIXED 2026-08-08 (§7 §0a): `let _openOrgId` was declared below the
  `render()` that reads it (TDZ ReferenceError on first paint).
- [x] Oceans `cause.html`: "Exception in ASGI application" when committing a p1 vote —
  **FIXED 2026-08-05 (build-seq §0a)**, reproduced and root-caused. Neither propose
  dialog sends a `mission_id`, so every user-proposed initiative was stored ORPHANED
  (`mission_id` NULL) — invisible to mission-scoped queries. The guard in
  `replace_p1_shares` read `Initiative.mission_id != mission_id`, which in SQL is
  NULL (never TRUE) for an orphan, so the orphan passed validation, was inserted
  under a second mission, and violated `UNIQUE(ben_id, tiv_id)` → unhandled
  `IntegrityError` → 500. Oceans hit it because ben #2 held an orphan vote row on
  *Coastal City Water Quality Monitoring Network* under `oce0` while voting in `oce1`.
  Four-part fix: (a) `crud.create_tiv` adopts the cause's open phase-1 mission when
  none is given; (b) the guard now matches ids explicitly, so NULL and unknown ids
  are both rejected; (c) `crud.adopt_orphan_tivs` repairs existing orphans (and
  re-points + renormalizes their vote rows) from a startup hook in `main.py`;
  (d) the router maps `IntegrityError` → 400 with a readable message so a bad slate
  can never be a 500 again. Verified against a copy of the live db.

### ▶ NEXT — cause / election UI (phases 1–2)
- [ ] **Org election experience redesign** (jax notes 2: "it's ugly"; build-seq §3: "p2 needs a strong redesign").
- ◑ **Active cause / active mission top card** has many errors (jax notes 2) — audit every stat on the main.html top card.
  Two found and fixed 2026-08-10 (§5): the org-election close date named one
  race and dated another (`_orgCloseDate`), and "d left" disagreed with the date
  printed beside it because `cycleStart` is noon (`_daysLeft` counts calendar
  days now). The remaining stats on the card — votes, pool, leader %, my
  commitment — read 0 across the board on the current db, so they have not been
  exercised against real numbers yet. Re-audit once a race has votes in it.
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
- [ ] **Self-serve password reset** — needs a mail transport: emailed single-use
  token, expiry, a redemption page, rate limiting. Staff can issue a temporary
  password today (§0d, 2026-08-08); this is the real flow.
- [ ] Admin page off `profile.html` — a link to `admin.html` from `profile.html` instead.
- [ ] Admin event log (`vote_events`: CAST/UPDATE/REMOVE) + duplicate/invalid-vote flags + CSV export.
- [ ] Mission Simulator — input votes, commits, budget suggestions/resolutions; step forward in time.
- [ ] `is_test` column + `cyclestart` config endpoint for simulations.
- [ ] v2-compatible seeder (pilot/seed are stale against the current schema).
- [ ] Working-tree corruption: avoid concurrent writers (mount sync vs. `uvicorn --reload`); commit often.
- [ ] Apache stack (Kafka/Flink/Airflow/Cassandra) — future.
