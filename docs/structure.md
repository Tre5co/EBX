# Structure — page-by-page build spec

## Site layout
| Surface | Page | What it shows | Posting |
|---|---|---|---|
| **Landing** | `index.html` | About Earthbux | Connects and explains everything | 
| **Context** | `main.html` | **voting home** - context for each tiv/phl | Can suggest causes/initiatives and nominate philanthropies |
| **Discussion** | `cause.html` | Full discussion home. | All benefactor posting |
| **Mission** | `mission.html` | Mission status page - | phl/ebx posts, budget resolutions |
| **Profile** | `profile.html` | all activity from the signed-in user | active threads |

## index.html (Landing) — **About Earthbux**
*backlog*
- **Donation breakdown** If I put $20 / week into earthbux, 100% of that is a donation.
$2 is going to the best researchers on our platform, $0-6 is going to Earthbux, and $6-18 is going to the mission.
Any of that $6-18 that is put towards the org election or specefied-must-donate will end up going to A mission.
- [ ] Suggest weekly/monthly/yearly donation to cover many missions.
- [ ] The philanthropy link should go to the cause.html of this weeks active mission.
- [ ] **Links** Initiative should link to the ME main.html (already does) and Organization should link to the OE main.html.
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
- ✅ **§1c**
Bringing publicity to philanthropy,
Enabling research based donations.

Higher transparency => Lower cost
Mission pool consumed by Earthbux
Lowest cost <-*Dormant(1/16) · Watching · Reporting · Auditing · Arbitrating(5/16)*-> Highest cost 

- ✅ **§1d**
_The system_ Each mission is slated to last a year, but can last longer or end sooner.
1. Commit tokens to elect an initiative in each weeks cause. | A 1 year mission targeting the winning initiative commences.
2. Commit to a philanthropy who will lead the mission | Tokens become mission-valued "credit coins" that are exchangeble and tax-deductable.
3. Determine how to allocate funds. | The top-rated context, investigation, and analysis studies are rewarded with credit coins.
4. Win Research Grants | Grow your credit.

Everyone is granted 10 EBX/week to contribute to the decision-making process for each mission.

Funding runway chart
Donating is currently funding $1 per week per active community member.
(Total funds / user count = weeks) Display #Activeusers.

