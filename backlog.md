# Backlog

## Automated build run — 2026-06-13 (pass 40)

Shipped the actionable bug in INSTRUCTIONS NOW **#1**: *"a just-elected-initiative vote currently mutates the phase-2 card instead of accruing to the next mission's phase-1 period."*

Root cause: the phase-2/org card's pool is `phase1Pool = mission.committed_ebx` (the elected tiv's committed EBX = its "phase-1 carry-over"). Nothing stopped EBX from being committed to an already-elected initiative — `commit_ebx` had no phase guard, `commitVote` POSTed from the RAW (unpruned) share store, and pass-39's new `commitEbxToInit` could target any tiv from the table. So committing to a just-elected tiv grew its `committed_ebx`, which the phase-2 card reads live → the phase-2 pool mutated instead of the money going to the next cycle's phase-1 election. Reproduced: a 100-EBX commit to a resolved tiv moved its pool 49→149.

Fix (authoritative at the backend, UX guards on the client):
1. **`crud.commit_ebx`** rejects commits unless `status in (suggested, debate)` — phase-1 is the only window EBX commitments are accepted. `POST /initiatives/{id}/commit` maps that to **409** (genuine missing tiv stays **404**).
2. **`commitVote`** skips any share whose tiv is no longer phase-1 before POSTing (guards the raw `loadShares` read; the widget already prunes these from view).
3. **`commitEbxToInit`** blocks with an explanation ("…already elected — its mission is now in the organization vote. Commit to a current phase-1 initiative instead.").

Verified end-to-end against a DB copy: elected/resolved tiv commit → **409**, `ebx_committed` unchanged (pool frozen); phase-1 tiv commit → **201** (40→80); missing tiv → **404**. `node --check` clean on the written cause.html.

