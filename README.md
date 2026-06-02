# Earthbucks — Backlog

Working memory for Claude. Top line = current state. Everything below is fair game for rework each pass.

> **State (2026-06-02, pass 19 — build):** Three P0 fixes landed this pass. (i) `cause.html` `renderElectionCard` dropped its `inPhase1 = state.causeIndex === cause.index` gate — every cause page now mounts the live phase-1 voting widget against its own next-decision cycle (was: 1/7). (ii) `index.html` table row-click is rebuilt as a delegated listener on `#init-table-body`; the broken inline `onclick="idxSelectInit(${JSON.stringify(JSON.stringify(init)).slice(1,-1)})"` was discarded — HTML attributes don't unescape `\"`, so the attribute terminated at the first internal quote and the handler never bound. Survives every `filterInitiatives()` rerender via `_ebxClickBound` flag. Watch ★ and website-cell anchors keep their own onclicks (the listener early-exits on `closest('button,a')`). (iii) `backend/seed/pilot.py` (new) stands up the pilot dataset: GameMaster as a real `BenefactorAccount`, 21 initiatives (Atm-Hpr 1001–1003) with backdated election dates, 21 orgs, mission rows for phase-3/4 tivs, GameMaster as sole voter (Contribution + Vote, share=1.0, committed=True), and every non-pilot sample initiative without committed EBX normalised to `status='suggested'`. Idempotent; entrypoint `python -m seed.pilot` from `backend/`. Top + side card build (P0 #4) is unblocked but not yet shipped — defer to pass 20.

> **Workflow clarification (carry-over)** STRUCTURE.md is design intent and stays mostly fixed between passes; INSTRUCTIONS.md is the per-pass build instructions; README owns state + the next-step backlog.

---

## 1. Current state — what's live

**index.html** (1704 host-side lines)

- Hero, annulus, page-mode toggle, 2-sided side cards (placeholders), initiative ↔ org table swap, Entity Card panel below the table, Propose / Register modals, info-tab default.
- **NEW (pass 19): row-click works.** Delegated listener at `_bindTableClickOnce(tbody)` runs once per page load, routes by `data-id` + `data-kind`, ignores clicks that originated inside a button or anchor. The Entity Card paints from the matched row's record in `_allInits` / `EBX.config.organizations`.
- Top card / topbar still pixel-misaligned. Top + side card front/back content is still placeholder — drawings are in (STRUCTURE.md roadblock 10), build-seq 2 is the next-up.
- Org-register section: removed from the page body, lives in `#org-register-modal-bg` (pass 15).

**cause.html** (2131 host-side lines)

- 7 cause tabs, annulus + now-marker, phase-1 election widget with sliders / floor / commit, propose modal, paged right cards.
- **NEW (pass 19): election widget mounts for every cause.** The `inPhase1` gate inside `renderElectionCard` was the diagnosis the README pass-18 predicted — removed. The `_causeDecisionMs` helper (pass 17) returns the correct next-decision date for every cause, so the widget reads decisions and `dayWord` correctly even when the selected cause isn't this week's active one. Behaviourally this means a benefactor visiting `cause.html?id=oceans` while atmosphere is in phase 1 still sees the oceans phase-1 voting widget pointing at oceans's next election.
- `_causeDecisionMs` off-by-one-week fix (pass 17) still in place.
- Best-effort `PUT /benefactors/me/votes` + `syncCauseTally` wired pass-16; localStorage still primary read.

**profile.html** — 3-card decision strip below upcoming-decision banner. Loads now that `/auth/me` is fixed.

**Backend** (FastAPI · SQLite dev)

- Schema (alembic `c7f2a4e8d0b1`): `Vote.cause_id`, `Vote.committed`, `Initiative.rating_avg/rating_count`, `BenefactorAccount.watched_initiative_ids` (JSON text), `initiative_ratings`.
- Routers: `votes.py` (`PUT /benefactors/me/votes`, `GET /causes/{id}/votes`, `POST /votes/commit`), `benefactors.py` (`GET/POST/DELETE /benefactors/me/watch[/id]`), `initiatives.py` `POST /initiatives/{id}/rate`.
- Server-side vote-weight formula `1 + b_contribution / (pool_excl_b * n_votes * size_factor)` is the single source of truth.
- `/auth/me` 500 fixed via `BenefactorRead.watched_initiative_ids` coercer (pass 17).
- Founding-49-EBX seed has run; sentinel mission row exists.
- **NEW (pass 19): `backend/seed/pilot.py`.** Run from `backend/`: `python -m seed.pilot`. Creates GameMaster, 21 initiatives, 21 orgs, mission rows for phases 3–5, and GameMaster votes. Re-runs are no-ops. Run *after* `python -m seed.seed` (needs causes loaded).

---

