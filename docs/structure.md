# Structure — page-by-page build spec

## Site layout
| Surface | Page | What it shows | Posting |
|---|---|---|---|
| **Landing** | `index.html` | About Earthbux | Connects and explains everything | 
| **Election** | `main.html` | **voting home** - context for each tiv/phl. The 7 cause tabs live here (2026-08-26) | Can suggest causes/initiatives and nominate philanthropies |
| **Discussion** | `cause.html` | Full discussion home. | All benefactor posting |
| **Mission** | `mission.html` | Mission status page - | phl/ebx posts, budget resolutions |
| **Profile** | `profile.html` | all activity from the signed-in user | active threads |

## index.html (Landing) — **About Earthbux**
*backlog*
- About section (Enlarged image) for each election card
- [ ] **§1f — everything the a–e outline does not carry.**
- **Donation breakdown** If I put $20 / week into earthbux, 100% of that is a donation.
$2 is going to the best researchers on our platform, $0-6 is going to Earthbux, and $6-18 is going to the mission.
Any of that $6-18 that is put towards the org election or specefied-must-donate will end up going to A mission.
- [ ] Suggest weekly/monthly/yearly donation to cover many missions.
- [ ] The philanthropy link should go to the cause.html of this weeks active mission.
- [ ] **Links** Initiative should link to the ME main.html (already does) and Organization should link to the OE main.html.
- Explain why a philanthropy and an organization are the same thing.
- **Messaging notes** We do NEWS. We are ideally not about legal and logistics. However, we share our resources with the people. MAYBE. . . One of the rewards is that we pay someone to travel and participate in the mission!
- FAQs
- What if my vote loses? - Only 10% is guaranteed to the pool, but you can choose how much to allocate.
- Are there limits? - No, but the more you commit, the less weight each dollar has.
- What if I want to vote in an OE that I didn't vote in the ME? - You can!

Each mission is crowdfunded and more importantly, crowd-ideated.

EXAMPLES - "The current active mission is ___" - This week - next week

Each mission is slated to last a year, but can last longer or end sooner.
1. Commit tokens to elect an initiative for the weekly cause. | The winner takes on the mission.
2. Commit to a philanthropy to lead the mission | Tokens become mission-valued "credit coins" that are exchangeble and tax-deductable.
3. Determine how to allocate funds, and vote for the best ideas. | The top-rated content is rewarded.

 A toggleable per-process detailed description/instructions/about.
