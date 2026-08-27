## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
*Everything below was BUILT 2026-08-27b — the entry at the top of the backlog
says what landed and what was deliberately left for you. Replace this queue when
you set the next one.*

0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- (c) **Inconsistencies** 
- (d) **Not blocking** Acknowledge but only fix if trivial.

Leave the top left card as the upcoming eleciton in the ME. Dont toggle the card, but do keep toggling the middle. For both elections, make the top left card glow brighter/thicker and create a bar at the top that says "This Weeks Election".
Clicking on the cards should have the same exact function as clicking on the cause toggle.
When the Mission elections toggle is clicked, the table should filter by the active cause too. 

1. **More Election page UX**
- Default election panel to upcoming election
- Ray < pointers pointing wrong way (Should pont same way as glowy one)
- Cause election box should be below the table.
- Move the cause selection toggle to below the ME/OE toggle, above the election panel. 
- Lock bottom of 3 side cards to top of cause toggle, and top of 3 to bottom of the top cards. Middle one halfway in between. 
- Now, the position of the upcoming election is enough to identify that it is upcoming. We can make the glow indicative of which election is selected. 
- Discussion sectors still pointing wrong way 

## CONVERSATION
Maybe we just get rid of the onclick for the sectors and move the cause selection bar so it is the same across both pages?
- This weeks elections should have a discussion snippet.
  *(absorbed into the backlog ▶ NEXT on 2026-08-21b — the two cards for THIS
  week now have room for one, since the buttons came off them.)*

- Without permission, only execute build sequence.
- Absorb amd modify backlog items and update structure as you see fit.
- note - s/s/s items can be suggested any time, but they can't be voted on until the budgeting opens.
- Until I make enough to hire security, I need to hide earthbux from corrupt organizations.
- Does calling an organization a "philanthropy" make sense?
- Need to start thinking about where the money lives.
- Kids accounts need a dedicated adult account to authorize any transactions.
- Security rule: The first time an account signs in, they are told they can't vote in any org elections except the first (most recently electeed tiv) org election. - This prevents from creating accounts just to vote your org in. - edit - they can vote in whatever election they want, but they are not allowed to buy extra votes until they've been a member long enough. 
- I need to set goals and plan - what am I going to do when and in what order?
- I wonder if I can create an animated diagram - kind of like a prezi - showing each step of the process.
## BACKLOG (for backlog management - ignore this section during build task)
*The single backlog. Absorbed `docs/backlog.md` + prior loose items on 2026-07-17.*
*Ordered by the current plan: **master the posting + newsfeed experience for phases
1–2 first**; everything from the end of phase 2 onward is **parked** until that
lands. Page specs live in `docs/structure.md`; the model in `README.md` §5.*

