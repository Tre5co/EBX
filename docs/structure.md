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
- Explain why a philanthropy and an organization are the same thing.
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
_The system_ Each mission is slated to last a year, but can last longer or end sooner.
1. Commit tokens to elect an initiative in each weeks cause. | A 1 year mission targeting the winning initiative commences.
2. Commit to a philanthropy who will lead the mission | Tokens become mission-valued "credit coins" that are exchangeble and tax-deductable.
3. Determine how to allocate funds. | The top-rated context, investigation, and analysis studies are rewarded with credit coins.
4. Win Research Grants | Grow your credit.

Lowest cost <-*Dormant(1/16) · Watching · Reporting · Auditing · Arbitrating(5/16)*-> Highest cost 
Mission pool consumed by Earthbux <- Move inside table


Everyone is granted 10 EBX every mission to research and contribute to each mission.
We connect citizen researchers with qualified scientists and 


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
- [ ] **Phl slider persistence** The commit is not finalized until the election date of the philanthropy. The user should be able to access the slider to edit the amount they are committing until the last day.
- [ ] **Roll to next mission slider** should remain editable until the phl is elected. Replace "keep here" with "commit to <tiv_name>". The 10-20% automatically added to the pool should also count towards that users commit and vote weight.
- [ ] **phl vote onclick tweaking** Currently, it opens and closes every time you click on it causing a bug where a mission is selected but its vote dialog is not open. When toggled by cause, the table should require a section to be toggled and this section should necessarily have the vote dialogue open
- - [ ] **OE voting UX** Clicking "Vote" on any OE needs to bring up the org election in the table below. -- clicking vote on the active cause on the ME side (because it is technically an OE) toggles the page to OE and also brings up the vote
  *(These two are the same mechanism — row selection and the vote bar — and are
  the NEXT main.html pass. Not built 2026-08-12: the four items below were, and
  touching the selection path without a test that drives a real vote would put
  the only working voting surface at risk.)*
- [x] **Timeline start/end** — BUILT 2026-08-12. `.hero__togglerow` is full-bleed: a lit rail runs from the toggle's right edge to the edge of the screen, with an invisible twin on the left keeping the toggle centred.
*EASY*
- [x] **Remove "next votes" indicator** — DONE 2026-08-12. Markup, `renderControlBlock` and every `.nextvotes*` rule deleted; the topgrid is two cells again. `window.renderControlBlock` survives as a no-op because the hero render calls it.
- [x] **Remove old page toggle** — DONE 2026-08-12. The hidden duplicate under the annulus (`#main-toggle-btn` + `#main-showing`) is gone, and `setMainMode` no longer writes to it.
- [x] **Mission/OrganizationS elections PLURAL** — DONE 2026-08-12 on the state toggle, which names the KIND of election. A card naming ONE race stays singular.
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
      - ◑  **Expanded rows** - In development
    - ✅ **OE** - Slider to commit vote forward - | starred | My commitment | tiv title | total pool | Week-0-date | [vote] (or <phl>) | — columns BUILT 2026-08-10 (§8); an elected race names the philanthropy in place of the button. Week 0 = the mission's own anchor.
      - ◑  **Expanded rows** - In development

## cause.html (Discussion) **the DISCUSSION hub**
*backlog*
- [x] **Budgeting/R&D** — BUILT 2026-08-12. No link rails in budgeting; no target/open/reward/rating chips and no examples; the three kinds are titled one row each (🛠 service · Labor required / 📦 supply · Commodities required / 🤝 support · Connections required). Toggling s/s/s swaps the row that REPLACES the title — service `|Job|hourly rate|days needed|`, supply `|Item|Supplier|Cost|`, support `|Item|` — **+ Add** appends it to the post's list, and the area below prints the three tables across every budgeting post on the mission, each row approvable. Threads are shared between benefactors and the philanthropy running the mission (said on the page; the philanthropy-authored side is not built).
  - **Where the rows live**: new `posts.line_items` (JSON), migration `a1f6b3c92d47`, applied automatically at server start. `est_setup_days` / `est_cost_usd` are still required for budgeting but may now be DERIVED — `post_config.estimates_from_line_items`: service = Σ days and Σ rate × days × **8h** (`HOURS_PER_DAY`, an assumption, named not inlined), supply = Σ cost, support = 0 (a connection costs nothing to ask for). Pre-2026-08-12 budgeting posts have no rows and render as one row built from their title + estimates rather than disappearing.
