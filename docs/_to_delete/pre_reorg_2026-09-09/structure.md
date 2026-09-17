# Structure — page-by-page build spec

## Site layout
| Surface | Page | What it shows | Posting |
|---|---|---|---|
| **Landing** | `index.html` | About Earthbux | Connects and explains everything | 
| **Election** | `main.html` | **voting home** - context for each tiv/phl. The 7 cause tabs live here (2026-08-26) | Can suggest causes/initiatives and nominate philanthropies |
| **Discussion** | `cause.html` | Full discussion home. | All benefactor posting |
| **Mission** | `mission.html` | Mission status page - | phl/ebx posts, budget resolutions |
| **Profile** | `profile.html` | all activity from the signed-in user | active threads |

## Communications
**Winning Org spiel** "Hi, we're here to work with you to help the cause. Either we report on the cause, or we report on you. The goal is to report on the cause. If you do a good job, we'll be able to tell intersting stories about the cause. You have 7 weeks to claim the profile on our website. If you don't, you will only receive a small donation (which we will still investigate)."
**Upon nomination** "Hi! you've been registered on Earthbux. This means someone wants to donate to you through our platform! Verify a few things to recieve the maximum donation!"
**If winning** "Looks like you might win! Here are some ways to incerase your chances, and here's what you'll need to do if you won"
**Member spiel** M: Navigate through missions, converse with members, build your version of the mission. Budget, interact with the community, get recognition, make your earthbux gain value, get spots on the mission trips...


## Site nav — the five tabs (BUILT 2026-09-08, build-seq Misc)
**About**(index) · **Elections**(main) · **Missions**(mission) · **News**(cause)
· **Profile**(profile), on every one of the five. Drawn by `EBX.initNav` in
`resources/js/ebx_shared.js` — once, for all five pages, because a nav copied
five times is a nav that drifts. Styles are in `resources/css/ebx_frontend.css`
(`.ebx-nav`), in `.ebx-home-mark`'s dark-pill language so one nav reads on the
parchment landing page and the dark election page without a per-page override.

**The lit tab IS the page tag.** main.html's top bar said "ELECTION" and
cause.html's said "Discussion · <cause>"; the lit tab says that and also says
what the other four are, so the tag came off where the nav went in. cause.html
keeps the CAUSE beside the tabs — that half of its tag is not navigation.

Two mount modes: `#ebx-nav-mount` where a page has a top-bar centre cell
(index, main, cause), and a centred `.ebx-navstrip` at the top of the body where
it does not (mission, profile). `admin.html` has neither the nav nor
`ebx_shared.js` — it is the staff console, not one of the five.

Every page section below ends in a **PAGE LAYOUT** node,

## index.html (Landing) — **About Earthbux**
*backlog*
- [ ] **Instructions** Detailed instructions of what to do with screenshots
- [ ] **Who profits?** You donate, we follow (explained). Also, you hold most of the liquid.
- [ ] **(Self) Advertising** Suggest weekly/monthly/yearly donation to cover many missions.
- [ ] **Vocabulary** User = Benefactor, Philanthropy = Organization, Mission = Initiative

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

- ✅ **PAGE LAYOUT**
  - ✅ **Topbar** — EBX brand · profile badge
  - ✅ **§1a Hero** — forum + research team couplet · "Earthbux News · you donate,
    we follow" · (Login/Sign up) · Vote now
  - ✅ **§1b Origin** — the 2026 couplet · publicity / research-based donation
  - ✅ **§1c How it Works** — maximizing donor control
    - ✅ **ME row** — elect an *Initiative* · Week 0 → `main.html`
    - ✅ **OE row** — elect a *Philanthropy* · Week 7 → `main.html?state=oe`
    - ✅ **Ten dimes** — `10 tokens · ten dimes · $1 · every week`
      — **says TOKENS since 2026-08-28** (§3). A granted token has not been
      minted and may never be, so it cannot be EBX.
    - ✅ **Runway** — committed $ ÷ (active members × $1), from `GET /stats`
  - ✅ **§1d A Public Forum** — three categories, type toggles
    - ✅ **Reviews** · ✅ **Research** (context · investigation · analysis)
      · ✅ **Budgeting** (service · supply · support)
  - ✅ **§1e What we do** — Dormant(1/16) → Arbitrating(5/16)
  - [ ] **Phase strip** — 3 cards: p1 → `main`, p2 → `cause`, p3 → `mission`
  - [ ] **Examples** — one ACTIVE mission (org vote + budgeting) · one UPCOMING
    (initiative election + causes)
  - [ ] **Instructions** — per-process, toggleable, with screenshots
  - [ ] **FAQ** — a losing vote · limits · voting an OE you skipped
  - [ ] **Vocabulary** — Benefactor · Organization · Mission
  - ✅ **Footer**

