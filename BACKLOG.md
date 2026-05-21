# Earthbucks -- Backlog
## Changelog
- **2026-05-15** -- Fixed main page alignment. Logged notes on wildlife chart, propose-login bug, and cycle model.
- **2026-05-15 (auto)** -- Three bugs fixed. Repaired silent corruption in `frontend/src/ebx_shared.ts` (duplicate tail after build sentinel was blocking all TS builds).
- **2026-05-19 (auto, audit-only)** -- No code changes. Diffed README structure vs BACKLOG and code. See archived notes below.
- **2026-05-19 (auto, pass 4 -- audit-only)** -- No code changes. Confirmed README truncation, cause.html handler deletion, ebx_shared.ts regression, and trailing-whitespace garbage. Full details in previous BACKLOG versions.
- **2026-05-19 (auto, pass 5 -- BUILD)** -- First real build pass. See "What shipped" below.

## What shipped in pass 5
1. **Restored corrupted files** -- README.md (was 49 lines / truncated, restored to 188), cause.html (propose-initiative POST handler was deleted, restored). Both recovered from HEAD via `git show`.
2. **Fixed ebx_shared.ts regression** -- Duplicate `missionStrip()` + second `EBX_TAIL_SENTINEL` stripped. File cleaned from 1658 lines to 1598, then extended cleanly to 1841 with new functions.
3. **Fixed trailing whitespace** -- Stripped from index.html, mission.html, profile.html, resources/js/ebx_shared.js.
4. **Renamed feed.html -> en.html** -- All cross-page hrefs updated (cause.html, index.html, mission.html, profile.html, ebx_shared.ts). en.html title updated to "Earthbux News (EN)". Footer nav link updated to "EN".
5. **New index.html layout** -- Implemented first batch of index.html changes per README:
   - Removed `#ebx-election-banner-mount` from top-bar center slot (tether line also removed).
   - Top-bar is now 2-column (tagline | user badge).
   - Center column now stacks: **top card** (dual org-election panel) -> **annulus** -> **bottom banner** (upcoming initiative decision).
   - Side cards switched from `raceCard` to new `sideCard` format: Initiative section (leader, x% EBX, Contribute link to cause page, total pool) + Organization section (leader, x% votes, Contribute to mission page, total pool) + "No votes yet" fallback.
