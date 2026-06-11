# Earthbucks — README

Earthbux is a weekly charity pool elected by our community. Earthbux News covers, supervises, and helps organize the missions.

- **STRUCTURE.md** — design intent (the model of the platform).
- **INSTRUCTIONS.md** — per-pass driver: BUILD SEQUENCE, ROADBLOCKS (Jax's responses), and BACKLOG (ordered least → most intensive).
- **backlog.md** — Claude's working memory.

---

## 1. Current state

**Pass 36 (Jun 11, automated)** shipped build-seq 0a/1–6 + a database rescue:
- **DB RESCUE.** `backend/earthbucks.db` was found corrupted — the sqlite header said 44 pages but the file held 40 (the mount-truncation plague hit a binary). Rebuilt: fresh schema via `alembic upgrade head`, then every salvageable row copied over. **Recovered intact: all 4 benefactor accounts, 55 initiatives, 21 votes, 33 contributions, 15 missions, 35 orgs, the org registration.** Lost (their pages were the truncated tail): the 15 `posts` rows and `credit_coins`. The corrupt original is preserved at `backend/earthbucks.corrupt-pass36.db`.
- **0a/4 Election rollover** — the missing clock. `backend/app/rollover.py`: phase 1→2 on each cause's vote day (winner = vote/EBX-weighted tally of ballots cast on/before the day), 2→3 on the org vote day (election + 8 weeks; Mission row created), 3→resolved at +33 weeks. Idempotent; wired into `GET /initiatives` (throttled 10 min) so a long-running server shifts without restart. Frontend twin `EBX.LocalElections` (ebx_shared.ts) finalizes LOCAL-only slates (Jax's CAFO vote never reached the DB): every saved share-slate gets an epoch (its decision date); once passed, the slate is tallied, archived to `ebx_local_elections`, shares+commit CLEARED (votes reset), and `applyOverrides()` promotes the winner to org_vote in-memory so rhs cards / recap / annulus / top card all shift. Phase-1 recap reads the archived record for "My vote".
- **1 Top-card faces swapped** (index.html): tiv mode now leads with the just-elected mission's org race ('front'), org mode shows the window-closing org vote on the reverse; header labels follow.
- **2 Per-account wallets/votes** — `EBX.Accounts`: all demo localStorage keys (vote shares, commits, org votes, regs, tasks, posts, profile, watchlist…) are stashed/restored per handle on login/logout, switched inside `loadAll()` before any page reads. First run claims existing data for the currently-signed-in account. Server data was already per-benefactor (`Vote`/`Contribution` keyed by benefactor_id) — the shared localStorage was the offender.
- **3 Unique pilot election dates** (seed/pilot.py): each pilot mission's election now sits on its own cause's REAL vote-day grid (`CYCLE_START + 7d*(cause_index+7k)`): 1003 = most recent strictly-past vote day (org_vote), 1002 = −2 rotations (active), 1001 = −5 rotations (resolved). Mission `started_at` re-synced. Verified: Lnd-1003 Apr 23, Oce-1003 Jun 4 — matches the frontend grid.
- **5 Phase-2 orgs unwired**: seed re-run cleared `winning_org_id` AND the GameMaster org-vote rows on all seven 1003s — org races are genuinely open until their org vote day.
- **6 Vote rows trimmed** (cause.html): the phase-1 vote/slider list shows ONLY the benefactor's voted initiatives + the currently-selected one; others are reachable via Leaders box / search / display area. Empty state hints accordingly.
- **Seed + migration RAN this pass** (pip works in the sandbox now — sqlalchemy/alembic/fastapi installed). API smoke-tested on :8077: GET /initiatives 200 with rollover wired, all 1003s org_vote with no winner.