## profile.html — Profiles
*backlog*
- [x] **Remove warning bar** — DONE 2026-09-08 (build-seq §1). It said the page
  "isn't developed yet" and linked to "the Context page", which has not been
  called that since 2026-08-26 — and the page it was apologising for was rebuilt
  to the drawing on 2026-08-28. It was the last thing a benefactor read before
  their own wallet.
- [ ] **Wallet**
  - indicate whether benefactor predicted correctly either of the 2 elections. 
  - Anything I voted on should have a coin in the wallet.
- [ ] **Allocations**
  - Conversions need work. Note that you can only move tokens if your vote lost.
  - Should have options to convert or withdraw ebx eventually too.
- [ ] **MEMBER MODE** - must have a coin selected.
  - What does the experience look like? Well, first the user is instructed to search their org in our database. If its there, they claim it. If not, they register it.
- [ ] **Choice cards**
  - Don't say "Week + x". Replace with "X weeks away" and remove the day count. Only have the election date on the top right.
  - cards should toggle page, not link to election.
- [ ] Beneficiary profiles
- [ ] Credit badge colorization (participation perk)
*end backlog*

- ✅ **PAGE LAYOUT**
  - ✅ **Topbar** — brand · profile badge
  - ✅ **Top row** — `c` | `b` | `a`
    - ✅ **(c) EBX wallet** — credit coins, horizontal strip
      - ✅ **A coin is SELECTABLE** — `pickCoin`; this is what gates `ab`
    - ✅ **(b) Allocations** — one bar, **three sets of two**, the same shape
      main.html draws: `unallocated (granted · purchased)` ·
      `committed (initiatives · organizations)` · `EBX (held · donated)`
      - ✅ **The grant's cause** on the head — "the grant carries its CAUSE,
        not a deadline"
      - ✅ **Conversion row** — `POST /wallet/move`, race → race
    - ✅ **(a) Profile** — badge · handle · mode
      - ✅ **aa Settings** · ✅ **ab Member / Benefactor** · ✅ **ac Sign out**
      - ✅ **ab is gated on a coin being SELECTED**, not merely held
  - ✅ **(e) Seven weekly windows** — the choices table, evolved
    - ✅ **Top card** — this week, split into COLUMNS: organization left,
      initiative right
    - ✅ **Right column** — weeks +1 +2 +3, split into ROWS: organization on
      top, initiative below (falling clockwise)
    - ✅ **Left column** — weeks +6 +5 +4, initiative on top, organization
      below (coming back up)
    - ✅ **Two cause colours per card** — the ME and the OE closing in one week are never the same cause, because 8 weeks is not 7
    - ✅ **Each half** — `{cause}` · my pick · `{ct}` committed → the election
  - ◑ **(d) The globe** — orthographic sphere, own graticule, turns continuously
    and eases round to the selected window's causes
    - ✅ Mounted, animating, aimed by `selectWindow`
    - [ ] **Real geography** — no model carries lat/lon, so it marks CAUSE
      ANCHORS and the caption says so. This is the blocker for everything else
      here, and for the same globe on mission.html.
    - [ ] Move / share the component with mission.html
  - ✅ **(f) Feed** — `GET /posts?ben_author_id=`
    - ✅ **Benefactor mode** — Posts · Comments · Research
    - ✅ **Member mode** — the user's research, plus research they commented on
  - ✅ **Settings modal** · ✅ **Switch to Organization mode** · ✅ **Admin console**
  - [ ] **ORG MODE registration** — search the database → claim, else register
  - [ ] **Organization profile** — initiative coins · tasklist · annulus 4 · memberships
  - [ ] **Beneficiary profile** — voice at phase-2 start
  - [ ] **Mission-member messageboard** — separate from posts
  - [ ] **Credit badge colorization**
  - **Checked by** `scripts/profile_check.js` — 42 assertions.

