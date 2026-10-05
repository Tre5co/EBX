# INSTRUCTIONS — the plan, the queue, the register

*The one file the build runs from.*

- **`## THE PLAN`** is the clock and the pass order. Read it first.
- **`## DECIDE`** is what only Jax can answer. A pass does not start with its blocking decisions open.
- **`## BUILD SEQUENCE`** is the queue, and the only section a build pass executes. One pass = one section, top down.
- **`## OPEN DEFECTS`** is every known-wrong thing, until it is fixed.
- **`## BACKLOG`** is named but not queued. It may be reorganized during a pass; it is not built.
- **`## REMOVAL REGISTER`** is what is safe to delete and what is not.
- **`## ARCHIVE`** is finished pass reports.

*Page specs live in `docs/structure.md`; the system model in `README.md` §5; the
money rulings in `docs/money_model.md` §0; each mission's process in
`docs/mission_model.md`. This file names the goal and the stop condition — it
never carries a second copy of a spec.*

<!-- TOC -->
## Contents

- [0. HOW A PASS RUNS](#0-how-a-pass-runs)
- [INBOX](#inbox)
- [1. THE PLAN](#1-the-plan)
  - [What this is all for](#what-this-is-all-for)
  - [Pass order, and why](#pass-order-and-why)
  - [Proposed re-order (2026-10-05) — awaiting D33](#proposed-re-order-2026-10-05--awaiting-d33)
  - [The build clock](#the-build-clock)
- [2. DECIDE](#2-decide)
- [3. BUILD SEQUENCE](#3-build-sequence)
  - [P1. Mission](#p1-mission)
  - [P2b · Organization experience](#p2b--organization-experience)
  - [P2 · Home](#p2--home)
  - [Footer](#footer)
  - [P3 · Posting](#p3--posting)
  - [P3b · News](#p3b--news)
  - [P4 · Event log + Inbox](#p4--event-log--inbox)
  - [P5 · Money made visible](#p5--money-made-visible)
  - [P6 · Counterparty](#p6--counterparty)
  - [P7 · Admin & trust](#p7--admin--trust)
  - [P8 · About](#p8--about)
  - [999 · Housekeeping — ends every pass](#999--housekeeping--ends-every-pass)
- [4. OPEN DEFECTS](#4-open-defects)
- [5. BACKLOG](#5-backlog)
- [REMOVAL REGISTER](#removal-register)
  - [§A — safe now, nothing reads them](#a--safe-now-nothing-reads-them)
  - [§B — one edit, then safe](#b--one-edit-then-safe)
  - [§C — live, but the replacement already exists](#c--live-but-the-replacement-already-exists)
  - [§D — looks dead, is not](#d--looks-dead-is-not)
  - [Also worth doing while here](#also-worth-doing-while-here)
  - [Added 2026-09-08 (build-seq §0 + §6)](#added-2026-09-08-build-seq-0--6)
  - [Added 2026-09-16 (build-seq §1)](#added-2026-09-16-build-seq-1)
  - [Added 2026-09-18 (build-seq §4–§6)](#added-2026-09-18-build-seq-46)
  - [Added 2026-09-24 (P1 — the merge)](#added-2026-09-24-p1--the-merge)
  - [Added 2026-09-25b (P2 · Home)](#added-2026-09-25b-p2--home)
  - [Added 2026-09-28 (P1 mission edits)](#added-2026-09-28-p1-mission-edits)
  - [Added 2026-09-29 (P3 · Posting)](#added-2026-09-29-p3--posting)
  - [Added 2026-09-29 (inbox)](#added-2026-09-29-inbox)
  - [Added 2026-09-30 (P2 · Home mods)](#added-2026-09-30-p2--home-mods)
  - [Added 2026-10-01c (Home tweaks)](#added-2026-10-01c-home-tweaks)
  - [Added 2026-10-01 (mission pass)](#added-2026-10-01-mission-pass)
- [ARCHIVE](#archive)
  - [2026-10-05 — About reshape · P1 mission items · P2 Home items · the re-order proposal](#2026-10-05--about-reshape--p1-mission-items--p2-home-items--the-re-order-proposal)
  - [2026-10-01d — P3 · the posting display pass](#2026-10-01d--p3--the-posting-display-pass)
  - [2026-10-01c — Home tweaks · HR2 backfilled · admin removal · Posting and Footer re-sorted](#2026-10-01c--home-tweaks--hr2-backfilled--admin-removal--posting-and-footer-re-sorted)
  - [2026-10-01b — P2 · Home pass (the four doors) · P2b rebuilt on D26/D28](#2026-10-01b--p2--home-pass-the-four-doors--p2b-rebuilt-on-d26d28)
  - [2026-10-01 — P1 mission pass (Jax's 17 items) · DECIDE cleared · P2b added](#2026-10-01--p1-mission-pass-jaxs-17-items--decide-cleared--p2b-added)
  - [2026-09-30 — P2 · Home mods (the five steps, the mission hub)](#2026-09-30--p2--home-mods-the-five-steps-the-mission-hub)
  - [2026-09-29b — Unified elections (Jax's CE · ME · OE panels)](#2026-09-29b--unified-elections-jaxs-ce--me--oe-panels)
  - [2026-09-29 — P3 · Posting (and the inbox, filed)](#2026-09-29--p3--posting-and-the-inbox-filed)
  - [2026-09-28 — P1 mission edits (the compact page)](#2026-09-28--p1-mission-edits-the-compact-page)
  - [2026-09-25c — Footer, Contact us, the bots](#2026-09-25c--footer-contact-us-the-bots)
  - [2026-09-25b — P2 · Home](#2026-09-25b--p2--home)
  - [2026-09-25 — P1 review 2 (the report is the main display)](#2026-09-25--p1-review-2-the-report-is-the-main-display)
  - [2026-09-24b — P1 review pass (Jax's review of the merged page)](#2026-09-24b--p1-review-pass-jaxs-review-of-the-merged-page)
  - [2026-09-24 — P1 · The Merge (Elect → Mission)](#2026-09-24--p1--the-merge-elect--mission)
  - [2026-09-20 — Landing top card + Elect two cards](#2026-09-20--landing-top-card--elect-two-cards)
  - [2026-09-18 — the wheel moves to the landing page](#2026-09-18--the-wheel-moves-to-the-landing-page)
  - [2026-09-17 — the percentage ballot](#2026-09-17--the-percentage-ballot)
  - [2026-09-16 — the money model rewrite](#2026-09-16--the-money-model-rewrite)

<!-- /TOC -->

## 0. HOW A PASS RUNS

1. **Stop first if `## INBOX` below is non-empty** — Jax has pasted something that has not been filed yet. File it, ask, and stop.
2. **Check the pass's `Decides`.** If one is unanswered, say which and stop. Do not guess a decision.
3. **§0 sweep** — (a) errors, (b) blockers, (c) inconsistencies, (d) not blocking → `## REMOVAL REGISTER`, updated. Anything found goes to `## OPEN DEFECTS` with an id, not only into the pass report.
4. **Build only what the pass's `Includes` names.** Everything else is out of scope even if it is one line away.
5. **Finish on the pass's `Done when`** — the named check script, green.
6. **Then 999 housekeeping** (below), and move the pass report to `## ARCHIVE`.

**Standing rules.** Without permission, only the build sequence is executed.
Money-moving code and schema migrations are proposed, not applied, without a
nod. A line starting with `!-` is read, not executed. The docs describe what
IS, not what ISN'T.

## INBOX

*Empty. Filed and built 2026-09-29 (unified elections): the organization vote
that did not update, "buy tokens" → **Donate more**, and the five election
panels — see `## ARCHIVE` › 2026-09-29b, where the drawings are kept.*

## 1. THE PLAN

### What this is all for

Five long-term goals. Every pass below serves one of them, and that is the test
for whether a new idea belongs in the queue at all.

| # | Goal | What it means in the product |
|---|---|---|
| **G1** | **Donors control the money** | The weekly pool goes where benefactors vote, not where a grantmaker decides. Cause → initiative → organization → framing → exchange, every week, forever. |
| **G2** | **The money is legible and final** | $1/week, 10 tokens, one commit; final at T+15; a public ledger; missions that can be COMPLETED. A benefactor can always answer "where is my money and what did it do?" |
| **G3** | **The network produces the decisions** | Research, news and budgeting are not decoration — they are how a mission gets decided and run. The social surfaces exist to make better allocation, not more time on site. |
| **G4** | **Earthbux News is the accountability engine** | A funded slice buys supervision and coverage: we report on the cause, or we report on the organization. |
| **G5** | **It survives contact with the world** | Nonprofit status, banking, a payee, vetted counterparties, and a thick skin against capture — vote-buying, collusion, spam. |

### Pass order, and why

**P1 The Merge** comes first because every other surface points at a mission,
and right now a mission lives in two places. Merging is also the cheapest
moment to delete the annulus leftovers — the code is already half-dead.

**P2 Home** comes second because it is the front door and it currently explains
instead of showing. It depends on P1 only for where its links land.

**P3 Posting** comes third because P4 has nothing to notify about until people
can post from anywhere, and Home's feed is thin until they do.

**P3b News** follows straight on, because once every post can be made
anywhere, News is where every post can be *found* — the one ordered,
searchable feed of everything, algorithmic but not personalized. Home is the
personalized cut of it and Mission the mission-ized one (G3, G4).

**P2b Organization experience** is next (added 2026-10-01: "I need to do this
asap"). Every mission ends in an organization, and today an organization has
no page, no way in before its initiative wins, and no voice. It comes before
P3b because News and the inbox both carry organization posts, and before P6
because P6 pays an organization that P2b lets claim itself.

**P4 Event log + Inbox** turns single visits into a habit (G3). It needs P3's
posts and P1's phase changes as its event sources.

**P5 Money made visible** is one pass, not five, because withdraw, convert,
allocations, the two accounting numbers and the coin price all read the same
token model (G2). Split across surfaces, they drift.

**P6 Counterparty** and **P7 Admin & trust** are gated by external lead times
and by having real activity to administer (G4, G5), so they sit behind the
surfaces — but their *enquiries* start now and are already on the clock.

### Proposed re-order (2026-10-05) — awaiting D33

*Read against the queue as it stood on 2026-10-05 and the whole BACKLOG. Nothing
below is queued until Jax answers D33; when he does, `## BUILD SEQUENCE` is
re-sorted to match and this section folds into "Pass order, and why".*

**Done this pass, and so off the front of the queue:** P1's five items (three
built, D31 and D32 filed), P2 · Home's six items, and the About reshape, which
was most of P8.

| # | Pass | What it combines | Why here |
|---|---|---|---|
| **A** | **P2b · Organization experience — finish** | P2b's open items (memberships reshape — migration proposed; suggestion → candidacy; verification rule; progress reports; framing shows the org's input) **+ Jax's org dev review** (org page → mission page logs you out; sign-up: no cause, Q&A split from admin questions, one agreement, website optional / phone-or-email, political candidates and corporations under integrity) **+ P6's "Org registration + claim" and "Initiative coins on the organization home"** (already P2b in practice) | Still the critical path on the clock, half-built, and the org-review bugs are live defects (a logout on navigation). Finishing it before News means News carries organization posts from organizations that can actually log in. |
| **B** | **P7a · Admin tools** *(pulled forward, split from P7)* | Edit any part of a mission (P7 Includes) · retarget posts and change tags · each account's dashboard viewable · fix Profile's admin link (BACKLOG › Admin) · pull live data to local (BACKLOG › Admin) · the bot console + bot task split + vote spread (**F6**) · D17 backfill tooling for **F11** · the relist-past-winners one-off (below) | Small (≈3 days), and every later pass needs Jax to be able to *fix data without a migration* — F11, F20, F24 and the stale `current_phase` all wait on it. Bots that spread votes make every later check meaningful. |
| **C** | **P3b · News + the weekly edition** | P3b as written **+** P4's leftovers (weekly edition on Home and in News, "a phase opens" events, the reports queue in admin) **+** P3's "Still waiting" (News cards → `EBX.Post.collapsed`, the cause-coloured top row linking to the *mission*, not News) **+** BACKLOG › Posting "Create the weekly report … with the date of the week" **+** BACKLOG › Admin "Google preview" and Future "share on social media" (= P3b's OG / sitemap / robots) **+** the Framing → **Prep** rename in copy (D27) | One pass over everything a reader *reads*. The weekly edition is the habit loop P4 built the back half of; News is where it lives. Fixes **F25**. |
| **D** | **Mission hygiene** *(P1 follow-ups, renamed)* | **F19** (phone width), **F22** (oe_check), **F24** (`meMission` skips missions past T; stale `current_phase`) · after-nominate the window collapses (BACKLOG › Mission) · bot cases on the mission page · retroactive posts for recent elections (clock `posts`) | Short and mechanical; best done right after C so the mission page and News agree on posts. |
| **E** | **Design direction** *(new, 1–2 days, decision first)* | BACKLOG › Future "simple, clean, monochrome, interlocking panels, calming white background" + "monochrome on things that aren't cause-related" + light/dark setting · **D32** (annulus as cause picker / profile navigator) · real images (BACKLOG › Home) · the instructional screen-recording (P2 · Home's first line) | Every pass so far re-polished the dark theme by hand. If the site is going light/monochrome, decide it **before** P5 rebuilds Profile — otherwise Profile is built twice. The screen-recording waits until the UI stops moving. |
| **F** | **P5 · Money made visible + the wallet** | P5 as written **+** BACKLOG › Profile "add funds first … every action relies on the wallet — create this asap" **+** the Profile reshape (two side panels, coins as "Donated", full dashboard, choice-card fixes **F7**) **+** **D31** (grant timing) **+** **F15 / F20 / F26** (legacy stakes — after B's read-only production counts) | The wallet-first model *is* "money made visible"; building it as a separate Profile pass would read the token model twice. Blocked on D11, D22–D25, D31 — answer them during A–E. **Decide BACKLOG › Future "budget day → T+16" and "scrap the initiative election?" here too**: both rewrite `money_model.md`. |
| **G** | **P6 · Counterparty** | P6 minus what A took: M1–M3 messages, vetting gates, beneficiary voice, mail transport (unblocks self-serve password reset, BACKLOG › Infra), check flow and payee | Still gated by D11, D12 and the bank/nonprofit enquiries — external clocks, not engineering. |
| **H** | **P7b · Trust** | New-account vote-buying gate · moderation, IP/spam, the real classifier · Rules page (Footer "soon") · kids accounts after legal review · commit-history record | Needs real activity to tune against, which C–G create. |
| **I** | **P8b · About & static pages** | What is left of P8 (the Posting/Earthbuck copy lives in How it works already) · Footer's "soon" pages: White paper (Jax's document), Help Center, Safety, Privacy, Terms, Accessibility · Jax's bio and photo on Our team | Copy-heavy and waiting on Jax's documents and the legal review, so it goes last; each page can ship the day its copy exists. |

**Pushed back (not queued):** the one-post-at-a-time reader (after C proves the
feed), the animated process diagram (`s4` — after E), the Mission "read-only +
News as the contribution hub" idea (revisit after C: News may already be that),
Locations and the globe, mission trips/travel (still deliberately off the chart),
the Apache stack, spending EBX on merch/travel (after G).

**Combined, so they stop appearing twice:** Profile appears in BACKLOG › Profile,
P5 and P2b's out-of-scope — now F. Admin appears in P7, BACKLOG › Admin and
BACKLOG › Bots — now B (tools) and H (trust). The weekly update appears in P3,
P4 and BACKLOG › Posting — now C.

### The build clock

Anchored at **Monday 2026-09-21** (W0). Durations are working estimates for one
builder plus this assistant, not commitments.

```mermaid
gantt
    title Earthbux build clock — W0 = 2026-09-21
    dateFormat YYYY-MM-DD
    axisFormat %b %d

    section Unblock (not engineering)
    Buy the earthbux domain + mailbox         :crit, unblock1, 2026-09-08, 2d
    Nonprofit status enquiry                  :crit, unblock2, 2026-09-08, 60d
    Banking / payee enquiry                   :crit, unblock3, 2026-09-08, 60d
    Answer the DECIDE list (P1 rows)          :done, unblock4, 2026-09-23, 1d
    Answer the DECIDE list (P2 rows + D13-D17) :done, unblock5, 2026-09-24, 2d
    Answer the DECIDE list (P3 rows D8 + D19-D21) :done, unblock6, 2026-09-28, 1d
    Answer D26 + D28 (organization accounts)  :done, unblock7, 2026-10-01, 1d
    Answer D29 + D30                          :done, unblock8, 2026-10-01, 1d

    section Surfaces
    Landing wheel + Elect two cards           :done, s0, 2026-09-20, 1d
    P1 The Merge (Elect -> Mission)           :done, p1, 2026-09-24, 1d
    P1 review pass (Jax's 13 items, D13-D16)  :done, p1r, 2026-09-24, 1d
    P1 review 2 (report is the main display)  :done, p1r2, 2026-09-25, 1d
    P1 follow-ups (dead top-card + box code)  :p1b, after p1r2, 2d
    P1 mission edits (the compact page)       :done, p1e, 2026-09-28, 1d
    P1 unified elections (CE/ME/OE panels)    :done, p1u, 2026-09-29, 1d
    P1 mission pass (Jax's 17 items)          :done, p1m, 2026-10-01, 1d
    P2 Home pass (four doors, steps list, hub) :done, p2h, 2026-10-01, 1d
    P2 Home tweaks + admin removal            :done, p2t, 2026-10-01, 1d
    P3c Posting display (card, votes on Home)  :done, p3c, 2026-10-01, 1d
    P2b Organization experience (accounts, 3 tabs, campaign pages) :crit, p2b, after p1m, 12d
    P2 Home (annulus + The Network + feed)    :done, p2, 2026-09-25, 1d
    P2 Home mods (five steps + mission hub)   :done, p2m, 2026-09-30, 1d
    Footer + Contact us (F9)                  :done, foot, 2026-09-25, 1d
    P3 Posting (post.html, gates off)         :done, p3, 2026-09-29, 1d
    P3b News (the feed of everything, RSS, OG) :p3b, after p2b, 4d
    P4 Event log + Inbox                      :done, p4, 2026-10-04, 1d
    P8 About reshape (tabs: story, goals, how, team) :done, p8, 2026-10-05, 1d
    P1 + P2 items (x leading, post about x, hub)  :done, p1x, 2026-10-05, 1d
    Animated process diagram                  :s4, after p4, 7d

    section Money model
    money_model.md rewrite + ladder in code   :done, m1, 2026-09-16, 1d
    Framing: losers exchange + cash withdrawal :active, m2, 2026-09-17, 10d
    P5 Money made visible (withdraw/convert)  :p5, after p4, 7d
    Budget day: org claim                     :m3, after m2, 3d
    Deployment order (provenance queue)       :m4, after m3, 7d

    section Data to build against
    Voting bots (admin simulation)            :done, bots, 2026-09-16, 1d
    Bot task split + vote spread fix          :bots2, after p1, 3d
    Retroactive posts for recent elections    :posts, after p3, 3d

    section Counterparty (P6)
    Mail transport                            :c1, after unblock1, 3d
    M1 registered / M2 might-win / M3 won     :c2, after c1, 7d
    Org registration + claim page (now P2b)   :c3, after p1m, 7d
    Vetting gates                             :c4, after c3, 7d
    Check flow + payee                        :c5, after unblock3, 14d

    section Trust and admin (P7)
    admin.html absorbed into the site         :t0, after p4, 4d
    New-account vote-buying gate              :t1, after m4, 4d
    Kids accounts (legal review first)        :t2, after unblock2, 14d
    Moderation / IP + real content classifier :t3, after t1, 7d

    section Housekeeping
    Docs reshuffle + indexes                  :h1, after p2, 3d
    ebx_shared.ts retired (js is source)      :done, h2, 2026-09-16, 1d
```

**Deliberately not on this chart.** Mission trips, travel and spots on missions
— the largest unscoped idea in the file, with its own safety, cost and
liability surface. It should not be designed until one mission has resolved.

## 2. DECIDE
*Only Jax answers these. A pass with an open blocker does not start. Answered
questions are cleared: each answer now lives in the pass or doc it shaped.*

| id | Question | Proposed | Blocks |
|---|---|---|---|
| **D11** | Fee-for-coverage instead of a cut of donations ("Earthbux donates 100%, collects a fee from the philanthropy")? | — (changes `money_model.md` and the nonprofit application; an independence risk) | P5, P6 |
| **D12** | Where does the money actually live — banking and custody? | — | P6 |
| **D17** | What happens to a race that closes with no approved candidate (wil0, hpr0 — F11)? | Jax backfills them | P5, P7 |
| **D18** | One-line descriptions for **Missions** and **News** (Home is "You donate. We follow."). | Missions: "Every mission, from the vote to the last receipt." · News: "What the network found this week." | P3b (not blocking) |
| **D22** | Research paid in minted EBX on budget day: (a) the pot, (b) which votes split it, (c) its place in deployment order, (d) EBX never buys anything personal. | 3/32 · only this mission's votes, weighted by EBX held · same tier as the initiative's winning backers · nothing personal | P5 |
| **D23** | Who checks a budget item, and how is a wrong one caught? | price — evidence attached · feasible — the organization · legal/honest — Earthbux News; a challenge with evidence, not a downvote | P5 |
| **D24** | What does budget day hand over? | the reporting, not the control; vetting finished before it | P5 |
| **D25** | Move budget day back (framing 8 or 10 weeks)? | the overlap is the rotation, not framing's length — separate ballots per benefactor instead | P5 |
| **D31** | *(P1, 2026-10-05)* "Tokens should be granted as soon as the initiative election opens." Today a grant exists only in its week and may enter only the ME/OE that **closes** that week (`money_model.md` §0.7, §4; `crud.replace_p1_shares` → `granted_allowed = mission.cause_id == active_cause_id()`). That is why only **4 tokens** (purchased) could go into the Land election: Land is not this week's door, so granted ct is refused there. Change the rule? | (a) keep the rule and say so on the ballot ("your 10 granted tokens open on <date>; purchased tokens can go in now"); or (b) a grant may enter **any initiative election that is open** in its week (still one grant per week, still non-transferable) — a one-line change to `granted_allowed`, plus §0.7/§4 rewritten. Money-moving: proposed, not applied. | P5 (or a small money pass before it) |
| **D32** | *(P1, 2026-10-05)* "I really should think about replacing the cause toggle with the rotating annulus." | Not yet — decide with the design-direction call (D33's step E): the annulus is already the mission page's centre, and a second, rotating one as the cause picker is the BACKLOG › Profile idea ("navigate using the annulus") too. Prototype once, use on both. | — (design) |
| **D33** | Adopt the re-ordered build sequence in `## THE PLAN` › *Proposed re-order (2026-10-05)*? | yes | the next pass |

## 3. BUILD SEQUENCE

### P1. Mission
*Pass 2026-10-05 — see `## ARCHIVE` › 2026-10-05.*
- ✅ In the mission navigator, instead of "which cause holds" and "Land x", display "x leading". — the cause card reads "<cause> leading · the window of <date>", an open initiative election "<initiative> leading", an organization election "<org> leading" in its sub-line.
- ⏸ for some reason I'm only able to commit 4 tokens for the land election at the moment. Also, tokens should be granted as soon as the initiative election opens. — **not a bug: the rule.** A granted token may only enter the election that closes in its grant week (Land isn't this week's), so only your 4 purchased tokens could go in. Changing it is money-moving → **D31**.
- ⏸ I really should think about replacing the cause toggle with the rotating annulus. — a design call → **D32**.
- ✅ instead of "discuss", have "post about x" — every ballot bar's Discuss → **Post about <initiative / Cause n / cause>**, opening the composer on that target.
- ✅ tivs should not be removed from the ballot after they have won. — `crud._relist_winner`: when an initiative wins, a fresh candidacy of it (`<id>-r<next cycle>`, no votes) is listed in the cause's next initiative election beside the re-listed losers. Forward-going only; winners elected before today are not copied (a one-off for P7a).

### P2b · Organization experience
*(Added 2026-10-01; rebuilt the same day on Jax's answers to D26 and D28, and his
notes on the public profile and the campaign page.)*

*Org dev review*
- The Q&A needs to be integrated into the mission, not seperate. - It's not seperate, it is appearing in both places, like it should. 
- ✅ *(built 2026-10-04)* "For charities" needs to direct you to an "Organization login" page. It's not actually on admin.html, it just looks similar. Also my org login did not work. — **For charities → `/org`**, whose sign-in is now drawn in admin.html's palette and card; a claimed profile (`/o/<org>`) links to it. The login "did not work" because an application's login stays **pending** until staff approve it: the sign-in now says so (pending · not approved · switched off, with the application number), and when the same browser is signed in as staff it offers **Approve it now**. The old `admin.html?register=1` doors (Home, Profile, Mission, the org dialog) now go to `/org#apply`.
- Signup - don't need to select which cause. - public contact information can also be a benefactor profile? - The short answer questions should be seperate from the administrative questions. - the integrity section is interesting. Add political candidates or corporations. - the 5 agreements can be made into one agreement.
- Website shouldn't even be required, someone can fill that in later. Or maybe they need a phone or an email..
- Going to the mission page from the org page logs you out.

**▶ Framework built 2026-10-02** (Jax: "build the framework and basic,
rudimentary pages … build a bot org for Earthbux … draft the questions on the org
application"). Spec of what exists: `structure.md` §8d. `org_check` 44/44,
`posting_check` 66/66 on a db copy.
- **Built:** organization accounts + their own login; every benefactor route
  refuses an organization token; the application (= the claim) and its
  questions (`org_config.py`, two stages); staff review in admin › *Org
  applications*; `/org` with Home · Initiatives · Profile + a tab per campaign;
  administrators create members' logins; Run for this; Suggest us (a post on the
  initiative, read back as "you suggested the winner"); the public profile
  claimed/UNCLAIMED; the campaign page's five sections; organization answers in
  the Q&A; the organization bot (`ebx_bots.py org`, Earthbux).
- **⚠ Migration `a7c4e2f9b1d3` (additive: two new tables).** The server
  migrates to head on startup, so it applies on the next deploy. Nothing
  existing is altered; `downgrade` drops only the two tables.
- **Still open in P2b:** the `memberships` reshape and
  `mission_candidacies.tiv_id` (both still proposed — Suggest us works without
  them); the verification rule (spec check, `mission_model.md` §6); progress
  reports beside EN's; framing showing the organization's input; a design
  pass on both pages; and the four Done-when items not covered by an
  automated suggestion→candidacy promotion.
- **Note for the live site:** run the bot once there —
  `python scripts/bots/ebx_bots.py --base https://earthbux.net org --staff-handle GameMaster`
  (add `--bot-key` so the login is marked as a test account).

**Goal.** Organizations get **their own accounts and their own experience**. An
organization cannot vote; it cares about the missions it might run and the
campaigns it is already in. Everyone else sees two public pages for it: its
**profile** and, for each election it runs in, its **campaign page** (G4, G5).

**Decided** *(cleared from DECIDE 2026-10-01 — D26, D28, then D29, D30)*.
- **D28 — its own login.** "Organization accounts will need their own login
  because people may want to be active on Earthbux separately from their
  involvement with the org they work for. Membership roles will need to be
  changed to account for this."
- **D26 — a different experience, in three tabs.** "The org has a unique campaign
  page for each mission. They will have an entirely different experience,
  because they are not able to vote … Home will be where they stay connected
  with Earthbux and navigate through their active campaigns. Initiatives will be
  where they find potential missions (similar to missions.html but only steps
  2–3), profile will be where they create general content, and create an
  outward facing profile. 3 tabs, and a campaign-specific tab for each campaign
  accessible from profile."

**Includes**

*Accounts*
- **Organization accounts** — a second account kind with its own sign-up and
  sign-in, never a mode of a benefactor account; one person may hold both. An
  organization account belongs to one organization. **D29:** "Each organization
  member will have their own login, with their account being created by someone
  with an administrative role in that organization" — the claimer becomes its
  first administrator and creates the others' logins (Profile › Members).
- **Membership roles reshaped** — `memberships` (community · rep · executive ·
  beneficiary, all on benefactor accounts today): rep and executive move to
  organization accounts; benefactors keep community and beneficiary. A
  migration — proposed, not applied.
- **No voting** — an organization account has no wallet and no ballots; every
  vote route refuses it (the server, not just the page).
- **Claiming makes the account** — a person claims an organization (the
  agreement already in `org_claims`); staff approve; the organization account is
  created, or linked if one exists. Registering an organization stays open to
  anyone, from Home, Mission and Profile, with or without an initiative.

*The organization's own site — the nav is three tabs, plus one per campaign*
- **Home** — where it stays connected with Earthbux: its active campaigns (each
  race, its standing and days left), what changed on them, Earthbux's updates,
  and a way into each campaign.
- **Initiatives** — where it finds potential missions: the mission page's steps
  2–3 only — the initiative elections (what may become a mission) and the open
  organization elections (what it can run for) — with **Run for this** (a
  candidacy) and **Suggest us** on an initiative that has not won.
- **Profile** — where it writes general content (organization updates) and edits
  its outward-facing profile; the campaign tabs open from here.
- **A tab per campaign** — where it writes what its campaign page shows: the
  plan, the promises, its answers in the Q&A.

- **Verification** — an organization that has not been in the top 3 of a race
  with 4 weeks left applies for a verified profile (Jax: "I think that was my
  spec" — the rule to confirm against `mission_model.md` §6 before building).

*Two public pages*
- **The organization profile** — `/o/<slug>`, for everyone, and every
  organization name on the site links here. Claimed: name, logo, website,
  description, verified state, its updates, its campaigns, the missions it won.
  **Unclaimed**: the title, a discussion, any missions won or running, and a big
  **UNCLAIMED** panel. **D30:** "a general all-purpose display describing to
  benefactors what Earthbux is doing to contact the organization, and what they
  might be able to do" — one shared panel (not written per organization), with
  the organization's contact state if Earthbux has one.
- **The campaign page** — one per election the organization runs in
  (`/o/<slug>/<mission>`):
  - **Plan** — budget, timeline, milestones (built from the mission's budget
    items, with the organization's own);
  - **Receipts** — past outcomes, dollars moved, missions completed;
  - **Live ballot slate** — who endorses it, its vote count, time left;
  - **Q&A** — every post about the organization, pulled in, with its answers;
  - **What they are promising** — the campaign's mission statement.
  The mission page's organization election links each candidate to its campaign
  page.

  The campaign page is the mission page seen from the organization's side
  (Jax): "Benefactors will see what the organization plans to do / wants to do,
  organizations will see what they have to do and what benefactors want them to
  do, both will see the progress and history and news." So it reuses the
  mission page's report and posts rather than building a second copy.

*Carried over from the first draft*
- **Suggestions become candidacies** — `mission_candidacies.tiv_id` (a
  migration — proposed, not applied), so an organization suggested for an
  initiative before it won becomes a pending candidate when it wins, and the
  `tiv:` tag link retires.
- **Progress reports** *(from P1 › The Report)* — once a campaign wins, its page
  carries the organization's report beside Earthbux News's parallel report,
  benefactor-moderated, facing Background · Investigation · Analysis.
- **Framing shows the organization's input** — the campaign's plan and its
  answers on the budget items, in place of the mission statement and initiative.
- **An organization-side bot** — a clearly fictional test organization with its
  own account that claims, runs a campaign and answers, so the pass can be
  exercised end to end.

**Decides.** — none open (D26, D28, D29, D30 answered 2026-10-01). The
verification rule above is a spec check, not a decision.

**Done when.** An `org_check` covers: signing up and in as an organization;
an organization account refused by every vote route; claiming, and the account
it creates; the three tabs and a campaign tab per campaign; the public profile
claimed and unclaimed; an organization administrator creating a member's
login; a campaign page's five sections against the API; Run
for this creating a candidacy; and a suggestion becoming a candidacy when its
initiative wins.

**Out of scope.** Payment, payee, check flow, vetting gates and mail (P6). The
benefactor profile ("still shoddy") — BACKLOG › Profile.

---

### P2 · Home
*Pass 2026-10-05 — see `## ARCHIVE` › 2026-10-05. Everything but the first line is built.*
- ⏸ The instructional video can go along with (or be replaceb by) instructional screen-recording of how to use the platform. — needs the recording; proposed for step E of the re-order, once the UI stops moving.
- ✅ In the missions hub, conserve space the same way we did in the descriptions - we don't need a full border and can have shared borders. Also, it needs to say "Leading: initiative". Right now it looks like the initiative count is the thing that's leading which is not accurate. The "closes x" line should be in the same line that shows the phase, so "Initiative election - closes oct 18" should be across the top row. The bottom row should show "cause - started x". No need for the "week x". Also, since causes are now in the boxes, no need for the row labels. Also, no need for the column labels (cause election, newest mission, ...)
- ✅ The collapsed version can remove the phase labels from inside the cards and have an all-time header for the 2 cards. Instead of "Missions", say "This Week's Decisions". There can be all time column headers that say Initiative Election and Organization Election, and the cards should be titled "Leading initiative/organization: x" with vote/commit count and have the runners up below.
- ✅ The 5 steps (to the right of the animation) should be labeled 1. - 5.
- ✅ The two key decisions should be numbered 1 and 2.
- ✅ Remove "The Network" and "What the network made this week", Put the toggle options in the same row as +Post


### Footer
*Built 2026-09-25 — see `## ARCHIVE` › 2026-09-25c, where the sorting table is
kept. Status 2026-10-01.*

**Done**
- Five columns — Earthbux · Take part · Causes (the seven) · Support · Legal — and
  the bottom line (© 2026 Earthbux · earthbux.net · earthbuxinc.com); the
  tagline "Collective action, measured in impact."
- Live links: About (and its sections), Join a mission → Missions, Read the
  news, Nominate an organization, Join the team, the seven causes.
- **Contact us** opens a dialog; every message is stored and emailed to
  jax@earthbux.net through Resend (2026-09-26).
- Anything without a page is drawn "soon", never a dead link (F9).

**Still waiting** (each is drawn "soon" until its page exists)
| Item | Waits on |
|---|---|
| White paper | Jax's document (BACKLOG › Footer: "Replace money model in white paper with my document") |
| Rules | a rules page (P7 › moderation) |
| Register a philanthropy | the organization accounts and claim flow — **P2b** |
| Help Center · Safety | a help page (`earthbux.net/help`) and a safety page |
| Privacy · Terms | legal copy (the nonprofit / legal review) |
| Accessibility | a statement page |
| Docs · GitHub | the repo going public |
| Beneficiaries | the beneficiary surface (P6) |
| Get the app | an app |
| Send love / Pay us | a donate-to-Earthbux link — D11, D12 |

### P3 · Posting
*Built 2026-09-29; the display pass 2026-10-01 — see `## ARCHIVE` › 2026-09-29,
› 2026-10-01 (the Mission statement) and › 2026-10-01d (the card). The posting
model, its diagrams and the card now live in `docs/structure.md` § 8c.*

**Goal.** One way to make a post, reachable from everywhere, easily customizable
for any posting purpose — every post displayable by every page on the platform.

**Done**
- One composer (`post.html`), reached from Home, News, a profile, every post
  button on the mission page and About; the link decides the type and target.
- All posting gates removed; the Review lane gone (Case, Evaluation and
  Mission statement are tags on the all-purpose post).
- Targets and limits per type, versions (D21), Backgrounds rolling (D19), votes
  per mission, pulling an old post, the Analysis composer with its leads (D20).
- `EBX.Post`, How to post on `about.html#posting`, the feed framework and the
  vote names; nominations may carry a post; admin deletes posts (P7).
- **The display pass (2026-10-01):** the card redrawn (title left · account,
  date, type, cause right · votes and Discussion → along the foot), no colour
  coding, voting from Home, up and down votes on general and research posts
  (a second press takes the vote back), and whether the author voted in the
  mission's initiative election.

**Still waiting**
- Let's improve the posting experience, and prepare to build the news feed in the process. After this, we'll build out the org experience.
- ✅ **Built 2026-10-02 (the items through "image … even in the small version" below)** — one card on Home, News and the mission page (`EBX.Post.collapsed`): top bar = target · the targeted mission's next decision and date (`next_decision` in `posting.serialize`) · cause, the whole bar linking to the mission; title · source · date · tag; the image even collapsed; …show more expands **in place** (citations, whether the author voted in the election, see more like this → News `?cause=` `?initiative=` `?author=` `?source=`, or `/o/<org>`; replies and a reply box); votes · comments · reply. Home's four toggles read `GET /posts?source=earthbux|charity|individual`; News has the same chips. There are no public benefactor profiles yet, so "from <user>" opens News filtered to that author. Checks updated: render, home (76), feed, landing (21).
- The posts are going to look the same whether you're on news or home. Clicking on the post will expand into the full post, (where the text trails off in a ..., have a show more button). In the expanded post, it shows more info like - voted in this election or not, citations, see more like this (in <cause>, about <initiative>, from <user>) which links to news or a user profile in the user case.
- The home page will have 3 toggles, basedon the source of the post, and a fourth "all" option. The 3 sources are Earthbux, Charities, and Individuals.
 _____________________________________________________________________________
|_*Target*___________________*Target <next_decision>: date*____________*Cause*|
| Post title - source(handle/org_name/earthbux) - date -               tag    |
|                                                                             |
|    contents                                                                 |
|                                                 ...show more                |
|_votes_number-of-comments_reply______________________________________________|

- Clicking anywhere in the top bar goes to the mission it's targeting.
- If the post is an image, the image should be shown even in the small version.


**MORE**
The top row should have the color of the cause and be more inviting for users to check it out.
The top row "Oceans" directs to the news. Should direct tot he oceans mission page.

- **News's cards** — `cause.html` still draws its own card (`fd-card`) with its
  own reactions; it moves to `EBX.Post.collapsed` with the News rebuild (P3b).
- **One post at a time as you scroll, centred** — the Instagram-like reader
  (BACKLOG › Future), with P3b.
- The reward for suggesting a winning initiative (Jax: "I should brainstorm").
- Notifications when a cited post changes (P4).
- Video on posts (needs file storage — F23).

**Decides.** — none open.

---

### P3b · News
*(inbox 2026-09-29: "Where is news in our plan?")*

**Goal.** News is **the ordered, searchable feed of everything, everywhere** —
algorithmically ordered, never personalized. Home is personalized; Mission is
mission-ized. The difference between Home and News is the point of the pass
(G3, G4).

| Surface | Scope | Personalization | Order |
|---|---|---|---|
| **News** | wide — every post | none | algorithmic (`feed_rank`), the reader picks: Latest · Trending · Research · Missions |
| **Home** | middle — the reader's causes and missions, and the most recent weekly update | full (follow-graph vs. best of the network — after P4's event log) | personalized |
| **Mission** | narrow — one mission, context-rich | none | the mission's own: leads, then votes in that mission |

*Jax's notes, kept:* Trending is velocity with time decay; outrage ranking is
the norm and we need something different; posts with identical timestamps will
cause problems (both handled in `feed_rank.py`). The signal list is in
`feed_rank.FUTURE_SIGNALS`.

**Includes**
- `cause.html` → **`news.html`** (the old address forwards): one feed, unified with filters — the four orders above, plus cause · type · tag · date · search.
- **What News carries:** every post; the **weekly updates** (P4 writes them; until then Earthbux's editorial posts); every Earthbux and organization post. A benefactor post is never "elevated" into News — it is in it from the start. Elevation is the Mission page's job (the report's leading posts).
- **Home vs News:** Home has no filters (Home mods, 2026-09-30); every filter, thread and search is News.
- **A thread has an address:** `/p/<post id>` serves the Full view (`EBX.Post.full`) as its own page.
- **Discoverability:** meta and social-preview tags on every page; **per-thread dynamic OG** (`/p/<id>` answers with the post's title, author and excerpt in its `<meta>`); an **RSS feed** of News (`/news.rss`, `?cause=` per cause); **`robots.txt`** and **`sitemap.xml`** (the pages, every mission by its slug, every post).

**Decides.** D18 (the one-liners for Missions and News) — not blocking.

**Done when.** `feed_check` rewritten for the unified page (each order, each
filter, search, the thread address); an `og_check` fetches `/p/<id>`,
`/news.rss`, `/sitemap.xml` and `/robots.txt` and reads their tags.

**Out of scope.** Personalization (Home, after P4). Tuning the orders (P5).

---

### P4 · Event log + Inbox

**▶ Built 2026-10-04** (Jax: "Build the inbox step"). `inbox_check` **65/65**;
`org_check` 44/44, `posting_check` 66/66 on db copies. Spec: `structure.md` §1 › Inbox.
- **Built:** `events` (the one log: kind, actor, post/mission/initiative/org, week, a
  `dedupe` key so a thing happens once) and `notifications` (per-benefactor fan-out,
  read / unread) — `backend/app/events.py`; hooks after the action commits, through
  `events.safe` (a failure to notify never undoes the vote/post/election): reply (incl.
  an organization's answer) · reaction thresholds 1·5·10·25·50·100·250·500·1000 ·
  cited_update · org_nominated (benefactor nomination, Run for this, Suggest us → the
  initiative's proposer and watchers) · tiv_elected / org_elected (voters read *before*
  the close moves stakes: won · lost · followed the winner, + what comes next) ·
  weekly_update (assembled from the clock and the log: new initiative + leading
  Background, new organization + leading Investigation, entered exchange + leading
  Analysis, prep, next week; published once a week by `scheduler.run_due`, staff can
  preview/publish at `/inbox/weekly/preview|publish`; `/inbox/weekly/latest` is
  public for Home/News). Messages: `message_threads` · `messages` ·
  `message_reports` — only between members of a shared mission (both voted in it),
  one thread per pair, report → staff `GET/POST /inbox/reports` hides it.
  `inbox.html`; the nav's Inbox tab is live with an unread badge.
- **⚠ Migration `b8d2f6a4c1e9` (additive: five new tables).** Applies on the next
  deploy (the server migrates to head on startup); `downgrade` drops only those.
- **Still open in P4:** the weekly edition on Home and in News (the endpoint exists);
  the reports queue in admin.html (API only); "a phase opens" events; organization
  accounts have no inbox (their Home carries what changed).

**Goal.** Give a benefactor a reason to come back that is about *them*. The
four loops: inbox · your stake changed · the weekly ritual · status and rewards.

**Includes**

- Start by messaging users when someone replies to their post, or when it gets a like. Also send out the weekly report.
- Also, orgs nominated for your initiative, like thresholds on your post
- Message threads vs. notifications - toggle.

- A **backend event log** — the single source for notifications, the weekly update, and later the admin audit trail.
- Event types that notify: replies, reactions, and **phase changes with win/lose/what is coming next** — and, from P3, **a post you cited has a new version** ("If you cite a post, you are notified when its author changes it"; the Full view already shows "cited v1 · now v3").
- `inbox.html`: the stream, read/unread, and **YOUR weekly update**.
- **What the weekly update carries** *(inbox 2026-09-29)* — assembled from the event log, the same edition on Home (the most recent one) and in News:
  - the **new initiative** and the **new organization** elected that week, each with its **winning posts** (the leading Background at T, the leading Investigation at T+8 — D20);
  - the mission that **entered exchange**: its tokens released and free to trade, its winning **Analysis**, and the research prize paid (D22 — reads P5's payout, so until P5 it says what *will* be paid);
  - an update on **each mission in prep** (phase 4 — Jax: "I'm calling it 'prep'", D27, 2026-09-29);
  - a **preview of next week**: the elections that close, the budget day that falls.
- Messaging, **mission members only**, with the no-campaigning rule stated in the UI and a report button.
- The nav's Inbox stub becomes real.

**Decided** *(cleared from DECIDE 2026-10-01)*. D9: email updates are
optional; many notifications are inbox-only. D10: no friendships — message
threads between users, searchable by name or by mission.

**Done when.** An `inbox_check` covers event creation for each notifying type,
per-user fan-out, and the weekly-update assembly.

**Out of scope.** Email delivery (needs mail transport — P6/c1). A friend graph (D10: none).

---

### P5 · Money made visible

**Goal.** One pass over everything that reads the token model, so the numbers
agree on every surface (G2).

**Includes**

- **Withdraw / convert** on the initiative, organization and framing ballots.
- **Allocations** shows which organization elections you hold tokens to vote in, and whether your votes won.
- The two accounting numbers everywhere: **EBX sent** and **EBX held**.
- A constant tally of the **guaranteed pool** and the **committed pool**, in EBX, against the EBX value.
- **Resolving a budget item moves the coin price**, by speed and efficiency; the suggestion → approval threshold that makes an item org-resolvable.
- Profile: **wallet value · money donated · spent**, a transaction history, the coin display integrated with allocations, and the coin actions (trade, budget).
- Credit-badge colorization perk ($10 participation, `vvv`).
- **Build the algorithm** — the ranking strategies P3 frames (`feed_rank.py`), tuned against real engagement once there is some, and the research ranking the payout reads.
- **Canonicalization of citations** — one id per cited source (the same report linked three ways is one reference), so the research split (D22) pays a source once and "cited by" counts are true.

**Decides.** D11 (affects what the fee line says, not whether the pass runs).

**Done when.** `wallet_check` and `token_model_check` extended to the new
actions, and one figure reconciled across ballot, profile and mission page.

**Out of scope.** The DEX. The framing exchange itself (backend, money_model §12).

---

### P6 · Counterparty

**Goal.** A real organization can be found, can claim, and can be paid (G4, G5).

**Includes.** Initiative coins on the organization home (P2b builds the home,
registration and claim) · the M1 registered / M2 might-win / M3 won
messages · vetting gates · beneficiary surface (voice at phase-2 start) ·
mail transport · check flow and payee.

**Decides.** D11, D12.

**Done when.** A claimed organization (P2b) appears as payee in a dry-run, with
the vetting state visible on the mission page and on its home.

---

### P7 · Admin & trust

**Goal.** Run the thing without a second website, and keep it from being gamed.

**Done** *(2026-10-01)*: staff **remove posts (with their replies),
initiatives and organizations** — admin.html › Remove, `DELETE
/admin/posts|initiatives|organizations/{id}` (`?dry_run=true` first). Refused:
an elected initiative or organization, an initiative with tokens on it, an
organization on the ledger. The bots' `backfill` now elects initiatives too
(`--missions hmr1`; staff password from `bots.local.json`).

**Includes.**
- **Admin edits any part of a mission** (Jax, 2026-10-01: "I would like to be
  able to go in from admin and edit any part of the mission") — its initiative
  and organization (elect / un-elect), dates and phase, title, candidacies,
  posts' targets and tags (BACKLOG › Admin), with every edit logged.
- `admin.html` absorbed into the site, off Profile · admin data hub
keyed on missions, accounts, organizations, purchases · bot task split
(voting · researching · proposing · exchanging · budgeting), scheduling and
network-wide deploy, and the **bot vote-spread bug** (**F6**) · vote event log
with duplicate/invalid flags and CSV · mission simulator, `is_test` +
`cyclestart`, v2 seeder · new-account vote-buying gate · kids accounts after
legal review · moderation, IP/spam blocking, the real content classifier ·
a record of commit history.

---

### P8 · About

**▶ Reshaped 2026-10-05** (BACKLOG › ABOUT PAGE RESHAPE, executed on Jax's
instruction). `about.html` has its own tab bar — **← Earthbux Home · Our story ·
Our goals · How it works · Our team** — and no site nav and no hero. Every old
anchor still lands (`#why` → Our story; `#grant` → Our goals; `#what`,
`#earthbuck`, `#posting`, `#ab-phases` → How it works). How it works has one
section per phase, its copy read from `EBX.Wheel.COPY` (the one source), each
with "the network here" (Background in 2, Investigation in 3, budget items and
Analysis in 4, the newsroom in 5), then the Earthbuck, How to post and **How we
compare**. Our team is a frame: Jax (photo and bio to fill), the open roles, Join
us and Contact us. New copy (Our story, Our goals › optimism, How we compare) is
drawn from `pitch/deck.md` and `RESEARCH.md` §2 — Jax to edit freely.
`landing_check` 39/39. What is left of P8 is the static pages — step I of the
proposed re-order.

**Goal.** One About page with a tab for each thing a newcomer has to understand,
so the working pages can stay compact (G3).

**Includes**

- `about.html` becomes tabbed. Tabs, proposed: Earthbux (today's copy) · Causes
  ("What is a cause") · The five phases ("How this phase works" — the Process /
  Reason copy that left the mission page 2026-09-28) · Initiatives ·
  Organizations · Missions · Posting (P3's How to post section) · The Earthbuck.
- The phase tab reads `EBX.Wheel.COPY`, the same text Home's top cards use, so
  there is one copy of it.
- A deep link per tab (`about.html#phases`, `#posting` …). The mission page's
  "How each phase works →" (today `about.html#ab-phases`) and the composer's
  guide link land on theirs.
- Sources: BACKLOG › Home feedback 1 ("Maybe I need an 'About' description page
  for everything … I could have my about page have a bunch of different tabs");
  › Step descriptions (moved here): "'What is a cause' and 'How this phase works'".

**Decides.** — (the tab list is a proposal; reorder freely).

**Done when.** `landing_check` extended: every tab renders, every deep link
lands, and the phase tab's copy is the same string Home shows.

**Out of scope.** New copy beyond moving and titling what exists.

---

### 999 · Housekeeping — ends every pass

- (a) **ToC** — `scripts/toc.py` over the docs it touched.
- (b) **structure.md** — page layouts updated, outdated content removed.
- (c) **The clock** — new items added, completed marked, behind-schedule flagged.
- (d) **README** — suggest the edits that align it with what now exists.
- (e) **This file** — defects filed, register updated, pass report moved to `## ARCHIVE`.

## 4. OPEN DEFECTS

*Filed until fixed. A pass that fixes one strikes it here, not in its report.*

| id | What is wrong | Found | Fixed by |
|---|---|---|---|
| ~~**F1**~~ | ~~Cause challenger: 6 or 7 weeks in a row.~~ D5: **six**, in the backend (`CAUSE_STREAK_WEEKS = 6`, split from the new `CAUSE_ROTATION = 7`), the page, the wheel, README, mission_model and structure. | 2026-09-20 | **P1, 2026-09-24** |
| ~~**F2**~~ | ~~13 dangling `getElementById` targets.~~ All gone with their writers; `ce-suggest`'s row now opens the CE panel's nominate dialog. `mission_layout_check` fails on any new one. | 2026-09-20 | **P1, 2026-09-24** |
| ~~**F3**~~ | ~~`scripts/landing_check.js` asserts the pre-2026-09-20 landing page.~~ Rewritten for Home + about.html (21, live API); `home_check.js` added (24, fixtures). | 2026-09-20 | **P2, 2026-09-25** |
| ~~**F4**~~ | ~~`oe_check.js` drove the 2026-08-20 table.~~ Rewritten against the merged page: *Show all races*, the race-is-a-mission move, the backers-only refusal. The full commit round-trip needs a closed ME stake — a bot-seeded DB (backlog). | 2026-09-08 | **P1, 2026-09-24** |
| ~~**F5**~~ | ~~`liveLine()` in `ebx_wheel.js` is no longer painted.~~ It is the left half of Home's top card now — the live facts for the focused cause. | 2026-09-20 | **P2, 2026-09-25** |
| **F6** | The bots only voted on Human Progress — the latest possible election. They should spread across open elections, weighted to the upcoming one. | 2026-09-20 | P7 (or bots2) |
| **F7** | Profile choice cards are in reverse order: each tiv/org should swap, running week+1 top-left counterclockwise to week+6 top-right. | — | P5 |
| ~~**F8**~~ | ~~`render_check.js` (13 MISS) and `ce_check.js` (timed out on `.hig__toggle`) asserted the pre-2026-09-20 Elect page.~~ Both rewritten against the merged page; clean. | 2026-09-24 | **P1, 2026-09-24** |
| ~~**F9**~~ | ~~The shared footer linked `en.html`, `initiative.html` and four `href="#"` items.~~ The footer (2026-09-25) links only pages that exist; the rest read "soon". | 2026-09-24 | **Footer, 2026-09-25** |
| ~~**F10**~~ | ~~The mission page's discussion box got `p2Active: ph >= 2` where `ph` was an object — always false.~~ Reads the mission now. | 2026-09-24 | **P1, 2026-09-24** |
| **F11** | wil0 and hpr0 are organization elections **past their close** (Sep 8, Sep 22) with no winner — their only candidates are `pending`. They sort first, so wil0 is "this week's race, open to everyone" and two live races (hpr1, atm2) fall outside `/wallet/rows`' eight. Needs D17. | 2026-09-24 | P5 / P7 |
| **F12** | ~~"Show all races" threw~~ — its `onclick` called `_oeScope()`, which in markup is the page's `let` string, not the accessor. **Fixed P1.** | 2026-09-24 | **P1, 2026-09-24** |
| ~~**F13**~~ | ~~A race missing from `/wallet/rows` (see F11) shows **live** Vote buttons.~~ The ballot now fetches a missing race's row (`GET /wallet/row/{id}`), so it knows `can_take_part` — and the stake, which was the "I can't withdraw my slate" bug. Signed out there is nothing to vote with. | 2026-09-24 | **Mission pass, 2026-10-01** |
| ~~**F14**~~ | ~~At phone width the top bar overflows.~~ At ≤640px the five tabs pin to the bottom and hide while scrolling down (`ebx_shared.js` `bindNavScroll`, `ebx_frontend.css`). | 2026-09-24 | **P2, 2026-09-25** |
| **F15** | Legacy phase-2 rows carry `donated_ct = 0` after their ME closed (oce1 is one), so the **guaranteed pool reads 0** where the ladder says 10% is final. The overview reads the rows as booked — the same number `read_wallet` gives — so this is data, not display. | 2026-09-24 | P5 |
| ~~**F17**~~ | ~~The initiative ballot's head printed the cause cadence ("decision Sep 22") over an election that closes Nov 10; its own topbar was right.~~ Reads the election's T now. | 2026-09-24 | **P1, 2026-09-24** |
| ~~**F16**~~ | ~~The landing trios link `mission.html?research=…` and `?budget=…`; the mission page ignores both params.~~ About's six cards link `post.html?type=…`, which preselects the type. | 2026-09-24 | **P3, 2026-09-29** |
| ~~**F18**~~ | ~~Breaking a sign-up rule shows `[object Object]` instead of the rule.~~ `Auth.signup` prints each broken rule's `msg`. | 2026-09-28 | **P3, 2026-09-29** |
| **F19** | At phone width (390px) the mission page is 536px wide: the final-standings "elected" pill and the candidate pills (`.ml-row__won`, `.mh-pill--nostmt`) and the ring layer run off the right edge. Predates 2026-09-28 (the same with the page before the mission edits). | 2026-09-28 | P1 follow-ups |
| ~~**F21**~~ | ~~The progress log sat at the far left of the mission page, outside the panel.~~ It is inside the panel, top left; the table is a full-width row under it. | 2026-09-29 | **Unified elections, 2026-09-29** |
| **F22** | *(P3 §0 sweep)* `scripts/oe_check.js` fails 3 of 23 on the compact mission page (2026-09-28): it expects "Organization Election" as the phase title and the initiative's name in the head. Same 3 failures with P3's code removed — the check predates the page, not a regression. | 2026-09-29 | P1 follow-ups |
| **F23** | *(P3)* Images on posts are stored as downscaled data URLs in `posts.image_url` (≤1280px JPEG). Fine at pilot scale; at volume they belong in file storage, and **video** needs that storage before the composer's Video button can work. | 2026-09-29 | BACKLOG › Infra |
| **F24** | *(Home mods §0 sweep)* hmr1's initiative election closed on Sep 8 with no winner, and `EBX.Wheel.meMission` picks the **oldest** un-won mission in phase `pre`/`initiative` — so for Human Rights it returns hmr1, not the open hmr2, wherever the wheel's "this week's initiative election" is read. `missions.current_phase` is also stale (every mission reads `initiative`, winners or not); the mission hub reads dates and winners instead. `meMission` should skip missions past T. | 2026-09-30 | P1 follow-ups |
| **F25** | *(mission pass §0 sweep)* `feed_check.js` fails "…a way through to the mission it was written in" on a fresh database: the HOT order's first post is a target-less general post (P3 made those possible), which has no mission to link. The same on the baseline — the check predates target-less posts. | 2026-10-01 | P3b (feed_check rewrite) |
| **F26** | *(mission pass)* Legacy organization-race rows with `donated_ct = 0` (F15) count nothing as final. `withdraw_stake` now treats the 10% initiative-election skim as final when it **materializes** a derived stake, but a row that already has `stake_ct` and no recorded skim (e.g. GameMaster's hmr1 locally) can still withdraw all of it. Needs the same read-only production count as F20 before a backfill. | 2026-10-01 | P5 |
| **F20** | Some organization races hold no carried initiative-election money: locally atm1, oce1, lan1, wil0 and hpr0 have `votes_p1` stakes but no `settle_me` element on their `votes_p2` rows (elected before the carry existed, or by a path that skipped it). The 2026-09-28 fix lets those voters vote; the money itself is still not in the race (cf. F15). Check production with a read-only count before any backfill. | 2026-09-28 | P5 |

## 5. BACKLOG

*Named, not queued. Reorganize freely during a pass; do not build.*

- ~~*ABOUT PAGE RESHAPE*~~ — built 2026-10-05 (P8 › Reshaped; `## ARCHIVE` › 2026-10-05).

**Future/Conceptual**
- Thinking about maybe scrapping the initiative election - we can have initiatives reach funding goals, and then once they hit their goal we move on to the 'election' where we vote on an organization. The issue with that is that it messes up the weekly-rotating nature of things. We could even remove the whole 'cause rotation' or maybe we just don't make it so you are forced to donate to something you didn't fund. issue with that is that you don't get the chance to donate if your thing never gets funded. Well, maybe you can have donations on the spot, and you always have the ability to move your donation to another source. 
- Make the UI more similar to other charity platforms - simple, clean, monochrome, interlocking panels, calming white background.
- Monochrome on things that aren't cause-related
  - The 4 home page descriptors
- Move budget day to T + 16
- Phase 6 - rewards and travel
- Framing → **Prep** — decided (D27, 2026-09-29: "I'm calling it 'prep'"); the phase tab, header line, About and the docs still say Framing.
- The grant can only be used on initiatives.
- A light/dark mode choice in settings would be nice. 
- *(inbox 2026-09-28)* Spend your EBX on things for the mission or for yourself — travel, merch, targeted journalism, shoutouts, specific budget items. This would be approved charitable options.
- *(inbox 2026-09-28)* Research the planning software large projects run on — Jira, Canvas/Moodle and the like — for mission steps and the organization tasklist (P6).
- I should have an option to share the link to earthbux on social media. 
- *(inbox 2026-09-29)* **`MissionStep` is out of date** (`models.py`): it still carries `guaranteed_ebx` / `potential_ebx` per step from the pre-2026-09-16 pool model, and nothing on the page writes steps. It needs reshaping around the mission clock (`mission_model.md`) and the organization's tasklist (P6; see the Jira/Canvas research note above) before anything builds on it.

**Admin**
- Create email addresses like inquiries@earthbux.net or admin or purchasing or hr or operations
- Maybe I can have a command to pull in the data from the online api to my local one so they match and I don't have to keep up with 2.
- A bot console in admin for me to run them autonomously.
- Can I get a google preview? I want it to come up if people search "earthbux" in their search engine.
- ~~Admin needs to be able to remove initiatives, organizations, and posts.~~ Built 2026-10-01 (P7 › Done).
- Edit any part of a mission from admin → P7 › Includes.
- I should also be able to retarget posts and change their tags.
- The link to the admin page from profile should direct to admin.html. The version it goes to is outdated and can be deleted. 
- Each accounts dashboard should be viewable by admin.
- I need a mission-editor so I can put in locations.
- Earthbux posting will come from the admin console - including approvals for the weekly updates and automatic posts.

**Mobile** — *both built 2026-10-02: the cause tabs stick to the top on phones; the initiative and organization tables lost the Vote and Standing columns everywhere, a row tap puts an initiative on the ballot, and on phones the rows are titles only under "Select an initiative/organization to vote". The old phone rule had hidden the title column itself.*
- ~~Causes can be always on the top of the screen when scrolling down on the missions page~~
- ~~In the tiv and org tables, I'm not able to see the titles of the rows. On mobile, tell the user "select an initiative/organization to vote", and the title should be the only thing in the row. Also, on all versions, remove the standing column, and remove the 'vote' column, selecting it puts it into the ballot, where you commit your vote.~~

**Posting**
- Have the posts kind of like the instagram thing, where as you scroll it shows you exactly 1 post at a time, centering it in your face.
- Create the weekly report. - Build display as we create the report - each updates each week - This is the first earthbux post - after that I can begin with updates. 
- Mission statements should be limited in length, justifications should not. There should be multiple options of what to post when you suggest an initiative or organization.
- Initiative proposal flow should include a few short questions - how does it apply to the cause? Admin approval
- Weekly update should have the date of the week.
- *(Up/down votes, the card, voting from Home, the initiative-election badge — built 2026-10-01, P3.)*
Maybe posts can only become research posts once they reach a certain level of popularity? - versions that build on each other. How does github do it? Github stars are the most similar analog. Github is honestly the most similar platform. 
Maybe research posts (and weekly updates, i think), will open actual 'articles' wheras normal posts will simply be contained in the feed. There are numerous things.
Maybe I should move the report to news and have a dedicated discussion on the misison page.
So news is exclusively earthbux and organization posts, not user posts... User posts are not news. But research can be news.
User posts can be discussions about news.

- user posts
- user research
- org posts
- org research????
- Earthbux updates
- Earthbux News

The preview will include the photograph (if there is one)

- Clicking anywhere on the post should take you to the expanded post in news
- I think maybe instead of having a dedicated post option, there should be a post dialog within news that you get taken to... 
*Home* POST - all purpose
*Missions* Post about x (cause, initiative, )

- The target is the most important part of a post. So posts that don't have targets are only shown to people with some connection to the account posting them. People need to be able to join communities around initiatives - initiatives are the CENTER of the platform. (they begin missions, so it's built right.) The thing the sit wants to know is WHAT SHOULD WE DO? (Facebook is *who are you*, linkedin is *what do you do*, reddit is *What do you want to learn*, x is *what are your opinions*). Every platform hits users with a feed as soon as they log on. I should do the same.. hit them with the weekly election. 

- So 

**Mission**
- After nominating, suggetsing, or posting, the window should automatically collapse back to the page.
- We can probably change the mission page to more of a read-only type of experience, and the news page can contain the whole contribution-hub for each mission.
- When the page opens up, it should be an animation that looks like the page is emerging out of the annulus.
- Each of the 7 causes will have an image 
- The post-support ring (annulus layer 1) returns inside the **framing** and **exchange** phase panels — review 2026-09-24. `GET /missions/{id}/post-support` is unchanged. Move this to backlog - I haven't yet decided what to do in these 2 rings.
- Mission gantt chart / annulus ring widget (deadlines, 7–12 steps).
- Tune step guaranteed/potential pool ratios + early-resolution bonus size.
- Tune `resolution_value_bump` and its relation to the global coin value.

**Home**

- When the screen is wide enough, we can put stuff beside the post feed.
- Real images for the five steps: each cause's vista and its three problems are drawn in `ebx_steps.js` › `PANOS`, as placeholders "until we report on real missions".
- Will need a real image behind the left side of the hero. Just 1. I will find a good one.
- *(Home pass 2026-10-01)* "I will probably want to have each of this week's races open even when the table is not collapsed" — collapsed now shows this week's two elections; open, the grid still glows them (`mc--now`). Revisit with the budget-day move (T+16, BACKLOG › Future).

**News**
- Post display is exactly the same as home
- One post at a time type of view. 
- With the news page, comes reporting. I'm going to need to create a plan for what the earthbux team actually does. These responsibilities won't be able to be undertaken until the website is running smoothly, and will be very difficult before there is cash flow, because organization won't want to join us before then. 
- The corner annulus — News is the only page without the large one; the corner one reflects the status of the mission of the post being viewed.
- Learn from: Meta, LinkedIn, Reddit, TikTok; fantasy sports, Polymarket, Strava, Duolingo, stock investing, GitHub.
- Mission member communication channel - inbox stage.
*Framing*
- Don't need to seperate the 7 into weeks, should be ALL TASKS DONE by budget day.
- (Budget items with the organization's input → P2b.)

**Profile**
- I want people to be able to navigate using the annulus. - Maybe on the profile page, they can rotate it with their touch and the center (or a box below it) shows all their commitments for that cause. It will be like 'Cause: oceans - starting x - my vote and leading + committed, started '
- The profile page is going to adopt a similar no-side-card but 2-side-panel approach to the mission page. RHS will include mission memberships (count) and settings and allocations. LHS will include all the credit coins. Down-scrollable like the mission navigator. Clicking on one will bring up a users individual contributions to that mission. The allocations are:
Committed (OE or ME)
Uncommitted (Grant or purchased)
And the header for the coins is "Donated".
- "The benefactor profile is still shoddy" (from ORG EXPERIENCE, 2026-10-01).
- In the profile, the choice cards need work. The organization choices don't say which initiative they're choosing, and it seems like one is choosing a related initiative + organization.
- Messageing should be about *Creating your fund* - choosing is important, but so is donating. 
- *(inbox 2026-09-29)* **The timeline as a visual on Home** — one mission's phases on a dated line (T, T+8, T+15, exchange). Pairs with the animated process diagram on the clock (`s4`), which may be the same drawing.
- Each benefactor needs to add funds to their account first, which appear in their wallet. The grants should appear as a seperate entity in the wallet, as should ebx and pre-ebx tokens. Every transaction made should rely on what is already in the wallet. Create this asap and organization and clarity will improve.
  - Every action relies on the contents of the wallet - if a user participates in a tiv election, the subsequent org election becomes a wallet item
  - If there are no unallocated funds in the wallet, it should prompt something like "Add funds..."
- Each person should have a full dashboard of everything they've done.

**Locations**
- `location_type` + coordinates on missions (site / region / distributed / global); home location on benefactors; location(s) on orgs.
- Globe rendering per location type (pin · shaded region · multi-pin).
- Budget items carry locations (travel, purchases, services).

**Accounts / kids (12–17)**
- Birthdate or age bracket on `BenefactorAccount` + guardian link.
- Parental approval on every money-in action; voice ungated.
- Approval UX: per-transaction vs. allowance.
- Legal review: COPPA/GDPR-K, minimum age 12, regional definitions.

**Infra**

- *(P3)* File storage for post media — images move out of `posts.image_url`, video becomes possible (F23).
- Self-serve password reset (needs mail transport).
- Working-tree corruption: avoid concurrent writers; commit often.
- Apache stack (Kafka / Flink / Airflow / Cassandra) — future.

**Docs** *(its own lane; not a build pass)*
- Reword all phase descriptions to the current state.
- Exchange phase: each tranche release is an exchange of actions for money; spending tracked; over/under moves the coin price. Budgeting, resolutions and tranche releases stay part of the phase without defining it.
- Build clock here; mission clock in `mission_model.md`. Separate gantt charts for missions and for project development.
- Split `money_model.md`: mission model vs. an operations/banking document; fold `roles.md` into it.
- A nonprofit-application section; fiscal sponsors and PRIs into `RESEARCH.md`.
- `the_social_network.md` becomes the design document — the four engagement loops live there, not here.
- An animated, Prezi-like diagram of the process and how the steps relate.
- Need a list of services used - vscode, google, windows, railway, sql, resend, cloudflare, etc.
*Cause*
If the same cause wins 6 weeks in a row, it replaces the old initiative for all future missions.

**Bots** 
- The api is not updating the phases at the proper time... backend issue and only affects bots.
- Have AIs respond to replies on their posts and also reply to each other. 

*(2026-09-25 — gathered here from where the notes had scattered: the
build clock (`bots`, `bots2`), P7's "bot task split", F6, the two lines that were
under Unrelated items, "Other" in Home feedback 1, README §10,
`scripts/bots/personas.json` and `scripts/bots/ebx_bots.py`. Nothing older was
found in `docs/_to_delete/` — those files predate the bots. If a note is still
missing, it was never in the repo.)*

*The bots* — three AI benefactors on the live site, one persona file, passwords
in `scripts/bots/bots.local.json` (git-ignored, never printed).

| Bot | Live id | Voice | Leans toward (cause affinity 1–5) | Cash appetite |
|---|---|---|---|---|
| **Jax3000** | 9 | Aggressive forest-and-wildlife defender: blunt, suspicious of corporate and greenwashing groups, backs direct action and small grassroots groups | forests 5 · wildlife 5 · land 3 | withdraws 5% |
| **JJ420** | 11 | Easygoing ecosystem expert: explains how species, soil, water and climate connect, finds the constructive middle, wants measurable outcomes | oceans 4 · land 4 · the rest 2–3 | withdraws 15% |
| **BotJoe9** | 10 | Establishment-leaning, big on social justice: trusts large charities, asks who benefits and whether communities have a voice | human rights 5 · human progress 5 · atmosphere 3 | withdraws 25% |
| *GameMaster* | staff | not a bot: the staff login `sync` and `backfill` use (`--staff-handle`, password from `EBX_STAFF_PASSWORD`) | — | — |

Proposed, not built — bots the actions below would need:
- **An organization-side bot** — a rep account for one real, consenting organization, or a clearly fictional test org, to exercise claim, org updates and the M1–M3 messages (P6).
- **A newsroom bot** — an Earthbux staff-role account that writes `editorial` / `mission_update` posts, so Home's News tile and the feed have news to show.
- **A newcomer bot** — signs up fresh each run, to test the new-account vote-buying gate (P7/t1) and the first-visit path.
- **A contrarian or auditor bot** — rates, replies and flags, to exercise the post-support layer (orange/red) and moderation (P7/t3).

*Bot actions* — what `ebx_bots.py` does today, one task per run, every bot at once:

| Task | Actions | Needs |
|---|---|---|
| `plan` | read-only: the week (active cause, initiative elections, organization races, framing missions, posts by mission) and each bot's tokens, stakes and posts | — |
| `initiatives` | vote in **every** open initiative election (tokens in the upcoming one, 0-token preferences elsewhere) · propose an initiative · write a case for/against · reply · rate fair/unfair | content file, or `--ai` |
| `organizations` | commit in this week's race and races it backed · pick an organization · nominate one (`/organizations/register`) · case · reply · rate | real organizations only |
| `budget` | costed service / supply / support items · upvote others' items | a stake in the mission |
| `research` | write or **update** Background · Vetting · Analysis. **No stake needed since 2026-09-25**, and vetting must name an `org_id` | content file |
| `exchange` | move stake between open organization races · withdraw the non-final part as cash (before budget day) | a stake |
| `sync` *(staff)* | copy the local database's non-pilot initiatives and organizations to the site | `--from-db`, staff login |
| `backfill` *(staff)* | elect an organization / initiative in past races that never got one | staff login |

Flags: `--content week.json` · `--ai` (Claude with web search, in character) ·
`--dry-run` · `--only <handle>` · `--bot-key` (marks new accounts `is_test`).
Content files so far: `week-2026-09-17.json`, `week-2026-09-25-vetting.json`.

Planned, not built:
- **Task split** (P7): voting · researching · proposing · exchanging · budgeting as separately schedulable jobs, rather than one task per manual run.
- **Vote spread** (F6): spread tokens across open elections, weighted to the upcoming one, not all on the latest.
- **A regularized schedule** for bot runs, e.g. a weekly scheduled task after each Monday close, plus network-wide deploy (P7).
- **Bots on the local copy** — a documented way to run them against `localhost:8000` (the script already takes `--base`; missing is a local seed of bot accounts and a local `EBX_BOT_KEY`).
- **Retroactive posts for recent elections** (clock: `posts`, after P3).
- **Bot cases on the mission page** (Home feedback 1 › Other): the cases the bots posted on future initiative elections (hpr2) must also show on that mission's page.
- **Replies to each other** across bots, so threads have more than one voice, and **framing-week exchanges** into another mission once the framing exchange exists (money_model §12).
- **Clean-up before real money**: remove or mark all bot accounts (`POST /admin/accounts/{id}/test`) before the first real donation.
- A bot console, where I can select which tasks to run.

**Footer**
- Replace money model in white paper with my document.


## REMOVAL REGISTER

*Folded in from `docs/to_delete.md` on 2026-09-09, unchanged except for heading
depth. One list, ordered by how safe each removal is: **§A** goes today with no
code change, **§B** needs one edit first, **§C** is live code whose replacement
already exists, **§D** only looks dead. Nothing here is deleted by reading it.*

*Created 2026-08-28 (build-seq §4). One list, ordered by how safe each removal
is. Nothing here has been deleted: this file is the inventory, and each entry
says what would break if it went and what has to happen first.*

**How to use it.** Work top down. Everything in **§A** can go today with no code
change. **§B** needs a one-line edit somewhere first. **§C** is live code whose
replacement exists but which still has a caller or a story to tell. **§D** is
the stuff that only LOOKS dead.

---

### §A — safe now, nothing reads them

| What | Where | Why it can go |
|---|---|---|
| 7 database backups | `backend/earthbucks.db.bak_20260809_194835`, `…bak_20260810_094142`, `…bak_aug08b`, `…bak_aug27c`, `…bak_jul19`, `…bak_jul31`, `…bak_premigrate` | ~1.7 MB of point-in-time copies going back to July. Git has the schema history and `alembic` has the path between versions; these are snapshots of *data* nobody has read since the day they were made. **Keep `…bak_aug27c`** until the finalized model has run a full cycle — it is the last state before it. |
| `backend/earthbucks.db.migrated_jul19` | same folder | The July cutover artefact. Superseded twice. |
| `backend/_to_delete/earthbucks.db-journal` | | An orphaned SQLite journal from an interrupted write on 2026-08-27. It is not a database and cannot be opened as one. |
| `_ebx_snapshot.tgz` | repo root | Written 2026-08-28 to move the tree into a container with Chromium on it, so `oe_check` and `ce_check` could be run for the first time. It has served its purpose. **Add `*.tgz` to `.gitignore`.** |
| `scripts/__pycache__/` | | Byte-code. `.gitignore` already covers `__pycache__` elsewhere. |

### §B — one edit, then safe

| What | Where | The edit first |
|---|---|---|
| `backend/seed/pilot.py` | | v1-shaped and unrunnable against the v2 schema. README §10 still lists it as "sample data" — say it is dead or rewrite it. |
| `README.md` §11 + §12 references to `*_old.py`, `routers_old/`, `backend/earthbucks.db.pre-v2.bak`, `backend/seed/port_v1.py` | README lines ~893, ~910–912, ~932, ~934, ~952 | **None of those files exist in the tree any more** — they were removed at some point and the README still documents them, including a `./.venv/bin/python -m seed.port_v1` command that cannot run. Delete the references, not the files. |
| `.pf-left` · `.pf-right` · `.pf-right-row` · `.pf-gear` · `.pf-badge-card*` · `.pf-orgmode` | `profile.html` CSS | Thirteen rules for the three-column rail the 2026-08-28 rebuild replaced. `.pf-grid` and `.annulus3-*` are already gone; these are what is left of the same layout. Check nothing else selects them, then cut. |
| `EBX.formatEBX` | `resources/js/ebx_shared.js` | Still correct for the surfaces that mean the MINTED state (the credit badge, the ledger, mission.html's pool and spend). After the 2026-08-28 unit sweep it has only a handful of callers. Do not delete it — but every new call site should be `formatTokens` unless it means minted money, and `scripts/unit_sweep.js` is the way to check. |

### §C — live, but the replacement already exists

| What | Where | Blocked on |
|---|---|---|
| `GET/PUT /missions/{id}/p1/carryover` | `backend/app/routers/votes.py:74–98` | The phase-1 carryover machinery describes a world that ended 2026-08-20. `crud.p1_carryover_state` / `carryover_p1` / `_send_floor` go with it. It still explains races finalized under the old rules honestly, so it cannot go until those races are archived or restated. `scripts/carryover_check.js` guards the signed-out path and would go too. |
| `crud._withdraw_p1_legacy` + `_send_floor` | `crud.py:1994`, `:2052` | Same story. `withdraw_p1` is a named refusal now; the legacy body is kept so an old race can still be explained. |
| The phase-2 **withdraw button** | `cause.html` | Named in the backlog since 2026-08-20b. It posts to an endpoint that refuses. Remove the button, keep the refusal. |
| `votes_p2.conversions`, `benefactor_accounts.grant_commit_by_week` | `models.py:307–323` | Deliberately not dropped by migration `c5d8f2a91e67` — they hold the last values written under the retired rules. Nothing reads them. Drop when the races they describe are settled. |
| `mint_mission_coins` firing at `finalize_p2` | `crud.py` | The coin should be issued at BUDGET, not at the mint (README §5, "Credits & EBX"). Named backlog item; moving it is a behaviour change, not a deletion. |
| `LocalElections` no-op stubs | `resources/js/ebx_shared.js:248` | Five empty methods kept so lingering call sites do not throw. Grep for callers; if there are none left, delete the object. |

### §D — looks dead, is not

- **`Votes.forCause`** — CHECKED 2026-08-28, and the answer is better than the
  question. Six functions in `ebx_shared.js` still call the synthetic vote
  distribution — `raceCard` · `electionPanel` · `electionBanner` · `sideCard` ·
  `upcomingCauseBanner` · `topCard` — and **no page calls any of the six.** The
  only mentions of `EBX.sideCard` and `EBX.topCard` left in `main.html` are two
  comments saying the page builds its own faces instead. So this is a large
  block of genuinely dead render code, not a live surface showing fake numbers,
  and it moves to §A the moment somebody confirms the same for `frontend/src/
  ebx_shared.ts`, which is the SOURCE these are built from — delete it there and
  rebuild, or the next `esbuild` run puts it all back.
  - What must stay: **`EBX.Votes.rankColor`**, which is a palette, not a
    simulation, and is called for real by `main.html:4322` and
    `cause.html:3943`.
- **`backend/app/post_config.classify_flag`** — a stub that returns green. It
  looks like dead scaffolding; it is the seam the real classifier plugs into,
  and `posts.flag` / `GET /missions/{id}/post-support` are built around it.
- **`ce_check.js`'s cause-table assertions** — they look stale next to the CE
  panel, but they were rewritten for the panel on 2026-08-27 and pass.

---

### Also worth doing while here

- **`.gitignore`**: add `*.tgz`, `backend/*.db.bak*`, `backend/*.db-journal`.
- **`backend/.venv/` is 103 MB** and inside the repo. It is git-ignored, but it
  is also why any archive of this tree is 11 MB instead of 800 KB. Moving it
  outside the repo would make the tree portable.
- **`docs/` has no index.** Nine files, three of which (`RESEARCH.md`,
  `Donation_Landscape_Brief.md`, `Endowed_Grantmakers_Deep_Dive.md`) are
  research rather than build documents. A `docs/README.md` naming what each one
  is for would stop the build docs and the research docs being read as one pile.

---

### Added 2026-09-08 (build-seq §0 + §6)

#### Done this pass — struck from the list above

- **`docs/` has no index** — it has one now: `README.md` §12, "The docs index",
  fourteen files with a verdict on each. The three folds and the one drop it
  recommends are entered below rather than done, because folding research
  documents is an editorial act, not a cleanup.
- **`.ebx_shared.build.js`** — a stray candidate build written into
  `resources/js/` while wiring the build guard, before it was taught to build
  into a temp directory instead. Moved to `docs/_to_delete/`; delete the folder.
- **`docs/_to_delete/gantt_probe.mmd`** — the mermaid block from the old `gantt.md` (now `## THE PLAN` §1),
  copied out so it could be rendered and looked at in a container with a
  browser. Served its purpose.

#### New — §A, safe now

| What | Where | Why it can go |
|---|---|---|
| `Donation_Landscape_Brief.md` · `Endowed_Grantmakers_Deep_Dive.md` | `docs/_to_delete/` | **Done 2026-09-09** — folded into `RESEARCH.md` §1 and §6 with every source link intact. The research is one document. |
| `Donation_Recipient_Landscape.xlsx` | `docs/_to_delete/` | **Done 2026-09-09** — dropped. `DRL.csv` is the same table and it diffs; `RESEARCH.md` §0 cites it. |
| `docs/_to_delete/` | | The whole folder, once its two files above are confirmed unwanted. |

#### New — §B, one edit then safe

| What | The edit first |
|---|---|
| `backend/seed/pilot.py` | **Retired 2026-09-08** — README §10 now says so instead of calling it "sample data". It stays on disk because the rows it generated (`init-0NN`, the GameMaster account) are the development database, and deleting the generator does not delete them. It goes when the **voting bots** replace it (`## THE PLAN` §1) — bots drive the real endpoints, so their data has the shape the code actually produces. |
| `docs/_to_delete/PLAN_2026-09-02.md` | **Done 2026-09-09** — retired to `docs/_to_delete/`. `gantt.md` outlived it and has itself been folded into `## THE PLAN` above, so the project has one plan in one file. |

#### New — §C, live and load-bearing, but wrong

| What | The problem |
|---|---|
| ~~**`frontend/src/ebx_shared.ts`**~~ | **Resolved 2026-09-16** — the TypeScript was retired and `resources/js/ebx_shared.js` is the source. The file is now a three-line tombstone; see "Added 2026-09-16" below.
| the six dead renderers in `ebx_shared.js` (§C above) | Unchanged, and now with a second reason to be careful: they are among the twelve functions whose `.js` and `.ts` bodies differ, so "delete it there and rebuild" is exactly the operation the guard now blocks. Resolve the divergence first. |

---

### Added 2026-09-16 (build-seq §1)

#### New — §A, safe now

| What | Where | Why it can go |
|---|---|---|
| `frontend/` (the whole folder: `src/ebx_shared.ts` tombstone, `src/types.ts`, `package.json`, `tsconfig.json`, `node_modules/`) | repo root | The TypeScript source was retired; `resources/js/ebx_shared.js` is edited directly. `package.json`'s build now refuses with a notice. Nothing reads the folder. |
| `scripts/build_guard.js` | `scripts/` | Guarded the retired build. Now prints a notice and exits. |
| `backend/earthbucks.db.bak_premigrate` | `backend/` | Written 2026-09-15 at the same size and time as the live dev DB. Keep only if that migration is in doubt. |

Not deleted from this session: the computer's shell could not reach the folder,
and file sync can write but not delete.

#### Unblocked by the retirement

- **The six dead renderers** in `ebx_shared.js` (§D, `Votes.forCause` callers:
  `raceCard` · `electionPanel` · `electionBanner` · `sideCard` ·
  `upcomingCauseBanner` · `topCard`) can be deleted directly from the `.js` —
  there is no longer a source to put them back. Keep `EBX.Votes.rankColor`.

#### New — §C, live but replaced by the 2026-09-16 model

| What | Where | Blocked on |
|---|---|---|
| Losing-organization backers minted behind the winner at T+8 | `crud._settle_oe_stakes` | The framing exchange (money_model §12 item 1). |
| Marked tokens movable into any open OE race during the OE | `wallet.move_stake`, `is_movable` | Same — losing-initiative backers move during framing now. |
| `BenefactorAccount.grant_commit_by_week`, `votes_p2.conversions` | `models.py` | Unchanged from §C above; still unread. |


### Added 2026-09-18 (build-seq §4–§6)

#### New — §B, one edit then safe

The Elect page's annulus left for the landing page; its code did not. Every
function below is still defined in `main.html` and still called, but each one
guards on a mount that no longer exists, so it paints nothing.

| What | Where | The one edit |
|---|---|---|
| `renderPie`, `_buildPieSVG`, `updateCenter` | `main.html` | Delete the calls in `render()` / `renderCards()` first, then the functions. `EBX.Wheel` draws the same ring. |
| `sideCardTiv`, `sideCardOrg`, the `left`/`right` block in `renderCards` | `main.html` | `sideCardTiv` is still called by `_topCardTivSide` (the ME top card's face) — keep it; the `renderOne` / panel block can go. |
| `.hero__layout`, `.hero__side`, `.hero__center`, `.hero__annulus-wrap`, `.hero__pie`, `.hero__statetoggle`, `.st-side`, `.st-now` CSS | `main.html` `<style>` | None — no element carries these classes now. |
| The hidden `#ebx-center-*` spans' handlers, `renderControlBlock` | `main.html` | None. |

#### New — §C, live and load-bearing, but wrong

| What | Where | Why it stays |
|---|---|---|
| `scripts/oe_check.js` | `scripts/` | Fails before this pass too: it clicks `tr[data-mission]` rows that the 2026-09-08 one-race OE table stopped painting by default. Needs a rewrite against *Show all races*, not a deletion. |

### Added 2026-09-24 (P1 — the merge)

#### New — §A, safe now

| What | Where | Why it can go |
|---|---|---|
| `scripts/election_layout_check.py` | `scripts/` | A stub that runs `mission_layout_check.py`, which grew out of it. Keep only while something still calls the old name. |

#### New — §B, one edit then safe

| What | Where | The one edit |
|---|---|---|
| `renderTopCardFull`, `renderTopCardFullHTML`, `_topCardTivSide`, `_topCardOrgSide`, `sideCardTiv`, `sideCardOrg`, `causeIndicatorHeader`, and the `.tc-*` / `.topcard-*` CSS | `mission.html` | The two top cards left with P1 and nothing mounts them; `renderCards` no longer calls them. Confirm no other caller (grep), then delete — it is several hundred lines. |
| ~140 CSS classes no markup or script names (`ce-tab*`, `uc-*`, `hero__*` leftovers, `mission-strip*`, `idx-toggle*`, `main-toggle*`, …) | `mission.html` `<style>` | Some are built at runtime (`'status-' + x`, `'fx-check__i--' + st`), so check each before cutting. The list is what `re.findall(r'\.([a-zA-Z][\w-]*)', css)` finds that no script or markup mentions. |

#### Added 2026-09-24b (the review pass) — §A, safe now

| What | Where | Why it can go |
|---|---|---|
| `resources/js/ebx_postsbox.js` and the `.pb*` / `.ct-startline*` rules in `ebx_frontend.css` | `resources/` | The discussion box. No page mounts it since the review folded it into the story ("we can delete everything from the discussion"). |
| `scripts/posts_box_check.js` | `scripts/` | Pinned that box; `composer_check.js` replaces it. |
| The `.ps-*`, `.mp-disc`, `.mp-circle*`, `.mp-grid`, `.mp-funnel`, `.mp-toggle*`, `.mp-search*` rules | `mission.html` `<style>` (the block "from the old mission.html") | Their markup is gone. |
| `showAllInitiatives` | `mission.html` | Its button is gone. |

#### Added 2026-09-25 (review 2) — §A, safe now

| What | Where | Why it can go |
|---|---|---|
| The `.mb-post*` and `.mp-cattab*` rules | `build/mx.css` (so `mission.html`) | The posts toggle and the dialogue under the story are gone — budget items have their own panel, research lives in the report's thread. |

#### New — §C, live but only for old links

| What | Where | Why it stays |
|---|---|---|
| `main.html` | repo root | A redirect to `mission.html` that keeps `?state= ?cause= ?init= ?org=`. Every old Elect link lands through it. Remove once the site's own links and any shared links have moved (the site's own already have). |

### Added 2026-09-25b (P2 · Home)

#### New — §A, safe now
- `ebx_frontend.css`: `.lw-top__p`, `.lw-top__lab`, `.lw-live__cause` (+ `i`, `span`), `.lw-step--you .lw-step__n`, `.lw-step--us .lw-step__n`, `.lw-step--us.on` — nothing draws those classes since Home's five toggles became phase cards.
- `ebx_frontend.css`: `.lw-steps { grid-template-columns: repeat(5, 1fr) … }` and its 860px rule — `.lw-rows` overrides both; the only `.lw-steps` element is the rows wrapper (kept for the arrow-key handler).
- `ebx_wheel.js` `STEPS[].half` is read only to build the `lw-phase--you/us` colour class — fold into `PHASE` when next touched.

#### New — §C, live but only for old links
- `index.html` `.ld-*` hero rules are live; everything below `.ld-rule` in `about.html`'s `<style>` is the old landing's and only about.html reads it.
- `ebx_postsbox.js` still labels `investigation` "Investigation" and `context` "Context" — retired with the box (§ 2026-09-24), not renamed.

### Added 2026-09-28 (P1 mission edits)

#### New — §A, safe now
- `mission.html` `<style>`: `.mb__grid` (+ its 860px rule), `.mp-log` / `.mp-log li*` / `.mp-log__date`, `.mb .mp-log li.upcoming::before`, `.mb-budget .mp-posts`, `.mp-posts` — the progress-log card and the budget panel left the page; nothing draws those classes.
- `mission.html` `<style>`: the D14 tab shape for `.mx-stage .mx-phase` (top-rounded, `border-bottom: 0`, `.on` with `margin-bottom: -1px`) and `.mx-phases { grid-template-columns: repeat(5, 1fr) }` + its 640px rules — `.mx-stage .mx-log` overrides every one of them.
- `mission.html` MB: `renderBudget()` only fetches now; `TYPE_WORD`, `costLine` and `rateHTML` stay (the report and thread use them).

#### New — §D, looks dead, is not
- `EBX.Wheel.COPY` in `ebx_wheel.js` — the mission page no longer reads it, but Home's top cards do, and P8's phase tab will.

### Added 2026-09-29 (P3 · Posting)

| What | Where | Why it can go / what first |
|---|---|---|
| `scripts/research_gate_check.py` | scripts | §A. Retired by P3 — it checked the 2026-09-25 gates, which no longer exist; it prints a pointer to `posting_check.py`. |
| The mission page's reply composer (`#mxc-bg`, `openComposer` with a parent) | `mission.html` | §C. Kept for REPLIES only — new posts go to `post.html`. Its type tabs, budget fields and vetting-org select only ran for new posts and are unreachable now; they go when the reply box moves to `EBX.Post.open`'s. |
| `post_config.LEGACY_TYPES` (case · evaluation) and `POST_REQUIRES_MEMBERSHIP` | `backend/app/post_config.py` | §D. Look dead, are not: legacy reads and a request in the old Review lane are rewritten through them. Remove once the bots and every client send general posts with tags. |
| `crud._rank_hot` / `db_reply_counts` | `backend/app/crud.py` | §C. `feed_rank.py`'s `hot` restates it and is what `/posts` calls; nothing else does. |

### Added 2026-09-29 (inbox)

| What | Where | The edit first |
|---|---|---|
| `data/causes/*.json` (causes, initiatives, orgs, feed) | repo root `data/` | **Byte-identical to `backend/seed/data/`**, which is where the seed reads them — so nothing is lost with it, and the content is already on the site (it was seeded into the database). The only reader is `ebx_shared.js`'s `fetchJSON`, the `useApi: false` fallback, and `useApi` is hard-coded `true`. Edit first: drop `fetchJSON` + `dataRoot` from `ebx_shared.js` and the `/data` mount in `backend/app/main.py`; then the folder goes (§B). |

### Added 2026-09-30 (P2 · Home mods)

| What | Where | Why it can go / what first |
|---|---|---|
| The wheel's **landing variant** — `shell()`'s phase rows, `topCardHTML`, `liveLine`, `sideOrder`, `spanHTML`, `aim`, the side cards (`cardHTML` outside the pie), `ROWS`, `PHASE[*].go`, the `?step=` URL | `resources/js/ebx_wheel.js` | §B. Home no longer mounts it; only `scripts/wheel_check.js` does (on a bare mount). Edit first: retire the landing half of `wheel_check.js` (the mission variant is pinned by `render_check` / `mission_layout_check`). Keep `PHASE[*].blurb` — the mission page reads it. |
| `.lw-rows`, `.lw-row*`, `.lw-phase*`, `.lw-top*`, `.lw-live*`, `.lw-pointer`, `.lw-stage`, `.lw-col`, `.lw-card*` (side cards), `.lw-span*`, `.lw-arrow` | `resources/css/ebx_frontend.css` | §B, with the row above — nothing else draws them. |
| `.hf-chip`, `.hf__side`, `.hf__search`, `.hf__more` styles | were `index.html` | Done — removed with Home's filters this pass. |
| `cause.html`'s `?q=` / `?cause=` handoff | `cause.html` | §D. Looks dead from Home (Home no longer sends them) — is not: the mission page's *Discuss* and bookmarked links still send `?cause=`. |

### Added 2026-10-01c (Home tweaks)
- §A, safe now: the Network tiles' CSS in `index.html` (`.hn__row`, `.hn__tile*`, `.hn__top`, `.hn__name`, `.hn__tag`, `.hn__n`) and `HomeFeed.row()` / `GROUPS[].tag` — nothing draws the row.

### Added 2026-10-01 (mission pass)

#### Done this pass
- `_rowPreview` (the one-line preview under a clicked row) — removed; the previews are in the ballot expansions.
- `rowConvert` / `rowDonate` and the expansion's Convert / Donate buttons — removed.
- The re-opening of the old inline initiative panel after a re-render (`filterInitiatives` → `idxRowExpand(…, 'tiv')`) — the row keeps only its highlight.

#### New — §B, one edit then safe
- `_idxInitDetailHTML` and the tiv branch of `_idxRowStatusHTML` (`mission.html`) — nothing on the mission page opens them now; `idxRowExpand` is still reached for organizations (`idxSelectOrg`). Drop the tiv path and the `window._idxInitDetailHTML` export.
- `buyVoteEbx` — an alert stub ("Buying tokens is not wired up yet"); still behind the initiative ballot's **Donate more**. Goes when purchasing lands (P5).

#### New — §C, live but replaced
- `initiatives.description` — replaced by Mission-statement / Justification posts. Still read as the report's last fallback until `POST /admin/initiatives/descriptions-to-posts?apply=true` has run on the live site; then the column can go (a migration — proposed, not applied).
- The `tiv:<id>`-tagged Justification as the link between a suggested organization and an initiative — replaced in P2b by `mission_candidacies.tiv_id`.

## ARCHIVE

### 2026-10-05 — About reshape · P1 mission items · P2 Home items · the re-order proposal

*Jax: "Execute the about page reshape as described in backlog. Also, execute the
changes in the build sequence home and mission steps … and suggest an updated
build sequence order."*

**About** (`about.html`, `ebx_shared.js`): see P8 › Reshaped. The site nav is
switched off by `<body data-ebx-nav="off">` (`initNav` honours it); the footer's
About column is Our story · Our goals · How it works · What an Earthbuck is · Our team.

**Mission** (`mission.html`, `backend/app/crud.py`): navigator cards say "x
leading"; the ballot bar's Discuss is "Post about x" (composer, target preset);
`_relist_winner` lists a winning initiative again in the next cycle (no votes
move; idempotent id `<id>-r<n>`). The 4-token report is the grant rule working
as written → D31. The annulus-as-toggle idea → D32.

**Home** (`index.html`): collapsed hub titled **This Week's Decisions**, standing
column heads (Initiative Election · Organization Election), each card "Leading
initiative/organization" with its EBX committed or votes, runners-up below, no
phase label inside; open grid on one hairline grid (no full borders, no row or
column labels), each card "phase · closes x" / title / "Leading: x" / "cause ·
started x", no "Week x"; the five steps numbered 1.–5.; the two decisions an
ordered list; "The Network" heading gone, the source toggles on the + Post row.

**Checks.** `landing_check` 39/39 (About section rewritten; hub row count reads
the grid), `home_check` 80/80 (hub, steps, decisions and feed head updated),
`mission_layout_check` 131/131 (its stale "Inbox is a stub" line updated for P4),
`ce_check` updated for "Post about" (needs Playwright; not run this pass). Pages
rendered at 1280 and 390 px with no script errors and no horizontal scroll.

**Not done / filed.** D31, D32, D33 in DECIDE; the instructional recording (P2
line 1); winners elected before today are not re-listed (one-off, P7a);
`structure.md` §4 (Home) and the About page entry still describe the old
layouts — 999(b) for the next pass.

*Finished pass reports. Nothing here is executed.*

### 2026-10-01d — P3 · the posting display pass

**Read as**: the card is `EBX.Post.collapsed`, so it changes everywhere that
uses it — Home's feed (which drew its own colour-coded card until now) and the
mission page's post lists. News keeps its own card until the P3b rebuild.

- ✅ *The card, redrawn* — title top left (the first line of the body when a post has no title), what it is about under it, the preview below; account and date, type/tags, cause top right; ▲ votes ▼ and replies bottom left, **Discussion →** bottom right. Stacks at phone width.
- ✅ *No color coding on posts* — the card is monochrome; Home's `.hp--*` colours and B · I · A badges are gone from the feed.
- ✅ *Vote on posts from Home* — `EBX.Post.bindVotes`; your arrow is lit (`GET /posts/votes/mine`); signed out, it opens sign-in. The mission page's lists vote too, without opening the post.
- ✅ *Up and down votes on general and research posts* — general posts take Upvote / Downvote (research already had both); budget items stay upvote-only. Pressing the vote you cast again takes it back.
- ✅ *Whether the author took part in the mission's initiative election* — `author_in_me` on every serialized post that belongs to a mission; the card says "✓ voted in its initiative election" or "didn't vote in its initiative election".
- ✅ *Move the diagrams and the built content to the docs* — the taxonomy, the research diagram, the timeline, the card and the full view are `docs/structure.md` § 8c; P3 here keeps Done and Still waiting.

**Checks.** `posting_check` **66** (down votes, take-back, my votes, no
neutral on a general post) · `home_check` **75** (the card's layout, no
colour, votes on every card, the source line) · `posts_box_check` 40 ·
`composer_check` 20 · `landing_check` 21 · `render_check` clean ·
`mission_layout_check` 131. Browser: an upvote on Home lights and counts; a
downvote in the mission page's pre-report list counts without opening the post.

### 2026-10-01c — Home tweaks · HR2 backfilled · admin removal · Posting and Footer re-sorted

- ✅ *"This week's elections" collapsed, "All missions" expanded* (was "4 decided this week").
- ✅ *The four descriptors not numbered.*
- ✅ *Maximize space: not separate boxes; "Make your impact" narrower; bigger text* — open columns divided by hairlines (impact at 0.62 of the others), body text 0.98rem, headings up to 1.35rem.
- ✅ *"Decide what gets funded" and "My profile" gone from the hero* — signed out, the hero keeps only Log in / Sign up; the doors carry both links.
- ✅ *"can be as impactful as your money"* — "just" dropped.
- ✅ *News · Research · Budgeting tabs gone* — the row is not drawn (its CSS is in the register, §A).
- ✅ *Initiative elections in the hub say Leading* — on the grid's cards ("Leading · 64% · 9 initiatives") and over the collapsed cards' top three.
- ✅ *"Show all missions"* (and "Collapse missions").

**Also done** (same message):
- **Human Rights 2 backfilled on the live site.** The bots' `backfill` task now
  elects initiatives in past initiative elections that never got one (it did
  only organizations), choosing from the content file, else the local
  database's winner (proposed on the site by staff if missing), else the most
  preferences; `--missions` limits it; the staff password can live in
  `bots.local.json`. Run: hmr1 → *Environmental Defender Emergency Fund*.
- **Admin removes posts, initiatives and organizations** — P7 › Done.
- **Posting and Footer** re-sorted into Done / Still waiting; Jax's new posting
  notes are the next posting pass (P3 › Still waiting).
- **P2b** takes D29 (each member their own login, created by the
  organization's administrator) and D30 (one general UNCLAIMED panel), the
  verification note and "the campaign page is the mission page from the
  organization's side". DECIDE has no organization questions left.
- **Not done — waits on a deploy:** the description conversion. The endpoint
  is in today's code, which is not on the live site yet (it answers 404).

**Checks.** `home_check` **72** · `landing_check` 21 · `render_check` clean ·
admin Remove driven in a browser (an initiative removed; an elected one refused
with its reason) · the removal routes against the local API (a post with its
reply, an initiative, an organization; the refusals; 403 for a non-staff
account).

**Jax's text, as written** (moved from `## BUILD SEQUENCE` › P2):

- Instead of "4 decided this week" say *This weeks elections* when collapsed and *All missions* when expanded.
- The 4 descriptors should not be numbered.
- Maximize space in the 4 descriptors - the Make your impact section can be narrower, and they don't need to be seperate boxes with extra padding and borders. The inner text should be bigger.
- "Decide what gets funded" and "My profile" links in the hero should be gone.
- "can be as impactful as your money" - drop "just"
- News research and budgeting tabs are still there. They should be gone.
- The initiative elections in the missions hub should say *Leading* to indicate that it isn't final yet.
"Show all missions", not "see"

### 2026-10-01b — P2 · Home pass (the four doors) · P2b rebuilt on D26/D28

**Read as** (no decision was open): the four doors sit between the hero and the
mission hub, Jax's words as written; "'Decide what gets funded' … replaces 'vote
now' in hero" — the hero's button now says it, and door 1 carries the same
link; "For charities" goes to the existing organization door
(`admin.html?register=1`) until P2b builds the organization accounts.

- ✅ *Navigation between the hero and the hub — 1 Two key decisions · 2 Every voice matters · 3 Feedback and accountability · 4 Make your impact* — `#hk`, four cards; links: Decide what gets funded → Missions · Who are we? → About · Go to the discussion → News · Sign in (My profile when signed in) + For charities.
- ✅ *"Decide what gets funded" replaces "Vote now" in the hero.*
- ✅ *Move the news, research and budgeting descriptions to the about page* — the tiles keep their names, tags and counts; About › What the network is for carries the three descriptions (`#ab-net`).
- ✅ *Remove "The social network for charities".*
- ✅ *To the right of the visual: Cause · Initiative · Organization · Network · Reporting stacked, arrows down, each glowing as it is shown* — `#ld-flow`; `EBX.Steps.mount(…, { onChange })` tells it the page; a click on a step shows it; at phone width it wraps into a row.
- ✅ *Only 1 column for posts.*
- ✅ *Missions hub collapsed by default* — a new remembered key, so everyone starts collapsed once.
- ✅ *"<cause> <number>", not "holds"* — a cause election card names the mission its window becomes (e.g. Oceans 5).
- ✅ *Week 0 at the bottom, week 6 at the top* — rows ordered by (active − cause) mod 7: Land, Forests, Wildlife, Human Rights, Human Progress, Atmosphere, Oceans today.
- ✅ *Collapsed: this week's two election cards (ME and OE) with the top 3 leaders* — `#mh-week`: the initiative election and the organization election that decide this week (else the next to), leaders by share / votes.
- ✅ *"See all missions" and "Collapse missions"* — the paging buttons show only when the grid is open.

**P2b** rebuilt on Jax's answers: organization accounts are their own login;
membership roles reshaped (rep · executive move to organization accounts); an
organization cannot vote; its site is Home · Initiatives (the mission page's
steps 2–3) · Profile, plus a tab per campaign; two public pages — the profile
(with the UNCLAIMED state) and a campaign page per election (plan · receipts ·
live ballot slate · Q&A · promises). D26 and D28 cleared; **D29** (who signs in
to an organization account) and **D30** (the unclaimed plan) added. The clock
gives P2b 12 days.

**Checks.** `home_check` **72** (new: collapsed by default, the two cards, row
order, "<cause> <number>", the steps list glowing and clickable, the four doors,
one column, the descriptions on About) · `landing_check` **21** · `render_check`
clean · `wheel_check` 40. No horizontal overflow at 390 · 1000 · 1400px.

Docs touched: this file (P2, P2b, DECIDE, the clock, BACKLOG › Home),
`structure.md` §4.

**Jax's text, as written** (moved from `## BUILD SEQUENCE` › P2):

- In between the mission hub and the hero will be navigation to the main uses of the site.
1. Two key decisions: 
What mission to fund, - We grant $1 to everybody each week to make this decision. 
Which organization to lead it. - To win money, a charity agrees to put it towards the elected mission
“Decide what gets funded” link to missions- replaces “vote now” in hero
2. Every voice matters
Public interest in charity is lacking, we’re changing that by creating a social network for philanthropy. We believe your ideas and opinions can be just as impactful as your money.
“Who are we?” - link to about
3. Feedback and accountability
Our news team covers each mission independently so that you are always equipped to make important decisions. Organizations don’t receive money until there is a plan and trust in their ability to complete it..
“Go to the discussion” - link to news
4. Make your impact
2 links:
 sign in/my profile - benefactor profile
For charities
- Move the news, research, and budgeting descriptions to the about page. 
- Remove "The social network for charities"
- To the right of the visual, have Cause · Initiative · Organization · Network · Reporting vertically stacked with arrows pointing downward, each step glowing as it is being shown
- only 1 column for posts.
- Missions hub 
  - should be collapsed by default
  - Say "<cause><number>", not "holds"
  - The current cause with amission in week 0 should be the bottom row of the hub, and week 6 should be the top row.
  - In the collapsed table row, show this weeks 2 election cards (ME and OE), and include the top 3 leaders. 
  - say "See all missions" instead of expand and "Collapse missions", not just collapse.

### 2026-10-01 — P1 mission pass (Jax's 17 items) · DECIDE cleared · P2b added

**Read as** (no decision was open): build every item in P1's list except the
two that are not page work — the Human Rights 2 backfill (a staff data op,
left with Jax) and the progress reports (they need organization accounts, so
they moved to the new P2b). "The organization election onclick expansion should
contain a description of the election…" is read as the description of the
*organization* being picked, else voted for, else leading.

- ✅ *Suggesting an initiative: a title and an optional "Suggest a mission statement"; a mission statement is a general post tied to an initiative* — the propose dialog's second box; the post is general, tagged `mission_statement` (new in `post_config.GENERAL_TAGS`), target the initiative, ≤280 characters (`posting.prepare_new` refuses longer, or untargeted).
- ✅ *The progress log only needs the title and date, in one row* — `paintPhases`: number · name · date (closes / opens / closed).
- ✅ *The top of the cause section: 6 horizontal bars for each of the 7 active causes; this page indicated; coloured if a replacement has won ≥1 week, the rest dim* — one bar per open window (slots 7–13, from `/causes/slate`'s `challenger_id` / `streak`), labelled by its holder; click → that window.
  - ✅ *keep/replace just below* · ✅ *the click-through below that* · ✅ *"Nominate a cause" to the right of the click-through* (out of the action bar).
- ✅ *"+ post" instead of "Post a <type>"* — `_ballotBar`; the title still names the type.
- ✅ *The proposer can rename an initiative until it is elected* — `PUT /initiatives/{id}/title` is open to the proposer (staff: any, any time); 403 for others, 409 once elected. `POST /initiatives` now records the proposer (it never did). **Rename** in the expansion.
- ✅ *Attach an org to an initiative in earlier phases, in the expansion* — **+ Suggest an organization**. Before the initiative wins there is no race to enter, so the organization is registered and linked by a Justification tagged `tiv:<id>`; the expansion lists "Suggested to run it", and once the initiative wins its race offers each suggestion with one-click **Nominate**. (The proper link, `mission_candidacies.tiv_id`, is a migration → P2b.)
- ✅ *Convert is not an option in the initiative election* — the expansion's Convert / Donate and their stubs are gone.
- ✅ *The initiative expansion: small — a slider row, a post preview, its page, suggest an org, post about it; no convert / donate / description / "selected initiative" / "oceans · suggested" / status* — `_meExpansionHTML`.
  - ✅ *Descriptions → Justifications or Mission statements by length* — `POST /admin/initiatives/descriptions-to-posts` (staff; dry run unless `?apply=true`; idempotent). Locally: 82 → 81 Mission statements + 1 Justification, written by the proposer, else the staff account. **Not run on the live site** — P1 lists it. The report's mission statement reads the leading Mission-statement post.
- ✅ *The organization expansion* — `_oeExpansionHTML`: the picked organization, else my vote, else the leader — name, website, description, discussion preview, + post (an Investigation).
- ✅ *Top row: "Finalized on x"; CE and ME stop there; the last three add the initiative on the right* — `renderBallotHeads` (exchange: "Began on x").
- ✅ *"My slate" in the org race is not an editable box; edited by withdrawing or donating more; "Donate" when nothing is donated* — My stake is a figure; Donate / Donate more opens an Add line (Commit sends it); Withdraw offers the non-final part.
- ✅ *Unable to withdraw my slate* — two causes. (1) `withdraw_stake` read only `stake_ct`, so a stake the page showed from the carried initiative-election money (legacy rows, F20) answered "You have no stake in that mission"; it now reads the same derived figure as every other wallet path, writes it onto the row, and treats the initiative-election skim as final if the row never recorded it. (2) The page offered Withdraw only for **unminted** ct, and a race outside `/wallet`'s eight rows (F11) had no row at all — `GET /wallet/row/{mission_id}` (new) and a non-final test fix both. ⚠ This is money-moving code, done because the pass names the bug: **review `wallet.withdraw_stake` before deploying.**
- ✅ *The Report: posts below the table before the report appears — CE: posts on the incumbent cause or a replacement; ME: posts on any initiative* — `#mx-pre` / `paintPrePosts`; the report waits for the initiative election.
- ✅ *Budget item suggestion up into the plan; the budget description deleted* — `budgetHTML` now sits under the plan.
- ↪ *Progress reports: org report vs. the Earthbux News report* — P2b.
- ↪ *Human Rights 2 backfill* — still in P1, Jax's.

**Also this pass** (asked in the same message): `## DECIDE` cleared of every
answered question (D6–D10, D13–D16, D19–D21, D27, D18's Home half) and
rewritten as one line each with the proposal beside it; D9/D10's answers moved
into P4, D8's remainder into D26; **D28** added (organization account: a login
or a role). **P2b · Organization experience** added to the build sequence, from
BACKLOG › ORG EXPERIENCE, D26, P6's profile and claim page and P1's report note;
P6 narrowed to payment, vetting and mail.

**§0 sweep.** F25 (feed_check's mission-link assertion fails on a target-less
first post — pre-existing), F26 (legacy rows with no recorded skim) filed; F13
struck. Register: § Added 2026-10-01.

**Checks.** `mission_layout_check` **131** (new § Mission pass, 16) · `ce_check`
**85** (the seven window bars, the order, Nominate a cause) · `composer_check`
**20** (posts before the report, + post, budget in the plan) · `posts_box_check`
**40** (the mission statement) · `render_check` clean · `posting_check` 62 ·
`wallet_check` 133 · `home_check` 52 · `wheel_check` 40 · `landing_check` 19 ·
`oe_check` 19/22 — the same three as the baseline (F22) · `feed_check` — F25,
same as the baseline. Browser runs: propose with a statement → rename →
suggest an organization → it shows under the initiative; rename refused once
elected (409) and for a non-proposer (403); a 300-character statement refused;
withdraw on lan1 / oce1 / oce2 (one outside the eight rows) succeeds. No new
overflow at 390px.

**Jax's text, as written** (moved from `## BUILD SEQUENCE` › P1):

- Human rights 2 still needs to be backfilled.
- When suggesting an initiative, the inputs should be a title, and the other box should be an optional "Suggest a mission statement." Mission statement should be a type of general post that is tied to an initiative.
- The progress log only needs the title and date - these can be accomplished in one row. Everything else is shown in the ballot.
- You misunderstood the top of the section for the causes - this is supposed to show the 6 horizontal bars for each of the 7 active causes, showing how close each of them are to replacement. Whichever cause page we are currently in should be indicated. Whichever ones have a replacement that has won at least 1 week should be colored, and the rest should be dim.
  - edit - move the keep/replace row to just below this
  - and just below that, have the click-through causes.
  - Move the nominate button to the right of the click through and have it say "nominate a cause"
- For each ballot, instead of "post a <type>" just have the "+ post" icon
- The proposer of an initiative should be allowed to change its name, as long as it hasn't already been elected.
- Option to attach an org to an initiative in earlier phases - shown in the expansion when you click on an initiative.
- Convert should not be an option for the initiative election.
- The initiative onclick expansion doesn't need to be gigantic. It should open up to a section with a new slider row, a post preview, link to its page, option to suggest an org for it, and option to post about it. No more convert and donate buttons, the description shouldn't even exist, no "selected initiative" or "oceans - suggested" or status. - they should all be converted to justificaiton posts or mission statements, depending on their length. Mission statements should be 1-2 liners.
- In a similar fashion, The organization election onclick expansion should contain a description of the election the user is currently selecting, if none the one they are currently voting for, and if still none the leading organization.
- The top row of the ballot panels only needs "Finalized on x" not "Initiative for oceans is finalized on x". For CE and ME, that's the full change. For the last 3, add the title of the initiative to the right.
- The "My slate" in org race shouldn't be a clickable editable box. It can be edited by withdrawing or donating more. If the user hasn't donated at all, it should just say "Donate".
- Theres an issue with being unable to withdraw my slate. Even when it detects me as having a slate, I cant withdraw because it says I have no slate.

*The Report*
- Progress reports: org report vs. the Earthbux News parallel report, benefactor-moderated — the org report faces B · I · A.
- Before the report appears, show posts below the table. In the cause election, focus on posts targeting either the incumbent cause or a potential replacement. For initiative election, show posts targeting any initiative.
- Move the budget item suggestion up to the plan area, and delete the budget item description, it lives inside the post page.

**The decisions cleared** (their answers, for the record): D6 — no filters on
Home (superseded 2026-09-30) · D7 — the phases are described on the mission
page · D8 — Case and Evaluation are tags; the rest is the org-UX design (D26) ·
D9 — optional email; many notifications inbox-only · D10 — no friendships,
message threads searchable by name or mission · D13 — old initiative titles
forward (built 2026-09-24) · D14 — ballot tabs folded into the phase toggle ·
D15 — six won elections; the sixth makes it the newest open ME race · D16 —
newest means newest · D18 — Home: "You donate. We follow." · D19 — a Background
is a cause's, tags any initiatives, is electable at once, edits after election
day go to the next mission · D20 — the leading Background fixed at T, the
leading Investigation at T+8 · D21 — edits are new versions, used versions lock,
pulled or cited posts restart their votes · D27 — phase 4 is "prep".

Docs touched: this file (DECIDE, P1, P2b, P4, P6, the clock, pass order,
defects, register, BACKLOG), `structure.md` §6. *README (999-d), suggested:*
§ API — add `GET /wallet/row/{mission_id}`, `POST
/admin/initiatives/descriptions-to-posts`, and that `PUT
/initiatives/{id}/title` is open to an initiative's proposer; § Posting — the
`mission_statement` tag.

### 2026-09-30 — P2 · Home mods (the five steps, the mission hub)

**Read as** (said at the start of the pass, no decision was open): the hero goes
left; the five steps become a 5-page animated carousel to its right; the phase
blurbs move into the mission page's ballot panels; the wheel block (phase rows,
top card, annulus, side cards, span) leaves Home — the annulus stays on the
mission page and in step 1's drawing; the mission hub takes its place; the feed
follows with no toggles.

- ✅ *Hero left-aligned; the 5 steps to its right* — `.hx`: hero left (words unchanged), `#ebx-steps` right; stacks under 900px.
- ✅ *5 pages, auto-paging ~10 s, fade, arrows, one message each, the only text* — new `resources/js/ebx_steps.js` (`EBX.Steps`): five SVG scenes on a 10-second timeline (a manual page restarts its scene), 0.8 s crossfade, ‹ › on the sides (wrap), a dot per step with its timer. Pauses off-screen and in a hidden tab; reduced motion = stills, no autoplay.
- ✅ *1 Cause* — the week's segment separates from the annulus, rises, grows and glows; its cause's vista shows inside it; a beam lights the cause's point on the globe; the annulus turns 1/7 in 10 s, bringing the next cause up.
- ✅ *2 Initiative* — the segment opens to fill the frame; the camera pans across the vista past three problem sectors (per cause: e.g. Oceans — a garbage patch, a tanker's slick, a ghost net), zooms out, and a cursor votes one, which glows.
- ✅ *3 Organization* — the voted sector shrinks and moves to a team: a building, people around a table talking, a van; donations fall in, then money, people and crates pour into the sector while its problem heals.
- ✅ *4 Network* — eight people with phones and laptops on a concept map around the sector (with the organization's badge and the bank); ideas, messages, photos, likes and dislikes travel in; the whole map closes into one coin.
- ✅ *5 Reporting* — a news crew (reporter, camera, satellite van) takes the coin in and sends articles, photos and video to people on phones and laptops, who trade coins between them.
- ✅ *Move the text inside the 5 steps to the election panels* — each ballot panel's header line is followed by its phase's line (`#el3-blurb-ce|me|oe|fr|ex`, read from `EBX.Wheel.PHASE`).
- ✅ *Retiring the side cards* — with the rows, top card, annulus and span; `ebx_wheel.js` stays loaded on Home as the hub's data layer.
- ✅ *The mission hub: collapsible 7-row grid, cause elections left, shift a column or a page, click → mission page* — rows = causes; column 0 = the cause's open window on the slate (→ `mission.html?slot=`); then missions newest first (→ `/m/<slug>`); « ‹ › » and Collapse (remembered per browser).
- ✅ *"Week x" on each post-ME mission* — whole weeks since T.
- ✅ *Missions with decisions this week are glowy* — T, T+8, budget day, or the window the cause election confirms, falling in this week. Today: the Oceans cause election, Land 3's initiative election, Oceans 2's organization election and Oceans 1's budget day (all Oct 6).
- ✅ *Feed directly below; no togglability on Home* — the Network tiles link to `cause.html?cat=`, posts to `?thread=`; the cause / mine / search filters are gone (D6 superseded).
- ↪ *Each of this week's races open* — BACKLOG › Home, as Jax said.

**§0 sweep.** F24 filed (`meMission` picks the closed hmr1 over hmr2; `current_phase` is stale — the hub reads dates). Register: the wheel's landing variant and its CSS (§B).

**Checks.** `home_check` **52** (rewritten: steps, hub, feed, the blurbs) · `landing_check` **19** (live API) · `wheel_check` **40** (landing variant on a bare mount) · `render_check` Home selectors rewritten, `#el3-blurb-me` added.

**Jax's text, as written** (moved from `## BUILD SEQUENCE` › P2):

**Home mods**
- Move the hero ro be left-aligned. To the right, we're going to put the 5 steps.
- Move the current text inside the 5 steps to inseide each of their election panel sections
- To the right of the hero, put 5 pages that automatically page every 10 seconds or so from cause-initiative-organization-network-reporting (Probably going to need better terminology.) This section is going to have images and diagrams that are visually aesthetic and represent the 5 steps. Each section will contain little arrows pointing to the left or right to make clear that it's just one step in the process. The transitions should have a fade effect. Each section will have a short message about the step. This will be the only text in this section.
1. Cause
- Message: A fresh focus each week
- The top segment physically removed from the annulus and glowing, as if it had just seperated itself and is ascending and growing. It projecs a glowing beam down on the globe at the center of the annulus. Whichever cause it is, we get a stunning broad vista representing the cause and its beauty and its vastness. The annulus should also slowly rotate (1/7 of a rotation in 10 seconds) and show that the causes cyclically repeat.
2. Initiative
- Message: Broad causes -> narrow missions
- The cause segment expanded to fill the region, the full annulus gone. Inside it, an image representing a specific problem within the cause. Garbage in the ocean, emissions from a mine or factory, deforestation, poisoned animals, suffering people, etc. Create one for each initiative. As we report on real missions, we will get real images to replace this. During the 10 seconds, pan to a few different sectors with different initiatives inside them, and have a mouse click 'vote' on one, causing it to glow right before paging to the next seciton (if the user is manually paging, just restart the visual.) The broad image is a smaller initiative being identified from within the vast landscape.
3. Organizaiton
- Message: Identify those worthy of the job
- The segment from the previous section, shrunk and passed to an organization, which is a group of people working to accomplish it. They have facilities, transportation, they communicate professionally with other people, they travel, and they help. They also receive the money, which allows them to hire people and get things done. Represent this by them pouring money, people, and resources into the sector. The broad image is a team of people, working together, discussing the initiative.
4. Network
- Message: Collaborate and create a plan
- Lots of people on the platform coming up with ideas (lightbulbs), writing messages to eachother and to the misison, and posting pictures, networking. The sector should be in the middle with the logo of the organization and the money/coin/bank account, and the people should be networking with each other all around and sending all their ideas and posts and likes and dislikes and feedback into the center. The money, the people, the initiative, the ideas, and the computers/phones should all be connected on a concept map. At the end of the 10 seconds, the whole network gets encapsulated within the sector and turns into a circular coin.
5. Reporting
- Message: Regular updates and built in control
- A news team with cameras and microphones, taking the whole network in, and spitting out articles and images and videos for people to consume. While they look at their phones and computers, they echange different missions (each its own little coin).

- Retiring the side cards
- Section below is the mission hub.
  - A collapsible, 7 row grid of all missions. Current cause elections to the left. Users will be able to shift the grid one column at a time, or do a full page (when eventually there are enough missions for multiple pages). Clicking on any mission brings you to its mission page.
  - Each post-ME mission card should have a "Week x" showing how many weeks into the mission we are.
  - The missions with decisions this week should be glowy.

- I will probably want to have each of this weeks races open even when the table is not collapsed. Backlogging because I'm probably going to switch what day is budget day. (probably going to be T + 16)

The feed can be directly below this. Remove all togglability from home page feed. It is only toggleable from news.


### 2026-09-29b — Unified elections (Jax's CE · ME · OE panels)

*"I'm trying to make the elections a more unified experience across them. I
only designed the CE, ME, and OE election panels."* The drawings, as they were
in the inbox (Framing and Exchange were drawn with the frame only):

```
 _____________________________________________________________________________________________  
| 1. ...    date  - Cause is/was finalized on DATE_-_x_d_left________________________|CAUSE___|
| 2. ...    date  | ======== ======== ======== ======== ======== ======== ======== <- progress bars for each cause
| 3. ...    date  |  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| <- this weeks vote distribution
| 4. ...    date  |             Click through all possible causes to vote for                 |Discuss -> News
| 5. ...    date  |     KEEP     incumbent          REPLACE with selected                     |
|_________________|_Commit|Cancel___Nominate___Discuss___________Post a background            |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|        Table of upcoming causes up to last open window.  Make rows smaller and add          |
|         'weeks won' column                                                                  |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|_____________________________________________________________________________________________|

 _____________________________________________________________________________________________  
| 1. ...    date  | Initiative for cause # is finalized on DATE_-_x_d_left___________|CAUSE # |
| 2. ...    date  -   Leading                                                                 |
| 3. ...    date  |   Slider rows                                            pool             |
| 4. ...    date  |   Unallocated                                            assigned%        |
| 5. ...    date  |                                                                           |
|_________________|_Commit|Cancel___propose___buy_tokens___discuss__Post a background         |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|_____________________________________________________________________________________________|
This one is good, but remove the "my commit of x tokens". My commit is made clear by the bars.
Also, bring back unallocated row. Not allocating should be an option, because it will be necessary for purchased tokens.
Instead of +org, there should be a link to that initiative's page. Which is a mission page with no ballot area, just a mission report.

 _____________________________________________________________________________________________  
| 1. ...    date  | Organization for initiative is finalized on DATE_-_x_d_left______|CAUSE # |
| 2. ...    date  |   Leading                                                                 |
| 3. ...    date  -   My vote                                                  pool           |
| 4. ...    date  |                                                          My stake         |
| 5. ...    date  |                                          buy tokens     WITHDRAW          |
|_________________|_Commit|Cancel___Nominate___discuss__________________Post an investigation_|
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|_____________________________________________________________________________________________|
Most of the stuff currently in here can be removed. "this race holds",  top 3, clickbox with 'tokens to', 'my vote', redundant title.

 _____________________________________________________________________________________________  
| 1. ...    date  | Preparation for initiative is finalized on DATE__________________|CAUSE   |
| 2. ...    date  |                                                                           |
| 3. ...    date  |                                                                           |
| 4. ...    date  -                                                                           |
| 5. ...    date  |                                                                           |
|_________________|_Commit|Cancel_____________________________________________________________|
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|_____________________________________________________________________________________________|

 _____________________________________________________________________________________________  
| 1. ...    date  | Exchange or initiative began on DATE_____________________________|CAUSE   |
| 2. ...    date  |                                                                           |
| 3. ...    date  |                                                                           |
| 4. ...    date  |                                                                           |
| 5. ...    date  -                                                                           |
|_________________|_Commit|Cancel_____________________________________________________________|
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|                                                                                             |
|_____________________________________________________________________________________________|
```

**What was built** (`mission.html`; checks below).
- ✅ **One panel (F21).** The progress log sits inside it, top left; the phase
  being shown joins the ballot; the table is a full-width row underneath.
- ✅ **One header line** for all five phases: "Cause for the window that runs
  <date> is finalized on <date>", "Initiative for <Cause n> is finalized on …",
  "Organization for <initiative> is finalized on …", "Preparation for
  <initiative> is finalized on …", "Exchange of <initiative> began on …" —
  with "n d left" and the cause (and mission number) as a chip on the right.
- ✅ **One action bar** (`window._ballotBar`): Commit | Cancel · the phase's own
  acts · Discuss (→ News, filtered to the cause) · and the post button on the
  right (Post a background / an investigation / an analysis / Suggest a budget
  item). The separate post bar above the ballot is gone.
- ✅ **Cause election:** a six-week progress bar for each cause on the ballot
  (the holder, then the six challengers closest to taking it; "+n more"), this
  week's vote as one distribution bar, "Click through the causes you can vote
  for", KEEP / REPLACE WITH, then the bar (Commit | Cancel · Nominate · Discuss ·
  Post a background). The CE table is always the cause table now (no Show / Hide
  button) — smaller rows and a **Weeks won** column.
- ✅ **Initiative election:** Leading · Pool · Assigned on one line; the slider
  rows; the **Unallocated** row back ("not allocating should be an option"). The
  typed "My commit of x tokens" is gone: a slider is a share of the tokens you
  can put in, what no slider holds stays unallocated and is **not** committed
  (it used to be spread across the slate on commit). Each row's "+ org" is now
  **Page →**, the initiative's own page. Bar: Commit | Cancel · Propose · Donate
  more · Discuss · Post a background.
- ✅ **Organization election:** Leading and My vote on the left; Pool, My stake,
  Donate more and **Withdraw** (the non-final part, to cash, until budget day —
  `POST /wallet/withdraw-stake`) on the right. Gone, as asked: "this race
  holds", the top 3, the source dropdown with its "tokens to", the My-vote chip,
  the repeated title. You vote by clicking an organization in the table. Bar:
  Commit | Cancel · Nominate · Discuss · Post an investigation.
- ✅ **Framing and Exchange** (not drawn beyond the frame): the header line and
  the bar; their contents are unchanged. They have nothing to commit, so their
  bar has no Commit | Cancel rather than two dead buttons.
- ✅ **An initiative's page** — "a mission page with no ballot area, just a
  mission report": any initiative that is not its mission's elected one (still
  running, or lost) opens with no ballot and no table, a notice with **Vote on
  it in that election →**, and its own report: what it is, what people say
  (posts that target or tag it), what it would need (its budget items), with
  Post a Justification · Post a Background · Suggest a budget item · Nominate an
  organization for it.
- ✅ **The organization vote updates the page** (inbox): after Commit the ballot
  reloads the benefactor's votes, the tallies and the mission's story. A refused
  pick now says why instead of silently reverting, and a race you may not vote
  in no longer takes a pick.
- ✅ **"Buy tokens" → "Donate more"** (inbox: "Maybe I should replace 'buy
  tokens' with commit more or donate") — every purchased token is a donation.
  One word to change back if you prefer "Commit more".

**Checks.** `ce_check` 81/81 (rewritten for the bars, the distribution, the bar,
the weeks-won column, the header line naming the window) · `render_check`
clean · `composer_check` 19/19 (the post button is in the bar) ·
`mission_layout_check` clean · `oe_check` 19/22 — the same three phase-title
assertions as before (F22), plus one rewritten ("the ballot does not repeat the
title"). A browser run: an initiative vote of 40% of a 10-token budget commits 4
tokens and leaves 6 unallocated, and reads back as 40% / 60% after a reload; an
organization vote shows as committed without reloading the page.

Docs touched: this file (INBOX, P1, clock, D27, F21, BACKLOG › Mission),
`structure.md` §6.

### 2026-09-29 — P3 · Posting (and the inbox, filed)

**The inbox, filed first** (§0 rule 1). Each note went where it builds: the
navigator → **F21** (P1 follow-ups); the data folder → the register (it is a
byte-identical copy of `backend/seed/data/`, read only by a fallback that is
switched off); the weekly report → **P4** (what the update carries); the
algorithm → **P3** (the framework, built) and **P5** (tuning); OG tags, RSS,
robots and the sitemap → the new **P3b · News**; the three vote names → **P3**
(built); the timeline on Home → BACKLOG › Home; "where is News" → **P3b**;
MissionStep → BACKLOG › Mission. P4's and P5's "Updates to disperse" were
folded into their Includes.

**Decides.** D8, D19, D20, D21 — answered 2026-09-28. Nothing guessed.

**§0 sweep.** F18 fixed (sign-up errors print the rule). F16 fixed by P3
(About's cards preselect `post.html`). Filed: **F22** (`oe_check` asserts the
pre-compact mission page — the same 3 failures without P3), **F23** (post media
storage).

**⚠ A schema migration, applied on the next deploy.** `e3b9c7a1d4f2`
(`backend/alembic/versions/e3b9c7a1d4f2_sep29_p3_posting.py`) — "make the
posting system operational" was taken as the nod the standing rules ask for.
It moves no money. The startup upgrade backs the database up first
(`.bak_premigrate`). It adds `posts.target_kind/target_id/tags/version/
updated_at`, `post_votes.mission_scope` (the unique key becomes post · person ·
mission), and four tables — `post_versions`, `post_missions`, `post_refs`,
`mission_leads` — then backfills: every post gets version 1 and its target,
every post with a mission its `origin` row, every vote its post's mission, and
**every Review-lane post (case · evaluation) becomes a general post carrying the
tag** (D8). The downgrade restores the columns and tables but not the Review
lane.

**Built.**
- ✅ **One composer** — `post.html`. General (tags) · Research (Background ·
  Investigation · Analysis) · Budget (Service · Supply · Support). The link
  decides the type and the target; the type's guide sits beside it. Images
  attach (downscaled data URLs, F23); Video stays drawn and off.
- ✅ **Reachable from everywhere** — Home's **+ Post**, News's **+ Post** and
  each card's *Respond in a post*, a profile's **+ New post**, every post
  button on the mission page (ballot post bar, the report's Budget buttons,
  *Write yours*), About's research and budget cards. Replies stay in their
  threads.
- ✅ **All posting gates removed** — no stake, for any type, and anyone replies
  to anything (Earthbux's and organizations' posts included). Winning a
  research reward still needs membership (P5).
- ✅ **The Review lane is gone** — Case and Evaluation are general tags; a
  request in the old lane is rewritten as one (the bots keep working).
- ✅ **Targets and limits** — Background → a cause (initiatives as tags), one per
  person per cause, electable at once in the cause's open initiative election;
  Investigation → an organization, one per person per organization, in every
  race it stands in; Analysis → a mission, one per person, open T+8 → T+15;
  budget item → an initiative any time, one OPEN per type per person per
  initiative; general → anything or nothing, unlimited. `app/posting.py`.
- ✅ **Versions (D21)** — every edit is a new version (`post_versions`); a
  mission keeps the version standing when its election for that type closed
  (`post_missions.pinned_version`, computed from the version timestamps, so it
  is the same answer whenever it is asked); those versions are locked for good.
- ✅ **Backgrounds roll (D19)** — once their initiative election closes they
  move to the cause's next one, the closed mission keeping its version; an
  Investigation moves to the next open race of its organization.
- ✅ **Votes count per mission (D21)** — `post_votes.mission_scope`; a post
  rolled, pulled or cited into a mission starts from zero there, and a list read
  with `mission_id=` shows that mission's counts and version.
- ✅ **Pull an old post into this mission** — `POST /posts/{id}/pull`, offered on
  `post.html?mission=`.
- ✅ **The Analysis composer** — `GET /posts/analysis-kit`: up to 12 + 12, any
  mission and age, budget items referenced; the **leads (D20)** fixed once each
  close has passed (`mission_leads` — the most-voted Background at T by votes cast
  in that mission, the most-voted Investigation of any candidate at T+8) and
  attached as `auto` references no edit can remove.
- ✅ **Display** — `EBX.Post` (`ebx_shared.js`): the collapsed view, the Full
  view (References with "cited v1 · now v3", the vote buttons named for the
  type, *Go to <mission>*, *Edit*, replies), and both say what the post targets.
  `GET /posts/{id}` is the full view's data.
- ✅ **Nominations** — proposing an initiative or a cause, or nominating an
  organization, may post a **Justification** (checked by default); the
  initiative's description is no longer written from the dialog. The
  organization dialog lost its initiative checkboxes: the mission comes from
  where it was opened, and opened with none it registers the organization on its
  own (the BACKLOG "I need a place to register new orgs" case). After a
  nomination with no justification: "post a Justification for it →".
- ✅ **Row previews** — clicking an initiative or organization row on the
  mission page shows one short post under it, a Justification first.
- ✅ **How to post** — `about.html#posting`: the model in plain words, one card
  per type, the tags, the three vote names — all from `GET /posts/guide`
  (`post_config.py`), which the composer and the mission thread's outline read
  too.
- ✅ **The feed framework** and **the vote names** (from the inbox) — see P3.
- ✅ Renames: Vetting → **Investigation** on Home, About, News, the mission page
  and profile (the P3 model's word).

**Interpretations to check** (none blocks anything; each is one line to change):
- An Analysis opens at T+8 even when the organization election has no winner
  (wil0, hpr0 — F11), so research is not held hostage to the backfill.
- A Background's lead is decided by Research votes cast *in that mission* before
  T; an Investigation's by votes on it anywhere before T+8 (an organization's
  investigation is read across races).
- Pulling a Background into a mission of another cause is refused (a Background
  belongs to its cause); pulling an Analysis is refused (it belongs to its
  mission).
- A general post is upvote-only, like a budget item.

**Not built** (in P3's text, deliberately left): the reward for suggesting a
winning initiative (Jax: "I should brainstorm") · what an organization account
writes (D26, P6) · notifications when a cited post changes (P4 — the Full view
already shows it) · video (F23).

**Checks.** New: `scripts/posting_check.py` — **63/63** (the API, then the clock
on a throwaway copy of the database: pins, locks, the roll, the leads);
`scripts/posts_box_check.js` (revived for the composer) — **40/40**. Updated for
P3: `composer_check` 19/19, `feed_check` clean, `home_check` 25/25,
`landing_check` 21/21. Unchanged and green: `token_model_check` 107,
`wallet_check` 133, `election_check` 51, `mission_layout_check` 117,
`profile_check` 42, `render_check`, `wheel_check` 40, `ce_check` 80.
`oe_check` 20/23 — F22, the same without P3. `research_gate_check` retired.

**README (999 d) — suggested, not applied:** §5 "The posting model — decided
2026-09-28 (builds in P3; the rewards in P5)" → "(built 2026-09-29; the rewards
in P5)", with a line pointing at `app/posting.py`, `post.html` and
`about.html#posting`; §10's bot notes: research is keyed by cause /
organization / mission now (`ebx_bots.py task_research`).

Docs touched: this file (INBOX, P3, P3b new, P4, P5, clock, F16/F18/F21–F23,
register, BACKLOG), `structure.md` §1, §4, §8b (new), §10, `mission_model.md` §4.

### 2026-09-28 — P1 mission edits (the compact page)

Jax's list, as it stood under `### P1. Mission`, each item and what was done.
Checked against a local copy of the site (the backend on `backend/earthbucks.db`,
Chromium at 1400px and 390px): `mission_layout_check.py` 117/117,
`render_check.js` clean, `composer_check.js` 19/19, `wallet_check.py` 139/139,
`token_model_check.py` 107/107. `oe_check.js` and `ce_check.js` were not run
(they need a bot-seeded database).

- ✅ *The initiative election table is not always showing the right thing … it
  shows the cause table (when I navigate from p1 to p2) and otherwise all the
  initiatives, not filtered by cause.* Two bugs. (1) Leaving the cause election
  for the initiative election did not switch the table back, because the mode
  already read 'tiv' — `setElectionCol` now also checks the table's tab.
  (2) `setMainMode` clears the hidden cause select, so the table showed every
  cause; the initiative table now falls back to the ballot's cause
  (`voteCauseId()`), on first load too.
- ✅ *Titled with the mission title (when applicable); the cause election and
  initiative election pages stay as they are.* From the organization election
  on, the title above the annulus is the mission's initiative; the phase is in
  the chips under it. An initiative that lost is titled with its own name.
- ✅ *The ME table's Cause column — drop it.* Gone (head, rows, colspans).
- ✅ *Move the process and reason sections to one of the tabs of the about page
  — add an about page creation task to the end of the build sequence.* The
  Process / Reason block left the mission page; the progress log ends in "How
  each phase works →" (`about.html#ab-phases` until P8 builds the tab). **P8 ·
  About** added.
- ✅ *Replace the 5 tabs with the progress log with selectable tabs, with the
  voting dialogue to its right.* The five phases are a vertical progress log —
  each phase a tab with its date line and its dated events (mission opened,
  budget day, steps, projected end) — and the ballot is to its right. The
  progress-log card in the story is gone.
- ✅ *Each voting dialogue should have a button to post a <post_type>.* A post
  button tops every live ballot: Background (cause, initiative), Vetting
  (organization), Analysis (framing), a budget item (exchange). On the cause
  election it opens the cause's current initiative election first, then the
  composer.
- ✅ *The report will now go directly below the ballot section.* It does; the
  section heading above it stepped aside.
- ✅ *Budget posting link and explanation appear in the report once the
  initiative has been elected.* A Budget block at the foot of the report —
  what service, supply and support are, and the three Suggest buttons — and a
  Budget tab in the report's thread with every item. The budget panel is gone.
- ✅ *Initiatives that have not won will have mission pages with an empty/locked
  ballot section and a link to the next applicable election.* A page for an
  initiative whose election is over and which lost: the ballot and table are
  replaced by "ran in … and lost to … on …; its ballot here is closed" and a link
  to its cause's current initiative election (to its own row there when it was
  re-listed). Its story section says it did not become a mission and links the
  one that did. Note: `_relist_losers` already moves a loser into the next
  cycle, so a loser's own URL usually lands on that live ballot — the locked
  page is for the ones that were not moved.
- ✅ *Mission Navigator: title it, search bar on top, scroll downward instead of
  page.* Done; the toggled cause is named beside the title.
- ↪ *Maybe "Analysis" instead of "preparation" replacing framing.* Not renamed —
  filed as **D27**.
- ✅ *Not able to vote in some organization elections (land, oceans) though I
  took part in their initiative elections.* The rule let a benefactor into a
  race other than this week's only if their initiative-election money had been
  carried into it (`settle_me`). Two ways that fails: a vote cast in another
  cause's initiative election carries no granted tokens (a preference,
  `stake_ct = 0`, nothing to carry), and some missions never had their stakes
  carried at all (**F20**). `wallet._voted_in_me` now counts any vote in the
  mission's own initiative election — ruling 16, "a benefactor who backed a
  mission's initiative election may vote in its organization election in any
  week" — in `oe_rows.can_take_part` and in `_check_takes_part` (both write
  paths). A permission rule, not a money move; it deploys with the page. The
  locked ballot already explains the rule when it applies.

Docs touched: this file (P1, P3, P8, DECIDE D25–D27, F19–F20, register),
`structure.md` §6 (the drawing, as built), `README.md` §5, `mission_model.md`
§4 and §9, `money_model.md` §14.

### 2026-09-25c — Footer, Contact us, the bots

- ✅ **The footer on every page** (`ebx_shared.js` `initFooter`; a page with no mount gets one). Brand column with **Contact us**; **About** (Why Earthbux · What we do · How it works · What an Earthbuck is → `about.html#why/#what/#how/#earthbuck` — the three "abouts" Jax asked for; White paper · Rules *soon*); **Take part** (Join a mission · Read the news · Nominate an organization · Register a philanthropy *soon* · Join the team → Contact); **Causes** (seven); **Help & legal** (Contact us · Help Center · Safety · Privacy · Terms *soon*); bottom line © · earthbux.net · earthbuxinc.com. `admin.html` (staff console, no shared script) has no footer until P7 absorbs it.
- ✅ **Contact us** — a dialog (`EBX.Dialogs.contact`; also any `[data-ebx-contact]` and a `#contact` hash) that POSTs `/contact`: name, email, topic, message, a hidden honeypot, 5 per address per 10 min. Every message is **stored** (`contact_messages`, migration `d2f8b6c1a9e4` — applied on deploy by the startup upgrade) and **emailed to jax@earthbux.net** when `SMTP_HOST`/`SMTP_USER`/`SMTP_PASSWORD` (+ optional `SMTP_PORT`, `SMTP_FROM`, `CONTACT_TO`) are set on Railway (`app/mailer.py`); until then `emailed` stays false and staff read them in **admin.html › Contact us · messages** (`GET/PUT /admin/contact`).
- ✅ **Research is open to everyone** (Jax's call, P3's rule landed early for research only): `post_config.OPEN_POSTING_CATEGORIES`. Budgeting and review stay gated. Winning a research reward still needs membership.
- ✅ **Vetting posts must target an organization** (Home feedback 1): the server refuses a new vetting post without an existing `org_id`; the mission page's composer asks which (elected first, then the race, then all).
- ✅ **Bots section** in `## BACKLOG` — the bot list and the action list, gathered from where the notes had scattered.
- ◑ **Vetting run** — three posts on **Save the Children** (hpr0, elected Sep 22), in `scripts/bots/week-2026-09-25-vetting.json`, approved by Jax; the dry run against earthbux.net is clean. It runs once this deploy is live (the live server still has the stake gate).

**Checks.** New `contact_check.py` 14 · new `research_gate_check.py` 7 · `wheel_check` 40 · `home_check` 24 · `landing_check` 21 · `mission_layout_check` 105 · `render_check` clean · `composer_check` 18 · `ce_check` 80 · `oe_check` 23 · `profile_check` 42 · `feed_check`.

**Not in this pass.** Home feedback 1 (except "vetting must target an organization") and the rest of "Other" — they are queued where Jax wrote them.

### 2026-09-25b — P2 · Home

**Decisions settled before building** (asked 2026-09-25): D18 Home = "You
donate. We follow." · the "Organization" research post is **Vetting** · the
explainer moved to **about.html** now (D7) · the hero stays as it is.

What shipped, item by item against the spec:

- ✅ *Two rows replace the toggle* — **Deciding the mission** (Cause Election → Initiative Election → Organization Election) and **Planning, feedback and accountability** (Mission Framing → Exchange), arrows left to right. Each card: number, title, one line from the live earthbux.net step cards (the cause line is new — the live site has no cause step), **What's new** (toggles the page) and **Vote / Frame / Trade →** (the mission page, `?state=…&cause=<focus>`). The whole card toggles too.
- ✅ *Descriptions gone from the top card, arrows into it, which phase is selected* — the selected card lights and points down; the top card carries a pointer that slides under the selected card. The top card is now **what is going on**: the phase and cause, the live facts (`liveLine`, F5), the vote button, and the cause's own card on the right. Process/Reason live on the mission page (review 2).
- ✅ *Outer edges aligned* — rows, top card, side cards, the Network row and the feed share the bleed container's edges; the top card's right column and the feed's filter column are the side cards' width.
- ✅ *The time span below the annulus* — e.g. "Sep 29 – Nov 10 · 7 weeks of initiative elections closing, one cause a week", per phase.
- ✅ *The Network — one row* — News (funded) · Research (wins rewards) · Budgeting (drives the mission), each with this week's count; each tile is the feed's filter.
- ✅ *The feed, all posts by default* — newest first, 12 on Home; research tagged **B · V · A**; a URL in a post shows as its source (pulled-in news links).
- ✅ *D6* — Home filters by cause or "mine" only. Search, a thread, replying and any further filter go to News: `cause.html?q=` · `?thread=<id>` (opens that post's replies, scrolls to it) · `?cat=` · `?cause=`, all now read by `cause.html`.
- ✅ *Signed out = signed in, minus vote highlighting* — unchanged; "Mine" is disabled signed out.
- ✅ *The copy spine* → `about.html`, in the spine's order: one sentence · the $1/week grant + dimes + runway · "How it Works — donate to the thing that happens, not the people who do it" + the five phases · what an Earthbuck is (the finality ladder, money_model §0) · research, news and budgeting bands · the origin couplet. Served at `/about.html` (`main.py`).
- ✅ *Organization posts are unclear* — renamed **Vetting** ("investigates the organization that would run the initiative") in `post_config.py`, the mission page's report and composer, News, Home, about.html and profile. Stored key stays `investigation`.
- ✅ *Mobile* — the five site tabs pin to the bottom at ≤640px and hide on scroll-down (F14).
- ◑ *Footer* — saved for later as asked; the list is categorized in `## BACKLOG` › Footer. F9 narrowed (about.html exists).

**Checks.** `wheel_check` 40 (rewritten for the rows) · **new** `home_check` 24 ·
`landing_check` 21 (rewritten, F3) · `render_check` clean (index + about) ·
`mission_layout_check` 105 · `composer_check` 18 (Vetting) · `ce_check` 80 ·
`oe_check` 23 · `profile_check` 42 · `feed_check` · `unit_sweep`.

**README (999d) — suggested, not applied:** l.561 research labels → "Background ·
Vetting · Analysis"; l.979 `index.html` → "Home — phase rows, wheel, the Network,
the feed" and add `about.html`; l.1116 add `about.html` to the page list; l.1122
`EBX.Wheel` "five step toggles" → "two phase rows + live top card"; l.1233
`landing_check` row rewritten and a `home_check` row added; l.544 "Landing
aggregates all posts" is true again, but it is Home's feed now.

**Not in this pass, on purpose.** The composer and `post.html` (P3) — so
"pulled-in news links as a research option" is display-only until then. The
footer. Missions/News one-liners (D18's other two).

<details><summary>The P2 spec as Jax wrote it</summary>

**P2 · Home**

**Goal.** Stop explaining the product and start showing it. Home is the ritual:
where the week stands, and what the network made this week.

**Includes**

- Annulus + top card, five phases, each card: **a** toggle title · **b** definition title · **c** process · **d** reason · **e** side card. Titles: Cause Election · Initiative Election · Organization Election · Mission Framing · Exchange.
  - c and d have been moved to the missions page
- **The time span below the annulus** (the 6–8 week window being shown).
- **The Network** — one row, not three sections: *News* (funded) · *Research* (wins rewards) · *Budgeting* (drives the mission). - below the annulus
- The feed underneath, **all posts by default**, the Network chips as filters; research posts tagged **B · I · A**; pulled-in news links allowed as a research option.
- **Search and detailed filters go to News**; replying goes to News. Simple filters stay on Home (D6).
- **Signed out = signed in**, minus vote highlighting.
- The copy spine, in this order: what Earthbux is in one sentence → the $1/week mechanism → donor control as the organizing idea → what an Earthbuck represents → what research and news are *for*. "How it Works — donate to the thing that happens, not the people who do it." - This is all going to eventually end up on an about.html which will be accessible from the footer.
- Footer: collective action, measured in impact · Causes / Platform / Community · Contact us · Join the team · Register a philanthropy · Send love.White paper
Rules
Accessibility
Help Center
earthbux.net/help 
Privacy and Terms / user agreement
Ads
Get the app
Contact Us
Join Us
Organizations
Join a mission
Beneficiaries
Pay us
Contact us
About
earthbuxinc.com 
Copyright 2026 earthbux
Safety
Docs
Links
Github

---- Save the footer for later, but try to categorize these and suggest which might and might not be necessary.

- Mobile: the five tabs pin to the bottom, hiding on scroll-down.

**Home plan**
- Above that, replace the current toggle with 2 rows:
  - Row 1: Deciding the mission: Cause, initiative, and organization elections, arrows pointing from left to right, short descriptions (use descriptions from what is still on the live version of earthbux.net)
  - Row 2: Planning, feedback, and accountability - framing and exchange.
  - Include buttons 'See what's new'(Or something like 'view' or 'status') that toggles the page, and 'vote' which brings you to the mission.
- The descriptions should be gone, replaced with arrows pointing to what is going on in the top card, and an indication of which of the above phases is selected
- Fix the formatting so the outer edges of the side cards and top card and phase descriptions are aligned.

- The organization posts are investigations into an organization - I need this to be clearer, I feel like there's some ambiguity about their purpose.

**Decides.** D6, D7.

**Done when.** `wheel_check.js` still green, a new `home_check` covers the
Network row, the default-all feed and the filter split, and
**`landing_check.js` is rewritten** — it currently asserts the pre-2026-09-20
page and fails (**F3**).

**Out of scope.** The composer itself (P3). Inbox (P4). News's own optimized
view beyond "search lands here".

</details>

### 2026-09-25 — P1 review 2 (the report is the main display)

Every item of the review, as written, and what was done:

- ✅ *The mission progress report… should be what is the main display… separate budgeting and research posts* — the story is now three stacked parts, no toggle between them: the progress log, the budget panel, then the report.
  - ✅ *Budgeting posts live in the "posts on this mission" panel… "suggest a budget item" buttons at the bottom* — the panel lists this mission's Service · Supply · Support items with their costs; **Suggest: Service · Supply · Support** sits at its foot and opens the composer on that type.
  - ✅ *Below, display the report… mission statement, a plan, background, organization, analysis* — the report is assembled from the leading post (by rating) of each category. **Mission statement:** the winning organization's candidacy statement, else the leading candidate's, else the initiative's description. **Plan:** the organization's steps once it has them, else the four leading budget items and their total. Then **Background · Organization · Analysis**. "Investigation" now reads **Organization** everywhere (`post_config.py`, `cause.html`, the composer); the stored key stays `investigation`.
  - ✅ *Clicking on the report should open a thread… read, reply to and rate… and create their own* — a full-screen thread with the three sections as tabs; every post has Helpful · Neutral · Harmful (`POST /posts/{id}/react`, the ratings that order the report), Reply, and its replies; **Write yours** opens the composer on the open section.
- ✅ *The table area should be absorbed into the ballot panel* — the initiative/organization table now sits inside the phase panel, under the ballot, and hides with it when the phase isn't live.
  - ✅ *Add the 'how it works' explanations from the home page to each of the toggled phase sections* — each phase panel opens with the Home wheel's copy for that phase (kicker, title, Process, Reason — one source, `EBX.Wheel.COPY`).
- ✅ *Delete the top title, and move the title from below the annulus to above it… titled with the current phase (whatever currently exists and whatever is being elected)* — the page head is gone. Above the annulus: the phase ("Organization Election"), and under it chips for what exists (✓ Cause · ✓ Initiative · ✓ Organization) and what is being elected ("Electing the organization — 4 running · closes Oct 2").
- ✅ *The cause toggle should be at the top. Its bottom flush with the top of that title and the left and right panels* — the cause tabs are the first thing on the page; the navigator, the title and the overview all start on one line under them.
- ✅ *Fit more than 3 missions on the lhs navigator — try 5* — five per page: the newest CE window, ME and OE, then the next two newest.

**Checks.** `mission_layout_check.py` 105/105 (new "review 2" section) ·
`composer_check.js` 18 (rewritten: budget panel → report plan; report → thread;
write, rate, reply) · `render_check` clean · `ce_check` 80 · `oe_check` 23 ·
`wheel_check` 27 · `feed_check` · `carryover_check` · `profile_check` · `unit_sweep`.

**Not in this pass, on purpose.** The Home plan (P2), "Other" (the bot run) and
the phase-6 line stay where Jax wrote them. The post-support ring's move to
framing and exchange is unchanged in `## BACKLOG`.

<details><summary>The review as Jax wrote it</summary>

**Mission page review 2**
- Trying to unite this with the original goal - The mission progress report becomes a self-improving document thanks to widespread community improvements. It should be what is the main display on the mission page. We can seperate budgeting and research posts in the mission story, and have them compliment each other rather than be 2 toggles of the same thing...
  - The budgeting posts can live in the current "posts on this mission" panel. Show current posts and have the "suggest a budget item" buttons at the bottom of the panel.
  - Below, display the report, which is the member-generated combination of the leading posts of each category. It should include a mission statement, a plan, and sections for background, investigation (maybe instead of 'investigation', title it 'organization'), and analysis.
  - Clicking on the report should open a thread where a user can read through and reply to and rate the various research posts on that mission, and create their own.
- For each of the sections, the table area should be absorbed into the ballot panel. They will be part of the same area. 
  - Also, add the 'how it works' explanations from the home page to each of the toggled phase sections.
- We don't need the title on top. We have it below the annulus... Delete the top title, and move the title from below the annulus to above it. It should be titled with the current phase (Include whatever currently exists and whatever is currently being elected), because the cause is already clear from the toggle above.
- The cause toggle should be at the top. Its bottom should be flush with the top of that title and the left and right panels.
- Looks like we can fit more than 3 missions on the lhs navigator. try 5, or as many as will fit.

</details>

### 2026-09-24b — P1 review pass (Jax's review of the merged page)

Every item of the review, as written, and what was done:

- ✅ *LHS pager needs to only page through missions in the toggled cause.* — the navigator is "<Cause> missions": page one is that cause's newest CE window, ME and OE; the pager goes back through its older missions (D16).
- ✅ *Cause toggle needs to only select 1 cause at a time* — the ME/OE marks (which looked like second selections) are gone; one glow.
- ✅ *Cause toggle should be above 5-step toggle*
- ✅ *Switching the 5 step toggle should not change the selected mission…* — a phase that is the mission's live one shows its ballot; a past one a recap ("Won by X on date"), a future one "hasn't happened yet — opens date", each with where this week's race in that phase is and a button to it. Every tab carries its one-line recap and date when closed. `?phase=` makes it linkable.
- ✅ *…Switching the cause toggle should not change the phase…* — it keeps the phase and lands on that cause's mission in it this week.
- ✅ *Initiative table should be separated by phase. Remove 'show all initiatives' and 'show active missions...' but keep search.* — the table is the open phase's (and the cause's); both buttons and their code are gone; search stays. A phase that is not live hides the table with the ballot.
- ✅ *"The story so far", "Claim this mission", final standings* — kept.
- ✅ *Remove any references to 'open the mission page' or 'discuss'* — Discuss (×4), "make your case", "View Organizations", "Mission →", "Open the mission page" removed; "Post a budget item" opens the composer; links to OTHER missions use their `/m/` address.
- ✅ *Remove allocations panel from m* — the mounts are gone and the painters are no-ops here; `unallocInnerHTML` waits for the profile page (register).
- ✅ *Remove the post support annulus section, plan to move it to framing and exchange* — removed; the move is in `## BACKLOG` › Mission; the endpoint is untouched.
- ✅ *Fold the discussion into the story; a posting dialogue below it…* — the discussion box is gone from the page (`ebx_postsbox.js` and `posts_box_check.js` are in the register). The dialogue at the foot of the story follows the "Posts on this mission" toggle: Research → Background · Investigation · Analysis; Budgeting → Service · Supply · Support with their costed fields; Review → a reply, to any post (every post has Reply; Review lists replies). "Context" reads **Background** everywhere (the stored key stays `context`).
  - ✅ *…a popup (like LinkedIn) with the whole screen… images or videos… media as the main part with a caption* — the full-screen composer; image, video and the media-led layout are drawn and disabled until P3.
  - ✅ *…situate everything to facilitate this future step* — posting works today through `POST /posts` with its existing rules (membership; one of each research post), so P3 only has to lift the gates and add media.
  - ✅ *The top of the page should say… "Atmosphere: Initiative Election"* — the head is "<Cause>: <Phase>", the mission on the line under it.
  - ◑ *A 1-line description for home, mission and news* — suggestions in DECIDE **D18**.
- **D13** stored slugs with history · **D14** ballot tabs folded into the phase toggle · **D15** six weekly elections · **D16** newest per cause — done; **D17** is Jax's backfill.

**Checks.** `mission_layout_check.py` 94/94 · `render_check` clean · `ce_check` 80 ·
`oe_check` 23 · new `composer_check.js` 15 (research, reply, budget item posted
through the composer by a member) · `wheel_check` 27 · `feed_check` · plus the
backend checks. `posts_box_check` is retired with the box it pinned.

<details><summary>The review as Jax wrote it</summary>

**P1. Mission**
**New mission.html review**
- LHS pager needs to only page through missions in the toggled cause.
- Cause toggle needs to only select 1 cause at a time
- Cause toggle should be above 5-step toggle
- Switching the 5 step toggle should not change the selected mission. If the selected phase is in the past or future, show a recap or inform that it hasn't happened yet, and inform the user that they can select that mission from the navigator. This brief recap (for example, the name of the winner) and the date should also be visile from the toggle even when it isn't opened.
- The inverse is also true. Switching the cause toggle should not change the phase. It should keep the current selected phase, and default to whichever mission is active in that phase this week.
- Initiative table should be seperated by phase. Remove 'show all initiatives' and 'show active missions...' but keep search. 
- I like the "The story so far" section. Good idea. I also like how you added the "Claim this mission" section at the bottom. The final standings section is also good.
- Remove any references to 'open the mission page' or 'discuss' here. They would just link to the page they are already on.
- Remove allocations panel from m, I'll deal with it when I get to the profile page.
- Remove the post support annulus section, move it (or plan to move it) to the framing and exchange phase.
- The entire discussion section can be folded into the new story section. We can delete everything from the discussion, and add a posting dialogue below the story where users can toggle between the 3 types using "posts on the misssion" toggle and tag their post as one of the 3 research posts if research is toggled, or the dialogue changes when budget is toggled and they can suggest budget items. Remember, context is now "background". For review, I'm going to remove the category, it's just going to be a reply - to anything.
  - Clicking on this will open what appears to be a popup (like on linkedin), where users have the whole screen to make their post, and can attach images or videos. They should also have the option to make the image/video the main part of the post, with a caption
  - This is on the posting step, for now, just situate everything on the mission page to facilitate this future step.
  - The top of the page should say what has just been selected, followed by the title of whichever phase is selected. For example: Atmosphere: Initiative Election
  - I'm going to need a good 1-line description for home, mission, and news. Suggest a few, and I'll think of sume during this pass. 



</details>

### 2026-09-24 — P1 · The Merge (Elect → Mission)

**What shipped.** `mission.html` is one page for a mission's whole life;
`main.html` forwards to it. Top to bottom: the page head (initiative title and
the mission's own link) · the annulus row — the **mission toggler** (D2: the
newest cause-election window, initiative election and organization election,
pager above, search below), the landing page's `EBX.Wheel` in its new
`variant: 'mission'` (ring · pie of the selected race · globe), the
**overview** (D3, in that order: phase · cause · initiative · organization with
website · guaranteed pool · committed pool · EBX value · EBX spent · members) ·
the **5-phase toggle** with each phase's date · the **7 cause toggles** with
their next ballot date on their face · the five ballots · the action row, table
and `#fx-view` · the allocations · the mission's own story (progress log, posts,
the final standings of its initiative election, the post-support ring, the
discussion box, the competing organizations and the claim gate).

- **D1** `/m/<initiative-title-slug>` for any initiative, won or not;
  `/m/<mission-id>` before an initiative wins; `/m` for the default;
  `/m?slot=N` for a cause window that is not a mission yet. Slugs are derived
  (`EBX.Slug`) — see D13. Old `?mission= ?id= ?init= ?state= ?cause=` links
  settle on the canonical address.
- **D2** as above. **D3** as above, from a new read-only
  `GET /missions/{id}/overview` (`wallet.mission_overview`): the committed pool
  is the race pool's own reading (`crud.p2_stake_by_ben`), the guaranteed pool
  is its final part (`tm.final_ct`). **D4** a cause toggle or a sector goes to
  that cause's current initiative election. **D5** six weeks, everywhere.
- Mission and phase toggles repaint the page and push history; the ballot tabs
  open a ballot and nothing else; a race row in the OE table moves the page.
- Nav: Home · Missions · News · Inbox · Profile (Inbox drawn, not linked).
- Deleted: `renderPie`, `_buildPieSVG`, `updateCenter`, the `renderOne` side
  cards, `_bindCardFilterClicks`, 92 dead CSS rules, all 13 dangling ids (F2).
  The wheel's CSS moved from `index.html` into `ebx_frontend.css`.
- Fixed on the way: F10 (discussion `p2Active`), F12 (*Show all races* threw), F17 (ME ballot date),
  the OE topbar naming a different race from its ballot.

**Checks.** `mission_layout_check.py` 63/63 · `render_check` clean ·
`ce_check` 80/80 · `oe_check` 22/22 (rewritten) · `wheel_check` 27/27 ·
`posts_box_check` · `feed_check` · `profile_check` · `carryover_check` ·
`unit_sweep` · `date_audit` · `election_check.py` 51 · `wallet_check.py` 139 ·
`token_model_check.py` 107 — all clean. `landing_check` still 7 (F3, P2).

**Not done, on purpose.** No money-moving code and no migration (the slug table
is D13). The two top cards' builders are dead but not deleted (register §B).

<details><summary>The P1 spec and D1–D5 as they stood</summary>

**P1 · The Merge — Elect → Mission**
**Goal.** One page for a mission's whole life. `main.html` stops being a
destination; `mission.html` carries the elections.

**Includes** — these ship together because none of them is testable alone:

- The five ballots (`#el3`: cause · initiative · organization · framing · exchange), the action row, the tables and the allocations panel move from `main.html` into `mission.html`.
- **Annulus, one component, two variants.** Home keeps the six side cards; Mission puts the **mission toggler** (three missions + pager) on the left and the **overview** on the right.
- The **5-phase toggle** and the **7 cause toggles** sit below the annulus.
- Toggling a mission and toggling a phase both repaint the whole page; **toggling the ballot keeps you on the same election**.
- **Ballot dates on the toggles.**
- **Every initiative has a mission page**, won or not, at a stable per-mission URL (D1).
- `main.html` becomes a redirect; the nav reads Home · Missions · News · Inbox · Profile (Inbox is a stub until P4).
- Delete the annulus leftovers while the page is open: `renderPie`, `_buildPieSVG`, `updateCenter`, the `renderOne`/panel block, the dead `.hero__*` CSS, and the 13 dangling `getElementById` targets (register §B, 2026-09-18; **F2**).
- Resolve **D5/F1** in the same pass — it is one number in one ballot.

**Decides.** D1, D2, D3, D4, D5.

**Done when.** `scripts/mission_layout_check.py` (grown from
`election_layout_check.py`'s 16 assertions) is green, and `ce_check` /
`oe_check` / `render_check` either pass or are rewritten against the merged
page. `oe_check` is already failing (**F4**) and this is where it gets fixed.

**Out of scope.** Withdraw/convert and any money action (P5). Posting gates and
`post.html` (P3). New tables beyond the ones that move. The mission gantt ring
widget (backlog).

Ok. New instructions, new model, let's grind. One step at a time.
- Note that md viewer is unable to display the gantt chart.
| **D1** | Mission URL scheme: `/m/solar-grids` (slug from the initiative title) or `/m/atm2` (cause + cycle)? Slug needs a uniqueness rule and a redirect when a title is edited. | P1 | - ANSWER - use the initiative title. This way the mission page will be identifiable as a link to someone who is not familiar with earthbux. The page may exist as simply m before the cause is decided and initiative is elected, but page-building from research and budgeting is possible for any initiative. 
| **D2** | The mission toggler on the left of the annulus shows **three** missions — which three (this cause's three most recent? one per open phase?), and what does the pager page through? | P1 | - ANSWER - It defaults to the 3 newest missions - 1 still in CE, 1 in ME, and 1 in OE. Paging through gets us to more mature missions.
| **D3** | What sits in the right-hand overview: which four or five facts about the mission, in what order? | P1 | ANSWER - It will depend on phase, but for now: Current phase, Cause, Initiative Title, Organization (with link to website), Guaranteed and committed pools, ebx value, ebx spent, member count, thats all I can think of at the moment.
| **D4** | On a mission page, what do the seven cause toggles *do* — jump to that cause's current mission, or filter the toggler's list? | P1 | - ANSWER - These make it easier to navigate through all possible missions. They jump to that causes current ME mission, with an undecided initiative, but a decided cause (the mission election is arguably the most impactful decision.)
| **D5** | A cause challenger needs **6** weeks in a row or **7**? The page prints 6; `weeks_required`, the cause cards, README and mission_model all count 7. (Also **F1**.) | P1 | - ANSWER - 6 weeks. This should be clear everywhere. I apologize for introducing 7, which surely caused confusion. 

- The mission page is going to become very large. I'm sure we will make many visual edits to perfect it. Again, this page is the decision hub, and the home for each mission.


</details>

### 2026-09-20 — Landing top card + Elect two cards

**Landing** (`index.html` + `resources/js/ebx_wheel.js`): the five panels carry
"how it works" alone; the top card is *dates · title · Process · Reason*; the
annulus lost its now marker and rotates with the focus; side cards put the
mission title above the dates and highlight my vote; a NEWS band
(journalists · scientists · auditors) sits under the research band. 27 checks,
`scripts/wheel_check.js`.

**Election** (`main.html`): two top cards instead of four, each with a home
cause; the seven-cause toggle moved directly under them; the five instruction
lines moved to the landing top card titles; every ballot box took the election
cards' topbar (title · days · date). 16 checks,
`scripts/election_layout_check.py`.

### 2026-09-18 — the wheel moves to the landing page

The annulus, its centre, the pie, the six side cards and the ME/OE toggle left
`main.html` for `index.html` as `EBX.Wheel`. Steps 4 and 5 — framing and the
exchange — joined the Elect page with `#fx-view`, and framing cash withdrawal
(`POST /wallet/withdraw-stake`) got its first page.

### 2026-09-17 — the percentage ballot

The initiative ballot became percentages of one commit; the organization ballot
got the My-votes ladder (0 tokens = 1 vote, 10 = 2, 20 = 3, 40 = 4, 80 = 5);
`cause.html` became the feed.

### 2026-09-16 — the money model rewrite

`money_model.md` rewritten with the finality ladder in code; the TypeScript
source retired, `resources/js/ebx_shared.js` is the source and there is no
frontend build; the voting bots ran for the first time.