- [ ] **Add cause suggestion** Remove the cause suggestor from main.html and include here, with options to make a case and reply - backlog
- [x] **Vote link from header** — BUILT 2026-08-12. "Phase 2 — Org Election" was a fact about our model, not something to do; the header now reads **{mission} · {phl}** · **[Vote]** *to elect an initiative / a philanthropy*, pointing at the Context table filtered to this cause on the matching side of the toggle.
*EASY*
- [x] **Active mission rhs cards order** — FIXED 2026-08-12. A cause can carry TWO elected initiatives at once, and `_phase2MissionCard` took whichever `find()` reached first. Both cards now order by the mission's own anchor (`_initWhen`, `started_at` with an election-date fallback), newest first, so the column reads strictly newest → oldest: Coastal City above Garbage Patch Analysis. *(If you meant the opposite — the finalizing race on top — it is one comparator to flip.)*
- [x] **Link requirements** — BUILT 2026-08-12. Research requires no link: the mission is on the post already, and the composer says so ("Linked automatically: …"). Analysis additionally auto-links the elected initiative and philanthropy. The rails stay for anything more the author wants to point at, and research carries an **edit it on your profile →** link. Only reviews still require one (case → initiative, case-for-a-philanthropy / evaluation → organization).
- [x] **Move post type toggle** — BUILT 2026-08-12. It sits in k beside the result. Every type of the open category is always drawn; the ones this stage has not opened are visible but dead, with the reason on hover.
- [x] **Plural** — DONE 2026-08-12: the rails read **Linked Initiatives** and **Linked Organizations**.
- [x] **Input deletion bug** — FIXED 2026-08-12, and it was mine. The box repaints as a whole, and an `innerHTML` swap discards what is in an input. Every repaint now CAPTURES title/body/row fields into the cell's draft, re-renders from it, and puts the caret back; each (category, phase, type) cell keeps its own draft, so leaving a cell and coming back finds the text still there. Regression-tested in `posts_box_check.js` — type, open a picker, attach a link, switch category and return.

- [ ] Add volunteer opportunity. Travel link? -backlog

*end backlog*

- ✅ Active-missions bar (7 cause squares).
- ◑ **Annulus 2** — inner pie (phase 1 = initiatives, phase 2 = org vote share), now-marker.
- ◑ **Left cards** — leading initiatives (ME); leading philanthropies
- ◑ **Right cards** — page 1: phase-1 (top) / phase-2 (middle) / most-recent prior (bottom); pages 2+ previous missions.

### ✅ The discussion box (BUILT 2026-08-12, build-seq §1)
Four dated stages across the top, three post categories across the middle, and
one cell — one explanation, one composer, one leading post — wherever they meet.
The four-section accordion (2026-08-10), the three-band P3 box (2026-08-08), the
dual panels (2026-08-02) and the per-phase checkbox threads (2026-08-01) are all
deleted; this is the single posting surface.


| § | Section | Date | What it holds |
|---|---|---|---|
| 1 | "atm2 (or whatever cause name and number it is) confirmed" | `T−14wk .. T−7wk` (Display T-14 wk until election actually running) |*case for the cause*|
| 2 | "Mission open" | `T − 49d` | The initiative election. Open: compose **case** (must reference the selected initiative) + **context**. Past: winning initiative + top case. |
| 3 | "Initiative Elected" | `T` | Before: **investigation only**, each naming ≥1 philanthropy. During: investigations target any org in the mission; **case for a philanthropy** shown beside the case for the initiative with the **aggregate** score; context migrated here. After: winning org + its case. |
| 4 | Philanthropy Elected | `T + 8wk` | Before: **S/S/S budgeting only**. After: context + investigation migrated here, **analysis** and **evaluation** open, budgeting filtered to mission + philanthropy. |
`T` = **mission started**