## mission.html — Mission page (REBUILT 2026-08-01 · jax notes 2 layout)

### ▶ NEXT — the redesign (build-seq §3). Build order, box by box.

*The ASCII in `jax notes 2` under **Mission**, mapped. `docs/mission_model.md` §9
maps the same layout onto the mission PROCESS; read the two together. Not started
2026-09-08.*

| Box | What it is | Blocked on | Order |
|---|---|---|---|
| **d** | about · reviews · graph — mission statement, org overview, case and context, status update | nothing | **1** |
| **f** | **IN PROGRESS** — "any input to the page is done from here" | the framing checklist (`mission_model.md` §6) | **2** |
| **g** | **DONE** — what has completed | f | **3** |
| **c** | high-level mission detail: membership, allocations, my votes & allocations, activity status, inbox | `GET /wallet/rows`, live | **4** |
| **b** | the globe from profile.html, inside main.html's 7-sector annulus | **the globe is built**; the annulus is built; ⚠ **real geography is not** — no model carries lat/lon, so both mark CAUSE ANCHORS | **5** |
| **a** | three previous missions in this cause, pager ABOVE them (it is below on cause.html today) | nothing | **6** |
| **h** | the 7-cause selection | the same bar main.html and cause.html carry | **6** |
| **i** | "essentially a less addictive version of cause.html" — the mission's own conversation | the cause.html feed (§3 first half) | **7** |

**Build d → f → g first and the page is already useful**, because those three are
the mission's own story and nothing else on the page is. b and i are the two that
depend on other work landing.

**The one hard blocker, stated once:** *real geography*. No model carries
latitude/longitude, so the globe on both this page and profile.html marks cause
anchors and says so. It is a schema question (a `lat`/`lon` on Initiative? on
Organization? on a new MissionSite?) and it should be answered before the globe
is built into a second page.

*backlog*
- [ ] **ASCII** DRAWING INCOMING!
- [ ] **My three research posts**, editable, on the card whose mission they target
- [ ] **Mission-member messageboard** — member pages carry a deeper messageboard / discussion console
- [ ] **Organization Nomination - Registration - Claim** - mission.html...
  - tokens become ebx. Ebx not convertable until well into the mission. Tokens only convertible during voting.
  - `GET /wallet` returns the four states — **unallocated · committed · minted · donated**
  - Coins are the visual representation of the ebx - what the initiative election made of these ct, and the philanthropy they minted behind.
  - Each benefactors available ebx is what they see.
  - on the mission page, the users 3 research posts should be displayed and editable, toggled by mission in the choices table/credit coin wallet.
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

