## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- (c) **Inconsistencies** 
- (d) **Not blocking** Acknowledge but only fix if trivial.


1. [ ] **Landing + context refinements + cause work** Structure.html has been refined through landing and context, and partially into discussion. Build.

## CONVERSATION
- **PHL addition from cause.html** Users need to be able to suggest organizations even before the initiative has been decided. In this case, they do not need to be associated with any particular initiative or cause. This is so they can tailor their page depending on how they want to fit into our structure, without being forced to make commitments they don't yet understand. There will be links elsewhere to register/nominate an org. These will take you to profile page, but when nominating for a mission currently in OE, the whole experience stays in main.html.

- Switching the 2 annuli on cause/mission? The mission one we just created fits better on cause. The cause on fits better on misison. 

- Without permission, only execute build sequence.
- Absorb amd modify backlog items and update structure as you see fit.
- Need to start thinking about where the money lives.

- From now on cau means cause
- While I'm the only person voting, Earthbux will be the winning phl
- Kids accounts need a dedicated adult account to authorize any transactions.

Security rule: The first time an account signs in, they are told they can't vote in any org elections except the first (most recently electeed tiv) org election. - This prevents from creating accounts just to vote your org in.

## BACKLOG (for backlog management - ignore this section during build task)
*The single backlog. Absorbed `docs/backlog.md` + prior loose items on 2026-07-17.*
*Ordered by the current plan: **master the posting + newsfeed experience for phases
1–2 first**; everything from the end of phase 2 onward is **parked** until that
lands. Page specs live in `docs/structure.md`; the model in `README.md` §5.*