**Pass 35 (Jun 10, automated)** shipped build-seq 0–6:
- **0a vote-share fix** (cause.html): stored shares referencing tivs that left the phase-1 election (org_vote/active/resolved) made visible shares sum <1 for causes with a resolved election. `pruneShares` drops stale ids on widget render and `renormalizeShares` (0.1 snap, drift→largest) restores the slate to 1.0; `withdrawSingleVote` now renormalizes; `addVoteFor` capped at 10 splits (an 11th 0.1-floor split would exceed 1).
- **1 Overview/Discussion** (index.html): Selected/News tabs → Overview/Discussion. Discussion = board with compose (categories per docs/posts.md — tiv mode: Case/Context/Analysis; org mode: Evaluation/Context/Analysis), POST /posts best-effort with `ebx_local_posts` fallback merged into the feed. Tiv discussions filter by cause, org discussions by initiative (the org table's filter).
- **2 Phase-1 redesign** (cause.html): STRUCTURE layout — left col Leaders + My-votes boxes + Pool-size/My-commit chips; right col Discussion (3 featured categories with helpful/neutral/wrong votes — local `ebx_post_votes` until POST /posts/{id}/vote ships — and inline compose) + initiative search (in-place filter, empty state + clear button); display area = selected tiv (default my top vote, else leader); footer View-initiatives/Commit-EBX. Recap face = Winner/2nd/3rd + My vote + chips left; most-helpful Case + winner description + disabled "See election details ▾" right. Home-page "Re-balance"/"Split your vote" links now carry `&add=<initId>`; cause.html runs `addVoteFor` on arrival (same effect as '+ Add').
- **3 Annulus 2 REDO** (cause.html): outer ring restored to the pre-pass-34 7-sector wheel with the selected cause's sector highlighted; inner pie toggles with the SELECTED mission's phase — phase 2 → orgs with votes (`causeOrgShares`: synthetic shares + my local org votes folded in), phase 1 → initiatives. `setSelectedMission` now fans out to `renderAnnulus`.
- **4 Org voting** (cause.html phase-2 area): org rows with vote buttons (1 vote 1 org), buy-additional-votes at 10×2^(n-1) EBX (autonomous pricing, see backlog), withdraw; POST /initiatives/{tiv}/vote when signed in, localStorage otherwise. `ebx_org_votes` is now object-shaped `{org_id, tiv_id, votes, at}` — index.html, profile.html and ebx_shared.ts readers normalize both shapes; index.html `_saveOrgVote` writes the new shape.
- **5 Org profile mode** (profile.html): the (c) switch re-renders profile.html in place — Initiative Coins (from `ebx_org_regs` + org-vote tiv links), Tasklist (5 starter tasks, checkboxes persisted in `ebx_org_tasks`), Annulus 4 placeholder, Switch-to-Benefactor — no more navigation to mission.html.
- **6 Pilot org links** (seed/pilot.py + ebx_shared.ts + cause.html): past-phase-2 pilot tivs keep/backfill `winning_org_id`; not-yet-decided tivs get it cleared (org_vote = race still open). `loadAll` resolves `winning_org` names from ids. Phase-2 RECAP completed per STRUCTURE: winner + runner-ups, my vote with 100%/20% outcome line, pool/commit chips, most-helpful Evaluation, winning-org statement. **Re-run the seed to apply the backfill.**

**backend** (FastAPI · SQLite)
- Alembic head `e8c5d2a7b491` — APPLIED (pass 36 rebuilt the DB at head; no pending migration).
- `app/rollover.py` (pass 36) — election clock: `run_rollover` / throttled `maybe_rollover` from `GET /initiatives`. Phase-1 tally = committed EBX + per-ballot `max(share, contribution*share)`, ballots cast on/before the vote day only (seed EBX alone never triggers an election).
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

- **Mount truncation now eats BINARIES too (pass 36).** `earthbucks.db` lost its last 4 pages (posts + credit_coins gone — see §1). It also struck twice DURING pass 36 via the Edit tool (pilot.py, initiatives.py — both caught by syntax checks and re-spliced from HEAD). Sandbox writes are now python-splice-only with tail asserts, but the DB corruption predates this pass. **Jax: keep DB backups outside the mount** (pass 36 left one at `backend/earthbucks.corrupt-pass36.db`; the recovered DB is live).
- **15 posts + credit_coins rows lost** in the DB rescue — unrecoverable (their pages were the truncated tail). Discussion seeds/posts will need re-creating.
- **git is healthy again** — passes 34/35 were committed (thanks), and pass 36 commits from the sandbox worked.
- **Org↔initiative registration proxy — half resolved.** `org_registrations` table + endpoints exist (pass 34) and capture initiative links on submit, but approved rows aren't yet promoted to `Organization` + a real org↔initiative join, so the index.html org filter still uses the cause-membership proxy. (Jax pass-35: auto-approve for now — backend auto-approval still to be written.)
- **Annulus 2 / phase-2 org race is still synthetic at the community level** — `Votes.forCause` deterministic shares with the local benefactor's own votes folded in (pass 35). Honest data needs the backend org-vote tally surfaced (`GET /initiatives/{id}/vote/tally` exists — wiring it into `causeOrgShares` is the next step).
- **Top-card BACK face winner is presumptive** — leading phase-1 tiv stands in for "most recent phase 2" until mission history rows exist. Pass-35 org voting writes real local votes, so the top card can start reading `ebx_org_votes` next pass (Jax's roadblock note).

---

## 4. Build & tooling

- **Build.** `npm run build` in `frontend/` compiles `src/ebx_shared.ts` → `resources/js/ebx_shared.js`. All pages load the compiled `.js` — a `.ts` edit without rebuild ships nothing.
- **Type-check.** `node node_modules/typescript/bin/tsc --noEmit` from `frontend/`.
- **Tests.** None yet. Pytest (backend) + playwright (frontend smoke) planned. Pilot uses cofounder accounts + simulated money.
- **Pre-commit hook.** Blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL`. Extend to `models.py` / `cause.html` / `index.html`.
- **Mount-truncation HARD RULE (tightened pass 36).** NO Edit-tool writes to repo files at all — python splice with `assert count==1` anchors + tail assert + `ast.parse`/sentinel check, every time. Pass 36 caught two Edit-tool truncations (pilot.py, initiatives.py) the moment they ran. Binary files are also at risk (earthbucks.db lost 4 pages) — checksum after copying any binary through the mount (`md5sum` both sides).
- **Sandbox CAN run the backend now** — `pip install --break-system-packages sqlalchemy alembic fastapi email-validator passlib[bcrypt] python-jose uvicorn python-multipart pydantic-settings` works (pass 36). Migrations, seeds, and uvicorn smoke tests are all runnable in-pass.

---

## 5. Infra · later

- Postgres for prod (env-var swap documented).
- Pagination on `/posts` and `/initiatives` (only `limit` today).
- `cycleStart` API endpoint for simulations.
- Static offline mode (hard-drive demo snapshot).
- Swift mobile version after pilot.
- Remote access: LAN-only confirmed; fly.io deferred until post-pilot smoke-tests.
