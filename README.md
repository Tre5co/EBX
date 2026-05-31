# Earthbucks — Backlog

Working memory for Claude. Jax keeps a one-line state summary at the very top; everything below is fair game for rework each pass.

> **State (2026-05-31):** Reverted to the pre-rotation main branch. No rotating display. Pass 13 (BUILD) shipped index.html feed/border cleanup and the cause.html 7-tab topbar, mission overview, and phase recaps. Next vote is the bottleneck — see "Roadblocks" below.

> **Noon 5/31** The cause and index pages look good, we need to implement a functional voting system, but first, ensure that all systems, dates, and ux is correct. MAIN BRANCH ONWARD!
---

## 1. Current state — what's live

**index.html** (home / mission cross-section)
- Hero: top-card header strip is flush with the topbar; annulus + side cards (front-only `sideCard`) stretch the center column; bottom banner removed.
- Initiative table: 7-column scrollable (Watch · Name · Cause · My EBX · Total EBX · Status · Next vote), search + Cause/Stage/Rating filters + Propose button. Watch persists in `localStorage`.
- Below table: News / Selected-Initiative tab toggle. Row click switches to the detail tab and scrolls.
- Org-register section (4-step guide → profile.html).
- "From Earthbux News" strip moved off this page (now on profile.html).
- Continuous dark background (`#0f1a14` hero, `#0f1a14` table band — no green seam).

**cause.html** (one cause, one missions feed)
- 7 mission-block tabs across the topbar (replaced the dropdown). Tabs carry the cause color and link to `cause.html?id=...`.
- Center: annulus + cause-colored Mission overview block (phase 1–5 mapped against the 49-day window).
- Below: 4 stacked phase-recap blocks (1 Pre-election · 2 New-Initiative · 3 New-Mission · 4 Credit-Release), each auto-populated with leader / dates / windows from sample data.
- All-dark theme (`#0a1410` page, `#0f1a14` hero/topbar).
- 401 console error from `Auth.fetchMe()` for signed-out visitors: silenced.

**profile.html** — now hosts the EN 3-card strip below the upcoming-decision banner.

**Backend** (FastAPI · SQLite dev)
- Schema additions live since pass 5: `logo_url` on Organization & Initiative, `vvv` on BenefactorAccount, nullable `Vote.org_id`, `Vote.share ≥ 0.1`, `size_factor` in config.
- Migration `b1c3e2f4a9d7_may19_schema_additions.py` applied.
- Founding-49-EBX bonus is coded; sentinel mission seeder (`seed_founding_bonus()`) exists but has not been run.

---

## 2. Imminent roadblocks

Listed in order of how badly they block the first real vote.

1. **No initiative-voting UI on cause.html.** STRUCTURE.md flags this as the single highest priority: "There's no initiative voting right now. Main priority is getting that active before the next vote is over." Phase-1 recap block needs to host the election card (vote options, share allocation down to 0.1, current tally) while the cause is in phase 1. Today the phase-1 block is text-only.
2. **Propose-Initiative has no cause picker.** STRUCTURE.md: "Users should select cause, title initiative, and describe it." The propose modal on both `index.html` and `cause.html` only collects title + description + handle. The submission stub also doesn't POST anywhere real yet.
3. **Initiative-election date on cause.html is one week late.** STRUCTURE.md: "The initiative election for a particular cause happens as the cause enters the active window. Currently we have it as happening at the end of the active window." Affects `renderPhaseRecaps()` decision-date math and the now-marker labeling.

4. **Right side cards on cause.html no longer exist.** STRUCTURE.md wants three right-column cards (one each for the mission currently in phase 2 / 3 / 4 of the selected cause). Pass 10 added them; pass 13 removed them in favor of the single mission-overview block. Need to re-introduce per the latest sketch — and on click, they should **swap the 4 phase-recap blocks below to that mission's data**, not expand in place.

5. **Mount truncation between Windows host and Linux sandbox.** Documented in passes 9 and 12. Symptoms: files arrive truncated or padded with NULs; `.git/index.lock` un-removable. Mitigation that has held up: write via `tempfile + os.replace` in Python; never let esbuild write the shipped JS bundle through the Linux mount.
6. **Founding-bonus sentinel mission not seeded.** Blocks the 49-EBX gift to ids ≤ 100. One command on the Windows side: `python -m seed.seed` from `backend/`.
7. **Table → feed wiring still feels off.** STRUCTURE.md still flags "Selections within the table still are not affecting the feed/description area like they should." Pass 11/12 wired filter dropdowns through `idxRenderFeed()`, but a **row click** should narrow the feed to that initiative — verify and tighten.
8. **Center-of-annulus needs to indicate the NEXT cause + a glowing inner border of that color.** Currently center text reads the active cause's leader, not the upcoming-cause cue. 
---

## 3. Build sequence — commentary for the next build

The build sequence in STRUCTURE.md is short. Here is the order I recommend, with the gotchas to watch for.

**0 · Errors.** Always start by tailing both files for `</html>`, counting `EBX_TAIL_SENTINEL` in `ebx_shared.ts` (must = 1), and checking the console on a signed-out load of cause.html. Pass 13 ended clean; verify before editing.