### ▶ NOW — posting & newsfeed (phases 1–2, the focus)
- [x] **§8 LANDING + CONTEXT REFINEMENTS + CAUSE NAMING (2026-08-10)** — build-seq §1.
  - **§0 The OE annulus centre named the wrong race.** Listed twice in
    structure ("still says methane leak detection grid" + the "New helpful
    rule"). It read `_electingMission` — the NEWEST open philanthropy election —
    where the rule is the **UPCOMING (oldest)** one, the race a benefactor can
    still move. Same newest/oldest mix-up the OE top card was corrected for on
    2026-08-09; now `_finalizingMission`, and it reads **Carbon Capture
    Expansion · Aug 11**. Its date came from `voteCloseDate(nextIdx)` — the NEXT
    cause's week-start under the ACTIVE cause's mission — and now comes from
    `_orgCloseDate` on the race it names. The ME centre likewise now dates the
    election it names (`_nextInitiativeElection`), not a cause week.
    Its label reads **Philanthropy election** (was "Organization election").
  - **§1 Landing rebuilt to the new §1c/§1d/§1e.**
    - **§1c** is now "Bringing publicity to philanthropy, / Enabling research
      based donations", over "Lower transparency ⇒ Lower efficiency / Mission
      pool consumed by Earthbux". The five-step scale is unchanged but its axis
      is **relabelled by COST** — "lowest cost → highest cost" rather than
      "most/least transparency" — because cost is the quantity the runway chart
      under it actually spends.
    - **§1d** now owns "The system", which moved out of §1c, gained the
      mission-length line and a **fourth row** (*Win Research Grants → Grow your
      credit*), and lost the "Benefactors…" preamble on each row. Row 2 links to
      `main.html?state=oe`, since committing to a philanthropy is a Context-page
      action. The grant line and the dime moved under it, and the runway note
      now states Jax's sentence — "Donating is currently funding **$1 per week**
      per active community member" — followed by the divisor it comes from
      (pool ÷ weekly cost) with the **active member count named**.
    - **§1e** is new: *The causes*. The seven seeded causes render as coloured
      chips from `/causes` — the section claims "I seeded this system with the 7
      causes", and showing them makes that checkable — plus the
      6-successive-votes rule and a link to `#cause-change`.
  - **§2 cause.html section names say what OPENS.** "Cause opened / Mission
    started / Philanthropy elected" named past events, which reads oddly on the
    three sections still ahead of you. Now:
    **"{cause} Confirmed for {mission start} Mission"** · **"Initiative Election
    Opens"** · **"Organization Election Opens"** · **"Budgeting Opens"**.
    §1's heading interpolates, so it carries a `nameFor` fn. Per structure
    ("Display T-14 wk until election actually running") §1's rail date is the
    **window opening as a point**, not the range — `range1` is still carried, so
    switching to a range once a live cause election exists is one condition.
  - **§3 Table vote-dialog columns, both states.**
    - **ME**: starred | **My commitment** | Initiative | Total EBX | Cause |
      Vote. "My vote" renamed to what it is; Cause moved right of the money so
      the two numbers sit together.
    - **OE**: starred | **My commitment** | Initiative | **Total pool** |
      **Week 0** | Vote. Drops Mission id, Cause, Phase and the Links column —
      four things a benefactor is not deciding between in a philanthropy
      election (the cause survives as a subtitle under the initiative; mission
      id and links live in the expanded row). **Week 0** is the mission's own
      anchor from `EBX.Cycle.missionDates`, not `started_at`. New
      `window._myP2For`. Where a philanthropy is already elected the Vote cell
      **names the winner** instead of offering a vote on a closed race.
  - **A stale check, found and fixed.** `render_check.js` had asserted
    `.ld-dime__viz svg` since it was written — an element that has never
    existed (the id is `#ld-dime-viz`, the class `.ld-dime`). It was the
    "pre-existing miss" reported as untouched in §5 and §6. Corrected: it now
    asserts `#ld-dime-viz svg` and finds **10 coins**. The suite is at **zero
    real failures** — the 5 remaining lines are the blocked Google-Fonts CDN.
  - **Verified**: render check clean on all five page/state combinations,
    `date_audit.js` DATE MODEL CONSISTENT with both fixed points, and
    `timeline_check.js` ACCORDION CLEAN.
  - **Not built, still open in structure** (outside this pass): the
    Philanthropy-vocabulary rename, "Remove old page toggle" below the annulus,
    the roll-to-next-mission slider, phl commit finalization, and the cause-page
    backlog (missing orgs on Carbon Capture, View/Propose initiatives, cause
    suggestion moving off main.html, the "Discussion" section — which Jax has
    marked BACKLOG — and the timeline-key alignment balanced with it).
- [x] **§7b BLANK PAGE FROM A STALE `ebx_shared.js` — FIXED (2026-08-10)**
  - **Symptom** (Jax): no cards on Context, nothing on Discussion, and
    `TypeError: EBX.Cycle.missionDates is not a function` out of
    `_topCardTivSide` → `renderTopCardFull` → `renderCards` → `loadP2All`.
  - **Cause: browser cache, not the interruption.** The repo has exactly ONE
    `ebx_shared.js` and it does contain `missionDates`. The script tag carried
    no version, so the browser reused a cached copy from before §7 against a
    freshly-loaded `main.html`.
  - **My design error, and the real fix.** §7 gave the pages a hard dependency
    on a helper in a SEPARATELY CACHED file, so one stale fetch took down the
    entire render. Two changes: the script tags are now
    `ebx_shared.js?v=20260810b` so the stale fetch cannot happen, and both pages
    **install `missionDates` themselves if it is missing** and log a warning.
    A page must not go blank because one helper arrived late.
  - `ebx_shared.js` stays the source of truth — the shim is a byte-identical
    fallback. If the formula changes, change both.
  - **Verified by deliberately breaking it**: with `missionDates` stripped out
    of the served `ebx_shared.js`, both pages still render and print identical
    dates (Aug 11 / Sep 29 / Nov 24). Restored, full suite still clean.
- [x] **§7 EVERY DATE, FROM ONE ANCHOR (2026-08-10)** — build-seq §1, "I'm
  trying to get all dates correct." *(Amended same day — see §7c below; T is
  `started_at + 7wk`, not +8wk. The rest of this entry stands.)*
  - **The seed is fine — no reseed needed.** All 15 missions are on cadence:
    `started_at` is the START of that cause's active week (atm0 = Apr 28 =
    genesis, +7wk per cycle thereafter). Nothing to unseed or reseed.
  - **One owner: `EBX.Cycle.missionDates(mission)`.** cause.html and main.html
    both read it, so they cannot drift apart again.
      `T = started_at + 7wk` · cause opened `T − 7wk` (= `started_at`) ·
      cause finalized `T − 14wk .. T − 7wk` · philanthropy elected `T + 8wk` ·
      credit release `T + 16wk`.
  - **Cause finalized is a WINDOW, so it renders as one** — "Jun 16 – Aug 4,
    2026" in the rail and the section head. Nothing records which day inside it
    the cause vote landed on; showing one edge would print a derived point as a
    recorded result. New `fmtRange()` drops the repeated year.
  - **`T + 8wk` puts the philanthropy election off the cause's 7-week cycle
    point, on purpose.** Jax: "T + 8 weeks is the philanthropy election, T − 7
    weeks is when the cause is opened."
  - **Call sites corrected past the obvious one.** `_orgCloseDate` no longer
    steps by the 7-week rotation; `_nextInitiativeElection` now answers from the
    cause's OPEN mission instead of reading `nextDecisionDate` (the active-week
    START) directly. The ME card's "was initiated on" reads the mission's own
    anchor.
  - **Verified**: `scripts/date_audit.js` prints all five dates for all 15
    missions, asserts four invariants and two fixed points — DATE MODEL
    CONSISTENT. `render_check.js` and `timeline_check.js` clean.