Notes for Jax:
- This freezes the carry-over pool at election close, which is the intended behavior (the elected mission's phase-1 money is settled; new money belongs to the next election). If you'd rather *redirect* a late commit to the next-cycle phase-1 candidate automatically (instead of rejecting), say so — it's a small follow-up on top of this guard.
- The rest of #1 (the rollover finalize / recap-convert / rhs-shift / vote-reset) is the engine shipped in passes 35-36; this pass closed the one remaining data-integrity leak. Still listed as "refine" if you see UI shift glitches on an actual vote day — point me at a specific cause/date and I'll trace it.
- **Lock churn continues:** `.git/index.lock` reappeared as a 0-byte file mid-session (the signature of an interrupted/killed git process — consistent with a background git GUI or sync client). Committed via the detached-index workaround again. Troubleshooting steps (resmon / procmon / handle64, check for OneDrive + git GUIs) given to Jax in chat.


## Automated build run — 2026-06-13 (pass 39)

Shipped INSTRUCTIONS NOW **#2 (vote counting)**. Symptom: phase-1 leaderboards showed 0 committed EBX and votes cast on one account were invisible from another. Root cause was NOT the backend — `POST /initiatives/{id}/commit` already creates a `Contribution` and increments `ebx_committed`, and I proved it end-to-end (two accounts → aggregate moves, public GET reflects it). The gap was the frontend: `cause.html`'s `commitVote` captured the EBX amount but only saved it to localStorage; it never called the endpoint, so the shared server aggregate stayed 0.

Changes (all in `cause.html`, safe-spliced):
1. **`commitVote` now persists.** On commit (when signed in), it splits the committed EBX across the voted initiatives by share and POSTs each slice to `/initiatives/{id}/commit`. Repeated "Update commitment" clicks only send the positive delta vs. an in-payload `synced` map, so nothing double-counts. Reductions are left server-side for now (commit_ebx only adds — simulated pilot money; flagged).
2. **Immediate local leaderboard attribution.** A new `_ebxOf(i)` adds the benefactor's own un-synced committed EBX (ebx×share, minus already-synced) on top of the backend `ebx_committed`, so the Leaders box / display area / pool reflect a commit instantly — even signed out — without inflating once the backend total catches up.
3. **Defined `commitEbxToInit`.** The table's selected-initiative panel had an `onclick="commitEbxToInit(...)"` button that was never defined (threw ReferenceError). It now prompts for an amount and POSTs to the same endpoint.

Verification: `node --check` on the written 109 KB script block (OK); a pure-function sim of the delta-guard + attribution (no double-count across commit/re-commit/update/signed-out); and a TestClient run against a DB **copy** (`/tmp/ebx_test.db`, pilot DB untouched) confirming a 100-EBX 0.6/0.4 split lands 60/40 and is visible from a second account.

Notes / decisions for Jax:
- **Cross-account visibility** falls out of (1): `ebx_committed` is the shared aggregate returned by `GET /initiatives`, so once a contribution is written every account sees it. No per-account leakage — contributions are keyed by `benefactor_id`; only the aggregate is shared (by design).
- **Backend env in the sandbox:** the host-made `backend/.venv` has broken script shebangs; drive it via `.venv/bin/python -m pip` / `-m alembic` / `-m uvicorn`. Had to (re)install `passlib[bcrypt]`, `python-jose`, `python-multipart`, `email-validator`, `pydantic-settings`, `httpx`. Migrations are at head (`e8c5d2a7b491`). DB backup saved to `/tmp` before any test.
- **Stray file:** `cause.html.stage` (my splice scratch) couldn't be deleted from the sandbox (same mount unlink restriction as the locks) — it's untracked and NOT committed; please delete it host-side.
- **Index lock:** resolved — you removed the locks and git works again; this pass committed normally.
- **Still open in NOW:** #1 (phase shift/rollover UI + the phase-2-card mutation bug), #4 (per-account wallet refinement), #5 (simulated past dates refinement).


## Automated build run — 2026-06-13 (pass 38)

Shipped INSTRUCTIONS NOW **#3 (recap date bug)** + the display half of **#5 (mission start date)**. Root cause: three spots in `cause.html` rendered a mission's `election_open` (the day the debate window opened = vote day − 7d) where the canonical value is `election_close` (the actual election/vote day = mission start = first day of the cause's active window). `missionPhaseDates`' own docstring says its argument is "the election date = mission start date = the day its initiative was elected" — i.e. `election_close`, but cause.html was feeding it `election_open`.

Fixes (all `election_open` → `election_close || election_open` fallback, so nothing breaks if a row lacks the close stamp):
1. **Phase-date anchor** (cause.html ~1335-1336) — `missionPhaseDates(...)` now anchored on `election_close`, so derived phase-2/3/4 boundaries land on the right week.
2. **Phase-1 recap "Voting closed — elected {when}"** (~1678) — the headline bug; now reads `election_close`.
3. **Mission-header "started {date}"** (~2843) — start date = election day per STRUCTURE/INSTRUCTIONS #5.

Verified by simulation against the seed's `cause_vote_day` grid (now=2026-06-13): displayed dates move from the wrong `election_open` values to the correct `election_close` ones, matching INSTRUCTIONS exactly — Land Jun 4→**Jun 11**, Oceans May 28→**Jun 4**, Atmosphere May 21→**May 28**. Forests (future live election Jun 18) renders via the live/`nextDecisionDate` path, not the recap path, so it was already correct and is untouched — consistent with INSTRUCTIONS' "Forests is correct" note.

Notes / decisions:
- **No rebuild needed.** The bug was inline in `cause.html`; `ebx_shared.ts`→`.js` was already correct (the function expected `election_close`). cause.html only changed which argument it passes.
- **Edit method:** Python splice via `scripts/safe_write.py` with `assert count==1` per anchor + `</html>` tail check + line-count invariant + byte read-back verify. Mount HARD RULE honored, no Edit-tool writes to the 147 KB file.
- **NOW #5 caveat:** only the *display* of start date was wrong-path here; the underlying seed dates were already correct (pass 36/37). The "shipped, refine" data-side of #5 still stands.
- **Blocker carried over:** `.git/index.lock` is still a stale, unremovable lock on the mount (host-side). `git status` shows phantom staged changes; worktree == HEAD verified by md5 against `git cat-file`. Committed this pass via the detached-index workaround (see README §3). Jax: please delete `.git/index.lock` so normal git resumes.


## Automated build run — 2026-06-12 (pass 37, audit-only)

Scheduled task asked for an item reconciliation, not a build: ~20 STRUCTURE.md items audited against live code — 13 to resolve ✅, 3 stale-text updates, 2 relocations, 2 new items (org-vote reset on election close; real tally → causeOrgShares). Full list in README §1 (Pass 37). STRUCTURE.md deliberately untouched per task. No code edits; NUL/tail sweep clean. Notable for Jax: the `vvv` colorization flag exists in the DB model but nothing renders it — that's the biggest "looks done in STRUCTURE-adjacent notes but isn't" gap found.


## Automated build run — 2026-06-11 (pass 36)

Shipped build-seq 0a + 1–6 (README §1 detail). Decisions + answers for Jax:

1. **Your DB was corrupt — rescued.** `earthbucks.db` had its last 4 pages truncated (mount plague, binary edition). Rebuilt at alembic head and copied every readable row: all accounts/initiatives/votes/contributions/missions/orgs survived. **Lost: the 15 posts and credit_coins** (they lived on the truncated pages). Corrupt original kept at `backend/earthbucks.corrupt-pass36.db`. Consider keeping periodic DB backups outside the mounted folder.
2. **"Is this because of the 1-day counting period?" — No.** Nothing was counting at all: phase statuses were static seed data and no code ever advanced them. Pass 36 adds the clock — backend `app/rollover.py` (runs lazily on GET /initiatives) + frontend `EBX.LocalElections` for slates that only exist in your browser. Which leads to…
3. **Your CAFO initiative/vote never reached the backend** — it isn't in the DB (no land proposals exist server-side). Your vote lived in localStorage only. The frontend rollover handles exactly this: on your next load of cause.html?id=land it will tally your local slate, declare CAFO elected (status org_vote, election_close Jun 11), reset your votes, convert phase 1 to recap, and shift the rhs cards. Worth checking why the POST /initiatives + PUT votes didn't fire when you proposed it — likely you weren't signed in.
4. **"Is there no backend for separate data in separate accounts?"** There IS — Vote/Contribution/etc. are keyed by benefactor_id. The bleed-through was the shared localStorage demo stores. `EBX.Accounts` now stashes/restores all of them per handle on login/logout (first run claims existing data for whoever is signed in — i.e. your GameMaster keeps what it has).
5. **Election rollover rules chosen autonomously:** phase-1 winner = weighted tally (committed EBX + max(share, contribution×share) per ballot) over ballots cast on/before the vote day; an election only tallies if ≥1 real ballot exists (seed EBX alone never elects — protects the sample proposals from mass-election). Phase 2→3 fires on election+8w ONLY if an org tally exists, else the race stays open for EN. Phase 3→resolved at +33w.
6. **Org-vote stores don't reset yet** when an org election closes (phase-2 equivalent of the vote-reset). Backlog candidate next pass.
7. **Recap "2nd/3rd" remain presumptive** (no per-election history rows). The local-election record now stores your full slate, so at least "My vote" is exact.
8. **Top-card swap (build-seq 1)** done by inverting the mode→face mapping (tiv mode → 'front' = just-elected mission). If you meant something more (e.g. a physical flip animation), say the word.
9. **`.git/index.lock` came BACK mid-pass** (stale, Jun 9 timestamp, undeletable from the sandbox). Pass 36 committed anyway via a detached index (`GIT_INDEX_FILE=/tmp/...` + `write-tree`/`commit-tree`/`update-ref`) — commit `7c1a47e` is real and complete; verified file-by-file against the worktree. Side effect: the repo's own .git/index is stale, so `git status` from the sandbox shows phantom staged changes until you delete `.git/index.lock` and run `git reset` (no data at risk — worktree == HEAD).
10. **email-validator** was missing from the sandbox pip set; if the API ever fails to boot with an ImportError, `pip install email-validator` (added to README §4 list).


## Automated build run — 2026-06-10 (pass 35)

Shipped build-seq 0–6 (README §1 per-item detail). Autonomous decisions + answers, flagging for Jax:

1. **Vote-share bug (0a) root cause**: not a math error in `voteShare` — stale share-store entries. When a tiv wins phase 1 its id stays in `ebx_vote_shares`, but pass 34 removed it from the widget/pie, so the visible sliders summed <1 exactly for causes whose election resolved (Oceans). Fix = prune + renormalize on render, renormalize on single-withdraw, cap splits at 10. Backend `replace_cause_votes` already rejects cross-cause ids, so pruned saves sync cleanly.
2. **MOUNT TRUNCATION — answer to your question.** Suggestions: (a) all big-file edits this pass were python `open/replace/write` with `assert count==1` anchors — zero HTML/TS truncations; keep that as the only write path for files >100 lines. (b) The pre-commit sentinel idea works — extend `EBX_TAIL_SENTINEL` to cause.html/index.html/profile.html (last line is always `</html>`; a 1-line check catches every truncation). (c) Commit after every pass — both 34 and 35 are uncommitted because of the index.lock, which multiplies the blast radius of any truncation. (d) This pass README.md itself turned up truncated (22 lines, mid-sentence) WITHOUT any tool having written it — reconstructed from context; original preserved in sandbox /tmp. Suspect the mount layer, not the Edit tool alone. (e) Post-pass NUL sweep found INSTRUCTIONS.md padded with 1,630 trailing NUL bytes (content itself intact — stripped, now 4,897 bytes); a repo-wide scan afterwards is clean. Recommend adding that one-liner NUL/tail scan to the pass-end checklist permanently.
3. **Org vote pricing**: "increasing prices" unspecified → 10 × 2^(n−1) EBX for the nth extra vote (10, 20, 40…), confirm() before buying, spend tracked in `ebx_org_votes[cause].spent`. Simulated money, no backend debit. Change the curve in `orgBuyVote` if you want.
4. **Org-mode profile**: Initiative Coins derive from local `ebx_org_regs` + org-vote `tiv_id`s (no real OrgAccount yet); Tasklist = 5 starter tasks from STRUCTURE's org responsibilities, persisted `ebx_org_tasks`. Memberships (Contributor/Representative/Executive/Beneficiary) untouched — needs backend design.
5. **Phase-2 recap runner-ups are presumptive** (synthetic shares; winner is real via `winning_org_id`). My-vote line only meaningful for the cause where you actually org-voted.
6. **Registration proxy / auto-approve**: not implemented this pass (backend `org_registrations` rows still aren't promoted to `Organization`); next pass candidate — small crud + seed of approved rows would let the index org filter drop the cause proxy.
7. **Top card back face**: org votes now write `ebx_org_votes` objects — the index top card can read them next pass for real data, per your note.
8. **Migration + seed still not run** — sandbox lacks sqlalchemy/alembic. Before next backend start: `alembic upgrade head` && re-run the pilot seed (winning_org_id backfill).
9. **Commit still blocked** — `.git/index.lock` cannot be removed from the sandbox (Operation not permitted). Passes 34+35 uncommitted. Please delete the lock and commit.

## Automated build run — 2026-06-10 (pass 34)

Shipped build-seq 0–5 (README §1 has the per-file detail). Autonomous decisions, flagging for Jax:

1. **Profile drawing interpretation.** Annulus 3 = dashed placeholder SVG with a working front/back toggle that only swaps the face label ("empty for now" per STRUCTURE). Org-mode switch (c) is disabled until the benefactor holds ≥1 credit coin; a coin = any cause with tiv or org EBX committed (local stores), pending real `CreditCoin` rows. CreditCoin Wallet derives one coin per such cause. Posts history kept below the grid — say the word and it's gone.
2. **Choices table links** point at `cause.html?id=<cause>` (STRUCTURE: "each links to its respective cause page"), not the initiative entry.
3. **Org reg/nom flow**: POST `/organizations/registrations` requires login; logged-out submissions stash to `ebx_org_regs` localStorage marked "saved locally". No replay mechanism yet — backlog candidate. Initiative checklist prefers elected (org_vote/active) tivs of the cause, falls back to voted, then all.
4. **Phase-2 "active" test** for showing the reg button = cause has a tiv with status `org_vote`.
5. **Annulus 2**: outer org layer reuses the synthetic `Votes.forCause` shares (matches homepage org cards) — honest data needs an org-vote tally endpoint. `voteShare()` is now current-election-only; left cards, slice clicks, and the pie all read `electionInits`.
6. **Right cards ordering**: "most recent" = status rank (org_vote → active → resolved) then `election_open` desc, since per-cycle mission history rows don't exist yet.
7. **Migration not run** — sandbox has no sqlalchemy/alembic. `alembic upgrade head` needed before next backend start (head `e8c5d2a7b491`).
8. **Could not commit pass 34** — `.git/index.lock` exists and can't be removed from the sandbox (host-side git process or stale lock). **Jax: delete `.git/index.lock` if nothing is using git, then commit** — the HARD-RULE recovery path needs a fresh blob. One truncation strike this pass (organizations.py mid-token corruption; recovered from HEAD + python splice, all subsequent edits spliced).

## Automated build run — 2026-06-10 (pass 33)

Shipped build-seq 0–5 (see README §1 for detail). Decisions made autonomou