- ✅ **§1e**
_The causes_
I seeded this system with the 7 causes I think sum up everything I would ever donate to.
However, benefactors can elect a replacement cause with overwhelming support. 
(6 votes - vote doesn't happen at the end of active week.)

## main.html (Context) — **the VOTING surface**
*backlog*
- [x] **New helpful rule** The active cause OE side annulus center displays the UPCOMING (oldest) philanthropy election, not the new one. — BUILT 2026-08-10 (§8): was `_electingMission` (newest open), now `_finalizingMission`. Reads Carbon Capture Expansion · Aug 11, and its date now comes from the race it names.
 - backlog - think about turning these 7 cause-election bars into an annulus to fit the theme.
- [ ] **Roll to next mission slider** should remain editable until the phl is elected. Replace "keep here" with "commit to <tiv_name>". The 10-20% automatically added to the pool should also count towards that users commit and vote weight.
- [x] **OE Center of annulus** still says methane leak detection grid — FIXED 2026-08-10 (§8), same fix as the rule above. Label also reads "Philanthropy election".
- [ ] **Remove old page toggle** Below annulus on the left
- [ ] **Phl commit finalization** The commit is not finalized until the election date of the philanthropy. The user should be able to access the slider to edit the amount they are committing until the last day.
- [ ] **Table row edits** see structure below
*end backlog*

- ✅ **Page toggle** — OE vs ME - Above annulus, center, below top cards
- ◑ **Annulus 1** — Rays out. orbited by election cards
  - ✅ **ME Center** - Next initiative election (upcoming cause)
  - ✅ **OE Center** - Next philanthropy election (active cause) — 2026-08-10 (§8)
- ✅ **Top cards**
  - **ME side**
    - **Left** Winner!
    - **Right** Cause Election
  - **OE side**
    - **Left** This weeks OE
    - **Right** next-cause Budgeting card 
- ✅ **Election cards** 
  - **Side card - ME** — `{cause} {mission_num}`
  - **Side card - OE** — `{tiv_title}`
- ◑ **Table** -list columns below-
  - ◑  **Vote dialog** 
    - ✅ **ME** - Sliders to split vote - | starred | My commitment | tiv title | total ebx | cause | [vote] | — columns BUILT 2026-08-10 (§8)
    - ✅ **OE** - Slider to commit vote forward - | starred | My commitment | tiv title | total pool | Week-0-date | [vote] (or <phl>) | — columns BUILT 2026-08-10 (§8); an elected race names the philanthropy in place of the button. Week 0 = the mission's own anchor.
- ◑  **Expanded row** - In development

## cause.html (Discussion) **the DISCUSSION hub**
*backlog*
S/S/S - Specific suggestions - P3 onward
- [ ] **Missing orgs** Carbon capture expansion is not showing the organizations competing for it in the lhs cards.
- [ ] **View and Propose initiatives** Change these 2 things (currently below lhs cards)
  - Delete "View initiatives" and change "Vote on context page" to simply "Vote"
  - Add propose an initiative dialog to area 1 (moving into ares 2 when it becomes active).
- [ ] **Add cause suggestion** Remove the cause suggestor from main.html and include here, with options to make a case and reply
- [ ] **Discussion Toggle** Each mission (or potential mission) toggles the full-page discussion to that entity. So clicking on one of the potential tivs on the left of the annulus means every post (only case an context will be available) is tagged with that tiv. This migh already be complete.
- [ ] **Move the header to above the annulus** *(not built — outside the §8 pass)*
- [ ] **Create "Discussion" section** Add a section titled "Discussion" in cause.html between annulus and timeline. The 3 tabs for each category of post bring up a 1-sentence description of that category. Within each tab toggle the types of post. In the dialogue area, show the target(s) of the post type, the phases it is open, the reward, a description and example post, and explain the rating system (rating systems are consistent through categories.) BACKLOG this - description not perfect - Will use to balance with the actual discussion sections.
- [ ] **Move down the top of the timeline key** to align it with the top of the cause finalized row. - balance with above step
- note - s/s/s items can be suggested any time, but they can't be voted on until the budgeting opens.
*end backlog*

**Annulus** Toggles between phases.


###

### ✅ The four-section timeline (BUILT 2026-08-10, build-seq §1)
The page is four dated sections, one open at a time. The rail on the left and
the section heads are the same set of buttons.

| § | Section | Date | What it holds |
|---|---|---|---|
| 1 | "atm2 (or whatever cause name and number it is) confirmed" | `T−14wk .. T−7wk` (Display T-14 wk until election actually running) |*case for the cause*|
| 2 | "Mission open" | `T − 49d` | The initiative election. Open: compose **case** (must reference the selected initiative) + **context**. Past: winning initiative + top case. |
| 3 | "Initiative Elected" | `T` | Before: **investigation only**, each naming ≥1 philanthropy. During: investigations target any org in the mission; **case for a philanthropy** shown beside the case for the initiative with the **aggregate** score; context migrated here. After: winning org + its case. |
| 4 | Philanthropy Elected | `T + 8wk` | Before: **S/S/S budgeting only**. After: context + investigation migrated here, **analysis** and **evaluation** open, budgeting filtered to mission + philanthropy. |
`T` = **mission started**

- Image attachments on posts —Image generation technology? Build an image search tool that finds/creates a good open source picture to represent the mission.

- [ ] Post composer (per-row, future pass) — Helpful / Neutral / Harmful + Reply; category by phase & scope (README §5).
Case - for/against

Context - tiv-research
Investigation - org-research
Analysis - Combined-research

Evaluation - star-rating

- ✅ Active-missions bar (7 cause squares).
- ◑ **Annulus 2** — inner pie (phase 1 = initiatives, phase 2 = org vote share), now-marker.
- ✅ **Left cards** — leading initiatives; ◑ **swap to competing organizations in phase 2** (paged, vote, buy-more).
- ◑ **Right cards** — page 1: phase-1 (top) / phase-2 (middle) / most-recent prior (bottom); pages 2+ previous missions.


- ✅ **§2 The P3 budgeting area is REPLACED by the three-band box** —
  2026-08-08, built to Jax's drawing: one frame, three bands, `sort by org`
  pinned right on the last one.
  - **a · Budgeting** (top) — service / supply / support suggestions, ranked by
    approval. A suggestion is costed or it is not a suggestion: every budgeting
    post carries **one setup-time estimate and one cost estimate**
    (`posts.est_setup_days` / `est_cost_usd`, required server-side in
    `crud.create_post` via `post_config.requires_estimates`). Composer takes
    kind · text · setup (days) · cost ($). New posts write `category:'budgeting',
    type:kind`; the legacy `category:'context' + stance` rows still render.
  - **b · Research** — one tile per leading type (**Context · Investigation ·
    Analysis**) showing that type's **highest-rated title**; click a tile to
    open its **ranked list**, with a search box scoped to it.
  - **c · Reviews** — cases and evaluations grouped by the organizations
    **running / registered** for the mission, in org-race order, with the
    **initiative** as its own group (always shown, even empty). The
    **sort-by-org** select filters to one group.
  - Replaces `renderSuggestions` / `sssApprove` / `sssSuggest` / `#sss-area`.
- [ ] **Pending budget items** surfaced in the resolutions area.
We will need an indicator / display for when a benefactors vote won.
     ______________________________________________________date_
    |winning_tiv Organization Election      |total fund   |     |         
    | ______________________ |  my_vote | my_commit     |vote  || This row shows which organization the logged-in benefactor has their vote going towards
p2  ||Leaderboards*         | _______  ______   _______        || *Not the recap, which it currently says. this is the organization race which will be elected at the date above
    ||                      ||sent   ||Limbo  ||wdrawn ||wdraw || *This row is all totals, not specific to benefactor
    ||                      ||_______||_______||_______||purchs||
    ||______________________|___________________________________|
    | evaluations of selected org or the one they are voting for| if none selected from leaderboard. Links to the expanded table row for that org.
    | Analysis for this mission                                 |
    |___________________________________________________________|
    _______________________________________________________date
    |"        *                "   |Posts recap:                | *As is
    | WINNER                       | best case for              |
p1* | ___my_vote. its_%_of_total__ | leading contex             | *recap
    || 2nd, 3rd, 4th.*            ||                            |* Only those 3. 
    ||                            ||                            |
    ||____________________________||                            |
    |______________________________|____________________________|

- For p1 pre-recap show 1 post each from mission support (top) and review (bottom) and dialogs below each to create your own post. You can toggle within each category between post types. You can page through the posts (by clicking/swiping left/right) and vote or reply to them.
- For phase 1, evaluation, Investigation, and analysis are grayed out. Evaluation is also grayed out through phase 2.

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
  posts, benefactors, transactions, admin, auth.
- [ ] Org claim/verify endpoints + acceptance record for the legal agreement.
- [ ] Guaranteed-to-pool rate (unclaimed vs claimed) in pool math.

 ## Long term
  - have 6 lower cards (Not either top left or top right) rotating with their center on the ray normal to the midpoint of its annulus section. Long term because requires major layout change.
  - You only receive as much ebx (max 10) as you committed to elect an org in the previous week.
  - [ ] **Bottom row of the 7 causes** This will fold in with the ambitious side card redesign later.