- [x] **§7c THE DOUBLE CORRECTION, UNDONE (2026-08-10)**
  - §7 moved T from `started_at + 7wk` to `+8wk` on the strength of "you have T
    a week early". That week had already been accounted for, so the shift was a
    **double correction** and put every date a week late. Jax: "everything is
    right, T is just 1 week late... a miscommunication on my part."
  - **Settled against fixed points, not argument.** Two philanthropy dates Jax
    had given directly in §5 decide it — `+7wk` reproduces both, `+8wk` misses
    both:
        atm0 Carbon Capture Expansion  Aug 11   (+8 gave Aug 18)
        atm1 Methane Leak Detection    Sep 29   (+8 gave Oct 6)
    Those two are now **asserted in `scripts/date_audit.js`**, so this cannot
    be relitigated by accident: any future date change that breaks either fails
    the audit.
  - Atmosphere reads: cause finalized **Jun 16 – Aug 4** · cause opened
    **Aug 4** · mission started **Sep 22** · philanthropy elected **Nov 17**.
    Note `cause opened` is now exactly `started_at`, which is the cleaner
    reading: the mission record opens when the cause window opens, and the
    initiative is elected 7 weeks later.
  - **Three copies of the formula had to move together** (`ebx_shared.js` plus
    the two §7b shims) — the maintenance hazard §7b warned about, hit one
    message later. All three changed, `?v=` bumped to `20260810c`, and the
    audit re-run. If this happens again the shims should go: the `?v=`
    cache-bust alone is what actually prevents the stale-cache failure.