## 2. Imminent roadblocks

Ordered by Jax's stated priorities in STRUCTURE.md ROADBLOCKS + INSTRUCTIONS.md. **Bold P0** items block the cofounder pilot.

1. **P0 — Build top + side cards.** STRUCTURE.md ROADBLOCKS 10: drawings complete. Build-seq 2 is next-up. 4 layouts: top-front (next org election), top-back (this-week newest initiative), side-front (org election), side-back (initiative election). `--entity-color` + box-shadow halo on top card.
2. **P0 — Run the pilot seed end-to-end.** Seed entrypoint shipped this pass; needs `python -m seed.pilot` against the real dev DB plus an eyeball pass to confirm cause-page right-cards now show a non-empty default (paging through pilot phase-3/4 missions).
3. **P1 — Smoke-test the two pass-19 P0 fixes.** Per the post-mortem on pass 17, open `index.html` and click any row; open `cause.html?id=oceans` (or any non-active cause) and check the election widget mounts. If either regresses, flag before shipping pass 20.
4. **P1 — Entity table collapsible** (build-seq 3 per INSTRUCTIONS). Default open, noun toggle ("Initiatives / Organizations") — Q4 confirmed closed. CSS `details/summary` is enough; no JS state needed.
5. **P1 — Cause-page annulus election markers** (build-seq 4b). "Initiative election" / "Organization election" labels at the start and end of the cause's active arc. Lives in the now-marker render path.
6. **P1 — Frontend swap to backend for votes / ratings / watch.** All three endpoints are live; UI still primarily reads localStorage. Need `getWatched`/`setWatched` → `/benefactors/me/watch`, a real Rating ★ dropdown wired to `POST /initiatives/{id}/rate`, and the cause-page tally as API-as-source-of-truth.
7. **P2 — Top-card / topbar alignment.** Backlogged ("doesn't cause operational problems").
8. **P2 — Right-card paging on cause.html.** Should feel right after the pilot seed runs.
9. **P2 — Dead CSS / JS in cause.html.** Pruning candidates: `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS: `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. Guarded; safe to bulk-delete when long.
10. **P3 — Mount-truncation footgun (carry-over).** Linux `wc -l` reported 776/1518 lines for index/cause this pass; Read tool reads through 1704/2131 — host-side files are intact. **Rule: validate file tails via Read, never via bash `wc/tail`.** Re-confirmed pass 19.

---

## 3. Build sequence — commentary on STRUCTURE.md + INSTRUCTIONS.md

INSTRUCTIONS.md is now the per-pass driver; STRUCTURE.md keeps the long-form layouts. Pass 19 took INSTRUCTIONS step 0 (errors) + step 1 (pilot seed).

**0 · Errors first** (carry-over). Both pass-18 P0 errors fixed this pass:

- Cause-page voting widget gated by `inPhase1` — dropped. Renders for all 7 causes now.
- Index row click broken by HTML-attribute over-escape — replaced with delegated listener.

**1 · Pilot data** (this pass, partial). `backend/seed/pilot.py` is in. Pending: actually run it against the dev DB and verify the cause-page right cards page through pilot phase-3/4 missions. Idempotent so a re-run is safe.

**2 · index.html top + side cards** (next pass). Drawings in STRUCTURE.md §STRUCTURE "Election Cards" and "Top card". 4 layouts, 2-sided, `--entity-color` accent + halo on top card.

**3 · index.html table — collapsible + entity-card** (after step 2). Roadblocks 4: collapsible default open, noun toggle per Q4, row-click works (shipped this pass).

**4 · cause.html voting parity** (shipped this pass for widget mount; markers still pending).

- 4a · widget on all 7 causes ✓ (pass 19).
- 4b · annulus markers ("Initiative election" / "Organization election") at the active-arc bounds — pending.

**5 · Frontend swap to backend** (votes / ratings / watch). Drop localStorage as primary read. Wire a real Rating ★ dropdown. `getWatched`/`setWatched` → `/benefactors/me/watch`.

**6 · Pruning** (carry-over).

**7 · Long-term (unchanged):** demo-ready core → initiative-vote pilot → mission/org layer → credits & cash → hardening & reach.

### Step-0 audit: errors, blockers, inconsistencies (INSTRUCTIONS.md step 0)

**Errors fixed this pass.** Both pass-18 P0 items.

**Blockers / open questions (carry-over).**

