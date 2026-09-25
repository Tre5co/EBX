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
  - [The build clock](#the-build-clock)
- [2. DECIDE](#2-decide)
- [3. BUILD SEQUENCE](#3-build-sequence)
  - [P1. Mission](#p1-mission)
  - [P2 · Home](#p2--home)
  - [NOW. Footer.](#now-footer)
  - [P3 · Posting](#p3--posting)
  - [P4 · Event log + Inbox](#p4--event-log--inbox)
  - [P5 · Money made visible](#p5--money-made-visible)
  - [P6 · Counterparty](#p6--counterparty)
  - [P7 · Admin & trust](#p7--admin--trust)
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
- [ARCHIVE](#archive)
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

**P4 Event log + Inbox** turns single visits into a habit (G3). It needs P3's
posts and P1's phase changes as its event sources.

**P5 Money made visible** is one pass, not five, because withdraw, convert,
allocations, the two accounting numbers and the coin price all read the same
token model (G2). Split across surfaces, they drift.

**P6 Counterparty** and **P7 Admin & trust** are gated by external lead times
and by having real activity to administer (G4, G5), so they sit behind the
surfaces — but their *enquiries* start now and are already on the clock.

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

    section Surfaces
    Landing wheel + Elect two cards           :done, s0, 2026-09-20, 1d
    P1 The Merge (Elect -> Mission)           :done, p1, 2026-09-24, 1d
    P1 review pass (Jax's 13 items, D13-D16)  :done, p1r, 2026-09-24, 1d
    P1 review 2 (report is the main display)  :done, p1r2, 2026-09-25, 1d
    P1 follow-ups (dead top-card + box code)  :p1b, after p1r2, 2d
    P2 Home (annulus + The Network + feed)    :done, p2, 2026-09-25, 1d
    Footer + Contact us (F9)                  :done, foot, 2026-09-25, 1d
    P3 Posting (post.html, gates off)         :p3, after p2, 4d
    P4 Event log + Inbox                      :p4, after p3, 5d
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
    Org registration + claim page             :c3, after p5, 14d
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
*Only Jax answers these. Each says which pass it blocks. A pass with an open
blocker does not start.*

| id | Question | Blocks |
|---|---|---|
| **D6** | Which filters keep you on Home and which throw you to News? Proposed: the three Network chips stay; anything with a second axis (cause + type + date, or any search) goes to News. | P2 | - ANSWER - For now, you can only filter by cause or by your own posts on home. Opening the thread or doing any further filters brings you to news.
| **D7** | Does any signed-out marketing copy survive on Home, given "the signed out version is not different"? If yes, where do the five phase descriptions and "How it Works" live once the feed is the first thing below the annulus? | P2 | - ANSWER - described in instructions
| **D8** | Post types on `post.html`, and which ones an organization account sees versus a benefactor. | P3 |
| **D9** | Which events notify, and where they land — inbox only, or inbox + email weekly digest? (Mail transport is a P6 dependency.) | P4 | - ANSWER - Users should be able to optionally get email updates, but there will be many notifications that only come through through the inbox.
| **D10** | Do friendships exist at all? Messaging is now mission-members-only, which may make a friend model unnecessary — but Profile still lists "friends". | P4 | - ANSWER - I think there could be some use to building friendships across missions - 2 people who collaborated on one mission might want to collaborate on another one.
| **D11** | Fee-for-coverage instead of a cut of donations ("Earthbux donates 100%, collects a fee from the philanthropy"). Changes `money_model.md` and the nonprofit application, and carries an independence risk worth writing down. | P5, P6 |
| **D12** | Where the money actually lives — the banking and custody question behind G2. | P6 |
| **D13** | *(from P1, 2026-09-24)* Mission URLs are derived from the initiative title, so **renaming an initiative moves its URL** and old links fall back to the default mission with a notice. Keeping old links alive needs a stored `slug` column plus a `slug_history` table (a migration — proposed, not applied). Do it now, or only once titles become editable? | P1 follow-up | - ANSWER - Yes, old titles of the initiative should also link to the new title. **→ Done 2026-09-24 (P1 review):** `initiative_slugs` (migration `c9e4a7d2b6f1`), `PUT /initiatives/{id}/title` keeps the old slug forwarding.
| **D14** | *(from P1)* The page now has **two five-way toggles**: the phase toggle under the annulus (moves the page to this cause's mission in that phase) and the ballot tabs (open a ballot, change nothing else). Keep both, or fold the ballot tabs into the phase toggle? | P2 | - ANSWER - Fold the ballot tabs into the phase toggle. Try to visually connect them as well. **→ Done 2026-09-24:** five tabs across the top of one panel.
| **D15** | *(from P1 / D5)* Six columns now. The oldest column **aggregates the six weeks before the contest opened** — does it count as one of the "6 weeks in a row", or should a challenger need six live weeks plus the head start? The code counts it (5 live + 1 aggregate). | — | - ANSWER - It needs to win 6 elections. Upon winning its sixth election, it will be the newest open ME race. **→ Done 2026-09-24:** six weekly columns, the aggregate head start removed. "Becomes the newest open ME race" is the spec for the swap, which is still unbuilt (README §4).
| **D16** | *(from P1)* The toggler's first page shows the newest **cause election** window (slot 7, not a mission yet — `/m?slot=7`), the newest **initiative** election and the newest **organization** election. "Newest" is the one furthest from closing; the one closing **this week** is on page 2+. Is newest right, or should page one be the three that close soonest? | P2 | - ANSWER - Newest means newest. That's right, but see issues in my review. **→ Done 2026-09-24:** newest, per toggled cause.
| **D17** | *(from P1 sweep, F11)* Two organization elections (wil0, hpr0) are **past their close date with no winner** — their only candidates are pending approval. They hold the "this week's race" slot and push live races out of `/wallet/rows`' eight. What happens to a race that closes with no approved candidate? | P5 / P7 | - ANSWER - I need to backfill these. **→ Open on Jax** (F11 waits on the backfill).

| **D18** | *(from the P1 review)* A one-line description for **Home**, **Missions** and **News**. Suggestions, to pick from or react to — **Home:** "You donate. We follow." · "A dollar a week, and a say in where it goes." · "The social network for charities." · "Where the week's giving is decided." **Missions:** "Every mission, from the vote to the last receipt." · "Pick the cause, elect the plan, watch the money work." · "One page for a mission's whole life." · "Where the pool becomes a plan." **News:** "What the network found this week." · "Journalists, scientists and auditors — on your missions." · "The reporting your donation paid for." · "Every mission, covered like a story." | P2 | - ANSWER - Home: "You donate. We follow." (the strapline stays as it is). **→ Done 2026-09-25 (P2).** Missions and News still open.

## 3. BUILD SEQUENCE

### P1. Mission
*Review 2 shipped 2026-09-25 — see `## ARCHIVE` › 2026-09-25. Nothing open here;
the next P1 work is the follow-ups on the build clock (dead top-card code, the
register below).*

### P2 · Home
*Shipped 2026-09-25 — see `## ARCHIVE` › 2026-09-25b. Nothing open here; the
footer was saved for later and sits in `## BACKLOG` › Footer with a proposed
categorization.*

### NOW. Footer.

*Built 2026-09-25 — see `## ARCHIVE` › 2026-09-25c. The table below is what it was built from; "later" items are drawn as "soon" in the footer, not linked.*

**Footer** *(saved for later by the P2 spec; about.html now exists — F9)*

Jax's list, sorted into four columns and a bottom line. **Keep** = worth a link
at launch; **later** = needs a page or a thing that does not exist yet;
**drop** = a duplicate, or not a footer item.

| Column | Keep | Later | Drop / merge |
|---|---|---|---|
| **Earthbux** | About (about.html) · White paper (→ `money_model.md` rendered) · Rules | Docs · GitHub (once the repo is public) | earthbuxinc.com (the company site — one link at the bottom line, not a column item) |
| **Take part** | Join a mission (→ Missions) · Register a philanthropy / Organizations (one link, P6's claim page) | Beneficiaries (P6: beneficiary surface) · Get the app | Join Us (= Join the team) |
| **Support** | Help Center (earthbux.net/help) · Contact us · Safety | Accessibility (a statement page) | the second Contact Us · Links |
| **Legal** | Privacy · Terms / user agreement | — | Ads (there are none; say so in Terms instead) |
| **Bottom line** | © 2026 Earthbux · earthbux.net · earthbuxinc.com | Send love / Pay us (a donate-to-Earthbux link — needs D11/D12) | Copyright (already the ©) |

- One important thing - 'Contact us' should open a dialogue for them to send a message, which messages jax@earthbux.net

Also kept from the spec: "collective action, measured in impact" as the
footer's tagline, and the seven Causes column (it is the only footer list that
links real pages today). "Join the team" belongs under Earthbux once there is a
careers page.

### P3 · Posting

**Goal.** One way to make a post, reachable from everywhere, with the context
already filled in.

**Includes**

- `post.html` — new posts only, never replies. Entry from Home's **+**, a mission, a profile, News.
- The link that opened it decides what is preselected: mission, cause, type.
- **All posting gates removed** — everyone can post, everyone can reply.
- **One of each research post per user per mission** (Background · Investigation · Analysis), and research posts become **editable**.
- Every post is tagged to at least one mission; every post links back to News.
- Mission discussion gets its instructions/outline.
- Backend: one create route per type, with the type's own required fields (service: job · rate · days; supply: item · cost; support: no cost line).

**Decides.** D8.

**Done when.** `posts_box_check` / `feed_check` extended to cover creation from
each entry point, the gate removal, and the one-of-each rule.

**Out of scope.** Notifications (P4). Rewards and post ranking (P5).

---

### P4 · Event log + Inbox

**Goal.** Give a benefactor a reason to come back that is about *them*. The
four loops: inbox · your stake changed · the weekly ritual · status and rewards.

**Includes**

- A **backend event log** — the single source for notifications, the weekly update, and later the admin audit trail.
- Event types that notify: replies, reactions, and **phase changes with win/lose/what is coming next**.
- `inbox.html`: the stream, read/unread, and **YOUR weekly update**.
- Messaging, **mission members only**, with the no-campaigning rule stated in the UI and a report button.
- The nav's Inbox stub becomes real.

**Decides.** D9, D10.

**Done when.** An `inbox_check` covers event creation for each notifying type,
per-user fan-out, and the weekly-update assembly.

**Out of scope.** Email delivery (needs mail transport — P6/c1). Friend graph, unless D10 says it exists.

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

**Decides.** D11 (affects what the fee line says, not whether the pass runs).

**Done when.** `wallet_check` and `token_model_check` extended to the new
actions, and one figure reconciled across ballot, profile and mission page.

**Out of scope.** The DEX. The framing exchange itself (backend, money_model §12).

---

### P6 · Counterparty

**Goal.** A real organization can be found, can claim, and can be paid (G4, G5).

**Includes.** Organization profile (initiative coins, tasklist, memberships) ·
registration and claim page · the M1 registered / M2 might-win / M3 won
messages · vetting gates · beneficiary surface (voice at phase-2 start) ·
mail transport · check flow and payee.

**Decides.** D11, D12.

**Done when.** An organization can be nominated, claim its page, and appear as
payee in a dry-run, with the vetting state visible on the mission page.

---

### P7 · Admin & trust

**Goal.** Run the thing without a second website, and keep it from being gamed.

**Includes.** `admin.html` absorbed into the site, off Profile · admin data hub
keyed on missions, accounts, organizations, purchases · bot task split
(voting · researching · proposing · exchanging · budgeting), scheduling and
network-wide deploy, and the **bot vote-spread bug** (**F6**) · vote event log
with duplicate/invalid flags and CSV · mission simulator, `is_test` +
`cyclestart`, v2 seeder · new-account vote-buying gate · kids accounts after
legal review · moderation, IP/spam blocking, the real content classifier ·
a record of commit history.

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
| **F13** | A race missing from `/wallet/rows` (see F11) shows **live** Vote buttons, because the ballot only locks on `can_take_part === false`; the server then refuses. The ballot should treat "no row" as closed. | 2026-09-24 | P5 |
| ~~**F14**~~ | ~~At phone width the top bar overflows.~~ At ≤640px the five tabs pin to the bottom and hide while scrolling down (`ebx_shared.js` `bindNavScroll`, `ebx_frontend.css`). | 2026-09-24 | **P2, 2026-09-25** |
| **F15** | Legacy phase-2 rows carry `donated_ct = 0` after their ME closed (oce1 is one), so the **guaranteed pool reads 0** where the ladder says 10% is final. The overview reads the rows as booked — the same number `read_wallet` gives — so this is data, not display. | 2026-09-24 | P5 |
| ~~**F17**~~ | ~~The initiative ballot's head printed the cause cadence ("decision Sep 22") over an election that closes Nov 10; its own topbar was right.~~ Reads the election's T now. | 2026-09-24 | **P1, 2026-09-24** |
| **F16** | The landing trios link `mission.html?research=…` and `?budget=…`; the mission page ignores both params. | 2026-09-24 | P3 (preselect from the link) |

## 5. BACKLOG

*Named, not queued. Reorganize freely during a pass; do not build.*

**Home feedback 1**
- The time span below the annulus is wrong - it should be true to the cause that is selected (from top card phase start to last card phase end)
- The ray-out display doesn't look great here. I'd rather have a line connecting the center of the sector with the center of the side of the election card.
- The top card needs to be titled something other than a giant <cause>.
- We can remove the cause title with the phase description that is below the annulus.
- Vetting posts must target an organization.
- The 3 'the network' things aren't meant to be toggles- they are meant to describe to the user how the system works as a whole... It might be best to put these in between the 5 phases and the top card.
- Each post should be connected to a mission as well - should have a link - "Go to mission"

**Other**
- Okay, the bots posted some cases, which are ties to future initiative elections... I need these posts to also be available on the mission page. 
- The footer needs an about - justification and also an about - what we do and also an about - how it works and a lot of differetn but related stuff. 

- The org nomination and Initiative nomination should not require you to make a case, it should be optional.
- Replace money model in white paper with my document.

**Mission**
- The post-support ring (annulus layer 1) returns inside the **framing** and **exchange** phase panels — review 2026-09-24. `GET /missions/{id}/post-support` is unchanged.
- The allocations panel moves to the profile page (review 2026-09-24; `unallocInnerHTML` is ready to mount).
- The ME table's Cause column is redundant now that the table is one cause's — drop it or make it the proposer.
- Mission gantt chart / annulus ring widget (deadlines, 7–12 steps).
- Tune step guaranteed/potential pool ratios + early-resolution bonus size.
- Tune `resolution_value_bump` and its relation to the global coin value.
- Progress reports: org report vs. the Earthbux News parallel report, benefactor-moderated — the org report faces B · I · A.
- Mission member communication channel.
- Tables inside missions (the same data News can produce with filters).
**Mission review 3**
- The story area should be different before the initiative is elected - it should be toggleable by initiative (or cause). The report only starts upon initiative election.
- The active phase should be highlighted in the toggles.
- It needs to be more clear that the mission navigator is a mission navigator. Title it 'Select any mission in <cause>'

- Now it's time to really grind out these ballot panels.

- Bug - the initiative election table is not always showing the right thing. Sometimes it shows the cause table (when I navigate from p1 to p2) and otherwise it shows all the initiatives, not filtered by cause. They should always be filtered by cause even upon initial opening of the page.

- Every post in missions has an underlying news thread. The report is a conglomeration of many posts, so it is seperate, but it has leading contributors (the highest rated threads in each category, and highest rated budget items.)

*Step descriptions*
- We have 'reason' and 'process' - how about 'What is a cause' and 'How this phase works'
*Cause*
If the same cause wins 6 weeks in a row, it replaces the old initiative for all future missions.


**News**
- The corner annulus — News is the only page without the large one; the corner one reflects the status of the mission of the post being viewed.
- Learn from: Meta, LinkedIn, Reddit, TikTok; fantasy sports, Polymarket, Strava, Duolingo, stock investing, GitHub.

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

**Side cards**
- Per-phase card locations (2 of 5 done) — when cause voting starts, when budget day is, which framing week matters.



**Bots** *(2026-09-25 — gathered here from where the notes had scattered: the
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

**Unrelated items**
- Footer
- I'm thinking that a phase 6 may include the rewards and travel opportunities.

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

## ARCHIVE

*Finished pass reports. Nothing here is executed.*

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