**How both drawings were built (2026-08-12).**
- **k** is `#pb-results`, and the notch under it (`.pb-k__joint > i.on`) sits over
  the tab whose date is the most recent one in the past — which is the stage the
  mission is IN, since a stage's date is the day it opened. The panel carries the
  election that opened that stage, so at stage 3 it reads *Initiative elected ·
  {tiv}* + its top case, exactly the drawing's example. k does **not** follow the
  tab you are browsing: you can read stage d's rules with the result that is
  actually on the table still in front of you.
- **a–d** are `#pb-phase`, each dated off `EBX.Cycle.missionDates` (the old rail's
  four dates, laid flat). **e–g** are `#pb-cat`, grayed per the spec: budgeting
  until the initiative is elected.
- **Cumulative, not migrating.** The 2026-08-10 model MOVED a thread down the
  timeline as stages closed. The rule here is the spec's own — "Context only in
  a-b, Context&Investigation in c, …" — a stage OPENS a type and later stages
  keep it. Same statement, without a thread vanishing from where you last read it.
- **h explains the CELL, not the pill.** "1 explanation per combined-tab-toggle",
  so h describes the type that stage opens (b→context, c→investigation, d→analysis
  in research; the case/evaluation ladder in reviews) and carries target · open ·
  reward · rating from `backend/app/post_config.py`. Budgeting is the exception:
  three blocks, one per s/s/s.
- **i** is title + body + the five rails. **Linked tivs → `posts.tiv_id`, linked
  phls → `posts.org_id`, media → `posts.image_url`.** A case must link an
  initiative and an investigation/evaluation must link a philanthropy — the rail
  is marked `*` and the send path refuses without it.
  **Budget items and external links are drawn but NOT wired** — a post has no
  column for either (backlog below).
- **j** is the leading post of that category with a pager through the ranked rest,
  the reactions `post_config` declares for the type (helpful/neutral/harmful,
  fair/unfair, or approve-only), plus the two filters the deleted P3 bands owned:
  a search inside research, sort-by-philanthropy inside reviews.

**The second pass (2026-08-12).** k gained the post-type toggle; the composer
lost its link requirement in research and gained the budgeting row editor; h
lost its chips for budgeting; j prints the three budget tables in place of the
leading post. Details in the backlog above.

- [ ] **Post links need somewhere to live** — `budget items` and `external links`
  have no field on a post. Options costed 2026-08-12: one `posts.links` JSON
  column (one migration, applies on next server start), or a `post_links` table
  (post_id · kind · target) if a post should carry many of each. Until then those
  two rails render disabled and say so. *(`posts.line_items` shipped on
  2026-08-12 by the same reasoning, so the migration path is proven.)*
- [ ] **The philanthropy side of a budget thread** — "budgeting posts shared
  between benefactors and philanthropies" is stated on the page, but only the
  benefactor can write one. An org-authored budgeting post needs the org
  composer (`author_type: 'org'`) and a place to write it from.

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
- on the profile page, the users 3 research posts should be displayed and editable.
- I need to build out org registration after cause.html is complete.
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
  posts, benefactors, transactions, admin, auth.
- [ ] Org claim/verify endpoints + acceptance record for the legal agreement.
- [ ] Guaranteed-to-pool rate (unclaimed vs claimed) in pool math.

 ## Long term
  - have 6 lower cards (Not either top left or top right) rotating with their center on the ray normal to the midpoint of its annulus section. Long term because requires major layout change.
  - You only receive as much ebx (max 10) as you committed to elect an org in the previous week.
  - [ ] **Bottom row of the 7 causes** This will fold in with the ambitious side card redesign later.