**1 · index.html**
- (a) **Propose-Initiative cause picker.** Add a `<select>` populated from `EBX.config.causes` above the title field in the propose modal (both pages share an identical modal — change once, copy). Make it required. Update `submitProposal()` to include `cause_id`.
- (b) **MAIN TOGGLE → Initiatives | Organizations.** Today the toggle below the annulus is News / Selected-Initiative. STRUCTURE.md wants Initiatives ↔ Organizations: flipping the toggle should swap the table contents (initiatives list ↔ orgs-applying list) and also swap the "Propose" button between "Propose initiative" and "Register organization." This subsumes the standalone org-register section.
- (c) **2-sided side cards.** Side cards are currently front-only. Per the STRUCTURE.md sketch, side cards 2–6 carry **back faces** showing the matching new-initiative (cause name, leader/choice/second/third by %, pool, my commitment). Treat as a single CSS-flip component in `ebx_shared.ts`.
- (d) **Center-of-annulus = NEXT cause cue.** Re-purpose `.ebx-center__sub` to read the upcoming cause (today's active + 1 mod 7) and add a 1–2px glowing inner ring in `--cause-color` for that next cause.
- (e) **Row-click filters the feed**, not just the row-detail tab. Plumb the selected initiative's id/cause into `idxRenderFeed()`.

**2 · cause.html (priority)**
- (a) **Phase-1 card = initiative election.** While the selected cause is in phase 1, render the actual voting widget in the Phase 1 block: list of initiatives with share-allocation sliders (floor 0.1), running tally, "Commit / Withdraw" button, and the existing vote-weight algorithm (`1 + b_contribution/(total_pool_not_b * n_total_votes * size_factor)`). Backend already supports this end-to-end.
- (b) **Fix the initiative-election date.** The decision should land **at the start** of the cause's active week, not the end. In `renderPhaseRecaps()` and the now-marker label, change `(curCycle * 7 + cause.index + 1)` to `(curCycle * 7 + cause.index)` and re-validate against the cycle math.
- (c) **Restore the 3 right-column cards.** Phase-2 / phase-3 / phase-4 cards for the active cause. Click does **not** expand them; it re-targets the 4 phase-recap blocks below to that mission's data. Wire via a `renderPhaseRecaps(cause, missionRef)` overload.
- (d) **Connect mission-overview to the phase recaps.** STRUCTURE.md: "Remove horizontal line below annulus, and mission overview should be connected directly to the 4 phases below." Drop the bottom border on the overview block; collapse the gap to 0.

**3 · After the first vote ships:** prune dead CSS in cause.html (`.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`). Listed in pass-13 notes; safe to delete.

**4 · Long-term sequencing (from STRUCTURE.md):**
0. Demo-ready core (now) — index.html, cause.html, m_indx.html look right; static demo link works.
1. Initiative-vote pilot — first 7 weekly votes with cofounder accounts + simulated money, real initiatives, simulated orgs.
2. Mission / organization layer — org registration → org-built mission pages → m_indx + org election → simulated org vote → mission annulus.
3. Credits & cash economy — real deposits, credit lifecycle, EN 5/16 cut, tax/redemption. This is the gate that finally makes the founding-49-EBX bonus relevant.
4. Hardening & reach — pytest / playwright, Postgres prod path, pagination, cycleStart from API, build-integrity check, static offline mode, Swift app.

`bye-bye` candidates per STRUCTURE.md: `m_indx.html`, `en.html`. Don't invest further here.

---

## 4. New concepts / tools we'll need before the next build

These are things that have shown up in the backlog but haven't been chosen, named, or installed yet. Worth a decision before the next pass touches voting.

- **Soft-vote share allocator (frontend component).** Reusable widget that lets a benefactor distribute 1.0 vote across N initiatives in 0.1 steps, with a running "remaining share" pill. Used in cause.html phase-1 card and later in m_indx for the org-election. Build once in `ebx_shared.ts`, export on the `EBX` object, render twice.
- **`Initiative.rating` aggregation.** Pass-12 Q6: the rating filter dropdown is a no-op until either (a) Initiative carries a numeric `rating` field, or (b) we aggregate from rating-tagged posts on the fly. Pick one. (a) is faster to ship; (b) is more honest. Recommend aggregation with a daily cron once the post model lands; placeholder field for now.
- **`watched_initiative_ids` on BenefactorAccount.** Pass-12 Q7. Move the Watch star out of `localStorage` and into a `Set[int]` column on `BenefactorAccount`, with `POST /benefactors/me/watch/{init_id}`. Migration + endpoint pair next pass.
- **`cycleStart` config endpoint.** Currently hardcoded in `ebx_shared.ts`. Lift to `GET /config/cycle` so it can change without a rebuild — also lets us simulate accelerated cycles for the pilot vote.
- **Build-integrity check.** Post-build script that fails if `resources/js/ebx_shared.js` doesn't end with the expected IIFE close or is under an expected byte size. Pairs with the existing pre-commit single-sentinel hook. Cheap insurance against the mount-truncation fault.
- **`tempfile + os.replace` write helper.** Codify the pass-12 mitigation as a tiny Python helper (`scripts/safe_write.py`) so any sandbox-side write to a tracked HTML file goes through it. Avoids reintroducing the truncation by hand.
- **Stage-2 toggle vocabulary.** Once the index.html main toggle becomes Initiatives ↔ Organizations, pick the verb pair now. Recommend "Initiatives" / "Organizations" as nouns (matches the table headers) over verbs ("Propose" / "Register") — keeps the toggle independent of the action button.
- **Test fixtures for the cofounder pilot.** Three benefactor accounts × seven causes × a small initiative set. Bake into `seed/seed.py` behind a `--pilot` flag so we can reset between dry runs.

---

## 5. Open questions for Jax

Carried over; some may be answerable next pass.

- **Q1 — Founding-bonus seed.** Run `python -m seed.seed` from `backend/` on Windows. Cannot run from Linux sandbox (SQLite on Windows mount is read-only).
- **Q2 — Now-marker.** Pass-8's marker is cause-independent and points at the active cause (verified pass 9). If still wrong: (a) prefer index.html style where "now" is pinned at 12 o'clock and the wheel rotates the cause to the top; or (b) rotation direction inverted; or (c) something else?
- **Q3 — Top-card per-cycle placeholder.** Deterministic tie-breaker keeps the panes distinct while `committed_ebx` is all-zero. OK as a stopgap, or hold identical until real per-cycle data lands?
- **Q4 — Stage-2 toggle nouns vs verbs.** See "New concepts" above.
- **Q5 — Annulus-center "leader" sub-line.** With the bottom banner gone, the annulus center shows date · "Upcoming initiative vote" · cause · leading initiative + EBX. Happy, or promote leader info back to a side card?
- **Q6 — Rating filter source.** Persisted field vs. on-the-fly aggregation? (see "New concepts")
- **Q7 — Watch persistence target.** `localStorage` or `BenefactorAccount.watched_initiative_ids`? (see "New concepts")

---

## 6. Build & dev tooling

- **Tests.** No suite yet. Pick **pytest** (backend) + **playwright** (frontend smoke). Pilot strategy from Jax: cofounder accounts + simulated money on the first 7 initiative votes; mission page locked in by week 7, ready for first org votes.
- **Type-check.** `tsc` not on PATH; use `node node_modules/typescript/bin/tsc --noEmit` from `frontend/`. `npm run build` also serves as a type+syntax check. Run on Windows (or with the mount confirmed in sync) to avoid checking a truncated copy.
- **Pre-commit hook.** `.git/hooks/pre-commit` blocks commits when `ebx_shared.ts` has more than one `EBX_TAIL_SENTINEL` (pass 6).

## 7. Infra

- **Postgres.** Stay on SQLite for dev; pick Postgres for prod; document the env-var swap.
- **Pagination on `/posts` and `/initiatives`.** Only `limit` today.
- **`cycleStart` from API.** Listed in "New concepts."

## 8. Phone / offline

- **Static offline mode.** Snapshot the current state of the project as a hard-drive demo (no server needed).
- **Swift.** Mobile version.

---

## 9. Recent changelog (current to oldest)

- **2026-05-31 (auto, backlog-management)** — README reorganized: roadblocks promoted, build-seq commentary added, new-concepts section introduced, verbose pass histories collapsed below.
- **2026-05-30 (auto, pass 13 — BUILD)** — STRUCTURE.md BUILD SEQUENCE items 0–2d: index.html feed/border cleanup; cause.html 7-tab topbar, mission overview, phase recaps, persistent black background.
- **2026-05-30 (auto, pass 12 — BUILD)** — Resolved 401 console error on cause.html; index.html build-seq 0–3.
- **2026-05-29 (auto, pass 11 — BUILD)** — Build-seq 1–4 on correct pages.
- **2026-05-28 (auto, pass 10 — BUILD)** — Build-seq 1–4 on cause.html and index.html (mission bar moved, toggle added, org register added).
- **2026-05-21 (auto, pass 9 — BUILD + audit)** — Top-card duplicate-initiative fix staged in TS; bottom-banner alignment live; vote-share annulus 0%/100% cases live. **Diagnosed Windows-mount truncation fault.** JS rebuild deliberately deferred.
- **2026-05-20 (passes 6–8 — BUILD)** — Q1/Q18/Q20/Q21/Q22 + now-marker + founding-bonus seed + topbar/top-card restyle.
- **2026-05-19 (passes 4–5 — audit + first BUILD)** — Restored corrupted files; fixed `ebx_shared.ts` regression; renamed feed.html → en.html; new index.html layout; backend schema additions.
- **2026-05-15** — Main page alignment; bug notes (wildlife chart, propose-login, cycle model).

---

## Archived pass details

The long-form per-pass shipping notes (passes 5–13) used to live at the top of this file. They are preserved in git history (`git log -p README.md`) and trimmed here to keep the working memory scannable. Pull them back inline if a pass needs to cross-reference one explicitly.