- ◑ **PAGE LAYOUT**
  - ✅ **Topbar**
  - ✅ **a Mission toggle** — ← → + initiative search
  - ✅ **g Name + core info**
  - ✅ **b Profile + membership status**
  - ✅ **c Post stream** — 3 category tabs at the foot
  - ✅ **e Phase circle** — 3 phases → ultimately the 3D globe
    - [ ] **Take profile.html's globe.** It is built (§1, 2026-08-28): an
      orthographic sphere with its own graticule that turns and eases round to a
      selection. It marks CAUSE ANCHORS because no model carries lat/lon — which
      is the same blocker this page has.
  - ✅ **d Progress log** — "Elected `{tiv}` with `{EBX}`" · "Approved `{step}`
    for `{cost}`"
  - ✅ **f Pool** — in-pool / committed / withdrawn
    - ✅ **Two units, on purpose** (§3, 2026-08-28): *in the pool* and *spent* are
      minted, mission-tied money — EBX. *Committed* is the live allocations
      behind the two elections, which are still tokens until the roll.
  - ◑ **Annulus — post support**
    - ✅ **Layer 1** — one arc per rated thread, grouped by org, coloured by flag
      · legend · per-org thread list · weekly-digest note
    - [ ] **Layers 2+** — nothing decided
    - [ ] **The real classifier** — `classify_flag` returns green for everything
  - ✅ **Competing organizations card**
  - ✅ **Click-through legal agreement** — gates register/claim
  - [ ] **Left — MONEY IN** — pool · commitments · withdrawals · coin value
  - [ ] **Right — MISSION OUT** — steps · resolutions · progress reports
  - [ ] **Full conversation** — the P3+ post source
  - [ ] **Suggestions → budget** — S/S/S feed the org's builder
  - [ ] **Steps → resolutions** — 7–12 step ring · early-resolution bonus
  - [ ] **Member channel** — contributor / representative / executive / beneficiary
  - [ ] **Creditcoin front/back + 3D earth**

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

## main.html (Election Page) — **the VOTING surface**
*Renamed 2026-08-26 (build-seq §1): "The name of this page is no longer the context
page. It is now the Election Page." Title, top-bar tag and this heading agree.*
*backlog*
- [x] **Perfect instructions/help** — DONE 2026-09-08 (build-seq §2). The
  election-experience block sits between the seven cause toggles and the cause
  ballot, in Jax's words: *"First, the cause is determined. Next, a mission is
  elected within it. Finally, an organization is elected to run the mission. The
  leaderboards are above. The candidates and ballots are below."* It replaced
  "Select a cause, and vote." on the top cards, which told a reader to act
  without telling them what the act was part of.
- [ ] **Perfect toggle specifics**
- [x] **One commit button** — resolved the other way, 2026-09-08. There is one
  write path (`commitAll`) and now **two doors** to it: the OE ballot's own
  Commit, and the one in the allocations panel. The ballot is where the decision
  is made and it used to end in three links with no way to act on them.
- [ ] **OE election panel fix** Link election panels with allocations + wallet
- [ ] **Perfect all 3 table columns**
- [x] **No more expanded rows** — DONE 2026-09-08. Clicking an initiative row
  opens its expansion **in the ballot**, not under the row. The inline `<tr>`
  pushed the rest of the field down the page, which is the comparison the table
  exists to make; the OE rows stopped expanding on 2026-08-20 for the same
  reason.
*end backlog*

