# Earthbucks — Backlog

Working memory for Claude. Top line = current state. Everything below is fair game for rework each pass.

> **State (2026-06-02, pass 18 — backlog management):** Jax's annotations on STRUCTURE.md disagree with the pass-17 changelog in two important places. (i) STRUCTURE.md `ERRORS`: "**Only 1 of the causes has the new phase 1 voting applied**" — the build-pass-15 voting-dialog rebuild is per-cause buggy, not the universal win we recorded. (ii) STRUCTURE.md `ERRORS`: "**Entity area table link — table items are not doing anything onclick. Putting in errors because Claude said this was complete (roadblocks 4)**" — the pass-16 Entity Card row-click claim was a false ship. Both block the cofounder pilot. STRUCTURE.md also adds a **new build-seq step 1 (scratch/seed dummy data, 21 missions, GameMaster solo voter)** that didn't exist before, and confirms **roadblock 10 — drawings are complete**, unblocking the top + side card build. Backend is otherwise solid: `/auth/me` 500 was fixed (pass-17 `field_validator` on `BenefactorRead`), initiative-vote API + ratings + watch endpoints exist (alembic `c7f2a4e8d0b1`), but the frontend swap to those endpoints is still pending and the seed for the pilot does not exist yet.

---

## 1. Current state — what's live

**index.html** (1518 lines, host-side)
- Hero, annulus, page-mode toggle (initiative ↔ organization), 2-sided side cards (front/back placeholders), initiative ↔ org table swap, Entity Card panel below the table, Propose / Register modals, info-tab default. Pass-15 dialog rebuild and Org-register modal lift are in place; pass-16 Entity Card with state-aware Vote buttons was wired.
- **Jax (this pass): row-click is doing nothing.** Pass-16/17 marked this resolved; it is not. Most likely the click handlers we added are running but the panel isn't reachable from the rendered DOM (or the handler is bound to a stale row reference after the table rerenders). Untested.
- Top card / topbar still pixel-misaligned. Top + side card front/back content is still placeholder — **Jax (this pass): drawings are complete**, unblocking build-seq 1a.
- Org-register section: removed from the page body, lives in `#org-register-modal-bg` (pass 15).

**cause.html** (2131 lines, host-side)
- 7 cause tabs, annulus + now-marker, phase-1 election widget with sliders / floor / commit, propose modal, paged right cards.
- **Jax (this pass): only 1 of the 7 causes shows the new phase-1 voting.** The rebuilt election widget probably renders against the active-cause cycle only and the other six causes fall through to the legacy `renderPhaseRecaps` static path. Needs a trace through `_rerenderElectionCard` to confirm.
- `_causeDecisionMs` off-by-one-week fixed pass-17 (delegates to `EBX.Cycle.nextDecisionDate`).
- Best-effort `PUT /benefactors/me/votes` + `syncCauseTally` wired pass-16; localStorage still primary.

**profile.html** — 3-card decision strip below upcoming-decision banner. Loads now that `/auth/me` is fixed.

**Backend** (FastAPI · SQLite dev)
- Schema (alembic `c7f2a4e8d0b1`): `Vote.cause_id`, `Vote.committed`, `Initiative.rating_avg/rating_count`, `BenefactorAccount.watched_initiative_ids` (JSON-encoded text), `initiative_ratings` table.
- Routers shipped: `votes.py` (`PUT /benefactors/me/votes`, `GET /causes/{id}/votes`, `POST /votes/commit`), `benefactors.py` (`GET/POST/DELETE /benefactors/me/watch[/id]`), `initiatives.py` adds `POST /initiatives/{id}/rate`.
- Server-side vote-weight formula `1 + b_contribution / (pool_excl_b * n_votes * size_factor)` is the single source of truth.
- `/auth/me` 500 fixed via `BenefactorRead.watched_initiative_ids` coercer (pass 17).
- Founding-49-EBX seed has run from `backend/`; sentinel mission row exists.

---

## 2. Imminent roadblocks

Ordered by Jax's stated priorities in STRUCTURE.md ROADBLOCKS + ERRORS. **Bold P0** items block the cofounder pilot.