### ▶ NOW — posting & newsfeed (phases 1–2, the focus)
- [x] **§1 SEVEN SMALL MOVES ON THE ELECTION PAGE (2026-08-27b)**
  - **The OE election panel opens on a race.** It wanted an explicit pick and
    said "Pick a mission below" until it got one, so the OE side of the page
    started empty while the ME side started on a race. `voteMissionId()` already
    knew the answer — the open race for the cause the page is pointed at, else
    the one closing soonest — and the panel asks it now.
  - **Every arrow points the way the clock moves.** The election annulus's
    chevron rays and the discussion wheel's chevron SECTORS both point
    **clockwise**, with the glowing marker. The sectors were flipped the other
    way on 2026-08-27 and that is what "still pointing wrong way" undoes: the
    marker is the only moving thing on either wheel, so it is what direction
    means.
  - **The cause election box moved below the table**, and the cause toggle moved
    below the ME/OE toggle at the foot of the hero. The reading order down the
    page is now: what won → what is running → pick a cause → vote in it → the
    field → and, last, the vote that decides a cause seven weeks out.
  - **The side cards lock to the furniture around them.** Each column runs the
    full height of the hero row: first card flush with the bottom of the top
    cards, last flush with the top of the cause toggle, the middle one exactly
    between. `justify-content: space-between` on a stretched column IS that
    instruction.
  - **The glow means SELECTED.** It marked the upcoming election, which the
    layout already says by putting it first; it marks the cause the page is
    pointed at now — a side card when you pick one, the top-left card otherwise.
  - **Verified**: `render_check` **CLEAN** · `ce_check` **80** (the panel is
    asserted BELOW the table now) · `oe_check` **83** · `posts_box_check`
    **CLEAN** · `landing_check` **43**.
  - **Answered, not built** (CONVERSATION, "maybe we just get rid of the onclick
    for the sectors and move the cause selection bar so it is the same across
    both pages?"): yes — that is one bar in one place on both pages, and it is
    the smaller surface. The sector click and the tab row do the same job on
    cause.html today, which is one too many ways to change cause. It needs your
    word before it lands, because it also decides whether the discussion page
    keeps a wheel at all or just a header bar.
- [x] **§1–§2 THE CE PANEL, AND ME/OE IN ONE SHAPE (2026-08-27)**
  - **§1 The cause election is an AREA above the election panel**, in the shape
    of the drawing: the streak down the left as **one column of seven lines**
    (it was seven columns of one-to-seven lines, which drew the RULE rather than
    the progress), *Show / Hide Cause Table* on the right, and in the middle the
    title row, then **Nominate a Cause · make your case · Commit · Cancel**,
    then keep-or-replace, then the pager. It **persists across ME and OE** —
    that is the whole reason it is a panel and not a card.
    - **The CE has no toggle of its own.** "It is toggled by the main page cause
      toggle." That works because every cause holds exactly ONE open window —
      the active cause's is slot 7, everybody else's is 8..13 — so the seven
      tabs and the seven replaceable windows are the same seven things. The
      panel carries `data-slot` / `data-cause` so a check can ask which.
    - **A vote is dialled, then committed.** Clicking keep-or-replace used to
      POST; it marks a draft now, Commit sends it, Cancel drops it. `ce_check`
      asserts the middle state: after the click and before Commit, the server
      still has nothing.
    - A row of the cause table now selects the CAUSE that holds that window, so
      the panel can never be pointed at a confirmed window and show a ballot
      with every button disabled.
  - **§2 The rest of the election page.**
    - **The ME/OE toggle moved BELOW the annulus** and lost the glowing rail;
      **the 7 cause tabs took its place** between the top cards and the annulus.
      (They spent one day in the top bar, where they read as site navigation.)
      They drive the annulus, the centre panel, the CE panel, the left top card
      and the table.
    - **The two top cards say the same thing in ME and OE now**: LEFT is the
      race still running, RIGHT is the race that just closed. The just-elected
      mission moved to the right and wears two bars — **"Winner of \<cause\>"**
      over it, **"Elected \<date\>"** under it — and the budgeting card wears the
      same pair for the organization election one race back. The how-to line is
      on the left card only, and reads *"Select a cause, and vote."*
    - **The ME ring shifted one place clockwise**: the upcoming election left it
      for the top-left card, everything moved up one, and a new card came in at
      the top right — **+7, the active cause's own next initiative election**,
      which had no card at all while the active cause sat in the top card. The
      OE ring kept its orientation.
    - **The allocations panel is parked at the bottom of the page** until its
      design is settled; the side cards run flush to the election panel.
    - **The filter under the table is a "Show all Initiatives" button.** The
      select survives hidden — it is still the field every filter path reads.
    - **Rays**: the election annulus has them now, as **chevrons pointing the
      way the queue moves** ("<" at the top); the discussion wheel lost its
      rays, and its chevron sectors point the other way — toward the cause whose
      turn comes next rather than the one whose turn has passed.
    - **Cancel beside Commit, everywhere**: the initiative slate, the
      organization amounts, and the cause ballot.
    - cause.html gained the line the wheel needed: *"Click on a cause to
      participate in the discussion."*
  - **Verified** against a copy of the live db: `render_check` **CLEAN** ·
    `ce_check` **80** (rewritten for the panel: the card and its seven toggles
    are gone, the panel sits above the election panel and survives the ME/OE
    switch, each of the seven tabs points it at that cause's own open window,
    the draft-then-commit path, and the way back out of the cause table) ·
    `oe_check` **83** (the allocations panel is asserted at the BOTTOM now, with
    a Cancel beside its Commit) · `posts_box_check` **CLEAN** ·
    `landing_check` **43**.
  - **Judgement calls, flagged rather than guessed:**
    - "The upcoming ME election is now the top lhs card" is read as the hero's
      top-LEFT CARD, and it follows the cause TOGGLE (defaulting to the upcoming
      cause, which is what the page opens on). If you meant the top-left SIDE
      card, the ring is one rotation away from that.
    - The CE panel's default window follows that same selection, so in ME it
      opens on the upcoming cause's window rather than the nearest open one
      (slot 7, the active cause's). A fresh OE load does open on slot 7.
  - **Not built**: the ME right card still shows the ACTIVE cause's winner while
    the left card follows the toggle — one card on the clock, one on the
    selection. It reads right today (this week we elected X, next week we decide
    Y) but it is a split brain, and if the pair should move together, say so.
- [x] **§1–§4 THE ELECTION PAGE, THE ANNULUS SWAP, AND THE CE DATES (2026-08-26)**
  - **§1 main.html is the ELECTION PAGE.** Title, top-bar tag and structure.md
    agree. The ME top-left card lost the propose-an-initiative dialogue (the
    table's propose row is still one click away) and lost the sentence that
    named the mission; the sentence is the card's CAPTION now, under it, in the
    words asked for: **"Winner of \<cause\>: \<tiv\>. Elected \<date\>."** Above
    the card, the page finally says how to vote, and the name of the other
    election in that line is the button that switches to it.
  - **§2 THE TWO ANNULI CHANGED PLACES.** The seven-sector WHEEL left main.html
    for cause.html; the PIE left cause.html for main.html; no card on either
    page moved. The wheel was always a cause SELECTOR, so it went to the page
    whose seven tabs it replaces — clicking a sector is how the discussion page
    changes cause now. The pie is a RACE, so it went to the page where the
    voting happens: initiative shares in ME, the philanthropy tally in OE,
    behind main.html's own centre panel (their radii agree, so the ring frames
    it). The **7 cause tabs** came with it into the election page's top bar and
    point the annulus, the centre and the table at one cause without touching a
    card and without scrolling the page. cause.html's centre stack, which the
    pie used to draw in SVG, is an HTML panel over the wheel's core.
    - One real bug found in the port: a **lone front-runner** is a 360° slice,
      and an SVG arc whose ends coincide draws NOTHING — the ring went blank on
      every race with one candidate, which is most of them this early. It is a
      circle now.
  - **§3 Allocations — DIAGNOSED, NOT FIXED** ("only discuss until you are sure
    about the solution"). Three separate things wear one word:
    1. **"Unallocated 10 while my vote is already allocated" is the ME side not
       being one-way.** Committing a phase-1 slate writes `VoteP1` rows and
       nothing else — `free_ct` is untouched — while the panel paints
       *Unallocated* from `free_ct` AND *Committed → initiatives* from those same
       rows (`_meAllocatedCt`). The same tokens are counted twice and the
       header total overstates the holding by exactly the ME commitment. The fix
       is the standing backlog item **"Make the ME table one-way too"**: route
       the p1 commit through `wallet.commit_stake` the way `/wallet/commit`
       does. Nothing smaller is honest.
    2. **The 10 that "carried into the OE from the ME" is not unallocated — it
       is UNASSIGNED**, which is a different state and a different word.
       `finalize_p1` ran on for1 this morning and wrote a `VoteP2` row of
       1000 ct with `org_id` NULL: staked in the organization election, no
       philanthropy named. It counts under *Committed → organizations* in the
       panel and shows as the race's `unassigned_ebx` chip in the vote bar. Two
       words one letter apart for two states is the actual defect here.
    3. **"0 tokens committable to any org in wolf habitat" is the rule, not a
       bug** — but the page never says so. `wallet.oe_rows` gives a row
       `headroom = free_ct` only for the race that finalizes soonest ("2 options,
       not 9"); every other row's ceiling is `purchased_ct`, and purchasing is
       still a localStorage simulation, so that is always 0. Wolf habitat (wil0)
       is not this week's race, so it offers 0 whatever the balance says.
    - **The grant clock, for the question in the queue**: the grant is topped up
      to 10 tokens per cycle week (`WEEKLY_GRANT_CT`) and carries a deadline one
      week out (`GRANT_COMMIT_BY_WEEKS = 1`) that ROLLS if it is missed. It is
      not issued seven weeks ahead of the election it can be spent in.
    - **Still to decide** (Jax): the split of the panel into **This week** and
      **Total**, with the detail on profile.html.
  - **§4 CE dates: one clock, one date per window.** A window is a WEEK — slot
    s is the week beginning s weeks after the week running now — but the date
    was derived from a MISSION (`_nextInitiativeElection`) plus a rotation for
    the far half of the table. That agreed with the clock only while the cause's
    next mission had not opened yet; the scheduler opens one every Tuesday, so
    the nearest open window (slot 7, always the active cause's own next
    appearance) had already jumped a cycle and then had a rotation added on top
    — seven weeks out and out of date order in the toggle row. The card was
    wrong the other way: it added no rotation at all, so card and table dated
    the same window differently. Both read `_windowRunsDay(slot)` now. The seven
    toggles read **FOR Oct 13 · WIL Oct 20 · HR Oct 27 · HP Nov 3 · ATM Nov 10 ·
    OCE Nov 17 · LAN Nov 24**, nearest first.
    - **Open question for Jax**: this makes the printed date the TUESDAY the
      window opens — the day that cause becomes active, its mission opens and
      the previous cycle's initiative election is decided. If "1 week early"
      meant you want the day the window CLOSES instead, that is a one-line
      change in `_windowRunsDay`; say which and it moves.
  - **Verified** against a copy of the live db: `render_check` **CLEAN** (with
    new assertions for the pie, the tabs, the wheel, the two captions) ·
    `ce_check` **67** · `oe_check` **82** · `posts_box_check` **CLEAN** ·
    `landing_check` **43**.
  - **Also fixed**: `ce_check` asserted that slot 11 refuses `atmosphere` as a
    challenger, which was only true in the week it was written — slot s is held
    by the cause at (active + s) % 7, and this week atmosphere IS slot 11's
    incumbent, so the post was a KEEP and correctly returned 200. The check asks
    the slate who holds the window now.
  - **§0d — acknowledged, not fixed: the two clocks disagree for four hours
    every Tuesday.** The browser reads `cycleStart` as `new Date("2026-04-28T12:00:00")`,
    which has no zone and is therefore LOCAL noon; the server counts weeks from
    the same wall-clock string as UTC (`datetime.utcnow()`). East of UTC the
    week rolls on the server first, west of it the browser rolls first — a
    window in which the page and the API name different active causes, and
    `cause_slate` is asked for a slot the client numbered against a different
    week. It is four hours wide in America/New_York and it has never been hit in
    a check, because the checks do not run at 8am on a Tuesday. Fixing it moves
    every date for somebody: either the browser's anchor becomes `…T12:00:00Z`
    (the week boundary shifts to 8am ET) or the server's becomes zone-aware.
    Jax's call, so it is written down rather than chosen.
  - **Not built**: `_proposeDialogue` / `togglePropose` survive in main.html
    with no caller (the card that used them is clean; the propose ROW still
    opens the shared dialog) — dead code, deliberately left rather than swept in
    a UX pass. cause.html's `selectInitByAnnulus` is likewise unreachable now
    that the pie's slices are on the other page.
- [x] **§0–§2 TOKENS, THE RACE POOL, AND THE PAGE AROUND THE WHEEL (2026-08-21b)**
  - **§0a Voting is counted in TOKENS.** "It's confusing because votes and ebx
    appear to be separate." Every visible EBX on main.html is now *tokens* —
    88 replacements across the cards, both dialogs, both table heads, the buy
    flow and the carryover panel — via `EBX.formatTokens`. `formatEBX` survives
    for the credit badge and the ledger, which are not the voting area. The
    other three pages still say EBX; that is a decision, not an oversight (see
    structure.md › Backend).
  - **§0b The race pool did not move when a vote was committed.** Real bug,
    reproduced and fixed. `p2_tally` measured phase-2 weight with
    `p2_ebx_by_ben` — the money phase 1 left behind — and knew nothing about
    `VoteP2.stake_ct`, which is what `POST /wallet/commit` has written since
    2026-08-19. The commit was real; the reported total was two days stale.
    `crud.p2_stake_by_ben` asks `wallet.stake_ct_of`, the function that already
    knows how to read a stake, rather than restating the rule. It took a second
    bug with it: `unassigned_ebx` was summed from the phase-1 carry, which for a
    stake committed straight out of the balance is ZERO — so tokens committed
    without a philanthropy named disappeared from the pool entirely. `oe_check`
    now guards both, in tokens, against the live server.
  - **§0c Allocations says what it cost.** `Allocations 88 tokens $8.80`.
  - **§1 The cause election, second pass.** All **7** replaceable windows are
    votable at once (the server opened exactly one and capped the slot at 7, so
    six of the seven toggles were locks and six streak clocks could never
    start). The card's seven toggles are those seven windows **in the order they
    run**, each carrying its own date — LAN Oct 6 · FOR Oct 13 · WIL Oct 20 · …
    — which is what fixes "this is correct in the CE table, but not in the top
    card": both are built from `_causeWindows()` now. The ballot is keep-or-swap
    with a **click-through pager** over challengers, and a challenger can only
    be a **nominated** cause — swapping two active causes inside the rotation
    reorders it and nothing else, so the server refuses it and the streak query
    stops crediting historical votes toward a swap it would refuse. Nominating a
    cause is a **dialog** now, like proposing an initiative, and it asks what the
    cause is FOR rather than just its name and a colour.
  - **§2 The page around the wheel.** Cards: no vote counts — **Leader:** and
    **My vote:**, two lines each, no buttons, and the card itself is the click
    target. Layout: **two columns of three**, the bottom row and its Help and
    Commit gone, and the **allocations panel** nestled under the annulus in BOTH
    states — two sets of two (Unallocated: granted · purchased | Committed:
    initiatives · organizations), no explanation, Commit inside it and
    mode-aware. The OE panel took the three links (Mission page → **View
    Organizations**), narrowed the ballot to the **ranked top 3**, and gained
    the **add-more-vote** control: unallocated · purchase · **from another OE**.
    That last one is the first way in to `POST /wallet/convert`, which has
    existed since 2026-08-20 with no UI — a benefactor could not move a stake
    they had changed their mind about at all. Two rows in the annulus centre.
  - **Verified**: `token_model_check` **101** · `wallet_check` **118** ·
    `oe_check` **82** (rewritten: the panel under the annulus, the links in the
    dialog, the two sets, the source dropdown, the top-3 ballot, a sweep proving
    no visible "EBX" survives on the voting surface, and the race-pool
    regression in both its forms) · `ce_check` **67** (the seven toggles in date
    order with the nearest first, all seven windows open, an active cause
    refused as a challenger while keeping the incumbent is allowed, the pager,
    the dialog) · `render_check` **CLEAN** · `landing_check` **43** ·
    `date_audit` · `posts_box_check` · `carryover_check` — no regression.
  - **Not built**: `slot` is RELATIVE to the active cause, so the same slot
    number names a different calendar window each week while `_week_winner`
    compares the same slot across weeks to build a streak. That predates this
    pass and the seven-weeks-in-a-row rule is written in those terms; if a
    streak should follow a fixed DATE, that is `CauseVote` and the streak query,
    not the UI. Purchasing is still the localStorage simulation, so the
    "Purchase" source routes to it. The ME side of the allocations bar is still
    derived client-side, because the ME table is still not one-way.
- [x] **§0–§2 THE CAUSE ELECTION TABLE, AND THE ALLOCATIONS BAR (2026-08-21)**
  - **§0 The Commit button was invisible, not missing.**
  - **§1 The cause election is a table now, and the card is a report.**
  - **§2 The allocations bar.**
- [x] **§1 THE ONE-WAY COMMITMENT, AND THE OE SURFACE (2026-08-20b)** —
  - **§1 Committing is ONE WAY.** 
  - **§2 Unallocated is granted + purchased, and nothing else.** 
- [x] **§1 THE ONE SKIM, THE GRANT CLOCK, AND THE CONVERSION BUDGET
  (2026-08-20)**
  - **§1 One skim, and the initiative election is not it.**
  - **§2 Being right pays in INFLUENCE, not in a cheaper skim.**
  - **§3 Nothing rolls to the next election of a cause any more.**
  - **§4 The grant carries a date; the date rolls; purchased tokens carry none.**
  - **§5 Three conversions replace the 15-week fuse.** `MAX_CONVERSIONS = 3`
  - **§6 The OE table: eight rows, and they do not expand.** 
  - **Not built**: the OE half of settlement is still derived rather than booked;
    nothing sweeps an unvoted foreign stake home at close (the read treats it
    correctly, no row moves); the multipliers drive the wallet's reported weight
    but are not wired into `p1_tally` / `p2_tally`, and budget/research voting do
    not tally weight at all yet; the mint still does not exist; the ME table
    still spends the old localStorage budget. `docs/token_model.md` §10.
- [x] **§1 THE GRANT, THE WALLET, AND THE OE TABLE (2026-08-19)**
- [x] **§1 THE LANDING PAGE IS THE OUTLINE (2026-08-18)**
  - **§1 Five sections, and only five.**
- [x] **§1 THE OE VOTE ROLLOVER, AND THE SELECTION PATH (2026-08-14)** —
  - **§1 The slider was a ratchet.**
- [x] **§2 DISCUSSION EDITS · BUDGETING DETAIL · main.html (2026-08-12)**
  - **§1 Research links itself.** 
  - **§2 The type toggle moved into k**
  - **§3 Budgeting is a costed LIST, not prose.**
- [x] **§1 THE DISCUSSION BOX (2026-08-12)**
  - **§1 One box replaces four systems.**
  - **§6 Also cleared from the cause backlog**: the header moved above the
    annulus, "View initiatives →" deleted with **Vote** promoted into the left
    column's header
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
  - **§3 — glow logic**
  - **Accounts console**`GET /admin/accounts` + `DELETE /admin/accounts/{id}`*Accounts · remove*
- [x] **§2 CARDS + THE REST OF main.html (2026-08-05)**
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
- [ ] **A discussion snippet on this week's elections** (absorbed from
  CONVERSATION, 2026-08-21b). The two top cards are the races running THIS week,
  and since 2026-08-21b they have the room: their buttons came off. One line of
  the leading post for that race, linking into `cause.html`, is what would turn
  a card from a scoreboard into a reason. Reads from the same `/posts` query the
  discussion box already runs; the open question is which post — the top-rated
  one, or the most recent.
- ◑ **The top cards and the third tab** (absorbed from CONVERSATION,
  2026-08-20 — Jax's own words kept, with what each one touches):
  - [x] "The table should have a **third tab — 'Cause Election'** — which
    absorbs much of the cause election top card." BUILT 2026-08-21 (build-seq
    §1). The third head, the third row renderer and the third dialog all exist;
    what is left of the card is the state and the way in. It is reached by
    **Decide the Cause** on the card and by `?state=ce`, and it is `_tableTab`
    rather than `_mainMode` — the tab had to change the table without touching
    the cards.
  - "The **OE votes must not carry over** across elections like the ME votes do.
    Every OE should start with no philanthropies nominated/registered and 0 votes
    across the board." Touches `finalize_p2` (or the mission opening it), and it
    is the phase-2 twin of the roll-forward that §1 (2026-08-20) removed from
    phase 1 — worth doing in the same shape.
  - "**Remove** the 'Propose an initiative' dialogue in the ME lhs top card. Also
    remove the 'Open the mission page'. Remove the 'Propose a cause' on the rhs
    ME top card."
  - "**Move** 'Mission \<tiv_name\> was initiated \<date\>…' to below the card and
    add '… The next mission election is for \<Cause_x\>' and point down to the
    card below."
  - "In the **OE rhs top card**, below the budgeting card, say '\<Phl\> was elected
    to run \<tiv\> on \<date\>. The next organization election is for \<tiv\>' and
    point to the left."
- [ ] **Each benefactor's EBX available to donate should always be visible**
  (CONVERSATION, 2026-08-20). The unallocated strip does this, but only on the OE
  table; it belongs in the header on every page. Spec'd in `structure.md`
  › profile.html.
- [ ] **Make the ME table one-way too.** The initiative slate still spends the
  old client-side `10 + localStorage.ebx_purchased_ebx` budget and still lets a
  commitment be dialled back down. Since 2026-08-20b the OE side cannot: ct
  leaves the unallocated bar for a race and only a conversion moves it. Same
  wallet, two rules, until this lands.
- [ ] **Buying tokens.** `buyVoteEbx` is still a localStorage simulation, so
  `purchased_ct` — the undated, goes-anywhere slice the model already
  distinguishes — is never actually written outside the checks.
- [ ] **Retire the phase-1 carryover machinery.** Nothing rolls to a cause's next
  election since 2026-08-20, so `GET/PUT /missions/{id}/p1/carryover`,
  `_send_floor`, `_reclaimable`, the `carryover` ledger bucket and the
  unreachable `carryoverPanel` in main.html describe a world that no longer
  exists. They still explain races finalized under the old rules, which is why
  they survived this pass — remove them once no open mission predates the change,
  and retire `scripts/carryover_check.js` with them. `crud.withdraw_p1` joined
  them on 2026-08-20b: it is a named refusal with its legacy body kept beside
  it, and `cause.html` still shows a Withdraw button wired to it.
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
- [ ] Move overview into the table; clicking a row expands it and filters discussion. **ME side only** — the OE side was decided the other way on 2026-08-20 ("the OE table rows should not be expandable"), where a click selects the race and points the dialog at it instead.
- [ ] Pool metrics: "guaranteed pool" vs "committed pool".
- [ ] Vote visualization (count + relative commit size per vote).
- [ ] Start dates on every mission card; show future dates after the cause shift.
- [ ] "Log in to vote" gating on the cause page (no phantom voting when signed out).
- [ ] Better active/upcoming indicator: **horizontal, not diagonal** — a 2-row box between the upcoming and active causes naming both.
- [ ] Move show & register/propose into the top "Active mission"/"Active cause" bar (adjust CSS).
- [ ] Various locations need black-on-white Times New Roman.
- [ ] Propose / nominate dialogs shared between context page and cause page.

### Elections / voting model
- [ ] **Tie-break rule** (from the hpr0 analysis, 2026-08-01, build-seq §3 — analyzed, nothing changed): a p1 tie is currently broken by *vote-row insertion order* (`p1_tally` sorts stably; `finalize_p1` takes `entries[0]`). Jax's 5/5 split on GEAG vs Solar Grids → GEAG won only because its vote row (id 26) predates Solar's. The "4.5 committed" was CORRECT behavior for its day, not corruption: the losing tiv rolled to hpr1 via the old `_carry_losers_forward` with the 10% commitment-fund skim (5 EBX → 4.5 EBX). **That path is gone as of 2026-08-20** — nothing rolls and nothing is skimmed at the initiative election, so a loser's 5 EBX now stays in hpr0 and funds its organization election in full. Still open: decide an explicit tie-break (earliest commit? most voters? sudden-death week?).
- [x] **Skim ledger rounding bug** — CLOSED 2026-08-20. Fixed on 2026-08-19 (round UP at centitoken granularity), and then made moot: `COMMITMENT_FUND_SKIM` is **0** and nothing rolls to a cause's next election, so there is no loser-carryover skim left to round. The one skim, at the organization election, is computed in integer ct by `token_model.settle_oe`.
- [x] **Winner-backer perk** — SUPERSEDED 2026-08-20. The cheaper-bonus-vote version died with the price ladder; the reward for being right is now INFLUENCE, published per arena in `token_model.influence_mult` (2x OE · 2x budgeting · 1.5x each on research, 2.25x for both). What remains open is wiring it into `p1_tally` / `p2_tally`, which is its own line below.
- [ ] **Wire weight into the tallies.** `p1_tally` is linear and `p2_tally` counts integer votes, so neither reads `token_model.weight_ct` or the influence multipliers — today they only drive the per-row weight the wallet reports. Budget and research voting do not tally weight at all yet, which is where 2x-on-budget and 2.25x-on-research have to land.
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