- ◑ **PAGE LAYOUT**
  - ✅ **Topbar** Logo and login
  - ✅ **Top cards**
    - **ME side**
      - **Left** This weeks ME
      - **Right** the just-elected initiative -> OE
    - **OE side**
      - **Left** This weeks OE
      - **Right** the just elected organization -> Budgeting
  - ✅ **Election cards** — **THE FIELD, and only the field** (§2, 2026-08-28)
    - ✅ **Top 3** — `1. {name} ({pct})` × 3, padded to three rows so seven
      cards keep one height. A decided OE race leads with its winner, marked.
    - ✅ **Side card - ME** — `{cause} {mission_num}`
    - ✅ **Side card - OE** — `{tiv_title}`
    - ✅ **"My vote" and "N to other initiatives" are GONE.** They were two of a
      card's three rows and they said nothing about the race. A benefactor's own
      position lives on profile.html now — all fourteen of them, on seven cards.
  - ✅ **Site nav** — the five tabs, in the top bar's centre cell, where the
    "ELECTION" page tag was (2026-09-08)
  - ✅ **Election experience** (`#hero-howitgoes`) — between the seven cause
    toggles and the cause ballot: three numbered steps and one line saying where
    each half of the page is (2026-09-08, build-seq §2)
  - ✅ **Cause election panel** — **directly under the seven cause toggles**
    (2026-09-08). It spent 2026-08-27b below the table, ordered by urgency; this
    orders it by SUBJECT — the seven tabs are the cause control, and the ballot
    that changes which seven they are belongs against them.
  - ✅ **The second election panel** (`#votebar-notice-mount`) — the pair always
    reads mission-election-above / organization-election-below, whichever the
    toggle is pointed at. The selected mode shows its ballot; the other slot
    shows what that race is doing and the toggle to reach it (2026-09-08,
    build-seq §2). Ordering is CSS `order`, so repainting one panel can never
    reshuffle the other.
  - ◑ **Annulus** — **one thin static ring, and the pie inside it** (§2, 2026-08-28)
    - ✅ **Seven sectors**, 8px band. Colour = the cause the page is pointed at
      (selection). White halo = the sector the WEEK is in (now).
    - ✅ **The sectors POINT CLOCKWISE** (2026-09-08, build-seq §2). Each is a
      chevron: leading edge drawn to a point at mid-band, trailing edge notched
      by the same angle, so a sector's tip lands in the notch of the one ahead —
      seven interlocking arrowheads sweeping the way the marker travels, with
      nothing sticking out of the 8px band. The retired chevron RAYS said the
      same thing from outside the ring; this says it from inside. Tip 0.14 rad
      with a 0.03 gap, chosen by rendering four and looking at them.
    - ✅ **The centre names the CAUSE and the ELECTION** (2026-09-08). Both
      states read the same three lines — cause · which election · when it closes
      — where the ME side used to say "<Cause> Decision:" with no phase line and
      the OE side said an initiative title over "Philanthropy election". The
      initiative moved to `.ebx-center__sub`, which had styles and no element.
    - ✅ **The glow travels clockwise** with the marker, which is the only moving
      thing on the ring — so it is what direction means.
    - ✅ **The chevron rays are RETIRED** — twenty-one arrowheads saying what the
      marker already said.
    - ✅ **The pie is untouched** and the ring frames it.
  - ✅ **Page toggle** ME/OE and 7 causes
  - ◑ **Table**
    - ◑  **Election Panel** 
      - ✅ **ME** - Sliders to split vote - | starred | My commitment | tiv title | total ebx | cause | [vote] | — columns BUILT 2026-08-10 (§8)
        - ✅ **Expanded rows** — REPLACED 2026-09-08. A row click paints
          `_idxInitDetailHTML` into `.vb-detail` inside the ME ballot and lights
          the row; clicking the same row again closes it. No `<tr>` unfolds.
        - ✅ **"+ org" per slider row** (2026-09-08) — nominate an organization
          for THAT initiative, from the moment a benefactor decides they want it
          to happen. `EBX.Dialogs.orgRegister` takes a `tivId` now and guarantees
          the named initiative onto its list, pre-checked: nomination used to be
          reachable only from the OE panel, i.e. only after the initiative had
          already won, and `jax notes 2` asks for the opposite ("Users need to be
          able to suggest organizations even before the initiative has been
          decided… Org nomination can fire upon tiv vote").
      - ✅ **OE** — **the table is ONE RACE's ORGANIZATIONS** (2026-09-08,
        build-seq §2): the candidates running in the selected cause's *upcoming*
        organization election (where a cause has two open, the one finalizing
        next), a caption row naming the contest, and a **nominate** row at the
        foot. Columns: | starred | My vote | Organization | Tokens behind it |
        Standing |. Clicking a row IS the pick.
        - The eight-open **deadline view** survives behind *Show all races* under
          the table (`_oeScope`), because 2026-08-20b's reason for it is still
          true: a benefactor with money in eight races needs to see eight dates.
        - ✅ **Commit + Cancel** are back on the ballot's foot, beside the three
          links, and arm with the race. Same `commitAll`; two doors.
        - ✅ The panel says **Organization Election**, not Philanthropy.
      - [ ] **CE** Expands when CE panel is interacted with
    - [ ] **CE Panel**

## cause.html (Discussion → **NEWS**) **the DISCUSSION hub**

### ▶ NEXT — the newsfeed rebuild (build-seq §3). Build order, box by box.

