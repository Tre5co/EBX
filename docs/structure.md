# Structure — page-by-page build spec

> UI/build spec, one section per route. The "why/how" system model lives in
> `README.md` (§3 lifecycle, §5 discussion + money); open / deferred items live
> in `INSTRUCTIONS.md` `## BACKLOG`.
> Status keys: ✅ done · ◑ partial · [ ] not started.
>
> **Current focus — the posting & newsfeed experience for phases 1–2.**
> Everything from the end of phase 2 onward (budget / release / resolutions UI)
> is modeled but parked; see the discussion model below and README §5.

## Discussion & newsfeed — the build focus (phases 1–2)

Posts drive every phase (README §5). Five surfaces show the same post stream in
different ways. **New discussions originate on the Context page or the Mission
page**; every other surface aggregates or replies.

| Surface | Page | What it shows | Posting |
|---|---|---|---|
| **Landing** | `index.html` | all posts, most-recent / trending | reply here; link out to Context/Mission to start a thread |
| **Context** | `main.html` | each tiv/org **expanded row has its own discussion**; the post source for **P1/P2** | **originate + continue** threads |
| **Election** | `cause.html` | only the **top few posts per phase** (view-only) + pending budget items in resolutions | none — read-only |
| **Mission** | `mission.html` | the **full conversation** for one mission; the post source for **P3+** | **originate + continue** threads |
| **Profile** | `profile.html` | all activity from the signed-in user | reply here |

Post-surface rules:
- **Comments = replies = posts with a `parent_post_id`.** Clicking a reply opens
  the **Context** page (P1/P2) or the **Mission** page (P3+), by the post's phase.
- **Where each post type may live:** *org reviews, investigations, testimonials*
  can be posted on **any org, any time** (no active mission needed); *analysis,
  comparisons, justifications* only exist **inside an active mission**.
- **Context table** — initiatives/orgs **currently in a mission** get a **distinct
  row type**: it names the mission, current phase, start date, and current votes,
  and links to the Mission or Election page. Rows with no active mission are where
  users post about that tiv/org.
- Every post shows its **date** and the **initiative/org it regards**, and is
  **colored by that cause**.
- Reactions are **Helpful / Neutral / Harmful**.
- **P1 recap** shows only two categories — **context** and **case**.
- The **resolutions** area links to the **Mission** page.
- Post categories route by phase & scope (Context/Case → P1; Analysis / Suggestion
  / Org-review → P2; Evaluation → P3) — taxonomy in README §5.
- Image attachments on posts — deferred (INSTRUCTIONS `## BACKLOG`).

> `index.html` is the **landing** page (we always land there); `main.html` is the
> **context** page. `en.html` also surfaces a feed — resolve its overlap with the
> Landing all-posts stream (curated cross-mission vs. everything).

## index.html — Landing (extreme-simplified, 2026-08-01 · jax notes 2)
- ✅ Topbar: EBX brand · profile badge.
- ✅ **a — founding blurb** ("In 2023, Earthbux was created with one goal…").
- ✅ **b — The System, 3 Phases, All Community-Controlled** with link cards
  p1 → `main.html` · p2 → `cause.html` · p3 → `mission.html`.
- The all-posts stream is GONE from index (lived here 2026-07-31 → 08-01);
  the newsfeed lives on the Context/Mission surfaces. This resolves the
  index-vs-`en.html` overlap: index carries no feed.

## main.html — Context (per-row discussions; P1/P2 post source)
> Each tiv/org expanded row has its **own discussion**; this is where users
> **originate** and continue P1/P2 threads. If a row has no active mission, this is
> where users post about that tiv/org.
- ◑ **Table** — state 1 initiatives (phase-1 only) / state 2 organizations.
    - [ ] **Per-row discussion** — each row's expanded columns filter posts by
      **tiv (or org)**, not just cause; users originate/continue P1/P2 posts here.
    - [ ] **In-mission row type** — initiatives/orgs currently in a mission get a
      **distinct row**: mission id, current phase, start date, current votes; links
      to the Mission or Election page.
    - [ ] **Choices table** — toggle **phase 1 / phase 2** (not initiatives/orgs);
      show p1 choices in phase 1, and at the election clear the user's choices and
      make the winning initiative the p2 row label.
- ◑ **Entity card** — leading initiative/org; vote button per mode.
- ✅ **Post dialog REMOVED from main.html** (2026-08-01, build-seq §4). Expanded
  rows = description + **status frame** (current votes · age · if_active ·
  winning case · posts that WON · org running it · key dates); winning-case /
  winning-posts render "—" until the per-row discussion wiring lands.
- [ ] Post composer (per-row, future pass) — Helpful / Neutral / Harmful + Reply; category by phase & scope (README §5).
- [ ] Propose / nominate dialogs shared with the cause page.
- [ ] Resolve overlap with `en.html` (curated cross-mission feed vs. Landing all-posts).

- ◑ **Annulus 1** — cause ring, glow marker for the next cause, `now` indicator.
    - [ ] **Center**
    - [ ] **Size and thickness**