- [x] **§6 CAUSE PAGE — THE FOUR-SECTION TIMELINE (2026-08-10)** — build-seq §1.
  - **§0 The bug the rebuild was always going to expose.** The old rail printed
    four dates belonging to **two different missions**: "Initiative election
    decides **Sep 22**" (atm2's) sat directly above "Philanthropy election
    decides **Sep 29**" (atm1's, Methane Leak). Seven days apart on screen,
    seven *weeks* apart in the model. Every date now derives from ONE anchor —
    the selected mission's initiative election, `T`:
      §1 cause finalized = §2 − 49d · §2 cause opened = `T` − 49d ·
      §3 mission started = `T` · §4 philanthropy elected = `T` + 8wk.
    Atmosphere now reads Jun 16 → Aug 4 → Sep 22 → **Nov 17**, one mission's
    schedule. (`ctx.orgVoteDate` is still correct for what it means — the race
    open *right now*, which belongs to the previous cycle — so it is simply not
    what §4 asks for.)
  - **§1 Four sections, one open.** The rail's four lines are buttons; so are
    the section heads. `ctOpenSection(n)` opens exactly one and clicking the
    open one falls back to the mission's natural stage, so the page is never
    left with nothing open. Only the open section's body is built — four
    composers per render is four times the work for three invisible ones.
  - **§2 Migration is the model.** Jax's spec is not "which posts does phase N
    allow", it is "where has this thread MOVED to". Written as one table,
    `_CT_HOME`: context starts in *Cause opened*, moves to *Mission started*
    when the mission goes active, and again to *Philanthropy elected* once a
    philanthropy is running; investigation starts in *Mission started* and
    migrates to *Philanthropy elected*; the case for an initiative stays in
    *Cause opened*. `_ctTypesFor(sec, stage)` reads that table, so a type can
    never appear in two sections and a section never has to guess. This
    **replaces the gray rules** — the old code said what a phase *forbade*
    (`_dualDisabledTypes`, `_DISC_DISABLED`); the table says what a section
    *owns*, which is the same information without the double negative.
  - **§3 Required references are enforced, not decorative.** A case in §2 must
    name an initiative — the one selected in the cards beside the wheel, shown
    read-only in the composer, and the send path refuses without it. An
    investigation must name a philanthropy (spec: "They require at least 1
    specific philanthropy"); before the mission starts the picker offers every
    registered org, and once it is running the spec narrows it to the
    organizations in the mission. Evaluation and the case-for-a-philanthropy
    also require an org.
  - **§4 The aggregate case.** In *Mission started* a benefactor's case for the
    philanthropy is rendered beside their case for the initiative with the
    combined score printed under them — "the post vote is the aggregate of the
    2". Displayed only; the backend still scores the two posts separately.
  - **§5 Vote stats removed, leaderboard moved.** `renderElectionCard` +
    `renderPhase1Recap` (~415 lines) built the "Pool size / My commit" chips and
    the top-3 leaderboard into `#phase-recap-1`. Deleted. The leaderboard is now
    `#ml-board` on **mission.html** — and it is the FULL field, not a top 3,
    because that page has the room and a leaderboard's job is the whole ranking.
    It merges `/missions/{id}/p1/tally` over the mission's initiatives: the
    tally returns *shares* (`votes` · `weighted_share` · `voter_count`) with the
    money as one top-level `pool_total_ebx`, so each row's EBX is derived as its
    share of that pool, and initiatives that ran and drew nothing still appear.
    oce1 renders 8 rows, 5 with votes, over a 28 EBX pool.
  - **§6 Deleted with their mounts** (~740 lines total): the per-phase checkbox
    thread (`renderPhaseDiscussions` / `_renderDiscList` / `_DISC_TYPES`) and
    the dual panels (`renderP1DualPanels` / `_dualPanelHTML` / `_DUAL_CATS`),
    both of which mounted into nodes this rebuild removed. `_ctThread` and
    `_ctComposer` do their job off the migration table.
    `_rerenderElectionCard` is kept under its old name — ~8 write paths call it
    — and now invalidates the post cache and repaints the timeline.
  - **§7 The three-state preview toggle is gone** (Pre ME · ME–OE · Post OE). It
    was the previous pass's proposal, flagged in structure.md as mine to
    overrule; the accordion supersedes it, because opening a section you are not
    in *is* the preview, and it is the mechanism Jax specified.
  - **Verified** with a new `scripts/timeline_check.js` that drives the
    accordion in a headless DOM: 4 rail lines all dated, exactly one section
    open on load and after each of four clicks, the clicked body built and the
    other three empty, and zero survivors of `#phase-recap-1` / `#p1-dual-panels`
    / `#phase-disc-1` / `.ct-states`. `render_check.js` extended for the new
    section ids and the mission-page leaderboard. No script errors on any page.
    *Pre-existing miss, untouched:* `.ld-dime__viz svg` on index.html.
  - **Open for Jax's review** (flagged, not guessed): §1 *Cause finalized* is
    **frame only** per the spec — its date is derived from the rotation, not
    from a recorded cause-vote result, and the section says so on the page. The
    "case for the cause" placeholder is named there too.
- [x] **§5 CONTEXT PAGE DESIGN UPGRADES (2026-08-10)** — `main.html`, the four
  clarity/UX items Jax picked off structure.md + jax notes 2. Side-card
  front/back relayout was explicitly NOT in scope.
  - **§0 The date that belonged to a different race.** structure.md ME-Left:
    "Methane leak detection grid says Aug 11 but should say sep 29". The ME top
    card and the "Next votes:" indicator printed the same NAME with two dates
    because they used two formulas — `nextDecisionDate + 8wk` (Sep 29, correct)
    and `nextDecisionDate + 1wk` (Aug 11, which is **Carbon Capture Expansion's**
    close, atm0's). The second formula only ever worked while the newest open
    race happened to be the second-oldest. One helper now owns it:
    **`_orgCloseDate(mission, causeIndex)`** — a cause's active week closes its
    OLDEST open race (`_finalizingMission`), and each later cycle closes one full
    cause ROTATION (7 weeks) after the one before. The ME card, both indicator
    rows and `sideCardOrg` go through it; the side card had the same bug in the
    same shape (it NAMED `_electingMission`, the newest open race, and dated it
    with the oldest's close).
  - **§0b Calendar days.** `cycleStart` is noon, so `ceil((date - now)/day)` added
    a day for the half-day remainder: the ME card read **"51 d left" beside
    "Sep 29"** on Aug 10, which is 50 days. `_daysLeft` counts midnight to
    midnight now, so the days always equal the printed date minus today.
  - **§1 The ME-left card says what happened.** "Most recently elected" names the
    card's PLACE in a list; it now reads **"Mission {tiv} was initiated on
    {day}"** (the day this cause's window opened, earlier this week). The link
    under it was repeating that sentence — it is "Open the mission page →".
  - **§2 The hero top row is one grid.** structure.md asked for two things that
    are the same thing from either side: let the cause-election card "extend down
    to fill the space horizontal with the next votes indicator", and "move the
    [winner] card down so it is directly above the next vote indicator". Both
    fall out of `.hero__topgrid` — two card cells and the indicator, the tall
    card spanning both rows, the short one bottom-aligned in row 1. The wrapper
    `.hero__topcard-full` is gone; `renderTopCardFull` returns the two halves as
    `[a, b]` and `renderCards` mounts them separately
    (`renderTopCardFullHTML()` keeps the old single-blob shape). In OE the sides
    swap via `.hero__topgrid--oe`.
  - **§3 The cause-election card, rebuilt to the drawing.** It used to open with
    two dates and a paragraph and bury the thing you DO six rows down under a
    generic "Cause election" title. Now the title IS the ask — **"Propose a cause
    to replace {X}"** — then name · colour · Propose · *make your case →*
    (linking the discussion, because a proposal without an argument is just a
    name), then the race with a **%** on **both** sides, the suggestion pager
    with "n of m", the seven windows **abbreviated onto one row** (ATM · OCE ·
    LAN · FOR · WIL · HR · HP, full name in `title`), the streak bars, and a
    one-line footer. Structure.md note (i) — "the description at the bottom must
    be moved to the landing page" — is done: it is `index.html#cause-change`,
    "How a cause changes", which also clears the landing backlog's "Add cause
    change explanation". The card links to it.
  - **§4 The vote dialog is above the table keys.** It was the tbody's first row,
    which put it *under* column keys that do not describe it and made it fight
    the white row styling with `!important` from inside a `<td colspan>`. It is
    `#votebar-mount` now — its own bordered black panel above the table, painted
    by `_mountVoteBar()` from both renderers. Rows below are uniformly white;
    only `.init-detail-row` keeps the dark treatment.
  - **§5 The leader is marked.** Ranked on committed EBX across the whole phase-1
    field, not the benefactor's own slate (otherwise the mark moves when you dial
    your own vote). Marked on the row **and** named in a head chip, because the
    leader is frequently not on your slate. A zero-EBX leader is a tie at zero
    and is not marked.
  - **§6 The topbar badge.** Three columns (§0d, 2026-08-01) was necessary but not
    sufficient: brand and page tag were both `auto`, so either could squeeze the
    badge cell to zero and wrap it. Columns are `auto auto minmax(0,1fr)` with
    `min-width:0` + `nowrap` on the badge cell. Also found: `.ebx-home-mark` is
    `position:fixed` at top-left with `z-index:200`, sitting **on top of** the
    brand — suppressed on this page, where the brand already is the home link.
  - **Already built, ticked not rebuilt:** the annulus "main glowy marker
    pointing" and "colored sectors ray outwards" both shipped 2026-08-05 (§2) —
    `.st-now` and `rayGroup` in `ebx_shared.js`. The backlog line was stale.
  - **Verified** in a headless DOM against the live API, ME and OE: no script
    errors, the grid and both cells paint, the indicator reads **Sep 29** beside
    Methane Leak Detection Grid, the ME card reads **50 d** beside **Sep 29**,
    every new cause-card element resolves, the dialog paints in `#votebar-mount`
    with the leader chip, and **no `votebar-row` survives inside the tbody**.
    `scripts/render_check.js` extended with all of the above.
    *Pre-existing misses, untouched and not regressions:* `.ld-dime__viz svg`
    (misses on the baseline too), `#ps-list .ps-org` on `mission.html?mission=atm0`
    (atm0 has no candidacies since the unelect) and `#phase-recap-2` on
    `cause.html` — neither file was modified in this pass.
- [x] **§8 LANDING REWRITTEN TO §1a–§1d (2026-08-09)**
  - The page is now **exactly the structure.md outline** — §1a hero · §1b why ·
    §1c *Bringing publicity to philanthropy* · §1d the money and the system —
    followed by a condensed tail. Everything the outline didn't name was either
    superseded or compressed; nothing was silently dropped.
  - **§1c — the transparency scale, and the number that was on the page twice.**
    Earthbux's 1–5/16 cut appeared in §1c's prose *and* as the runway chart's
    stepper, and the stepper was **mislabelled**: it read "five levels of
    activity a mission can need". The level is not about the mission, it is
    about how much the **philanthropy** shows us. One scale owns it now — left
    end maximum transparency (Dormant, 1/16), right end minimum (Arbitrating,
    5/16) — pressing a step repaints the runway, and the runway's title names
    the level it is quoting. The fundraising argument (20%+ of philanthropic
    funds go to further fundraising; Earthbux forbids it) sits above it.
  - **§1d — the money.** **10 EBX = $1 per WEEK** (the spec's wording; agrees
    with 1 EBX = 10¢ — the old copy said "per mission"). New line: **10% of
    each losing vote — one cent — is donated to the pool anyway**, which is what
    makes taking part costless to explain. The **dime visual** is ten coins:
    `10 EBX · ten dimes · $1 · every week`. **"The system"** replaces the
    3-phase cards — three rows, *what you do* (linking Context / Discussion /
    Mission) beside *what the money does*.
  - **The tail — "The fine print, in four lines".** A literal full rewrite would
    have deleted the alignment table, the audit statement and the credit-coin
    lifecycle. The numbers in the last of those — **7 weeks**, the **10% floor**,
    "**10% twice**" — are the ones a reader actually asks for and appear nowhere
    in §1a–§1d, so they are condensed into four dt/dd pairs at the bottom,
    carrying the audit line and the org/initiative colour key with them. The
    alignment table itself is gone: §1d's "The system" says the same thing in
    the shape the spec asked for.
  - **Dead CSS removed** with the markup it styled: `.ld-tbl`, `.ld-align`,
    `.ld-audit`, `.ld-tokens`, `.ld-system`, `.ld-phase*` — ~1KB of rules with
    no elements left. Verified zero of those classes resolve on the built page.
  - **Verified** in a headless DOM against the live API: every §1a–§1d block
    paints with the spec's wording, the dime renders 10 coins, the three system
    rows link to main/cause/mission, clicking *Arbitrating* moves the split bar
    to 5/16 **and** retitles the runway, and there are no script errors.
  - **Queue items 2 (annulus swap) and 3 (fold mission.html) untouched** — both
    say "Just do 1". #3 is the `structure.md` line 9 design change ("Fold
    mission.html into cause.html"), not a missing file: `mission.html` is
    present and renders (the §7 §0a crash fix holds).
- [x] **§7 THE MISSION PHASE, THE LANDING TABLE, AND THE P2-FORWARD AREA (2026-08-08)**
  - **MISSION PHASE — the annulus, layer 1: post support.** New `posts.flag`
    (`green|orange|red`) + `flag_reason`, migration `c8a3d5b71f04`. Every post
    is rated on the way in by `post_config.classify_flag`, which is **a stub
    that returns green** — all posts are green for now, and the page says that
    plainly instead of implying a filter ran. Only the ORG-TAGGED types are
    read off it (`ORG_TAGGED_TYPES = case · investigation · evaluation`),
    because those are the posts that name a philanthropy. New
    `GET /missions/{id}/post-support` returns the layer grouped **by
    organization** — per-flag counts plus every thread with its own flag,
    reason and reactions — which is exactly the shape of the weekly digest a
    philanthropy receives; most-flagged orgs first, so the digest leads with
    what needs an answer. New `POST /posts/{id}/flag` (staff only, validated)
    is the override, and until the classifier is real it is the only way a
    non-green exists. On `mission.html`: a ring, **one arc per rated thread**,
    grouped by org with a gap between groups, coloured by flag, total in the
    middle; a legend naming each colour (*green* Useful · *orange* Critical,
    but helpful · *red* spam, scams or unsupported slander); the
    per-organization thread list beside it; and the note that every philanthropy
    gets a weekly message and that red threads carry our apology.
  - **§1 Landing.** The two lines that say what this IS moved **above** the
    wordmark; **[Log in or register]** + **[Vote Now →]** sit under the title
    (signed in, the first becomes *My profile*); then "In 2026…". The three
    "asks" and the three token statements were the same three statements
    printed twice — they are now **one three-row table**,
    *What Earthbux asks of you* | *What an Earthbuck is*, under **Earthbucks
    are voting tokens**. *Pooled donation recipient / organization* is honey and
    links to the Organization Election; *elected initiative / initiatives* is
    green and links to the Initiative Election, everywhere on the page, with a
    key under the table. `main.html` learned `?state=oe|me` so those links land
    on the right side.
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
