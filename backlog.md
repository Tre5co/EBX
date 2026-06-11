# Backlog

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
9. **email-validator** was missing from the sandbox pip set; if the API ever fails to boot with an ImportError, `pip install email-validator` (added to README §4 list).


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