*`jax notes 2` **Newsfeed**: "designed to capture attention. NOT sorted by
mission." The ASCII is five boxes and a reply affordance. This is the order to
build them in, and what each one already has to build on. Nothing below was
started on 2026-09-08 — the pass stopped here deliberately rather than leave a
feed half-swapped over a working discussion page.*

| Box | What it is | Build on | Order |
|---|---|---|---|
| **a** | the feed itself — articles, conversations, reactions, short-form, image and video. "The hub for scrolling." | **`GET /posts?sort=hot` — BUILT 2026-09-08**, see Backend below | **1** |
| **d** | the feed's control panel: search, filters, settings, compose | the existing composer (`#pb-compose`), lifted out of the phase box | **2** |
| **b** | reactions, per card, down the right edge | `POST /posts/{id}/react`, live | **3** |
| **f** | reply, per card | `parent_id` threading, live | **3** |
| **c** | the cause annulus, SMALLER: no text inside the sectors, no white marker, keep the glow on the active sector, keep the rotation so the active sector is always toward the top; centre says the active cause and days left | `EBX.Annulus`, already here | **4** |
| **e** | a small per-card annulus linking to that post's mission home | new; the smallest thing on the page and the last | **5** |

**The two rules that decide the layout.** *All posts are included* — one feed,
every category, no per-mission tabs — and *not sorted by mission*, which is why
the ordering is engagement-with-decay rather than anything structural.

**What happens to the discussion box.** It does not disappear: it is the
COMPOSER (d) plus the phase context, and phases 1–2 still need it. Build the feed
as the page's spine and move the phase/category tabs into d's filter set — the
same four phase tabs and three category tabs, as filters rather than as a frame.
The `posts_box_check.js` suite (16 assertions) pins the composer's behaviour;
keep it passing and the move is safe.

**The rename.** *Discussion → News*, and *news team → newsroom*, land with this
rebuild rather than before it, so the page is renamed once. The nav already says
**News**; the page tag already carries only the cause.

*backlog*
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