causes/initiative vote/philanthropy vote/discussion/budgeting/news cycle/etc.
_The causes_
I seeded this system with the 7 causes I think sum up everything I would ever donate to.
However, benefactors can elect a replacement cause with overwhelming support. 
(6 votes - vote doesn't happen at the end of active week.)
Earthbux connects citizen researchers with policymakers and qualified scientists.
*end backlog*

- ✅ Topbar: EBX brand · profile badge.
- ✅ **§1a**
A public forum to direct pooled philanthropic missions. 
An independent research team to publicize their impact.
Earthbux News
you donate, we follow
(Login/Sign up) -- Vote now.
- ✅ **§1b**
In 2026, the world seemed at risk of total destruction. 
Earthbux was invented to give us control so we save it.
Bringing publicity to charity,
Enabling research based donations.
  — BUILT 2026-08-18: the couplet used to be the *title* of the §1c argument
  ("Bringing publicity to philanthropy"); it reads here now, in §1b's words.

- ✅ **§1c** — BUILT 2026-08-18
_"How it Works"_ Maximizing donor control.
Each mission undergoes 2 key elections:
1. Mission Election - Benefactors elect an *Initiative* (Week 0)
2. Organizaiton Election - Benefactors elect a *Philanthropy* (Week 7)

- ✅ **§1d** — BUILT 2026-08-18
_"A Public Forum"_ Crowdsourcing Ideas.
Each mission has its own discussion with 3 categories of post.
*1. Reviews* Cases or evaluations arguing why a cause, initiative, or philanthropy should or shouldn't be funded.
*2. Research* An in-depth study into a mission. 3 different types: 
Context (researches the cause and compares/contextualizes initiatives)
Investigation (researches the initiative and compares/investigates philanthropies)
Analysis (researches the initiative and the philanthropy and analyzes potential action plans)
*3. Budgeting* Itemized and cost-allocated items. 3 different types: 
Service (labor required — job · hourly rate · days)
Supply (commodities required — item · cost)
Support (connections required — an approval, professional or legal help; no cost line, because a connection is not a purchase)
- For 2 and 3, allow users to toggle between types to read the descriptions.

- ✅ **§1e** — BUILT 2026-08-18
_"What we do"_ Earthbux uses part of the pool to bring you the news.
Higher transparency => Lower cost
Lowest cost <-*Dormant(1/16) · Watching · Reporting · Auditing · Arbitrating(5/16)*-> Highest cost 

Benefactors vote by donating Earthbucks (1 EBX = 10c). 
Funding runway chart - "Everyone is granted 10 EBX per mission."
(Total funds / user count = weeks) Display #Activeusers.
  - The two rows link the election that decides them (`main.html` /
    `main.html?state=oe`) and carry **Week 0** / **Week 7** in the right column.
  - The ten-dime graphic stays: 10 EBX · ten dimes · $1 · every week.
  - **The runway changed meaning.** It used to be *Earthbux's n/16 share ÷ a
    week of voting*, which coupled it to the §1e scale. §1c defines it as
    **total funds ÷ user count**, so it is now the GRANT's runway: committed $
    ÷ (active members × $1). Both numbers come from one new endpoint.
  - **`GET /stats`** (new, public, `backend/app/routers/stats.py`) —
    `members · active_members · committed_ebx · committed_usd ·
    weekly_cost_usd · runway_weeks`. It exists because "Display #Activeusers"
    was being *estimated*: the page summed `voter_count` across every mission's
    phase-1 tally, counting vote rows rather than people and double-counting
    anyone who votes in more than one mission — 19 where the answer is 4. No
    identities in the response; `/admin/accounts` remains the only surface that
    names anybody.

## main.html (Election Page) — **the VOTING surface**
*Renamed 2026-08-26 (build-seq §1): "The name of this page is no longer the context
page. It is now the Election Page." Title, top-bar tag and this heading agree.*
*backlog*
- ✅ **Election Cards Update** — BUILT 2026-08-21 (build-seq §2)
  - ✅ no vote counts. **"Leader: x"** and **"My vote: x"**, each labelled, each
    allowed two lines. The card used to lead both lines with a NUMBER and put
    the name after an arrow, so the two things a glance is for — who is winning,
    and who I backed — were the least prominent text on it. The count is a
    column in the table for anyone who wants it.
  - ✅ no Discuss button on the OE card (it is in the voting panel), and no
    buttons at all on the ME card.
  - ✅ **the card IS the button.** Clicking anywhere on it filters the table and
    opens the vote panel — `voteOnCause(cause[, mission])`, which is exactly
    what the Vote button called. Fourteen controls became seven cards.
  - ✅ two lines of overflow on the OE initiative titles and on both value lines.
  - ✅ **two columns of three**, the bottom row gone with its Help and Commit
    buttons, and the allocations panel nestled between the columns under the
    annulus — painted in BOTH page states.
- ✅ **Allocations Panel** — BUILT 2026-08-21 (build-seq §0 + §2)
  - ✅ **two sets of two**: Unallocated (granted · purchased) and Committed (to
    an initiative · to an organization). One four-segment bar made the two pairs
    look like four peers; they are not. Two bars, each carrying its own pair,
    with the whole in the header.
  - ✅ **`Allocations  88 tokens  $8.80`** — the header says what it counts and
    what it cost, because voting IS donating. `EBX.formatTokenUSD`, 1 token = 10¢.
  - ✅ the explanatory paragraph is gone. What survives is the commit-by date,
    which is a fact about the tokens rather than an explanation of the panel.
  - ✅ Commit lives here, and means the right thing in each state: `commitAll()`
    on the OE side, `commitVotes()` on the ME side. It is the panel's button,
    not a mode's.
  - ✅ nominate/register, the mission link and the discussion link all moved
    into the OE election panel.
  - It sits in `.hero__center` under the annulus wrap, at the centre column's
    width — that is what makes it "between them and up against the bottom of the
    annulus" rather than below two columns that are taller than the wheel.
- ✅ **OE Election panel** — BUILT 2026-08-21 (build-seq §2)
  - ✅ **where the next token comes from** is a choice now, not an assumption:
    a source `<select>` (unallocated · purchase · **from another OE**) beside the
    amount. The third one finally reaches `POST /wallet/convert`, which has
    existed since 2026-08-20 with no way in — so a benefactor holding tokens in
    a race they had changed their mind about could not move them at all. A
    conversion IS a vote at the destination, so the control refuses without a
    philanthropy picked, and it says it spends one of three.
  - ✅ **the ballot is the ranked top 3.** A race with a dozen candidacies was a
    scroll, not a choice. A philanthropy already picked stays on the list
    whatever its rank — the one thing worse than a long list is one that hides
    your own vote — and the rest are counted off ("n more registered").
  - ✅ **"View Organizations"** replaced "Mission page": the page is where a
    race's organizations are read in full, which is what a benefactor looking at
    a three-name ballot wants from it.
  - ✅ two rows in the annulus centre. "Indigenous La…" named nothing at the
    exact centre of the page.

*EASY*
*end backlog*
- ✅ **Side cards** — each column runs the full height of the hero row:
  **top card flush with the bottom of the top cards, bottom card flush with the
  top of the cause toggle, the middle one exactly between** (2026-08-27b).
- ✅ **The glow is SELECTION** (2026-08-27b) — "the position of the upcoming
  election is enough to identify that it is upcoming", so the halo says which
  election the page is pointed at instead of repeating what the layout says.
- ✅ **Page toggle** — OE vs ME. **BELOW the annulus** since 2026-08-27
  (build-seq §2), centred under the wheel, and the glowing rail that ran off its
  right edge is gone. It sat above the annulus from 2026-08-09; the cause toggle
  has that place now, and a switch belongs with the thing it switches.
- ✅ **The 7 cause tabs** — **below the ME/OE toggle, at the foot of the hero**
  since 2026-08-27b (top bar → above the annulus → here, in three days). The
  three side cards in each column lock their bottom edge to this bar. "This will function as a toggle for the ME table and the CE panel
  as well as the election panel." A tab points the ANNULUS, the centre panel,
  the CE PANEL, the left top card and the TABLE at one cause; it does not touch
  the ring of election cards, and it does not scroll the page.
- ◑ **Annulus 1 — the PIE** (swapped in from cause.html, 2026-08-26)
  - The seven-sector wheel that used to be here is on cause.html now, where its
    sectors are that page's cause toggle. What sits here is the race: in ME the
    focused cause's initiative shares, in OE its philanthropy tally, with the
    seven-cause ring around it and the cycle now-marker on that ring.
  - A lone front-runner is drawn as a CIRCLE, not a 360° arc — an arc whose ends
    coincide draws nothing, and most early races have exactly one candidate.
  - **Rays**: three chevrons per cause outside the ring, pointing **clockwise —
    the way the now-marker travels** (2026-08-27b). Every arrow on either wheel
    points that way now.
  - ✅ **ME Center** - Next initiative election (upcoming cause, or the tab)
  - ✅ **OE Center** - Next philanthropy election (active cause, or the tab) — 2026-08-10 (§8)
  - The centre panel is HTML over the pie's hole and did not move; the pie's
    inner radius and the panel's diameter agree by construction.
- ✅ **The two top cards say the same thing in ME and OE** — REBUILT 2026-08-27
  (build-seq §2). **LEFT is the race still running, RIGHT is the race that just
  closed**, in both states:
  - **ME left** the focused cause's INITIATIVE election, with the one line that
    says what to do with the page: *"Select a cause, and vote."* (only there —
    the full-width how-to line above the grid is gone).
  - **ME right** the initiative elected this week, between two BARS: **"Winner
    of \<cause\>"** across the top and **"Elected \<date\>"** across the bottom.
  - **OE left** the philanthropy election closing soonest, same how-to line.
  - **OE right** the budgeting card, wearing the same two bars: **"Winner of
    \<tiv\>"** / **"Elected \<date\>"** — the organization election one race back.
  - The propose-an-initiative dialogue is off these cards entirely; proposing
    lives in the table's propose row.
- ✅ **The ring of election cards** — ME shifted one place CLOCKWISE on
  2026-08-27: the upcoming election (+1) left the ring for the top-left card,
  every other card moved up one, and a NEW card came in at the top right — **+7,
  the active cause's own next initiative election**, which had no card at all
  while the active cause occupied the top of the page. Left column +2 · +3 · +4,
  right column +7 · +6 · +5. The **OE ring keeps its orientation** — "Keep the
  orientation of the OE cards the same".
- ✅ **Allocations panel — PARKED at the bottom of the page** (2026-08-27) "until
  its design is complete". It hugged the underside of the annulus from
  2026-08-21; the ME/OE toggle has that place now and the side cards run flush
  to the election panel.
- ✅ **Under the table**: the cause filter is a **"Show all Initiatives"** button
  (2026-08-27). The cause is chosen by the toggle at the top of the page, so a
  second cause picker down there could only disagree with it; the select
  survives hidden because every filter path still reads and writes it.
- ✅ **Cancel beside Commit, everywhere** (2026-08-27) — the initiative slate,
  the organization amounts and the cause ballot each dial a draft that one press
  drops. Committing is still one-way once it lands.
- ✅ **Top cards**
  - **ME side**
    - **Left** Winner!
    - **Right** the just-elected initiative (see the two top cards above). The
      **Cause Election left this card entirely on 2026-08-27** — it is a PANEL
      **below the table** now (it was above the election panel for a day; the
      two elections running this week come first):

      ```
      | a |  c                                   | b |
      |   |  f    g    h    i                    |   |
      |   |  d                                   |   |
      |   |  e                                   |   |
      ```

      **a** one column of seven lines, colouring as the weeks of a streak are
      won (it was seven columns of one-to-seven lines, which drew the RULE
      rather than the progress) · **b** Show / Hide Cause Table ·
      **c** "Cause Election — \<holder\> holds the window that runs \<date\>",
      with this week's votes and my vote · **f** Nominate a Cause ·
      **g** make your case → · **h** Commit · **i** Cancel ·
      **d** keep \<incumbent\> or replace with \<challenger\> ·
      **e** the click-through pager over nominated causes.

      - It **persists across ME and OE** — that is why it is a panel.
      - **There is no cause toggle inside it.** Every cause holds exactly one
        OPEN window (the active cause's is slot 7, everybody else's is 8..13),
        so the seven page tabs and the seven replaceable windows are the same
        seven things: picking a cause picks its window. `data-slot` /
        `data-cause` on the panel say which.
      - **A vote is DIALLED, then committed.** Clicking keep-or-replace marks a
        draft and posts nothing; Commit sends it, Cancel drops it.
      - A row of the cause table selects the CAUSE that holds that window, so
        the panel always shows an open window and never a locked ballot.

      - ✅ **All 7 ballots votable at once** — BUILT 2026-08-21 (build-seq §1).
        The server used to open exactly ONE window (slot 7) and cap the slot at
        7, so a benefactor with something to say about the window five weeks
        past that had nowhere to say it and its streak clock could never start.
        `crud.CAUSE_CONFIRMED_SLOTS = 6` · `CAUSE_FIRST_OPEN_SLOT = 7` ·
        `CAUSE_SLOTS = 13`; `_slot_is_open` opens everything past the confirmed
        six, `cause_slate` returns all thirteen with a `confirmed` flag, and
        `cast_cause_vote` accepts 1..13 and refuses the confirmed ones by name.
      - ✅ **The 7 toggles are the 7 REPLACEABLE windows, in the order they run**
        — LAN Oct 6 · FOR Oct 13 · WIL Oct 20 · HR Oct 27 · HP Nov 3 ·
        ATM Nov 10 · OCE Nov 17, each carrying its own date. They used to be the
        seven CAUSES in cause order, which is the seven upcoming *initiative*
        elections — six of those are confirmed, so six of the seven toggles were
        locks. The nearest replaceable window is the first entry in the row,
        which is what "on the left of the 7 toggleable causes" now means.
      - ✅ **…and the dates are right.** "The nearest possible cause replacement
        day is at least 6 weeks out. This is correct in the CE table, but not in
        the top card." Both read it the same way now — the toggles are built from
        `_causeWindows()`, the same function the table's thirteen rows come from.
      - ✅ **No toggles in the CE vote area; a click-through pager instead.**
        "Users should be able to click through potential replacement causes, and
        see how much of the vote they have." The ballot is keep-or-swap — the
        incumbent on the left, one challenger on the right, « » between them and
        its share of this week's vote underneath.
      - ✅ **A cause can only be replaced by a NEW one.** `causeSuggestions`
        returns only `status === 'suggested'` causes, and `cast_cause_vote`
        refuses an active cause as a challenger — swapping two active causes
        around inside the rotation changes the order and nothing else, and would
        let a window be "won" by a cause already guaranteed to run six weeks
        later. Voting to KEEP the incumbent is exempt: that is not a replacement.
        `cause_ballot_state` also stops crediting a streak to an ineligible
        winner, so votes cast before the rule cannot accrue toward a swap the
        server would now refuse.
      - ✅ **Nominating a cause is a dialog**, like proposing an initiative —
        `EBX.Dialogs.causePropose`, same shell, and it asks what the cause is
        FOR rather than just its name and a colour.
      - ✅ Once the election card is created, the cause is confirmed.
      - ✅ **"Show Cause Table"** (on the CE panel) toggles the table to the
        cause table, and flips to **"Hide Cause Table"** to bring the elections
        back — the toolbar under the cause table is hidden, so nothing else does.
      - ✅ **The table** — 13 windows, 6 confirmed + 7 open. Only the nearest
        open one is tinted: all seven are votable, and seven tinted rows out of
        thirteen is a background, not an emphasis.
      - **Open question, not built**: `slot` is RELATIVE to the active cause, so
        the same slot number names a different calendar window each week, while
        `_week_winner` compares the same slot number across weeks to build a
        streak. That predates this pass and the seven-weeks-in-a-row rule is
        written in those terms; if a streak should follow a fixed DATE rather
        than a fixed distance-from-now, that is a change to `CauseVote` and the
        streak query, not to the UI.
  - **OE side**
    - **Left** This weeks OE
    - **Right** next-cause Budgeting card 
- ✅ **Election cards** 
  - **Side card - ME** — `{cause} {mission_num}`
  - **Side card - OE** — `{tiv_title}`
- ◑ **Table** -list columns below-
  - ◑  **Vote dialog** 
    - ✅ **ME** - Sliders to split vote - | starred | My commitment | tiv title | total ebx | cause | [vote] | — columns BUILT 2026-08-10 (§8)
      - ◑  **Expanded rows** - In development
    - ✅ **OE** — REBUILT 2026-08-19, REVISED TWICE on 2026-08-20 (build-seq §1).
      Three things stacked, in the order the decision has: **what I have** →
      **which race** → **the eight deadlines**.
      - **The action row is GONE** (2026-08-21, build-seq §2). It existed for
        one day. Per Jax on 2026-08-20: "Discuss, register/nominate, and mission
        page should all be in the row with the unallocated slider, which should
        be above the cause-toggled OE race area." Per Jax on 2026-08-21, the
        balance belongs under the annulus in **both** page states, and the three
        links belong in the election panel — so the row had nothing left to hold
        and both halves went where they were actually about:
        - **the balance → the allocations panel** under the annulus (see the
          main.html backlog above, ✅ *Allocations Panel*), painted in ME and OE
          alike. Commit went with it, because it is the button that spends it.
        - **the three links → the OE election panel**, which is about the race
          they describe. "Mission page" became **View Organizations**.
        - **§0 (2026-08-21) — the Commit button was invisible, not missing.**
          `.vb-btn` paints `background: var(--vb)` with `color:#0f1a14`, and
          `--vb` was declared on `.votebar` only; the action row was that panel's
          SIBLING, not its child. So Commit rendered near-black text on a
          near-black panel at 0.35 opacity. The ghost buttons beside it survived
          only because `--ghost` overrides both properties, which is exactly why
          Discuss and Register read fine and Commit read as absent. `.oe-actions`
          declares the variable it uses, disabled means outlined rather than
          dissolved, and `oe_check` asserts CONTRAST rather than presence.
          The same fault was live in `.cause-election` (Propose and the two
          pager arrows) and is fixed the same way.
        - **Register → "Nominate / Register"**: an organization arrives two ways
          and one verb hid the other.
        - **Stale copy removed**: the empty dialog told a benefactor to "press
          its **Vote** button", a control deleted on 2026-08-20b, and carried a
          second copy of the Register button already in the row above.
        - "Allocated to initiatives" is summed client-side from the committed
          phase-1 vote rows, and counts only missions whose initiative election
          is still open — once `finalize_p1` runs, that commitment is already
          inside `wallet.staked_ct` and counting it twice would overstate the
          bar. There is no server-side ct figure for the ME side until the ME
          table is made one-way (backlog).
      - **The dialog**: nominated philanthropies, the pool, and an **amount
        field** beside the choice. One-way money is typed, not dragged.
      - **The table**: exactly eight rows, one per mission with an OPEN
        philanthropy election; the eight closing soonest if the database holds
        more.
        | starred | **My commitment** (read-only) | tiv title | total pool | **Vote date** |
        - Sorted by DEADLINE, soonest first, on entry to the mode — "the next
          election at the top and the subsequent elections proceeding
          downwards". Headers still re-sort once you are there.
        - **No Vote column** — "clicking on the row is sufficient".
        - **Rows do not expand.** A panel unfolding inside a queue of eight
          deadlines pushes the other seven off the screen.
        - **No scrollbar**, sized to its eight rows: "it should be a consistent
          size to fit the 8 races".
        - **No filter, no search, always all eight.** A filter on eight rows can
          only hide a race a benefactor still has money in — which is what
          pressing **Vote** on an OE card did, so that button is gone from the
          cards too.
        - The active-cause row is tinted and tagged **THIS WEEK**: the only row
          granted ct may enter ("2 options, not 9"). Purchased ct may enter any.
        - A row holding ct that has been converted says how many of its three
          conversions are left.
      - **Committing is one way.** The sliders are gone with the rule: ct leaves
        the unallocated bar for a race and only a conversion moves it again.
        `POST /wallet/commit` (amount + philanthropy, add-only) and
        `POST /wallet/convert` (race → race, spends one of three, philanthropy
        required) are the two writes; `PUT /wallet/stake` is deleted.

## cause.html (Discussion) **the DISCUSSION hub**
*backlog*
- [x] **OE election annulus** Pie chart of election status, just like in the ME
  — SUPERSEDED 2026-08-26: the pie went the other way. Both phases of the pie
  (initiative shares · philanthropy tally) are on main.html now, mode-aware.
- [ ] **Add cause suggestion** Remove the cause suggestor from main.html and include here, with options to make a case and reply - backlog
- [ ] **Linked entities** Linked initiatives should be grayed out after the initive is elected. Linked organizations should be grayed out after the philanthropy is elected.
- [ ] **Explanations** Remove the explanations and the examples and the target-open-reward-rating from all posts. Include a brief explanation in the dialogue box. For example, replace "write your context" with "What is the curent state of <cause_name>". Also delete the "linked automatically" line and the "Already posted one?" line. There will be a posting rules explanation elsewhere.
- [ ] **Budgeting report** Remove the "Why this is needed" section and add a "Budgeting report" section in the table at the bottom.
- [ ] **Research** Similar to the current budgeting ux, when research is toggled, it should have 1 row in "Leading research" for each post type.
- [ ] Add volunteer opportunity. Travel link? -backlog
- [ ] **Post links** Case posts only have maximum 1 link. Research posts can have numerous links. Context can link tivs, investigation can link phls, and ALL can link budget items.
*EASY*
- [ ] **Replace "supplier" with "quantity"** - better flow
- [ ] **Links** Head the links column with "Add links" and remove the word "Linked" from the buttons. This should provide a little bit more horizontal space for writing.
- [ ] **Budgeting redundancy** There are 3 rows just below the voting dialogue saying the 3 post types, and there are also 3 rows below showing the posts. Remove the former, and highlight the one of the latter that is currently toggled.
*end backlog*

- ✅ Active-missions bar (7 cause squares) — MOVED to main.html's top bar on
  2026-08-26 (build-seq §2). The top bar carries a page tag ("Discussion ·
  \<cause\>") instead; the wheel is the cause toggle now.
- ◑ **Annulus 2 — the WHEEL** (swapped in from main.html, 2026-08-26).
  `EBX.Annulus`: seven sectors, its own now-marker, rotating with the cycle
  clock, the page's cause lit. **No rays** since 2026-08-27 — they were spikes
  around a control — and the chevron sectors **point the other way**, toward the
  cause whose turn comes next rather than the one whose turn has passed. Above
  it: *"Click on a cause to participate in the discussion."* **Clicking a sector changes cause** — "the
  discussion page toggles itself from the 7 annulus sections". The pie that used
  to be here is on main.html. The phase-aware centre stack it drew in SVG is an
  HTML panel over the wheel's dark core (`renderAnnulusCenter`), unchanged in
  content: today / the race / its phase / its decision date.
- ◑ **Left cards** — leading initiatives (ME); leading philanthropies
- ◑ **Right cards** — page 1: phase-1 (top) / phase-2 (middle) / most-recent prior (bottom); pages 2+ previous missions.
- [ ] **DISCUSSION**
  - [ ] **Case - cau <review>**
    - Open always - rolling
  - [ ] **Case - tiv <review>**
    - Open mission_open-initiative_elected
  - [ ] **Case - phl <review>**
    - open initiative_elected - philanthropy_elected
  - [ ] **Evaluation <review>**
    - open post philanthropy_elected
  - [ ] **Context <research>**
    - open post cause_confirmed
  - [ ] **Investigation <research>**
    - open post initiative_elected
  - [ ] **Analysis <research>**
    - open post philanthropy-elected
  - [ ] **Service <budgeting>**
    - open post initiative_elected
  - [ ] **Support <budgeting>**
    - open post initiative_elected
  - [ ] **Supplies <budgeting>**
    - open post initiative_elected

### ✅ The discussion box (BUILT 2026-08-12, build-seq §1)

| § | Section | Date | What it holds |
|---|---|---|---|
| 1 | "atm2 (or whatever cause name and number it is) confirmed" | `T−14wk .. T−7wk` (Display T-14 wk until election actually running) |*case for the cause*|
| 2 | "Mission open" | `T − 49d` | The initiative election. Open: compose **case** (must reference the selected initiative) + **context**. Past: winning initiative + top case. |
| 3 | "Initiative Elected" | `T` | Before: **investigation only**, each naming ≥1 philanthropy. During: investigations target any org in the mission; **case for a philanthropy** shown beside the case for the initiative with the **aggregate** score; context migrated here. After: winning org + its case. |
| 4 | Philanthropy Elected | `T + 8wk` | Before: **S/S/S budgeting only**. After: context + investigation migrated here, **analysis** and **evaluation** open, budgeting filtered to mission + philanthropy. |
`T` = **mission started**


## mission.html — Mission page (REBUILT 2026-08-01 · jax notes 2 layout)
*backlog*
- I'm going to start moving things to mission.html that don't belong on cause.html. This is to get them out of the way without losing them. Don't worry about making mission.html look good for the moment.
- Mission page does not form until after 7-week budgeting period. It only exists for active missions now. Sorry for the rollback.
- The top right card on cause.html can toggle between all potential tivs.
- Move recaps to mission page !!!
- Cause page redraw.
*end backlog*
> Grid: **a** mission toggle ←→ + initiative search · **g** name + core info ·
> **b** profile + membership status · **c** post stream (3 category tabs:
> budgeting / mission_support / review) · **e** phase circle, 3 phases
> (ultimately a 3D globe) · **d** dated progress log ("Elected {tiv} with
> {EBX}", "Approved {step} for {cost}"…) · **f** pool (in-pool / committed /
> withdrawn). Cause color accents the whole page.
- ✅ Layout a–g live against the API (posts, pool, steps, tallies).
- ✅ **Click-through legal agreement** gating register/claim (kept verbatim).
- ✅ Competing-organizations card kept below the grid (slot TBD in globe era).
- [ ] **Full conversation** — the **P3+ post source**; users originate/continue
  mission threads here (the resolutions link from other surfaces lands here).
- [ ] **Suggestions → budget** — S/S/S *suggestion* posts (open the moment the tiv
  is elected) feed the org's budget & plan builder, between the guaranteed floor
  and the uncapped max.
- [ ] **Steps → resolutions** — 7–12 step ring; *suggestion* (S/S/S) posts resolve
  into coin-value bumps; early resolution flagged for bonus.
- [ ] Progress reports (org report vs EN parallel report, benefactor-moderated).
- [ ] Member communication channel (contributor / representative / executive / beneficiary).
- [ ] Mission annulus / ring widget (deadlines, 7–12 steps).
- [ ] Creditcoin front/back + 3D earth (born here).

- [ ] **Left (Money input)**
- [ ] **Right (Mission output)**

- ◑ **Annulus** (This annulus will have many layers.) The first layer is the post-support layer. I'm going to run every post through a filter to determine which are critical and which are spam/scam.
Note - need to have a way for bens to contact phls. -> We send out weekly messages to phls informing them of content created. Each thread will be flagged by our system as green/orange/red where green is Useful, orange is CRITICAL but helpful, and red is spam scams or unsupported slander that we apologize for and ensure them we are working to keep it off our platform.
- On the mission page, this is the annulus.
- This is only for posts that have an organization tag- case, investigation, and evaluation.
  - ✅ **LAYER 1 BUILT — 2026-08-08.** `posts.flag` (`green|orange|red`) +
    `flag_reason`, migration `c8a3d5b71f04`. Every post is rated on the way in
    by `post_config.classify_flag`, which is **a stub that returns green** —
    so everything is green today and the page says so rather than implying a
    filter ran. Only the org-tagged types are read off it
    (`post_config.ORG_TAGGED_TYPES = case · investigation · evaluation`).
    `GET /missions/{id}/post-support` returns the layer grouped **by
    organization** — counts per flag, plus each thread with its own flag,
    reason and reactions — which is the shape of the weekly digest a
    philanthropy receives. Ordered most-flagged first, so the digest leads with
    what needs an answer. `POST /posts/{id}/flag` is the staff override
    (green→orange→red, validated); it is the only way a non-green appears until
    the classifier is real.
    On the page: a ring under the grid, **one arc per rated thread**, grouped
    by org with a gap between groups and coloured by flag, the total in the
    middle; a legend naming what each colour means with its count; and the
    per-organization thread list beside it. Below it, the note that every
    philanthropy gets a weekly message and that red threads carry our apology.
  - [ ] Layers 2+ — the annulus is designed to take more; nothing decided yet.
  - [ ] The real content classifier (this is the whole point of the layer).
  - [ ] The weekly digest itself — needs a mail transport, same blocker as the
    self-serve password reset.
  - [ ] Ben → phl contact path.


## profile.html — Profiles
*backlog*
- [ ] **BUILD 3D EARTH**
- [ ] **Wallet** — the model is SETTLED and the backend is built (2026-08-19,
  `docs/token_model.md`); what is missing is this page's surface for it.
Cash - Uncommitted.
Tokens - Up to 10 uncommitted, rest Committed, not yet converted
EBX - Committed and converted - Tied to a mission.
  - Built: `GET /wallet` returns the four segments — **free · staked · claimed ·
    minted** — in centitokens, plus the week's grant. One bar, four segments.
  - The bins and the states are not the same list: *claimed* is a state of money
    that has left the Tokens bin and not yet become a coin. Cash · Tokens ·
    Coins are the bins; free · staked · claimed · minted are the states.
  - Naming: **EBX stays the unit** (1 EBX = 1 token = 10¢). The third bin is
    **Coins** (`models.CreditCoin`, and this page's existing CC), because a bin
    called EBX would make "10 EBX per week" name the wrong thing.
  - 2026-08-20: the wallet also carries the grant's **commit-by date**, the
    **purchased** slice (undated, goes anywhere), and per-stake **conversions
    left** — so the profile surface, when it is built, can show a coin's two
    elements: what the initiative election made of these ct, and every
    philanthropy they have stood behind since.
  - **"Each benefactor's EBX available to donate should always be visible to
    them"** (CONVERSATION, 2026-08-20) — the unallocated strip does this on the
    OE table only. It belongs in the header, on every page.

- on the profile page, the users 3 research posts should be displayed and editable, toggled by mission in the choices table/credit coin wallet.
- [ ] **ORG MODE** I need to build out org registration after cause.html is complete.
  - What does the experience look like? Well, first the user is instructed to search their org in our database. If its there, they claim it. If not, they register it.
*end backlog*

2 Wallets - One for credit tokens (CT) (Essentially cash) and one for CC (Essentially donation receipts). CT are static. CC can be exchanged.
Credit tokens consumed by a phl "Fund" credit coins. Tokens spent by Earthbux defund them. This is one balance driving the rate. The more efficient/transparent money spent by the phl, the more valuable their donation.
- ✅ Benefactor profile: credit-coin wallet, choices table, settings.
- [ ] **All of the signed-in user's activity** — users can **reply** to posts from
  here. The choices table **toggles a discussion area**; if the user hasn't posted
  about a mission, show that mission's **leading posts** instead. Clicking a post
  opens the **Context** (P1/P2) or **Mission** (P3+) page.
- [ ] **Mission-member messageboard** — member pages carry a deeper messageboard /
  discussion console, **separate from posts**.
- ✅ **Switch to Organization mode** gated on holding a credit coin → membership picker.
- [ ] Organization profile: initiative coins, tasklist, annulus 4, memberships.
- [ ] Beneficiary profile (unique page; voice at phase-2 start).
- [ ] Credit badge colorization (participation perk).

## admin.html — Data console
- ◑ Search by user / filter by election / by organization / export CSV / sort by timestamp.
- ✅ **Accounts · reset password** — 2026-08-08 (§0d). `POST
  /admin/accounts/{id}/reset-password`, staff-only, issues a one-off temporary
  password and returns the plaintext exactly once for staff to send to the
  address on the account. Earthbux has no mail transport, so a self-serve
  *forgot password* flow (emailed single-use token, expiry, redemption page) is
  on the backlog; this recovers a locked-out account today.
- ✅ **Derived tallies stay derived** — 2026-08-08 (§0). Removing an account now
  rebuilds `Pool` and `MissionCandidacy.p2_vote_tally` for every mission it
  touched, and a startup hook repairs what earlier removals left behind (atm0
  was carrying 150 phase-2 EBX and a 5-vote tally from a deleted pilot account).
- [ ] Event log (vote_events: CAST/UPDATE/REMOVE), duplicate/invalid-vote flags.
- [ ] Full mission table; org verification queue (EN, 1/week).
- [ ] In the benefactor accounts table, add most-recent-vote date and target columns for each of the 3 votes.
- [ ] In the ledger transactions table, make sortable by benefactor account and by target + action.

## Backend (FastAPI + SQLAlchemy + Alembic)
- Models: Cause, Mission, Initiative, Organization, BenefactorAccount, Membership,
  MissionCandidacy, VoteP1, VoteP2, Pool, CreditCoin, Post, PostVote, Transaction.
- Endpoints: causes, missions, initiatives, organizations, candidacies, votes (p1/p2),
  posts, benefactors, transactions, admin, auth, **wallet** (`GET /wallet`,
  `GET /wallet/rows`, `POST /wallet/commit`, `POST /wallet/convert`,
  `PUT /wallet/org`), stats.
- The money lives in `token_model.py` (pure arithmetic) and `wallet.py` (the only
  module that lets it touch the database; committing is one way, and
  `convert_stake` is the only path out of a live race) — `docs/token_model.md` is the prose
  version. `finalize_p1` carries every backer's stake into the winning
  initiative's organization election and writes the coin's first element;
  nothing rolls to a cause's next election any more.
- **§0 (2026-08-21) — the race pool reads the STAKE now.** `p2_tally` measured
  phase-2 weight with `p2_ebx_by_ben` (surviving `VoteP1.ebx_committed` for the
  mission) and knew nothing about `VoteP2.stake_ct`, which is what
  `POST /wallet/commit` has written since 2026-08-19. So committing tokens moved
  the benefactor's own row and their balance and left the race pool exactly where
  it was — "the OE race pool is not updating when I commit votes". `crud.p2_stake_by_ben`
  asks `wallet.stake_ct_of`, the one function that already knows how to read a
  stake, so there is no second opinion; `unassigned_ebx` is computed from the same
  map, which also fixes a stake committed with no philanthropy named vanishing from
  the pool entirely.
- **§1 (2026-08-21) — the cause ballot is thirteen windows wide.**
  `CAUSE_CONFIRMED_SLOTS` 6 · `CAUSE_FIRST_OPEN_SLOT` 7 · `CAUSE_SLOTS` 13.
  `_slot_is_open` opens every window past the confirmed six, `cause_slate`
  returns all thirteen with a `confirmed` flag per slot, `cast_cause_vote`
  accepts 1..13 and refuses **an active cause as a challenger** (only a
  nominated one can take a window; keeping the incumbent is exempt), and
  `cause_ballot_state` will not credit a streak to an ineligible winner.
- [ ] Org claim/verify endpoints + acceptance record for the legal agreement.
- [ ] Guaranteed-to-pool rate (unclaimed vs claimed) in pool math.
- [ ] **The unit is TOKENS on the voting surface, EBX elsewhere.** main.html
  says tokens everywhere (2026-08-21, build-seq §0) via `EBX.formatTokens` /
  `EBX.formatTokenUSD`; `formatEBX` survives for the credit badge and the
  ledger. cause.html, mission.html and profile.html still say EBX — sweep them
  too, or decide EBX is the ledger's name and tokens are the vote's.

 ## Long term
  - have 6 lower cards (Not either top left or top right) rotating with their center on the ray normal to the midpoint of its annulus section. Long term because requires major layout change.
  - You only receive as much ebx (max 10) as you committed to elect an org in the previous week.
  - [ ] **Bottom row of the 7 causes** This will fold in with the ambitious side card redesign later.