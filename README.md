# Earthbucks — README

Earthbux is a weekly charity pool elected by our community. Earthbux News covers, supervises, and helps organize the missions.

- **STRUCTURE.md** — design intent (the model of the platform).
- **INSTRUCTIONS.md** — per-pass driver: BUILD SEQUENCE, ROADBLOCKS (Jax's responses), and BACKLOG (ordered least → most intensive).
- **backlog.md** — Claude's working memory.

---

## 1. Current state

**Pass 35 (Jun 10, automated)** shipped build-seq 0–6:
- **0a vote-share fix** (cause.html): stored shares referencing tivs that left the phase-1 election (org_vote/active/resolved) made visible shares sum <1 for causes with a resolved election. `pruneShares` drops stale ids on widget render and `renormalizeShares` (0.1 snap, drift→largest) restores the slate to 1.0; `withdrawSingleVote` now renormalizes; `addVoteFor` capped at 10 splits (an 11th 0.1-floor split would exceed 1).
- **1 Overview/Discussion** (index.html): Selected/News tabs → Overview/Discussion. Discussion = board with compose (categories per docs/posts.md — tiv mode: Case/Context/Analysis; org mode: Evaluation/Context/Analysis), POST /posts best-effort with `ebx_local_posts` fallback merged into the feed. Tiv discussions filter by cause, org discussions by initiative (the org table's filter).
- **2 Phase-1 redesign** (cause.html): STRUCTURE layout — left col Leaders + My-votes boxes + Pool-size/My-commit chips; right col Discussion (3 featured categories with helpful/neutral/wrong votes — local `ebx_post_votes` until POST /posts/{id}/vote ships — and inline compose) + initiative search (in-place filter, empty state + clear button); display area = selected tiv (default my top vote, else leader); footer View-initiatives/Commit-EBX. Recap face = Winner/2nd/3rd + My vote + chips left; most-helpful Case + winner description + disabled "See election details ▾" right. Home-page "Re-balance"/"Split your vote" links now carry `&add=<initId>`; cause.html runs `addVoteFor` on arrival (same effect as '+ Add').
- **3 Annulus 2 REDO** (cause.html): outer ring restored to the pre-pass-34 7-sector wheel with the selected cause's sector highlighted; inner pie toggles with the SELECTED mission's phase — phase 2 → orgs with votes (`causeOrgShares`: synthetic shares + my local org votes folded in), phase 1 → initiatives. `setSelectedMission` now fans out to `renderAnnulus`.
- **4 Org voting** (cause.html phase-2 area): org rows with vote buttons (1 vote 1 org), buy-additional-votes at 10×2^(n-1) EBX (autonomous pricing, see backlog), withdraw; POST /initiatives/{tiv}/vote when signed in, localStorage otherwise. `ebx_org_votes` is now object-shaped `{org_id, tiv_id, votes, at}` — index.html, profile.html and ebx_shared.ts readers normalize both shapes; index.html `_saveOrgVote` writes the new shape.
- **5 Org profile mode** (profile.html): the (c) switch re-renders profile.html in place — Initiative Coins (from `ebx_org_regs` + org-vote tiv links), Tasklist (5 starter tasks, checkboxes persisted in `ebx_org_tasks`), Annulus 4 placeholder, Switch-to-Benefactor — no more navigation to mission.html.
- **6 Pilot org links** (seed/pilot.py + ebx_shared.ts + cause.html): past-phase-2 pilot tivs keep/backfill `winning_org_id`; not-yet-decided tivs get it cleared (org_vote = race still open). `loadAll` resolves `winning_org` names from ids. Phase-2 RECAP completed per STRUCTURE: winner + runner-ups, my vote with 100%/20% outcome line, pool/commit chips, most-helpful Evaluation, winning-org statement. **Re-run the seed to apply the backfill.**

**backend** (FastAPI · SQLite · ~1571 LOC)
- Alembic head `e8c5d2a7b491` (Jun 10) — `org_registrations` table (pass 34 build-seq 2). **Run `alembic upgrade head` before next API start.**
- `routers/organizations.py` — `GET/POST /organizations/registrations` (declared before `/{org_id}`). POST requires auth; `kind=registration` additionally requires member name + position; both kinds require ≥1 `initiative_ids`.
- `routers/votes.py` — `PUT /benefactors/me/votes`, `GET /causes/{id}/votes`, `POST /votes/commit`.
- `routers/posts.py` — `GET/POST /posts` only. **No `POST /posts/{id}/vote` yet.**
- `routers/initiatives.py` — `POST /initiatives/{id}/rate` (to be removed with `InitiativeRating`); `POST /initiatives/{id}/vote` + `GET /initiatives/{id}/vote/tally` (hard org-election vote — now driven by the pass-35 phase-2 widget).
- `backend/seed/pilot.py` — GameMaster + 21 initiatives + 21 orgs + mission rows. Idempotent. Pass 35: winning_org_id only on past-phase-2 tivs (backfills/clears existing rows).

**index.html** — hero, annulus, page-mode toggle, 2-sided side cards, table swap, entity card, modals. Pass 35: Overview/Discussion toggle (see above). Pass 34 (Jun 10): `?init=<id>` deep link selects + scrolls to an initiative's entry (target of cause-page left-card links). Pass 33 (Jun 10) shipped build-seq 1–3: electionCardFace 2-row My-choice/My-commitment footer + 2-line header spill (no "org race" suffix); tiv face date = first day of upcoming active window, org face date = last day (+1wk); pool split — tiv card = phase-1 pool only, org card = mission phase-1 carry-over + phase-2 commits (`ebx_org_committed` store, commit control now kind-aware); top card = TWO org-elections via shared `EBX.topCard(active, face)` (glowing, electionCardFace format; old 2-column body + local `topCardBack` deleted); filters = cause-only (tiv) / initiative-only (org, **proxy: org.causes ∋ init.cause_index until a real registration table lands — honors `org.initiative_ids` when the API grows one**); Phase column dropped (table lists phase-1 tivs only); org table Cause column → Initiative; hint text = "Select an initiative/organization to learn more"; card-click filters the table (3d).

**cause.html** — 7 cause tabs, annulus + now-marker, phase-1 election widget, propose + org-reg modals, paged left/right cards. Pass 35: share-store prune/renormalize, STRUCTURE phase-1 layout + recap, Annulus-2 redo, phase-2 org voting + completed recap (see above). Pass 34 (Jun 10) shipped build-seq 2–5: org register/nominate modal wired into the phase-2 recap when a tiv is in `org_vote` (POST when authed, `ebx_org_regs` localStorage fallback); annulus filtered to `electionInits` (current phase-1 only — past elections' tivs no longer pollute pie or `voteShare`); left cards page through ALL voted current-election tivs 3/page with "Home page entry →" links; right cards = chronological missions only (`org_vote`→`active`→`resolved`, 3/page, page count = ceil(missions/3) — phantom phase-2 cards on p2+ eliminated). Pass 33: Phase-1 recap "My vote" block. Election dates verified: Oceans Jun 4, Land Jun 11.

**profile.html** — Pass 35 (build-seq 5): in-place org mode (see above); `ebx_org_votes` object shape accepted in the choices table. Pass 34 (build-seq 1) rebuilt to the STRUCTURE drawing: left = CreditCoin Wallet (h-scroll coin strip from tiv+org commits) + choices table (tiv/org toggle; multi-tiv split shows top share only; rows link to cause pages); center = Annulus 3 placeholder w/ front-back toggle (empty per STRUCTURE); right = credit badge (a) + settings gear (b) + org-mode switch (c, gated on holding a credit coin). Fixed: duplicate `choices-table-orgs` id (first copy rendered tiv data) and `openSettingsModal` was referenced but never defined (gear was dead). Upcoming-decisions banner removed (drawing + BACKLOG). Posts history kept below the fold.

---

## 3. Active roadblocks

- **README.md mount truncation (pass 35).** README.md was found truncated to 22 lines mid-pass (ended mid-sentence in the cause.html paragraph). Reconstructed from the pass-34 text + pass-35 additions; the truncated copy is preserved at /tmp inside the sandbox only. Sections 4–5 re-typed from pass-34 state — Jax: sanity-check them.
- **`.git/index.lock` still immovable from the sandbox (passes 34–35)** — `rm` returns "Operation not permitted"; passes 34 AND 35 are uncommitted. **Jax: delete `.git/index.lock`, then commit — two passes of work are sitting unprotected in the working tree.**
- **Org↔initiative registration proxy — half resolved.** `org_registrations` table + endpoints exist (pass 34) and capture initiative links on submit, but approved rows aren't yet promoted to `Organization` + a real org↔initiative join, so the index.html org filter still uses the cause-membership proxy. (Jax pass-35: auto-approve for now — backend auto-approval still to be written.)
- **Annulus 2 / phase-2 org race is still synthetic at the community level** — `Votes.forCause` deterministic shares with the local benefactor's own votes folded in (pass 35). Honest data needs the backend org-vote tally surfaced (`GET /initiatives/{id}/vote/tally` exists — wiring it into `causeOrgShares` is the next step).
- **Top-card BACK face winner is presumptive** — leading phase-1 tiv stands in for "most recent phase 2" until mission history rows exist. Pass-35 org voting writes real local votes, so the top card can start reading `ebx_org_votes` next pass (Jax's roadblock note).

---

## 4. Build & tooling

- **Build.** `npm run build` in `frontend/` compiles `src/ebx_shared.ts` → `resources/js/ebx_shared.js`. All pages load the compiled `.js` — a `.ts` edit without rebuild ships nothing.
- **Type-check.** `node node_modules/typescript/bin/tsc --noEmit` from `frontend/`.
- **Tests.** None yet. Pytest (backend) + playwright (frontend smoke) planned. Pilot uses cofounder accounts + simulated money.
- **Pre-commit hook.** Blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL`. Extend to `models.py` / `cause.html` / `index.html`.
- **Mount-truncation HARD RULE.** After every Edit on files >100 lines, `Read` the last 30–50 lines confirming the tail. Recovery: `git show HEAD:<path> > <path>` then in-place rewrite via Python splice — NOT another Edit-tool call. Pass 35 went further: ALL edits to the big HTML files were python splices with anchor asserts; the only truncation this pass hit a file (README.md) edited by nothing at all — see roadblocks.

---

## 5. Infra · later

- Postgres for prod (env-var swap documented).
- Pagination on `/posts` and `/initiatives` (only `limit` today).
- `cycleStart` API endpoint for simulations.
- Static offline mode (hard-drive demo snapshot).
- Swift mobile version after pilot.
- Remote access: LAN-only confirmed; fly.io deferred until post-pilot smoke-tests.