- ◑ **PAGE LAYOUT**
  - ✅ **Topbar** — page tag "Discussion · `{cause}`"
  - ✅ **Cause bar** — seven tabs, **the same bar main.html carries**, in the same
    styles (§2, 2026-08-28). "Cause selection bar will move to discussion page
    too." Links to `cause.html?id=…`, the same destination the wheel's sectors
    already navigate to.
  - ✅ **Guide line** — the sentence that used to caption the wheel ("Click on a
    cause…") belongs to the seven causes, so it moved up to the bar, and it now
    also names **the step the chosen cause is standing on**: `Step {n} · {name}`
    + what is happening + `Decided {date}` + the vote link. Seven names in a row
    tell a newcomer nothing about what happens when they pick one.
  - ◑ **Annulus 2 — the WHEEL** — untouched this pass ("Don't worry about
    cause.html annulus yet"). Still rotates, still navigates.
    - ✅ **Centre panel** — today / the race / its phase / its decision date
    - [ ] Merge with main.html's thin ring, and drop the sector click — with one
      bar on both pages the wheel is a second way to do the same thing.
  - ◑ **Left cards** — leading initiatives (ME) · leading philanthropies (OE)
  - ◑ **Right cards** — p1 (top) / p2 (middle) / most-recent prior (bottom);
    pages 2+ previous missions
  - ✅ **Discussion box** (BUILT 2026-08-12) — see the table above
    - ✅ **Phase tabs** — a Cause confirmed · b Mission open · c Initiative
      elected · d Philanthropy elected
    - [ ] **Results strip (k)** — the previous section's outcome, joined visually
      to the most recent dated tab
    - ✅ **Category tabs** — e Research · f Reviews · g Budgeting
      (Research greyed until the cause is confirmed; Budgeting until the tiv is elected)
    - [ ] **Explanation area (h)** — one per combined tab pair, except budgeting,
      which explains each of S/S/S
    - ◑ **Compose (i)** — title · body · type selector · link rails
      (tivs · phls · budget items · media · external, headed **"Add links"**)
      · about strip
    - ◑ **Leading posts (j)** — one row per post TYPE when research is toggled;
      highlight the toggled row
  - [ ] **Cause suggestion box** — moved off main.html, with case + replies
  - [ ] **Budgeting report** — in the table at the foot
  - ✅ **Units** — a running race's pool is **tokens**, not EBX (§3, 2026-08-28).


## admin.html — Data console
*backlog*
- [ ] Ability to send email updates to all users- for example if we move to a new domain.
- [ ] Ability to remove initiatives, organizations, posts, etc as well as benefactoraccounts.
- [ ] Event log (vote_events: CAST/UPDATE/REMOVE), duplicate/invalid-vote flags.
- [ ] Full mission table; org verification queue (EN, 1/week).
- [ ] In the benefactor accounts table, add most-recent-vote date and target columns for each of the 3 votes.
- [ ] In the ledger transactions table, make sortable by benefactor account and by target + action.
*end backlog*

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

- ◑ **PAGE LAYOUT**
  - ✅ **Sidebar nav** — the filetree of all 15 tables
  - ◑ **Accounts** — search by user · ✅ reset password · [ ] remove account
    · [ ] most-recent-vote date + target, per election
  - ◑ **Elections** — filter by election · [ ] full mission table
  - ◑ **Organizations** — filter by org · [ ] verification queue (EN, 1/week)
  - ◑ **Ledger** — [ ] sortable by benefactor and by target + action
  - [ ] **Event log** — vote_events CAST/UPDATE/REMOVE · duplicate/invalid flags
  - [ ] **Removal tools** — initiatives · organizations · posts
  - [ ] **Broadcast email** — blocked on a mail transport, same as the self-serve
    password reset and the weekly philanthropy digest
  - ✅ **Export CSV · sort by timestamp**

## Backend (FastAPI + SQLAlchemy + Alembic)
- Models: Cause, Mission, Initiative, Organization, BenefactorAccount, Membership,
  MissionCandidacy, VoteP1, VoteP2, Pool, CreditCoin, Post, PostVote, Transaction.
- Endpoints: causes, missions, initiatives, organizations, candidacies, votes (p1/p2),
  posts, benefactors, transactions, admin, auth, **wallet** (`GET /wallet`,
  `GET /wallet/rows`, `POST /wallet/commit`, `POST /wallet/move`,
  `POST /wallet/withdraw`, `PUT /wallet/org`), stats.
- **`GET /posts?sort=hot`** (new, 2026-09-08, build-seq §3) — the NEWSFEED
  order. `recent` stays the default and every existing caller is unchanged.
  `hot` is decayed engagement: `(helpful + 2·replies + ¼·neutral − ½·harmful
  + launch gravity) ÷ (age_hours + 2)^1.5`. A reply is worth two reactions
  because writing back costs more than pressing a button; harmful subtracts at
  half weight rather than sinking a post, because a disputed post is
  interesting and what removes one is the FLAG; a `red` flag floors the score,
  because red means spam or unsupported slander and Earthbux apologises to
  organizations for those. The gravity for headline/editorial/org_update
  expires after 48h — as a permanent term it gave old news tenure instead of a
  head start, which showed up the first time it ran. Ranked in Python:
  the inputs include a reply COUNT, the score is not a column, and a feed page
  is a few hundred rows.
- The money lives in `token_model.py` (pure arithmetic) and `wallet.py` (the only
  module that lets it touch the database) — `docs/token_model.md` is the prose
  version. Since 2026-08-27c: an allocation is a position inside its own week and
  EBX after the roll (`wallet.harden_due`, run by the scheduler and lazily on
  `GET /wallet`); `finalize_p1` mints the winning initiative's backers as EARLY
  EBX and marks the rest; `finalize_p2` mints what is left and books the first
  donation tranche at a clean 10%. Both halves of settlement are booked now —
  the OE half used to be recomputed on every read.
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
- **§0a (2026-09-08) — three places read the wrong column, and one of them was
  deleting a benefactor's money.**
  - **`wallet.read_wallet` dropped a phase-1 position when its election closed.**
    The rule was "the initiative election closed, so the OE row holds it now",
    applied whether or not there IS an OE row. `finalize_p1` writes one, but
    every mission decided before 2026-08-27c closed without it — so for those the
    skip handed the money to nobody. **jjager12's 8 tokens, their only vote on
    the platform, read as ZERO committed**; Jackson lost 1 more the same way. The
    row is skipped now only when a phase-2 row exists to carry it.
    `scripts/carry_audit.py` (new) lists the eight orphaned positions; six have
    an OE still open and can simply be carried, two are past it and need a
    case-by-case call.
  - **`GET /stats` summed `VoteP1.ebx_committed` + `VoteP2.ebx_spent`.** The
    second is `p2_vote_cost` — the price of EXTRA votes, 0 for a first vote and 0
    for every row ever written — so the whole organization-election side counted
    as nothing, and the phase-1 term carried the un-roundable legacy 1.7142857,
    publishing a FRACTIONAL token count on the landing page. It also summed every
    vote row while `members` counted only live benefactors, so 111 of the 152
    "committed" tokens belonged to the admin account the membership count
    excludes. It reads the wallet once per live member now: 78.7 tokens, $7.87,
    2 weeks of runway, where it used to say 152.7143 and 5.
  - **`crud.mint_mission_coins` sized coins with `ebx_spent` too**, then rounded
    to an int — so a benefactor whose whole position was in the ORGANIZATION
    election minted `int(round(0))` and got no coin at all. That is why
    profile.html's backlog has been asking for "anything I voted on should have a
    coin in the wallet". `crud.global_coin_value` had the same read.
- [ ] Org claim/verify endpoints + acceptance record for the legal agreement.
- [ ] Guaranteed-to-pool rate (unclaimed vs claimed) in pool math.
- ✅ **The unit question is ANSWERED** (2026-08-27c): tokens and EBX are two
  STATES of one asset, not two names for it. main.html says tokens on the voting
  surface because that is where tokens are; EBX is correct wherever
  mission-tied, minted money is meant. What is left is a copy sweep of
  cause.html / mission.html / profile.html to make sure each use of "EBX" means
  the minted state and not the vote.
  - ✅ **THE SWEEP IS DONE** (§3, 2026-08-28). `scripts/unit_sweep.js` renders
    each page and walks its VISIBLE text nodes, because a grep of the source
    cannot do this — `EBX.` is the client namespace and it is on every line of
    every page. It flags any visible "EBX" sitting beside a vote/commit word.
    Fixed: the landing page's grant and dime line, cause.html's race pools,
    mission.html's phase-1 pool, leaderboard, approval note and "committed"
    stat. Left as EBX, correctly: mission.html's *in the pool* and *spent*, and
    main.html's third allocation set and its week-roll sentence. **Currently
    CLEAN — 3 visible uses, none of them a unit.**

 ## Long term
  - [ ] **BUILD 3D EARTH** - Globe with benefactor at center. Geolocate different initiatives/organizations.
  - [ ] **Image attachments** Image generation technology? Build an image search tool that finds/creates a good open source picture to represent the mission.
  - [ ] **Next-gen desktop UX** have 6 lower cards (Not either top left or top right) rotating with their center on the ray normal to the midpoint of its annulus section. Long term because requires major layout change.
  - [ ] **Reorganize docs files** Also I should reestablish a section for "Stuff that should be removed"


  #### The drafted trees that were parked here are LANDED (2026-08-28).
  Each one is now in its own page's section above, corrected against what the
  build actually did rather than what the plan expected:
  - **index.html** — the ten-dime line says *tokens*, not EBX.
  - **profile.html** — the whole tree is new; the page was rebuilt to the
    drawing in the build sequence, not to the plan's guess at it.
  - **main.html** — the cards are the top 3, and the annulus is one thin static
    ring with the pie inside it.
  - **cause.html** — the cause bar and its guide line are built; the wheel is
    deliberately untouched.
  - **mission.html** — the Left/Right stubs became the full a–g tree.
  - **admin.html** — new.