- **Q4 — Stage-2 toggle nouns vs verbs.** Resolved per INSTRUCTIONS QUESTIONS: nouns ("Initiatives / Organizations") + Propose / Register on action buttons. Ready to land in build-seq 3.
- **Q8 — Pilot access model.** LAN-only confirmed per INSTRUCTIONS QUESTIONS.
- **Q10 — Vote-weight preview client-side?** Server-only confirmed per INSTRUCTIONS QUESTIONS.
- **Q11 — GameMaster account model.** INSTRUCTIONS confirms: real `BenefactorAccount` with `is_test=True`. The model column doesn't yet exist; pilot.py creates GameMaster as a real account but the `is_test` flag is omitted. **Follow-up: alembic migration adding `BenefactorAccount.is_test: bool = False` + retro-set GameMaster + filter founding-49 path on `is_test == False`.**
- **Q12 — Where does STRUCTURE.md §STRUCTURE belong?** Still pending Jax decision.

**Inconsistencies in STRUCTURE.md / INSTRUCTIONS.md.**

- STRUCTURE.md §SYSTEM says "Weekly missions - 4 phases" then lists 5 (Pre-Initiative-Election, New-Initiative, New-Mission, Credit-Release, Resolution). Either the header should read "5 phases" or one of the listed phases is sub-phase of another. Recommend "5 phases".
- STRUCTURE.md §SYSTEM `cause rotation` lists 7 causes as "Atmosphere - Oceans - Land - Forests - Wildlife - Rights - Progress" but the seed data has them as "human-rights" / "human-progress". Mostly cosmetic but the pilot seed uses code letters Atm/Oce/Lnd/Frs/Wld/Rts/Hpr derived from the seed-data ids; the STRUCTURE.md `Atm-Hpr 1001-1003` shorthand resolves cleanly under that mapping.
- STRUCTURE.md `Development` section reads `\`backlog management\`` and `\`build\`` as two passes — these are now described in INSTRUCTIONS.md; STRUCTURE.md could drop them.
- STRUCTURE.md §STRUCTURE checkboxes are stale (Jax: "not updated" in earlier passes). Items shipped this pass (election widget on all causes, row-click) are still ☐. Keep this in mind when reading STRUCTURE.md as a checklist — it isn't one.
- INSTRUCTIONS.md `## UPDATE TASKS` is empty between the heading and `## BUILD SEQUENCE` — the `@CLAUDE Stop process now if there are any lines in between here and ##SYSTEM` directive refers to that gap and currently allows pass to proceed. Good. (If Jax adds a queued task there, the next pass should halt and report.)

### Critique of the current build sequence

- INSTRUCTIONS.md numbering is now clean (1–7, no duplicates). STRUCTURE.md still has the duplicate `1` + missing `5` — superseded by INSTRUCTIONS.md.
- INSTRUCTIONS.md step 5 says "Frontend swap to backend" but is marked "Not immediately imperative" — that aligns with build-seq priority P1 in this README §2.
- INSTRUCTIONS.md ROADBLOCKS items 1–3 reference earlier pass items; carry-over text below the line is stable.

---

## 4. Concepts & tools that need attention before the next build

- **GameMaster `is_test` migration.** Pilot.py creates GameMaster as a real account without an `is_test` flag because the column doesn't exist. Add `BenefactorAccount.is_test: bool = False` via alembic; backfill GameMaster + the founding-49 path filter (so test accounts don't burn through the first-100 bonus pool).
- **Cause-page annulus election markers.** "Initiative election" / "Organization election" labels at the start and end of the cause's active arc. Quick win in the now-marker render path.
- **`cycleStart` config endpoint** (`GET /config/cycle`). Required for Jax's simulations. One route returning `{cycle_start: int, cycle_weeks: 7, size_factor: float}` reading from `Settings`; `ebx_shared.ts` hydrates at boot.
- **Collapsible table.** Default open. CSS `details/summary` is enough.
- **`Initiative.status='suggested'`.** Pilot seed normalises non-pilot samples on run. New initiatives without committed EBX should default to `suggested` — already the model default; confirmed.
- **`scripts/safe_write.py`** (carried). Exists for sandbox-side bulk writes; not needed for host-side Edit/Write.
- **Build-integrity check** (carried). Post-build script: fail if `resources/js/ebx_shared.js` doesn't end with the IIFE close or is below an expected size.
- **IIFE** = Immediately-Invoked Function Expression — `(function(){…})()`. `ebx_shared.ts` wraps in one so inner names don't leak and the build has a known closing shape we can sanity-check.
- **Remote-access for the pilot.** LAN-only confirmed (Q8). Defer fly.io until after pilot smoke-tests.

---

## 5. Open questions for Jax

- **Q11 — `is_test` column.** Confirm OK to add as alembic migration. Pilot.py currently relies on handle-only identification of GameMaster.
- **Q12 — STRUCTURE.md §STRUCTURE location.** Still open.
- **New — Run the pilot seed?** Pilot.py is in. Want me to execute `python -m seed.pilot` against `backend/earthbucks.db` next pass and verify cause-page right cards populate, or wait for you to run it locally?
- **New — Cause-page widget for non-active causes — content.** Pass-19 made all 7 causes mount the live phase-1 widget. For a cause that's mid-mission (i.e. its phase 1 already decided), this means the widget points at the *next* cycle's election. Intended? STRUCTURE.md INSTRUCTIONS roadblock 1 reads as yes ("Whichever phase is in its active decision cycle should render the election information") but please confirm before I wire annulus markers in step 4b.