1. **P0 — Cause-page phase-1 voting only applies to 1/7 causes.** STRUCTURE.md `ERRORS`. Most likely cause: `renderElectionCard` is only invoked when `cause.index === state.causeIndex`; the other six routes through the old recap path. Verify by opening cause.html?id=oceans and watching whether the election widget mounts. Fix path: make `renderPhaseRecaps` always call the election widget for the cause's NEXT-decision cycle (the `_causeDecisionMs` helper already returns the correct date for non-active causes).
2. **P0 — index.html row-click does nothing.** STRUCTURE.md `ERRORS`. Pass-16 changelog claimed this shipped, Jax says it doesn't fire. Likely diagnosis: the Entity Card panel exists, but the row handler was bound on initial table render and is gone after `filterInitiatives()` rerenders the `<tbody>`. Switch to delegated `#init-table-body` listener (one `addEventListener` on the body, dispatch by `data-init-id`).
3. **P0 — No scratch/pilot seed.** New STRUCTURE.md build-seq 1: dummy missions Atm-Hpr 1001-1003 (21 total) with past "win" dates, GameMaster as the only voter on each, dummy orgs 1-21 assigned to phase-2+ tivs, sample tivs relabeled `suggested`. Needs a new entrypoint — `python -m seed.seed --pilot` against `backend/`. Without this the index/cause demos can't show realistic feed/recap state.
4. **P0 — Build top + side cards.** STRUCTURE.md ROADBLOCKS 10: **drawings complete**. Build-seq 1a unblocked. 4 drawings → top-card front (next org election), top-card back (this-week newest initiative), side-card front (org election), side-card back (initiative election). Layouts spelled out in STRUCTURE.md §STRUCTURE "Election Cards" and "Top card". `--entity-color` accent + glow on top card.
5. **P1 — Main-page table redesign per ROADBLOCKS 4.** Jax: "Make table collapsible but still default to open" + "TOGGLE REDESIGNED". Read STRUCTURE.md before building — Jax has changed the toggle pattern.
6. **P1 — Frontend swap to backend for votes / ratings / watch.** All three endpoints are live; index.html + cause.html still primarily read localStorage. Need `getWatched`/`setWatched` swap, a real Rating ★ dropdown wired to `POST /initiatives/{id}/rate`, and the cause-page tally to switch from "best-effort PUT + localStorage fallback" to API-as-source-of-truth.
7. **P2 — Top-card / topbar alignment.** ROADBLOCKS 7: backlogged ("doesn't cause operational problems"). Still in QUESTIONS list under (c). Defer until pilot.
8. **P2 — Right-card paging on cause.html.** Won't feel right until a real mission has cycled past phase 1. Defer.
9. **P2 — Dead CSS / JS in cause.html.** Pruning candidates section. Hold and bulk-purge when long.
10. **P3 — Mount-truncation footgun.** Linux `wc -l` reported 1518/776 lines for cause/index this pass; host-side files are 2131/1518. Re-confirmed. **Rule: validate file tails via Read tool, never via bash wc/tail.** `scripts/safe_write.py` exists as the safe-write helper but Edit-tool writes from the host side remain the primary path.

---

## 3. Build sequence — commentary on STRUCTURE.md

STRUCTURE.md BUILD SEQUENCE has **two `1`s** (scratch data and index.html) and skips from 4 → 6. Renumber to 0–5 + 7 below for clarity. Jax should pick whether the renumbering goes back into STRUCTURE.md.

**0 · Errors first.** Resolve the two STRUCTURE.md `ERRORS` items before any other build work — both are pilot-blocking. Confirm `EBX_TAIL_SENTINEL` count = 1 via Read (not bash). Verify cause.html ends with `</html>` at line 2131 and index.html at 1518.

**1 · Scratch data (new).** Add `seed/pilot.py` (or `seed.py --pilot`): 21 missions Atm-Hpr 1001-1003 with backdated election dates, GameMaster as solo voter on each, orgs 1-21 mapped to phase-2+ initiatives. Relabel every sample initiative `status='suggested'`. **This unlocks meaningful right-card paging on cause.html** and gives the entity-card a non-empty default-info state. Idempotent under re-runs.

**2 · index.html top + side cards.** Drawings are in. 4 layouts: side-front (org election), side-back (initiative election), top-front (next org election), top-back (this-week newest initiative). Use `--entity-color` + box-shadow halo on top card (matches the annulus center treatment). Stay 2-sided.

