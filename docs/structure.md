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

Posts drive every phase (README §5). The immediate goal is to master the
**posting and newsfeed experience** across four surfaces — each a different
filtered view of the same post stream:

| Surface | Filter | Click-through |
|---|---|---|
| **Landing / newsfeed** (`main.html`) | all posts | stays on landing; users continue discussion threads |
| **Context page** (`index.html`) table | tiv-filtered | → landing |
| **Cause page** (`cause.html`) phase areas | cause-filtered | → context-page expanded table row |
| **Profile** (`profile.html`) | user-filtered | → cause page |

Post-surface rules:
- **Posts are view-only on the cause page** — no writing-in there.
- Every post everywhere shows its **date** and the **initiative/organization it
  regards**, and is **colored by that cause**.
- Reactions are **Helpful / Neutral / Harmful**, plus **Reply** — replying opens
  the landing-page discussion thread, where replies render *inside* the post.
- **Comments are posts with a parent** (`parent_post_id`).
- Post categories route by phase & scope (Context/Case → P1; Analysis / Suggestion
  / Org-review → P2; Evaluation → P3) — taxonomy in README §5.
- Table **expanded columns** filter by **tiv (or org)**, not just by cause (today
  it only filters by cause).
- Image attachments on posts — deferred (INSTRUCTIONS `## BACKLOG`).

> The "home page" is being renamed the **context page**. `main.html` and
> `en.html` both surface feeds — resolve their overlap (landing/all-posts vs.
> EN's curated cross-mission feed) as part of this focus.

## main.html — Landing / newsfeed (all-posts discussion) — DESIGN PENDING
- ◑ Feed + discussion scaffold exists; full **landing design is pending**.
- [ ] **All-posts stream** — unfiltered; the destination every other surface's
  post-clicks lead to.
- [ ] **Discussion threads** — users continue threads here; replies render
  *inside* the parent post (`parent_post_id`).
- [ ] **Post composer** — Helpful / Neutral / Harmful reactions + Reply; category
  chosen by phase & scope (README §5). The primary place to *write* posts (cause
  page is view-only).
- [ ] Resolve overlap with `en.html` (all-posts landing vs. EN curated feed).

## index.html — Context page (home / newsfeed)
- [ ] **Rename** "home" → **context page** throughout nav/copy.
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
- ◑ **Table** — state 1 initiatives (phase-1 only) / state 2 organizations.
    - [ ] **Tiv-filtered post view** — the row's expanded columns filter posts by
      **tiv (or org)**, not just cause; clicking a row leads to the **landing**
      newsfeed.
    - [ ] **Choices table** — instead of an initiatives/organizations toggle,
      toggle **phase 1 / phase 2**: show the p1 election choices in phase 1; once
      the election happens, clear the user's choices and the winning initiative
      becomes the p2 row label.
- ◑ **Entity card** — leading initiative/org; vote button per mode.
- [ ] Propose / nominate dialogs shared with the cause page.

## cause.html — Cause / election surface
- ✅ Active-missions bar (7 cause squares).
- ◑ **Annulus 2** — inner pie (phase 1 = initiatives, phase 2 = org vote share), now-marker.
- ✅ **Left cards** — leading initiatives; ◑ **swap to competing organizations in phase 2** (paged, vote, buy-more).
- ◑ **Right cards** — page 1: phase-1 (top) / phase-2 (middle) / most-recent prior (bottom); pages 2+ previous missions.
- ◑ **Phase recaps** — five stacked blocks (5 at top → 1 at bottom); live election widget in the active phase.
- ◑ **Phase 2 area** — org election: evaluation/context/analysis + org pitch; nominate/register entry.
- [ ] **Discussion, view-only** — posts here are **cause-filtered** and **read-only**
  (no writing-in); clicking a post leads to the **context-page expanded table row**.
- [ ] Discussion categories per phase (Context/Case → P1; Analysis/Suggestion/
  Org-review → P2 — README §5).

## mission.html — Mission hub (NEW, skeleton) — resolutions phase (parked)
> Phase 3. Everything here is the **resolutions stream** (budget → release →
> resolve, README §3/§5). Modeled, but parked behind the phase-1/2 posting focus.
- ✅ Skeleton + function blurb.
- ✅ **Click-through legal agreement** gating register/claim.
- [ ] **Suggestions → budget** — S/S/S *suggestion* posts (open the moment the tiv
  is elected) feed the org's budget & plan builder, between the guaranteed floor
  and the uncapped max.
- [ ] **Steps → resolutions** — 7–12 step ring; *context* posts carrying an S/S/S
  stance resolve into coin-value bumps; early resolution flagged for bonus.
- [ ] Progress reports (org report vs EN parallel report, benefactor-moderated).
- [ ] Member communication channel (contributor / representative / executive / beneficiary).
- [ ] Mission annulus / ring widget (deadlines, 7–12 steps).
- [ ] Creditcoin front/back + 3D earth (born here).

## en.html — Earthbux News (NEW, skeleton)
- ✅ Skeleton + function blurb.
- [ ] Cross-mission feed: featured evaluations, context, analysis.
- [ ] EN parallel progress reports & accountability coverage.
- [ ] Post categories & moderation.
- [ ] Resolve overlap with `main.html` (curated cross-mission feed vs. all-posts landing).

## profile.html — Profiles
- ✅ Benefactor profile: credit-coin wallet, choices table, settings.
- [ ] **User-filtered discussion** — the choices table **toggles a discussion
  area**; if the user hasn't posted about a mission, show that mission's **leading
  posts** instead. Clicking a post leads to the **cause page**.
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
