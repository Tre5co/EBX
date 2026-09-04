# to_delete — what is outdated, replaced, or dead

*Created 2026-08-28 (build-seq §4). One list, ordered by how safe each removal
is. Nothing here has been deleted: this file is the inventory, and each entry
says what would break if it went and what has to happen first.*

**How to use it.** Work top down. Everything in **§A** can go today with no code
change. **§B** needs a one-line edit somewhere first. **§C** is live code whose
replacement exists but which still has a caller or a story to tell. **§D** is
the stuff that only LOOKS dead.

---

## §A — safe now, nothing reads them

| What | Where | Why it can go |
|---|---|---|
| 7 database backups | `backend/earthbucks.db.bak_20260809_194835`, `…bak_20260810_094142`, `…bak_aug08b`, `…bak_aug27c`, `…bak_jul19`, `…bak_jul31`, `…bak_premigrate` | ~1.7 MB of point-in-time copies going back to July. Git has the schema history and `alembic` has the path between versions; these are snapshots of *data* nobody has read since the day they were made. **Keep `…bak_aug27c`** until the finalized model has run a full cycle — it is the last state before it. |
| `backend/earthbucks.db.migrated_jul19` | same folder | The July cutover artefact. Superseded twice. |
| `backend/_to_delete/earthbucks.db-journal` | | An orphaned SQLite journal from an interrupted write on 2026-08-27. It is not a database and cannot be opened as one. |
| `_ebx_snapshot.tgz` | repo root | Written 2026-08-28 to move the tree into a container with Chromium on it, so `oe_check` and `ce_check` could be run for the first time. It has served its purpose. **Add `*.tgz` to `.gitignore`.** |
| `scripts/__pycache__/` | | Byte-code. `.gitignore` already covers `__pycache__` elsewhere. |

## §B — one edit, then safe

| What | Where | The edit first |
|---|---|---|
| `backend/seed/pilot.py` | | v1-shaped and unrunnable against the v2 schema. README §10 still lists it as "sample data" — say it is dead or rewrite it. |
| `README.md` §11 + §12 references to `*_old.py`, `routers_old/`, `backend/earthbucks.db.pre-v2.bak`, `backend/seed/port_v1.py` | README lines ~893, ~910–912, ~932, ~934, ~952 | **None of those files exist in the tree any more** — they were removed at some point and the README still documents them, including a `./.venv/bin/python -m seed.port_v1` command that cannot run. Delete the references, not the files. |
| `.pf-left` · `.pf-right` · `.pf-right-row` · `.pf-gear` · `.pf-badge-card*` · `.pf-orgmode` | `profile.html` CSS | Thirteen rules for the three-column rail the 2026-08-28 rebuild replaced. `.pf-grid` and `.annulus3-*` are already gone; these are what is left of the same layout. Check nothing else selects them, then cut. |
| `EBX.formatEBX` | `resources/js/ebx_shared.js` | Still correct for the surfaces that mean the MINTED state (the credit badge, the ledger, mission.html's pool and spend). After the 2026-08-28 unit sweep it has only a handful of callers. Do not delete it — but every new call site should be `formatTokens` unless it means minted money, and `scripts/unit_sweep.js` is the way to check. |

## §C — live, but the replacement already exists

| What | Where | Blocked on |
|---|---|---|
| `GET/PUT /missions/{id}/p1/carryover` | `backend/app/routers/votes.py:74–98` | The phase-1 carryover machinery describes a world that ended 2026-08-20. `crud.p1_carryover_state` / `carryover_p1` / `_send_floor` go with it. It still explains races finalized under the old rules honestly, so it cannot go until those races are archived or restated. `scripts/carryover_check.js` guards the signed-out path and would go too. |
| `crud._withdraw_p1_legacy` + `_send_floor` | `crud.py:1994`, `:2052` | Same story. `withdraw_p1` is a named refusal now; the legacy body is kept so an old race can still be explained. |
| The phase-2 **withdraw button** | `cause.html` | Named in the backlog since 2026-08-20b. It posts to an endpoint that refuses. Remove the button, keep the refusal. |
| `votes_p2.conversions`, `benefactor_accounts.grant_commit_by_week` | `models.py:307–323` | Deliberately not dropped by migration `c5d8f2a91e67` — they hold the last values written under the retired rules. Nothing reads them. Drop when the races they describe are settled. |
| `mint_mission_coins` firing at `finalize_p2` | `crud.py` | The coin should be issued at BUDGET, not at the mint (README §5, "Credits & EBX"). Named backlog item; moving it is a behaviour change, not a deletion. |
| `LocalElections` no-op stubs | `resources/js/ebx_shared.js:248` | Five empty methods kept so lingering call sites do not throw. Grep for callers; if there are none left, delete the object. |

## §D — looks dead, is not

- **`Votes.forCause`** — CHECKED 2026-08-28, and the answer is better than the
  question. Six functions in `ebx_shared.js` still call the synthetic vote
  distribution — `raceCard` · `electionPanel` · `electionBanner` · `sideCard` ·
  `upcomingCauseBanner` · `topCard` — and **no page calls any of the six.** The
  only mentions of `EBX.sideCard` and `EBX.topCard` left in `main.html` are two
  comments saying the page builds its own faces instead. So this is a large
  block of genuinely dead render code, not a live surface showing fake numbers,
  and it moves to §A the moment somebody confirms the same for `frontend/src/
  ebx_shared.ts`, which is the SOURCE these are built from — delete it there and
  rebuild, or the next `esbuild` run puts it all back.
  - What must stay: **`EBX.Votes.rankColor`**, which is a palette, not a
    simulation, and is called for real by `main.html:4322` and
    `cause.html:3943`.
- **`backend/app/post_config.classify_flag`** — a stub that returns green. It
  looks like dead scaffolding; it is the seam the real classifier plugs into,
  and `posts.flag` / `GET /missions/{id}/post-support` are built around it.
- **`ce_check.js`'s cause-table assertions** — they look stale next to the CE
  panel, but they were rewritten for the panel on 2026-08-27 and pass.

---

## Also worth doing while here

- **`.gitignore`**: add `*.tgz`, `backend/*.db.bak*`, `backend/*.db-journal`.
- **`backend/.venv/` is 103 MB** and inside the repo. It is git-ignored, but it
  is also why any archive of this tree is 11 MB instead of 800 KB. Moving it
  outside the repo would make the tree portable.
- **`docs/` has no index.** Nine files, three of which (`RESEARCH.md`,
  `Donation_Landscape_Brief.md`, `Endowed_Grantmakers_Deep_Dive.md`) are
  research rather than build documents. A `docs/README.md` naming what each one
  is for would stop the build docs and the research docs being read as one pile.