**3 · index.html table + entity-card.** Roadblocks 4 expansion:
- Collapsible table, default open.
- Row click → entity-card opens with state-aware Vote (delegated listener, fix P0 #2).
- Toggle redesigned per STRUCTURE.md (verify the noun-vs-verb decision: Q4 still open).

**4 · cause.html voting parity.** Fix P0 #1 — voting widget on all 7 causes' next-decision cycle, not just the active one. Also add the start/end annulus markers ("Initiative election" / "Organization election", listed in §4).

**5 · Frontend swap to backend** (votes / ratings / watch). Drop localStorage as primary read. Wire a real Rating ★ dropdown. `getWatched`/`setWatched` → `/benefactors/me/watch`.

**6 · Pruning** (carry-over). Dead CSS in cause.html: `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS: `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. Currently guarded; safe to bulk-delete when list grows.

**7 · Long-term (unchanged from STRUCTURE.md):** demo-ready core → initiative-vote pilot → mission/org layer → credits & cash → hardening & reach. `bye-bye` candidates: `m_indx.html`, `en.html`.

### Criticism of the current build sequence

- **Sequence numbering is broken.** Two `1`s and no `5` in STRUCTURE.md. Easy to miss in a hurry.
- **The pilot dataset (new step 1) is a prerequisite for steps 2–5 looking right** — paging, leader-card defaults, and the entity card all degrade with empty data. Build it first.
- **Steps 3 (backend) and 4 (ratings + watch backend) have already shipped** at the backend layer (alembic `c7f2a4e8d0b1`). STRUCTURE.md still lists them as upcoming work. The remaining work on both is purely **frontend swap**. Rephrase them to make that explicit so the next build pass doesn't redo the migration.
- **STRUCTURE.md §STRUCTURE is explicitly stale** ("not updated" in the header). It's still the source of truth for layouts (e.g., the card mockups in step 1a), but its checkboxes don't reflect ship state. Either re-mark or move the layout mocks to a `/design` doc.
- **README and STRUCTURE.md are diverging.** Both list build sequence, roadblocks, questions. Pick one as primary. Suggest: STRUCTURE.md owns intent + design (the "model of the platform"), README owns state + next-step backlog.
- **ERRORS belong in STRUCTURE.md only when they're new bugs Jax discovered.** Pass-by-pass changelog of fixed errors belongs in this README. Today the same content is in both.
- **Build-pass-17 marked pass-16 features "shipped" without testing them.** Both P0 errors are pass-16 work that the next reviewer (Jax) immediately found broken. Add a "smoke test before claiming ship" step to the verification protocol: open the page, click the row, watch the panel. Do this for every build pass.

---

## 4. Concepts & tools that need attention before the next build

- **`GameMaster` account / pilot seed.** New. STRUCTURE.md build-seq 1 introduces a single solo-voter persona used for backdated election results. Decide: is GameMaster a real `BenefactorAccount` (id=1?) or a flag on `Vote.voter_id` that bypasses the auth check? Recommend a regular account with `is_test=True`, so the founding-49-EBX path still works.
- **Cause-page annulus election markers.** Listed in STRUCTURE.md QUESTIONS. Add "Initiative election" / "Organization election" labels at the start and end of the cause's active arc. Lives in the existing now-marker render path; quick win.
- **Single-vote-default dialog.** Already shipped in cause.html pass-15. STRUCTURE.md ERRORS suggests it isn't running for 6/7 causes — re-verify before reusing it for the m_indx-style org election.
- **`cycleStart` config endpoint** (`GET /config/cycle`). Required for Jax's simulations and explicitly called out in STRUCTURE.md QUESTIONS. Still hardcoded in `ebx_shared.ts`. Add a one-route response shape `{cycle_start: int, cycle_weeks: 7, size_factor: float}` reading from `Settings`; have `ebx_shared.ts` hydrate it at boot.
- **Collapsible table.** ROADBLOCKS 4. Default open. CSS `details/summary` is enough; no JS state needed.
- **Entity Card row click — delegated listener.** P0 fix. One `addEventListener` on `#init-table-body`, route by `data-init-id`. Survives table rerenders, which the per-row bind does not.
- **`Initiative.status='suggested'`.** STRUCTURE.md build-seq 1 expects all sample initiatives without committed EBX to read `suggested`. Today the seed sets various statuses; the pilot seed needs to normalize.
- **`scripts/safe_write.py`** (carried). Exists; only useful for sandbox-side bulk writes. Edit-tool writes from the host don't need it.
- **Build-integrity check** (carried). Post-build script: fail if `resources/js/ebx_shared.js` doesn't end with the IIFE close or is below an expected size. Pairs with the existing pre-commit single-sentinel hook.
- **IIFE** = Immediately-Invoked Function Expression — `(function(){…})()`. `ebx_shared.ts` wraps in one so the inner names don't leak globally and the build has a known closing-paren shape we can sanity-check.
- **Remote-access for the pilot.** Open: LAN-only off Jax's localhost, or stand up fly.io now? Drives whether hardening (step 7.4) is pulled forward.

---

## 5. Open questions for Jax

- **Q4 — Stage-2 toggle nouns vs verbs.** "Initiatives / Organizations" on the toggle, with "Propose / Register" on the action button — recommend. Pick before §3 step 3.
- **Q8 — Pilot access model.** LAN-only or fly.io? Drives §7.4 ordering.
- **Q10 — Vote-weight preview client-side?** Recommend server-only (single source of truth). Confirm before any cause-page tally redesign.
- **Q11 (new) — GameMaster account model.** Real `BenefactorAccount` row with `is_test=True`, or a magic value? Affects pilot-seed shape.
- **Q12 (new) — Where does STRUCTURE.md §STRUCTURE belong?** Move the long-form layout mocks to a `/design` doc, or keep them in STRUCTURE.md and re-mark the checkboxes? Either is fine; pick.

---

## 6. Build & dev tooling

- **Tests.** No suite. Pick pytest (backend) + playwright (frontend smoke). Pilot strategy: cofounder accounts + simulated money on first 7 weekly votes; mission page locks in by week 7, ready for first org vote.
- **Type-check.** `tsc` not on PATH; `node node_modules/typescript/bin/tsc --noEmit` from `frontend/`. Run on Windows (or with the mount confirmed in sync).
- **Pre-commit hook.** `.git/hooks/pre-commit` blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL` (pass 6).
- **Smoke test (new — recommended).** Before claiming any UI change "shipped": open the page in a real browser, click the affected element, watch the panel / network tab. Pass-17's two P0 errors would have been caught by 30 seconds of clicking.

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

- **2026-06-02 (auto, pass 18 — BACKLOG)** — README reorganized around the STRUCTURE.md annotations Jax added overnight. Two P0 errors surfaced from STRUCTURE.md `ERRORS` (cause-page phase-1 voting only on 1/7 causes; index.html row-click no-op — both pass-16 claims that didn't hold). New build-seq 1 (scratch/pilot seed) added to the front of the build sequence — GameMaster solo voter, 21 dummy missions, sample tivs → "suggested". Drawings confirmed complete, unblocking top + side cards. Sequence renumbered to remove STRUCTURE.md's duplicate `1` and missing `5`. Backend ratings/watch and initiative-vote endpoints reframed as "frontend swap pending" rather than "shipped" so the next pass focuses on UI wiring, not migrations. Critique of structure + build sequence added: numbering broken, README/STRUCTURE.md diverging, ERRORS straddling both docs, pass-17 shipped without smoke tests.
- **2026-06-01 (auto, pass 17 — ERRORS)** — `/auth/me` 500 fixed via `BenefactorRead.watched_initiative_ids` coercer (`None → []`, JSON string → list). cause.html `_causeDecisionMs` off-by-one-week fixed (delegates to `EBX.Cycle.nextDecisionDate`). Mount-truncation reminder logged.
- **2026-06-01 (auto, pass 16 — BUILD)** — Shipped STRUCTURE.md build seq 0, 1a, 2a, 3, 4. **(Pass-18 note: 1a and 2a were claimed shipped but Jax reports both broken — see §2 P0s.)** Backend votes router, ratings + watch router, alembic `c7f2a4e8d0b1`.
- **2026-06-01 (auto, pass 15 — BUILD)** — Org-register modal lift, annulus-center circle, single-vote-default dialog, `submitProposal` wired, `scripts/safe_write.py`.
- **2026-05-31 (auto, backlog-management)** — README reorganized around pass-14 walkthrough.
- **2026-05-31 (auto, pass 14 — BUILD)** — STRUCTURE.md build-seq 1a–1e and 2a–2e end-to-end.
- **2026-05-30 (auto, pass 13 — BUILD)** — index.html feed/border cleanup; cause.html topbar, mission overview, phase recaps, black background.
- **2026-05-30 (auto, pass 12 — BUILD)** — cause.html 401 fix; index.html build-seq 0–3.
- **2026-05-29 (auto, pass 11)** — build-seq 1–4 on correct pages.
- **2026-05-28 (auto, pass 10)** — build-seq 1–4 on cause.html and index.html.
- **2026-05-21 (auto, pass 9)** — Top-card duplicate-initiative fix staged; bottom-banner alignment live; vote-share annulus edge cases. **Diagnosed Windows-mount truncation.**
- **2026-05-20 (passes 6–8)** — Q1/Q18/Q20–22 + now-marker + founding-bonus seed + topbar/top-card restyle.
- **2026-05-19 (passes 4–5)** — File-corruption recovery; `ebx_shared.ts` regression fix; feed.html → en.html; new index.html layout; backend schema additions.
- **2026-05-15** — Main page alignment; bug notes (wildlife chart, propose-login, cycle model).

---

## Archived pass details

Long-form per-pass shipping notes (passes 5–14) live in git history (`git log -p README.md`). Pull inline if a pass needs to cross-reference.
