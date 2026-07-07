# Structure — page-by-page build spec

> UI/build spec, one section per route. The "why/how" system model lives in
> `mission_lifecycle.md`; open ideas live in `backlog.md`.
> Status keys: ✅ done · ◑ partial · [ ] not started.
> Scaffold — migrate remaining detail from the root `STRUCTURE.md`.

## index.html — Home
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
- ◑ **Entity card** — leading initiative/org; vote button per mode.
- [ ] Propose / nominate dialogs shared with the cause page.

## cause.html — Cause / election surface
- ✅ Active-missions bar (7 cause squares).
- ◑ **Annulus 2** — inner pie (phase 1 = initiatives, phase 2 = org vote share), now-marker.
- ✅ **Left cards** — leading initiatives; ◑ **swap to competing organizations in phase 2** (paged, vote, buy-more).
- ◑ **Right cards** — page 1: phase-1 (top) / phase-2 (middle) / most-recent prior (bottom); pages 2+ previous missions.
- ◑ **Phase recaps** — five stacked blocks (5 at top → 1 at bottom); live election widget in the active phase.
- ◑ **Phase 2 area** — org election: evaluation/context/analysis + org pitch; nominate/register entry.
- [ ] Discussion categories per phase.

## mission.html — Mission hub (NEW, skeleton)
- ✅ Skeleton + function blurb.
- ✅ **Click-through legal agreement** gating register/claim.
- [ ] Budget & plan builder (org).
- [ ] Progress reports (org report vs EN parallel report, benefactor-moderated).
- [ ] Member communication channel (contributor / representative / executive / beneficiary).
- [ ] Mission annulus / ring widget (deadlines, 7–12 steps).

## en.html — Earthbux News (NEW, skeleton)
- ✅ Skeleton + function blurb.
- [ ] Cross-mission feed: featured evaluations, context, analysis.
- [ ] EN parallel progress reports & accountability coverage.
- [ ] Post categories & moderation.

## profile.html — Profiles
- ✅ Benefactor profile: credit-coin wallet, choices table, settings.
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