- ✅ **Page toggle** — upcoming org vs initiative elections.
- ◑ **Election cards** — two-sided (front = upcoming phase 2, back = phase 3); show EBX counts.
    - [ ] **Side cards** Note that we will be changing ebx counts instead of %s because that allows one to estimate the total pool size
        - ✅ **Location**
        - [ ] **back** upcoming phase 3
        ____________________________________
        |tiv_name                      date*| *Last day of cards upcoming active window
        |1. org_name                  #votes|
        |2. org_name                  #votes|
        |3._org_name__________________#votes|
        |My choice - choice_name     |ebx   |
        |My committment_-_x_ebx______|pool__|
        - [ ] **front** - upcoming phase 2
        ____________________________________
        |cause_name mission_num        date*| *First day of cards upcoming active window
        |1. tiv_name                  #votes|
        |2. tiv_name                  #votes|
        |3._tiv_name__________________#votes|
        |My choice - choice_name     |ebx   |
        |My committment_-_x_ebx______|pool__|
    - [ ] **Top card** only card with 2 org-elections
    The front and back are the 2 consecutive org elections in the active cause.
        - [ ] **Glowy** top card glows white like now marker
        - ✅ **Location**
            Horizontal: In between the side cards
            Vertical: From the now marker all the way to the top of the display.
        - [ ] **back** upcoming phase 3
        ____________________________________
        |tiv_name                      date*| *Last day of current active window
        |1. org_name                  #votes|
        |2. org_name                  #votes|
        |3._org_name__________________#votes|
        |My choice - choice_name     |ebx   |
        |My committment_-_x_ebx______|pool__|
        - [ ] **front** Most recent phase 2
        ____________________________________
        |tiv_name                      date*| *Last day of NEXT active window (in 7-8 weeks)
        |1. org_name                  #votes|
        |2. org_name                  #votes|
        |3._org_name__________________#votes|
        |My choice - choice_name     |ebx   |
        |My committment_-_x_ebx______|pool__|
- ◑ **Election cards → context** — cards link to the tiv/org row on the **Context**
  page (`main.html`), which owns the interactive table + per-row discussion.

## cause.html — Cause / election surface
- ✅ Active-missions bar (7 cause squares).
- ◑ **Annulus 2** — inner pie (phase 1 = initiatives, phase 2 = org vote share), now-marker.
- ✅ **Left cards** — leading initiatives; ◑ **swap to competing organizations in phase 2** (paged, vote, buy-more).
- ◑ **Right cards** — page 1: phase-1 (top) / phase-2 (middle) / most-recent prior (bottom); pages 2+ previous missions.
- ◑ **Phase recaps** — five stacked blocks (5 at top → 1 at bottom); live election widget in the active phase.
- ◑ **Phase 2 area** — org election: evaluation/context/analysis + org pitch; nominate/register entry.
- ◑ **Discussion, view-only** — 2026-08-01 (build-seq §3): each ACTIVE phase
  area splits into its own thread — **checkbox post-type filters** (P1
  context·case / P2 analysis·investigation·evaluation / P3
  service·supply·support·evaluation), **sort** relevance / popularity /
  recency, **pager** (5/page). No writing-in; clicking a post opens the
  **Context** page (P1/P2) or **Mission** page (P3). Remaining: narrow to
  "top few" on first paint per the original spec if the full thread is noisy.
- ✅ **Three phases only** — recap stack collapsed 5 → 3 (2026-08-01): the back
  half is one **Budgeting & Resolution** area (S/S/S suggestions folded in;
  annulus center reads "Phase 3 · Budgeting & Resolution" for enum 3/4/5).
  P2 still needs its strong redesign (build-seq §3 note).
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
## mission.html — Mission page (REBUILT 2026-08-01 · jax notes 2 layout)
> Every initiative has a unique mission page (`?mission=` / `?id=<tiv>`).
> Grid: **a** mission toggle ←→ + initiative search · **g** name + core info ·
> **b** profile + membership status · **c** post stream (3 category tabs:
> budgeting / mission_support / review) · **e** phase circle, 3 phases
> (ultimately a 3D globe) · **d** dated progress log ("Elected <tiv> with
> <EBX>", "Approved <step> for <cost>"…) · **f** pool (in-pool / committed /
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

## profile.html — Profiles
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
- [ ] Event log (vote_events: CAST/UPDATE/REMOVE), duplicate/invalid-vote flags.
- [ ] Full mission table; org verification queue (EN, 1/week).

## Backend (FastAPI + SQLAlchemy + Alembic)
- Models: Cause, Mission, Initiative, Organization, BenefactorAccount, Membership,
  MissionCandidacy, VoteP1, VoteP2, Pool, CreditCoin, Post, PostVote, Transaction.
- Endpoints: causes, missions, initiatives, organizations, candidacies, votes (p1/p2),
  posts, benefactors, transactions, admin, auth.
- [ ] Org claim/verify endpoints + acceptance record for the legal agreement.
- [ ] Guaranteed-to-pool rate (unclaimed vs claimed) in pool math.