---

## 6. Build & dev tooling

- **Tests.** No suite. Pytest (backend) + playwright (frontend smoke). Pilot strategy: cofounder accounts + simulated money.
- **Type-check.** `tsc` not on PATH; `node node_modules/typescript/bin/tsc --noEmit` from `frontend/`.
- **Pre-commit hook.** `.git/hooks/pre-commit` blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL` (pass 6).
- **Smoke test (carry-over from pass 18 critique).** Before claiming any UI change "shipped": open the page in a real browser, click the affected element, watch the panel / network tab. Pass-17's two P0 errors would have been caught by 30 seconds of clicking. Apply this to pass-19's two fixes before closing.

---

## 7. Infra

- **Postgres** for prod; env-var swap documented.
- **Pagination** on `/posts` and `/initiatives` — only `limit` today.
- **`cycleStart` from API** — see §4.

---

## 8. Phone / offline

- **Static offline mode** — hard-drive demo snapshot.
- **Swift** — mobile version, after pilot.

---

## 9. Recent changelog (current to oldest)

- **2026-06-02 (auto, pass 19 — BUILD)** — Two P0 errors from pass-18 fixed: cause.html election widget now mounts for all 7 causes (`inPhase1` gate dropped from `renderElectionCard`); index.html table row-click rebuilt as a delegated listener on `#init-table-body` (the inline `onclick` had been corrupted by HTML-attribute over-escape). Pilot seed (`backend/seed/pilot.py`) added per STRUCTURE.md build-seq 1: GameMaster benefactor, 21 initiatives Atm-Hpr 1001–1003 with backdated election dates, 21 orgs, mission rows for phase-3/4 tivs, GameMaster as sole voter, non-pilot sample initiatives normalised to `status='suggested'`. Idempotent; entrypoint `python -m seed.pilot` from `backend/`. Top + side cards (build-seq 2) unblocked but not shipped — next pass.
- **2026-06-02 (auto, pass 18 — BACKLOG)** — README reorganized around STRUCTURE.md annotations. Two P0 errors surfaced (cause-page phase-1 voting only on 1/7 causes; index.html row-click no-op). New build-seq 1 (scratch/pilot seed) added. Drawings confirmed complete, unblocking top + side cards.
- **2026-06-01 (auto, pass 17 — ERRORS)** — `/auth/me` 500 fixed via `BenefactorRead.watched_initiative_ids` coercer. cause.html `_causeDecisionMs` off-by-one-week fixed.
- **2026-06-01 (auto, pass 16 — BUILD)** — Shipped STRUCTURE.md build seq 0, 1a, 2a, 3, 4. (Pass-18 note: 1a and 2a were claimed shipped but Jax reports both broken — pass-19 fixed.)
- **2026-06-01 (auto, pass 15 — BUILD)** — Org-register modal lift, annulus-center circle, single-vote-default dialog, `submitProposal` wired, `scripts/safe_write.py`.
- **2026-05-31 (auto, backlog-management)** — README reorganized around pass-14 walkthrough.
- **2026-05-31 (auto, pass 14 — BUILD)** — STRUCTURE.md build-seq 1a–1e and 2a–2e end-to-end.
- **2026-05-30 (auto, pass 13 — BUILD)** — index.html feed/border cleanup; cause.html topbar, mission overview, phase recaps, black background.
- **2026-05-30 (auto, pass 12 — BUILD)** — cause.html 401 fix; index.html build-seq 0–3.
- **2026-05-29 (auto, pass 11)** — build-seq 1–4 on correct pages.
- **2026-05-28 (auto, pass 10)** — build-seq 1–4 on cause.html and index.html.
- **2026-05-21 (auto, pass 9)** — Top-card duplicate-initiative fix staged; bottom-banner alignment live; vote-share annulus edge cases. Diagnosed Windows-mount truncation.
- **2026-05-20 (passes 6–8)** — Q1/Q18/Q20–22 + now-marker + founding-bonus seed + topbar/top-card restyle.
- **2026-05-19 (passes 4–5)** — File-corruption recovery; `ebx_shared.ts` regression fix; feed.html → en.html; new index.html layout; backend schema additions.
- **2026-05-15** — Main page alignment; bug notes (wildlife chart, propose-login, cycle model).

---

## Archived pass details

Long-form per-pass shipping notes (passes 5–14) live in git history (`git log -p README.md`). Pull inline if a pass needs to cross-reference.
