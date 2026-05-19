# Earthbucks — Backlog
Things were getting out of hand so I reverted...

## Changelog
- **2026-05-15** — Fixed main page alignment (see below). Logged notes on wildlife chart, propose-login bug, and cycle model.
- **2026-05-15 (auto)** — Three bugs fixed (see notes below). Also repaired a silent corruption in `frontend/src/ebx_shared.ts` where duplicate code had been appended after the build sentinel — this was blocking all TS builds.
- **2026-05-19 (auto, audit-only)** — No code changes. Diffed README.md structure tree vs BACKLOG.md and current code. See "Notes from 2026-05-19" section below for conflicts, suggested structure-tree edits, and questions for Jax.
- **2026-05-19 (auto, pass 2 — audit-only)** — No code changes. Re-read the (further-expanded) README after Jax's May 18 edits. Several questions from the morning pass are now resolved by README phrasing; several net-new items appeared. See "Notes from 2026-05-19 (pass 2)" below.

## Notes from 2026-05-19 (auto) — README ↔ BACKLOG audit

This run made no code edits. Goal was to compare the (much-expanded) README structure tree against BACKLOG and the actual codebase, and surface anything that needs your attention. README is treated as the canonical structure tree, BACKLOG as the live working doc.

### Conflicts between README and BACKLOG that need resolution

1. **"EN" vs "newsfeed" rename.** README says: *EN Newsfeed → Rename everything to EN (Earthbux News)*. BACKLOG (line ~50) says the opposite: *NEWSFEED → Rename feed everywhere to newsfeed*. These can't both be right. README also self-conflicts: the cause-page feed filter is labeled *"Filter Newsfeed"* even though the parent section says rename everything to EN. **Question for Jax:** is the canonical name **EN** (with full name *Earthbux News*) everywhere — including the filter label, the page filename, and the in-app strings? If yes, BACKLOG's "Rename feed everywhere to newsfeed" should be deleted and README's "Filter Newsfeed" should be retitled "Filter EN".

> This is a bit complex.

2. **Vote-weight formula changed in README.**

3. **Newsfeed inconsistency in README itself.**

### New things in README that aren't yet reflected in BACKLOG or code

These are README items that have no corresponding BACKLOG task and aren't implemented. Listing so they don't fall through the cracks:

