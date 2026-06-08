# Earthbucks — README

Earthbux is a weekly charity pool elected by our community. Earthbux News covers, supervises, and helps organize the missions.

- **STRUCTURE.md** — design intent (the model of the platform).
- **INSTRUCTIONS.md** — per-pass driver: BUILD SEQUENCE, ROADBLOCKS (Jax's responses), and BACKLOG (ordered least → most intensive).
- **backlog.md** — Claude's working memory.

---

## 1. Current state

**backend** (FastAPI · SQLite · ~1571 LOC)
- Alembic head `d3a1f7c2e5b8` (Jun 06) — `post_votes` table + `helpful/neutral/wrong_count` on `Post`.
- `routers/votes.py` — `PUT /benefactors/me/votes`, `GET /causes/{id}/votes`, `POST /votes/commit`.
- `routers/posts.py` — `GET/POST /posts` only. **No `POST /posts/{id}/vote` yet.**
- `routers/initiatives.py` — `POST /initiatives/{id}/rate` (to be removed with `InitiativeRating`).
- `backend/seed/pilot.py` — GameMaster + 21 initiatives + 21 orgs + mission rows. Idempotent.

**index.html** — hero, annulus, page-mode toggle, 2-sided side cards, table swap, entity card, modals. Top + side card content variants still spec-only.

**cause.html** — 7 cause tabs, annulus + now-marker, phase-1 election widget, propose modal, paged right cards. Pass 32 shipped: `setSelectedMission` reducer, `EBX.Cycle.missionPhaseDates` anchor helper, Phase-1 recap branch (stub), mission header row. Election dates verified: Oceans Jun 4, Land Jun 11.

**profile.html** — 3-card decision strip, settings group (Identity + Reset local data only).

---

## 2. Next steps

Per `INSTRUCTIONS.md ## BUILD SEQUENCE`:

1. **Finish Step 1.** Verify recap-fills-phase-1 against a resolved pilot mission (needs `election_open` on pilot rows). Polish `.mission-header` CSS.
2. **Step 3 — Phase-1 Recap + Phase-2 Pre/Active cards** per STRUCTURE drawings. Encode mission start dates on pilot rows; render on every mission view.
3. **Step 4 — Side-card content variants** (top-front, top-back, side-front, side-back).
4. **Step 6 backend — `POST /posts/{id}/vote`** + `GET /missions/{id}/posts?sort=score` (spec-complete; required by Phase-1 Active Discussion column).
5. **Step 7 — Vote-commit UI** on index entity card and cause.html vote card. Queue behind Step 3.
6. **Step 5 — Settings window** — awaiting Jax scope elaboration; do not build blind.

Then drain `INSTRUCTIONS.md ## BACKLOG` in tier order.

---

## 3. Active roadblocks

- **Phase-2 vote areas don't exist yet** (Jax 6/8 afternoon note). Required for Step 3.
- **Vote area + recap displays don't match the new STRUCTURE drawings.** `renderPhase1Recap` is a stub; the Phase-1 Active widget predates the drawings.
- **Bug A** — clicking from home into cause page: phase header defaults to "phase 2 — new initiative" but Phase-1 voting dialog is open and should say phase 1. *(Add to Step 0 errors.)*
- **Bug B** — first of the 7 cause sections lacks right-card navigability; other 6 work. *(Add to Step 0 errors.)*
- **Vote-pool weighting bug.** Phase-1 pool weighting needs to be **vote pool**, not the EBX pool. Committing EBX adds weight to your vote; total pool size is the EBX total. Winner is determined by vote weight, not raw EBX committed. *(Tier 4 — Vote-commit UI scope.)*
- **`election_open` field on pilot rows** (loose-end #1) — without it, Phase-2/3/4 sub-text on past missions falls back to the cause's current decision date. Step-3 dependency that surfaced in Step 1.
- **Pass-32b source fix uncommitted** — `frontend/src/ebx_shared.ts` removal of `targetWeek + 1` is working-tree-only. Next `git restore` will wipe it a third time. **Commit before the next pass.**
- **Settings window scope** — Jax: "not sure yet." Pending elaboration on UI surface and v1 knobs.

Closed since last pass: election-date off-by-one (verified Oceans Jun 4 / Land Jun 11), `selectMission` reducer promotion, mission overview → header row.

---

## 4. Build & tooling

- **Build.** `npm run build` in `frontend/` compiles `src/ebx_shared.ts` → `resources/js/ebx_shared.js`. All pages load the compiled `.js` — a `.ts` edit without rebuild ships nothing.
- **Type-check.** `node node_modules/typescript/bin/tsc --noEmit` from `frontend/`.
- **Tests.** None yet. Pytest (backend) + playwright (frontend smoke) planned. Pilot uses cofounder accounts + simulated money.
- **Pre-commit hook.** Blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL`. Extend to `models.py` / `cause.html` / `index.html`.
- **Mount-truncation HARD RULE.** After every Edit on files >100 lines, `Read` the last 30–50 lines confirming the tail. Recovery: `git show HEAD:<path> > <path>` then in-place rewrite via Python splice — NOT another Edit-tool call.

---

## 5. Infra · later

- Postgres for prod (env-var swap documented).
- Pagination on `/posts` and `/initiatives` (only `limit` today).
- `cycleStart` API endpoint for simulations.
- Static offline mode (hard-drive demo snapshot).
- Swift mobile version after pilot.
- Remote access: LAN-only confirmed; fly.io deferred until post-pilot smoke-tests.
