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

## Open questions for Jax
- **Q1 -- founding-bonus seed.** Run `python -m seed.seed` from `backend/` to create the sentinel mission. Cannot run from sandbox (SQLite on Windows mount is read-only from Linux).

## Build & dev tooling
- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke.
    - [ ] **Current strat** Me and my cofounders will each create a few accounts with simulated money. We will use real initiatives (probably the ones already in use) and simulate organizations (also probably the ones already in use). We will start with the first 7 initiative votes, and hopefully after those first 7 weeks we'll have the mission page locked in and be ready for the first organization votes.
- **Note on tsc/typecheck:** `tsc --noEmit` is not available in the sandbox (tsc not on PATH). Use `npm run build` as the type+syntax check instead.

## Infra
- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only.
- [ ] **cycleStart from API.** Currently hardcoded in ebx_shared.ts -- should come from a config endpoint so it can change without a rebuild.

## Phone and other
- [ ] **Static off-line mode** Create an offline-mode that saves the current state of the project as an example so that I can download it on a hard drive and demonstrate it for someone without needing server access.
- [ ] **Swift** Create mobile version.