- **Main page → Cause Cards → Top card.** Largest card, horizontally between side cards and vertically from now-marker to top. Right pane = newly-elected initiative + org + pool size + election date + current org vote. Left pane = detail metrics for the org election being decided this week (leaders with links to mission-page prototypes, EN-feed link, votes/commitments). Current `index.html` has only generic `hero__left` / `hero__right` panels and a center annulus mount — no "top card" concept. This is a sizable layout restructure.
- **Main page → Cause Cards → Bottom banner.** Existing banner needs to be relocated to directly below the annulus, between the left and right cause cards, recolored to the cause-after-active-cause, and used to display upcoming-initiative-decision metrics.
- **Main page → Cause Cards → Side cards.** Two stacked sections per side: *Initiative* (leader · x% · Contribute → links to cause page, total pool) and *Organization for [initiative]* (leader · x% · Contribute → links to org's mission page, total pool). Show "No votes yet" when empty.
- **Cause page → Right cards** with three slots: Bottom = previous mission + status, Middle = active mission + status, Top = upcoming org election with initiative name and current org pick. Not present in code or BACKLOG.
- **Cause page → Initiative Table** with explicit columns: Name | Rating | Proposed-by | Credit (cause-color dot placeholder) | Pool share %. BACKLOG has no row-for-row spec.
- **Cause page → Initiative annulus → Mission Progress annulus.** A *third* tier around the outside that tracks mission metrics, surrounding the inner two sections. Backlogged in README until mission progress interface is built — flagging here so BACKLOG carries it too.
- **Cause page → Handle when 1 or 0 initiatives have votes.** If only 0 or 1 initiatives received votes, drop the pie chart and indicate the case in the middle of the annulus. (We already special-cased `n===1` for the wildlife chart label position on 2026-05-15 pass 2; this is a broader requirement.)
- **Mission Index page (`mission_index.html`).** README says: *"REPLACE Initiatives.html with mission_index.html and Initiatives.html can be deleted."* Status check: there is currently no `Initiatives.html` (already gone) and no `mission_index.html`. So this is a net-new page to build. 
- **Multi-initiative vote division floor.** README adds: *"Benefactors can not divide votes smaller than 0.1."* Enforce this in the upcoming Commit dialog (Initiatives → Committing UX in BACKLOG).
- **MEMBERSHIPS / HUMAN security layer.** README adds a HUMAN classification: *"Any user of the app is verified to be a human or the authorized AI agent of Earthbux or an authorized organization."* Today the backend has `BenefactorAccount`, `Organization`, `Membership` — but no notion of human-verification or an authorized-AI-agent principal. **Suggested BACKLOG task:** decide whether this is a new column on `BenefactorAccount` (`verified_human: bool`, `principal_type: 'human'|'ebx_agent'|'org_agent'`) or a separate `Principal` table. Probably the simpler column approach for now.

- **Organization logos / Initiative logos as halves of the credit coin.** super backlog
 use the rgb color wheel with green=ebx_contribution r=org b=benefactors. This will be the animation in the middle of the cause annulus.
 Each of the other annuli will have a way of combining their colors. 
I'm really experimenting deep here, but this type of visual interface could be illuminating.
Every vote you contribute a color.
Color is automated by our means but users can easily change their color choices.
This idea will change as do most super-backlogged items.
### Suggested README structure-tree edits (since I can't edit README directly)

If you agree with the below, please make these edits to `README.md` yourself:

1. **Resolve EN/Newsfeed.**
2. **Clarify EN-cut thresholds.**
3. **Fix "newly elected initiative" phrasing in Top card.**
4. **Add Mission Progress annulus to a top-level Mission Index section.** 
5. **Bottom banner relocation note.**
6. **Naming: "mission x-8" not "cause x-8".** You already corrected me on this in BACKLOG (Cycle / process modeling note). Suggest threading the same naming into README — e.g. "Org decision week (week N+8 for **mission** X)" rather than "cause X".

### Open questions for Jax (consolidated)

- **Q1 (EN rename):** Confirm canonical name is "EN" / "Earthbux News" everywhere. Should `feed.html` be renamed `en.html`? (or keep the route, just relabel UI?)
- **Q2 (Vote-weight formula):** Confirm the new `1 + b_contribution / (total_pool_not_including_b * n_total_votes)` is canonical. The `n_total_votes` denominator is new — was it intentional?
- **Q3 (EN cut threshold semantics):** Tiered by total pool or by individual donation amount? Evaluated when?
- **Q4 (mission_index.html):** Build this as the next major piece, after the cause-page top-card / bottom-banner reshuffle? Or before?
- **Q5 (HUMAN verification):** Add as columns on `BenefactorAccount` for now (`verified_human: bool`, `principal_type: enum`), or hold off until we know what the AI-agent principal pattern needs?
- **Q6 (Top-card "banner"):** Which DOM element is the "banner" being relocated? Best guess: the `mission-strip` band on `index.html`. Confirm before I move it.
- **Q7 (Initiative logos):** Add `logo_url` to `Initiative` mirroring `Organization.logo_url`, with cause-color emoji-initial placeholder until upload — sound right?


## Notes from 2026-05-19 (pass 2, auto) — README diff since pass 1

No code changes this run. The README grew between pass 1 and now (mtime jumped May 18 21:40); below I record what the new wording resolves, what's net-new, and what should land in BACKLOG so it doesn't disappear.

### Previous open questions that are now (effectively) answered by README

- **Q5 — HUMAN verification.** README now reads literally `**HUMAN** \n backlog security questions` and the parent `**Security**` task says *"For now all posts, initiatives, org inputs, votes, commits, etc will automatically be valid and public. Protect in future (from both sides)."* → Treat as **deferred**. Don't add `verified_human` / `principal_type` columns yet. Close Q5.
- **Q3 — EN cut threshold.** README now says *"EN Thresholds: We only take money if the pool is above $100."* → Threshold is on **pool size**, not per-donation. Evaluated at pool-lock (24h before selection). Close Q3 with that interpretation unless you disagree.
- **Q1 (partial) — EN rename.** README is now self-consistent on **EN / Earthbux News**: feed/sidebar filter is just labeled "Filter", and the section is titled "EN Newsfeed". Only loose end is the **filename** — see Q1' below.

### Net-new items in README since pass 1 (not yet in BACKLOG, not yet in code)


6. **Initiative logos as ½ of credit coin.** Mirrors `Organization.logo_url` on the Initiative side. Today's `Initiative` (models.py 158-209) has no `logo_url`. → Backend schema change.
7. **Coin generation trigger.** *"Coins and mission are created when org is elected."* Backend needs an `on_org_election_win` hook that mints the `Mission` row + an initial batch of `CreditCoin` rows. Not implemented.
10. **Mission Progress annulus = third tier on the cause page.** Backlogged in README until the mission-progress interface is built. Carry forward.
11. **Coin geometry spec.**
12. **RGB color-wheel coin/annulus animation.** Super-backlog (red=org, green=ebx, blue=benefactor). Carry forward from pass 1.
13. **Mission Annulus = 7–12 step linear flow.** *"Deadlines. Budget submission, beneficiary approval/outreach, issue resolution, Earthbux check-ins. Will increase in complexity. 7–12 steps which can just be labeled 1–12 and will all link to the mission page."* New concrete spec; not implemented. Missions will be divided in this way.
14. **Now-marker should live on the cause-page initiative annulus, not on index.** README explicitly says: *"Additional marker incorrectly on this page needs to be relocated to the initiative annulus."* Worth checking — the 2026-05-15 pass-2 changelog added the "now" glowing line *to* the cause wheel on index. Confirm that's what was meant, or whether the marker now needs to be moved off `index.html` to `cause.html`. → Q11.
> There should be markers on both annuli. they each indicate the current date and time for their respective pages.

### Code-state observations relevant to README

- **HTML files are at project root**, not under `frontend/`: `index.html`, `cause.html`, `mission.html`, `feed.html`, `profile.html`, `about.html`. Frontend TS source still lives at `frontend/src/ebx_shared.ts` and builds to `resources/js/ebx_shared.js`. README doesn't describe the file layout; not a problem, just noting.
- **`mission_index.html` still does not exist.** README references it in multiple places (Profile → Choices_Table = "Snippet of mission index"; main page side-cards link into it; mission-index is its own top-level section). Net-new page. Pass-1 question Q4 (build mission_index before or after the cause-page reshuffle?) is **still open**.
- **`Organization` model has no `logo_url`.** Carrying forward from pass 1.
> Unite logos with color wheel
- **No `Initiative.logo_url` either.** New consequence of README changes.
> Unite logos with color wheel
- **`Vote` model exists** (models.py 370–384) with `benefactor_id`/`initiative_id`/`org_id` unique-keyed per (benefactor, initiative). Good — there is somewhere to hang the 0.1-division and `n_total_votes` logic. But no fractional-vote column; today a Vote row is binary. Multi-initiative vote-share will need a `share: float` column or a separate `VoteShare` table.
> Great, lets enable fractional voting.
- **README ends mid-thought.** Last bullet is `- [ ] **1/16 to evaluation**` with no description. Looks truncated. → Q12.

### Suggested README structure-tree edits (since I can't edit README)

If you agree, please apply to `README.md`:

1. **Define `size_factor`** in the vote-weight section. Even a one-line "(constant TBD, used to dampen large pools)" would unblock implementation.
2. **Finish the trailing `1/16 to evaluation` bullet** — what's the payout mechanism, who decides "Helpful", over what window.
3. **Clarify donation-threshold scope.** Is `$20` the threshold for initiative-side logo colorization, org-side visibility, or both?


6. **Add a Mission Index file note** confirming `mission_index.html` is net-new (no Initiatives.html legacy to delete; pass-1 README said "REPLACE Initiatives.html" but that note has since been removed — wanted to confirm it was intentional removal, not editing accident).

### Open questions for Jax (refreshed)

- **Q1' (EN filename):** Rename `feed.html` → `en.html`, or keep filename and only relabel UI?
Rename
- **Q4 (mission_index.html):** Build before or after the cause-page top-card / bottom-banner restructure?
After
- **Q6 (Top-card "banner"):** Still pending from pass 1. Which DOM element on `index.html` is the "banner" being relocated below the annulus? Best guess remains the mission-strip band.
election banner is labeled in index.html. it's the one currently being pointed to by the original (index) glowy white now marker.
- **Q7 (Initiative logos):** Add `logo_url` to `Initiative` mirroring `Organization.logo_url`, with cause-color placeholder until upload?
Yes, they each have this identifying information
- **Q8 (size_factor):** What is `size_factor` in the vote-weight formula? Constant? Function of pool size? Per-cause?
added
- **Q9 (49-EBX bonus):** Startup hook on signup (if `id <= 100`) or a one-time admin script after the first 100 register?
id
- **Q10 (donation thresholds):** Is `$20` the initiative-side threshold, the org-side threshold, or both? Same number for both, or two configs?
must be the total contributions to pool after active period (org election)
- **Q11 (now-marker location):** Keep the white "now" line we added on `index.html`'s cause wheel, or move it to `cause.html`'s initiative annulus (and leave the index wheel marker-less)? 
Index.html already had a line. Now cause.html needs a now marker that will rotate once per 7 weeks and indicate the time difference to the next iteration of the selected cause. 
- **Q12 (trailing bullet):** What's the rest of the `1/16 to evaluation` bullet — payout mechanism, judging criteria, timing?
That'ss be backlogged for now. good questions.
---

## Cause Page
- [ ] **Page design**
Good for now.
EBX                                                                        profile
___Leading initiatives___  [cause] decision - [date] ___Past, present, future    ___
|                        | Select upcoming mission*  |                             |
|________________________|       Cause               |_____________________________|
                                 Wheel**                                                         **see cause wheel item
   ____________________________________________________________________________________       
   - Selected initiative area - Remove the numbered "click to jump" section
   Flows seamlessly into feed - ONLY posts directly related to selected initiativwe
   If no initiative is selected display all feed info for cause
   Remove header from feed section for clean flow from initiative above
Vote for x - Commit donation - contribute to the discussion
   _____________________________________________________________________________________
   __________________________Initiatives table__________________________________________
Search                                                         Propose an Initiative

   And the bottom section contains more detailed information about the initiative, including ratings, posts/comments/user feedback, history (it might have been edited/improved), budget, org backing, etc.


## Profile / accounts
- [ ] **UI/UX**
Good 4 now.
EBX                                                Profile badge        
   _____  _______________________________________     ______________
   | a  | |_________________b____________________| |       d      |   
   |____|                                          |              |  
   | c  |                   e                      |              |
   |____|                                          |______________|

a. Same handle-card as current 
b. [Upcoming Cause] - [User initiative choice] - [ebx committed] - [timer countdown] | [Upcoming Initiative] - [User organization choice] - [ebx committed] - [timer countdown]
c. wallet - remove the ebx balance, replace with the credit portfolio because it is the same thing. Benefactors will be able to click on each credit coin to see their stake in that mission.
d. Table with the user choices for each cause. Toggle between initiatives and organizations, linked to the cause (initiative) or mission (organization) page.
e. History of feed content posted by the user.
- [ ] **Security** For now all posts, initiatives, org inputs, votes, commits, etc will automaticaally be valid and public. 
    - [ ] **Protect in future. (from both sides)**
    org affiliations/members


## Build & dev tooling
- **TS build was silently broken (fixed 2026-05-15 auto).** The file `frontend/src/ebx_shared.ts` had duplicate corrupted code appended after the `// EBX_TAIL_SENTINEL` line — a second copy of the tail of `missionStrip()` and the `EBX` namespace object. esbuild failed with a syntax error (`Expected ";" but found ":"`) at line 1551. The sentinel grep check still passed (it was present twice), so the error only appeared when actually running `npm run build`. Cleaned up by truncating to line 1549.

  > **How to rebuild after any future JS edits, Jax:** From the `frontend/` folder, run `npm run build`. If you see `✘ [ERROR]` output, the TypeScript source has a syntax problem. You can also run `npm run typecheck` to catch type errors without building. The output always goes to `resources/js/ebx_shared.js`.
>> earthbucks-frontend@0.2.0 typecheck
> tsc --noEmit

'tsc' is not recognized as an internal or external command,
operable program or batch file.

- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke. (Right?)
    - [ ] **Current strat** Me and my cofounders will each create a few accounts with simulated money. We will use real initiatives (probably the ones already in use) and simulate organizations (also probably the ones already in use). We will start with the first 7 initiative votes, and hopefully after those first 7 weeks we'll have the mission page locked in and be ready for the first organization votes.


## Infra
- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only. What does this mean?
- [ ] **cycleStart from API.** Currently hardcoded in ebx_shared.ts — should come from a config endpoint so it can change without a rebuild.


## Phone and other
- [ ] **Static off-line mode** Create an offline-mode that saves the current state of the project as an example so that I can download it on a hard drive and demonstrate it for someone without needing server access.
- [ ] **Swift** Create mobile version.