6. **New TS functions** -- Added `sideCard(causeIndex)`, `upcomingCauseBanner(activeIndex)`, `topCard(activeIndex)` to `ebx_shared.ts` and exported via `EBX` object.
7. **Backend schema changes (all confirmed by Jax in pass 2/3)**:
   - `Organization.logo_url: Optional[str]` added
   - `Initiative.logo_url: Optional[str]` added
   - `BenefactorAccount.vvv: bool` added (vote-verified visual flag)
   - `Vote.org_id` made nullable (soft initiative votes don't need an org pick)
   - `Vote.share: float` added (default 1.0, min 0.1 enforced in schemas.py)
   - `size_factor: float` added to `config.py` (default 1.0, override via env var)
8. **Alembic migration** -- `b1c3e2f4a9d7_may19_schema_additions.py` created and applied to earthbucks.db.
9. **schemas.py** -- `OrganizationRead`, `InitiativeRead`, `VoteCreate`, `VoteRead`, `BenefactorRead` updated to include new fields. `VoteCreate.share` validated >= 0.1.

- **2026-05-20 (auto, pass 6 -- BUILD)** -- Q18/Q21/Q22 + now-marker arrow + founding-bonus seed. See "What shipped in pass 6" below.
- **2026-05-20 (auto, pass 7 -- BUILD)** -- Q20/Q21 corrected + now-marker arrowhead fixed. See "What shipped in pass 7" below.
- **2026-05-20 (auto, pass 8 -- BUILD)** -- Q1 top-card-into-topbar + content fix + global now-marker. See "What shipped in pass 8" below.
- **2026-05-21 (auto, pass 9 -- BUILD + audit)** -- Build-seq #1 top-card duplicate-initiative fix (staged in TS), #1 bottom-banner alignment (live), #3 vote-share annulus cases (live). Now-marker #2 verified already-correct (no change). **Diagnosed a Windows-mount truncation fault that very likely answers Jax's "why do updates take a long time to ship" question.** JS rebuild deliberately deferred -- see "What shipped/staged in pass 9" below.

## What shipped in pass 6
1. **Pre-commit hook (Q18)** -- `.git/hooks/pre-commit` now blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL`. Tested against clean file (passes) and a doubled file (fails with clear message).
2. **topCard() redesigned as 1-row (Q21)** -- Replaced the tall 2-pane block with a compact 2-row ticker: Row 1 = upcoming cause dot + name + leading initiative title + org leader + Vote button + countdown. Row 2 = later cause name + leading org %. Immediately scannable, no multi-line blocks.
3. **Annulus expanded + side cards fill columns (Q22)** -- Annulus grew from 420px → 460px (top-card and bottom-banner matched). `sideCard()` changed from `width:248px` to `width:100%;box-sizing:border-box` so cards fill their `1fr` columns at all widths. Responsive breakpoints updated: compress at 1160px, collapse side cards at 980px.
4. **Now-marker direction arrow (cause.html)** -- Small clockwise arrowhead rendered ~18° ahead of the now-marker dot on the initiative annulus. Label updated to "now ↻".
5. **Founding-bonus mission seeded** -- Added `seed_founding_bonus()` to `backend/seed/seed.py`. Creates sentinel org (`ebx-internal`), initiative (`founding-bonus-init`), and mission (`founding-bonus`) so `crud.create_benefactor` can mint 49 EBX to the first 100 signups. Run `python -m seed.seed` from `backend/` to apply. - will do when becomes necessary
6. **JS rebuilt** -- `resources/js/ebx_shared.js` rebuilt from updated TS (64.4 kb, clean). Null-byte padding artifact from Windows mount stripped.

## What shipped in pass 7
1. **topCard() corrected (Q20)** -- Pass 6 had incorrectly implemented `topCard()` as a 1-row upcoming-cause ticker. Reverted to correct design per STRUCTURE.md: 2-column panel showing the **active cause's** two org elections (left = "This week", right = "Newest / ~7 weeks away"). Each pane shows org leader + vote-share bars + pool size + election date + Vote button. Header strip shows cause name + color dot. No top border-radius so it connects flush to the topbar.
2. **upcomingCauseBanner() corrected (Q21)** -- Replaced broken string-concatenation (`''` double-quote artifacts) with clean template literals. Now renders as a proper 1-row `<a>` tag: cause dot → "Up next: CAUSE-NAME" → leading initiative title (flex:1, truncated) → org leader % → pool size → Vote date+countdown button. Colored by the next cause (activeIndex+1 mod 7).
3. **cause.html now-marker arrowhead fixed** -- Replaced the malformed 3-point path (was rendering a confusing asymmetric hook) with a clean symmetric V-shape. Tip points clockwise along the ring. Uses tangent vector (`-sin`, `cos`) for correct orientation at any marker position.
4. **JS rebuilt** -- `resources/js/ebx_shared.js` rebuilt clean (67.7 kb). Build passes with zero errors.

## What shipped in pass 8
1. **Top card header into topbar (Q1)** -- Topbar restyled as 3-column grid (`1fr auto 1fr`). Center slot `#ebx-topcard-header-mount` (width: 460px) hosts `topCardHeader()`: cause color dot + cause name + "Organization Election" label, rendered as a rounded-top card strip that sits flush at the topbar bottom border. Topbar has `overflow: visible` and bottom padding removed so the strip extends downward seamlessly into the top card body.
2. **Top card body stretches to fill (Q1)** -- Hero `padding-top` removed. `.hero__top-card { flex: 1; min-height: 80px }` so the body grows to fill all space between topbar and annulus. `.hero__layout { align-items: stretch }` so side cards dictate the column height. Bottom banner stays at the natural bottom of the center column, aligned with side card bottoms.
3. **Top card content fix (BUILD item 1)** -- Both panes now lead with the **initiative title** (large, bold) instead of the leading org. Org vote-share bars follow below. Vote button links to `m_indx.html` (org votes belong there, not on cause.html).
4. **`topCardHeader()` added and exported** -- New function in `ebx_shared.ts`, exported on `EBX` object. Renders the topbar strip for a given active cause index.
5. **cause.html now-marker: global cycle position** -- Replaced per-cause `1 - msUntilDecision/cycleWindow` formula with `((Date.now() - cycleStart) % cycleWindow) / cycleWindow`. Marker now shows identical position regardless of which cause is selected on cause.html.
6. **JS rebuilt** -- `resources/js/ebx_shared.js` rebuilt clean at 67.9 kb.
7. **Mobile fallback** -- At ≤980px, `ebx-topbar__center` is hidden and hero gets `padding-top: 10px` restored. Top card body renders standalone with its own border styling.

## What shipped/staged in pass 9

### LIVE NOW (edits to directly-served files — no build needed)
1. **Bottom-banner alignment (build-seq #1, "Align bottom card").** `index.html` CSS. The top card no longer grows to fill space (`.hero__top-card` changed `flex:1` → `flex:0 0 auto`). The flexible space now sits *above* the banner (`.hero__bottom-banner { margin-top:auto }`), so the banner drops to the bottom of the center column (height-matched to the side cards via `align-items:stretch`) while the annulus + top card are pushed up toward the topbar — exactly the inversion Jax asked for ("push the top card upwards"). NOTE: the banner only visibly lines up with the side-card bottoms when the side cards are at least as tall as top-card + annulus + banner. With the current 460px annulus the center column is the taller element, so true bottom-alignment depends on the "side cards at max size" work (Q22). Flagged below.
2. **Vote-share annulus 0%/100% cases (build-seq #3).** `cause.html` `buildAnnulusSVG()`. Previously branched on *proposal count* and ignored the (computed-but-unused) `hasVotes` flag, so a cause with 2+ proposals but no votes drew a misleading even pie. Now branches on the number of initiatives **with votes** (`ebx_committed > 0`): 0 proposals → "No proposals"; proposals but 0 votes → "No votes yet · N proposals"; exactly 1 voted → drop pie, show "100% · sole front-runner" + leader; 2+ voted → normal pie divided by vote share (unvoted proposals get a 0-width slice). This is inline JS in cause.html, so it is already live.

### STAGED IN SOURCE (needs a JS rebuild to go live — see mount issue below)
3. **Top-card duplicate-initiative fix (build-seq #1, "Answer top card question").** `frontend/src/ebx_shared.ts`. Added `Votes.initiativesForCause(causeIndex, cycleNum, inits)` and used it in `topCard()` with `cycleNum` for the "This week" pane and `cycleNum+1` for the "Newest" pane. Verified type-clean (`tsc --noEmit` exit 0) and build-clean (esbuild, 68.8kb, 1 sentinel) against a host-equivalent reconstruction. **Not yet built into `resources/js/ebx_shared.js`** — see "Mount truncation" below.

   **Answer to your top-card question (you asked me to "let you know"):** it is *both* sample data and code.
   (a) Every initiative in `data/causes/initiatives.json` has `committed_ebx: 0` (checked: 26/26). So sorting "leader by EBX committed" is a tie for every cause and just returns the first array element.
   (b) Both panes filtered the *identical* set (`config.initiatives.filter(cause_index === activeIndex)`) and sorted it the same way, with no per-cycle dimension — so they always collapsed onto that same first initiative.
   My fix breaks the tie deterministically per-cycle (so "This week" and "Newest" surface different leaders) **while still letting real `committed_ebx` win the moment it is non-zero.** The proper long-term fix is real per-cycle data: record which initiative actually won each cycle's initiative vote, and key each org-election pane off that. The per-cycle tie-breaker is a clearly-labelled placeholder until then.

### VERIFIED, NO CHANGE
4. **Now-marker (build-seq #2).** You said "better, but still wrong — the correct marker will be in the same location around the circle no matter which cause is selected." I checked pass-8's formula and it already satisfies that literal property: `cycleFraction = ((Date.now() - cycleStart) % (49d)) / 49d` contains **no `cause.index` term**, so the marker's angle is identical for every selected cause. I also confirmed it points at the *active* cause: for today (2026-05-21) elapsed=140.5d → weekNum 20 → active cause index 6, and the marker lands at sector 6.07. Both correct. I did **not** change it, because a speculative edit would risk regressing a now-correct behavior. If something still looks off, it's probably one of these — please pick one (see question below).

### ASSESSED ONLY (sequenced/blocked — no change this pass)
5. **m_indx.html (build-seq #3, second item).** Already substantially built (table, expandable rows, ring-minis). Explicitly sequenced *after* the cause.html reshuffle, so left as-is.
6. **Voting separation (build-seq #4).** Schema already supports it: `Vote.initiative_id` (required), `Vote.org_id` (nullable — NULL for soft initiative-only votes), `Vote.share` (default 1.0, min 0.1). `POST /initiatives/{id}/vote` + tally exist. What's still missing is the dedicated org-election-phase vote flow/UI (the m_indx side). Larger feature — recommend its own pass.
7. **Founding 49-EBX credits (build-seq #5).** Already fully coded: `crud.py` mints 49×1-EBX for `benefactor.id <= 100` when the `founding-bonus` mission row exists; `seed/seed.py:seed_founding_bonus()` creates that sentinel. Still only blocked on *running* the seed (Q1 below).

## ⚠️ Mount truncation — likely answer to "why updates take a long time to ship"
While building this pass I hit concrete evidence of an intermittent **file-sync truncation** between the Windows files and the Linux build sandbox:
- After editing `frontend/src/ebx_shared.ts`, the Windows/host copy was complete and correct (1850 lines, exactly 1 `EBX_TAIL_SENTINEL`, all edits present).
- The sandbox/mount copy had my edits **but was truncated mid-`missionStrip()`** — missing the final ~33 lines (the whole `EBX` export object *and* the sentinel), with its mtime frozen at the previous day. A second host edit did not dislodge it; the mount stayed stale.
- The sandbox `.git/index.lock` was also un-removable ("Operation not permitted").

This matches your symptom exactly: a file that is briefly broken right after an update (a half-written/truncated artifact is being served) and then "fine in the morning" once the sync finishes. It's also consistent with this project's past "silent corruption" / "null-byte padding from the Windows mount" notes. **Because of this I deliberately did NOT rebuild `resources/js/ebx_shared.js` this pass** — esbuild reads the (truncated) mount source and, worse, writes the bundle *back* through the same flaky mount, so a rebuild right now could land a truncated JS bundle on the live site and break it. The current served `resources/js/ebx_shared.js` is the intact pass-8 build (69,533 bytes, ends cleanly), so the site is healthy; the top-card fix simply isn't live yet.

**To ship the top-card fix:** run `npm run build` in `frontend/` **on the Windows side directly** (no Linux mount in the loop), or trigger a build once the mount is confirmed consistent. The source is ready and verified.

**Suggested mitigations (your call):**
- Add a post-build integrity check to the `build` script: after esbuild, fail if `resources/js/ebx_shared.js` doesn't end with the expected IIFE close / is under an expected byte size. Pairs well with the existing pre-commit single-sentinel hook.
- Treat "edit on Windows, build on Windows" as the rule; use the Linux sandbox only for read-only checks (tsc/lint), never for writing the shipped bundle, until the sync fault is fixed.

## Open questions for Jax
- **Q1 -- founding-bonus seed.** Run `python -m seed.seed` from `backend/` to create the sentinel mission. Cannot run from sandbox (SQLite on Windows mount is read-only from Linux).
- **Q2 -- now-marker, what specifically is wrong?** Pass-8's marker is already cause-independent and points at the active cause (verified above). If it still looks wrong, which is it: (a) you want it consistent with `index.html`, where "now" is always pinned at 12 o'clock and the *wheel* rotates the active cause to the top (cause.html currently keeps the wheel static and moves the marker instead); (b) the rotation **direction** is wrong (it currently advances clockwise, matching index.html's apparent motion); or (c) something else? Tell me which and I'll implement it precisely.
- **Q3 -- top-card per-cycle placeholder OK?** My tie-breaker invents a deterministic "different leader per cycle" only while `committed_ebx` is all-zero. Fine as a stopgap, or do you want the panes to stay identical until there's real per-cycle winning-initiative data?
- **Q4 -- top-card JS not live yet.** The top-card fix is staged in `ebx_shared.ts` but needs a Windows-side `npm run build` to reach `resources/js/ebx_shared.js` (see mount note). Want me to attempt the rebuild next pass if the mount looks healthy?

## Build & dev tooling
- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke.
    - [ ] **Current strat** Me and my cofounders will each create a few accounts with simulated money. We will use real initiatives (probably the ones already in use) and simulate organizations (also probably the ones already in use). We will start with the first 7 initiative votes, and hopefully after those first 7 weeks we'll have the mission page locked in and be ready for the first organization votes.
- **Note on tsc/typecheck:** `tsc` is not on PATH, but the local binary works: `node node_modules/typescript/bin/tsc --noEmit` from `frontend/` (used for verification in pass 9, exit 0). `npm run build` also serves as a type+syntax check. Caveat: both read through the Linux mount, so run them on Windows (or after confirming the mount is in sync) to avoid checking a truncated copy — see the mount-truncation note above.

## Infra
- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only.
- [ ] **cycleStart from API.** Currently hardcoded in ebx_shared.ts -- should come from a config endpoint so it can change without a rebuild.

## Phone and other
- [ ] **Static off-line mode** Create an offline-mode that saves the current state of the project as an example so that I can download it on a hard drive and demonstrate it for someone without needing server access.
- [ ] **Swift** Create mobile version.
