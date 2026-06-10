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

**index.html** — hero, annulus, page-mode toggle, 2-sided side cards, table swap, entity card, modals. Pass 33 (Jun 10) shipped build-seq 1–3: electionCardFace 2-row My-choice/My-commitment footer + 2-line header spill (no "org race" suffix); tiv face date = first day of upcoming active window, org face date = last day (+1wk); pool split — tiv card = phase-1 pool only, org card = mission phase-1 carry-over + phase-2 commits (`ebx_org_committed` store, commit control now kind-aware); top card = TWO org-elections via shared `EBX.topCard(active, face)` (glowing, electionCardFace format; old 2-column body + local `topCardBack` deleted); filters = cause-only (tiv) / initiative-only (org, **proxy: org.causes ∋ init.cause_index until a real registration table lands — honors `org.initiative_ids` when the API grows one**); Phase column dropped (table lists phase-1 tivs only); org table Cause column → Initiative; hint text = "Select an initiative/organization to learn more"; card-click filters the table (3d).

**cause.html** — 7 cause tabs, annulus + now-marker, phase-1 election widget, propose modal, paged right cards. Pass 32: `setSelectedMission` reducer, `missionPhaseDates`, mission header row. Pass 33: Phase-1 recap "My vote" block (build-seq 4) — share committed to the winner, win/loss, resulting EBX contribution at 20%-win/10%-lose. Election dates verified: Oceans Jun 4, Land Jun 11.

**profile.html** — 3-card decision strip. Pass 33 (build-seq 5): settings moved into a modal window opened from a gear on the profile card (Identity + Reset local data).

---

## 3. Active roadblocks

- **Mount truncation struck 3× in pass 33** (ebx_shared.ts NUL-padding, index.html + cause.html + profile.html tail loss). All recovered via git-blob splice per §4 HARD RULE — but **cause.html recovery must come from the STAGED blob (`git show :cause.html`)**, not HEAD, while Jax's uncommitted edits are in flight. Commit soon to shrink the blast radius.
- **Org↔initiative registration is a proxy** (cause membership). Backend needs a real registration table before the org filter/table column are truthful (see index.html note).
- **Top-card BACK face winner is presumptive** — leading phase-1 tiv stands in for "most recent phase 2" until mission history rows exist.

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