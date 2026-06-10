## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
Trying to hammer down these side cards.

0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- (c) **Inconsistencies**
- (d) **Not blocking** Acknowledge but do not attempt to fix yet.

1. **Card refining**
a. *design* I updated the my committment and my choice layout. Also, remove "org race" from the headers and allow them to spill to 2 lines.
b. *dates* I switched the front and back for the side cards so tiv elections are now on the front. Currently, the org vote date is the first day of the active window, and the tiv vote date is the first day of the previous active window. The correct dates: Org vote day is the last day of active window (1 week after current state) and the tiv vote day is the first day of the active window (what currently displays as the org vote day).
c. *pool* The total pool on the front and back of the cards is calculating the combined pool for one cycles org vote and the next cycles tiv vote. This is incorrect. the org vote pool adds the previous (phase 1) pool to the current (phase 2) pool for the same mission, and the tiv vote is only the current phase 1 pool.
d. *top card* Complete the top card according to drawings

2. **Table Filters**
  a. **Tivs filters** remove ratings and phases. only filter by cause
  b. **orgs filters** only filter by initiatives (orgs must register for an initiative)
3. **Table refinements**
  a. **Description** Instead of "Showing tivs/orgs competing for the next mission" Say "Select an initiative/organization (depending on page toggle state) to learn more"
  b. **remove status from initiatives** All are in phase 1
  c. **remove causes from orgs** orgs filter by initiative, not cause
  d. **onclick table filtering** clicking on a card filters the table

4. **P0 — Cause.html phase-1 & phase-2 UI** 
**Visible-tivs hardening (step 2).** - A benefactor sees in the recap how much of the vote was committed to the tiv they selected, as well as whether their vote won and the resulting amount of ebx they contributed.

5. **P1 — Settings window from profile**

**Long-term** demo-ready core → initiative-vote pilot → mission/org layer → credits & cash → hardening & reach. 

## ROADBLOCKS (Jaxs response to readme)
1. **Recap-fills-phase-1 when mission's vote already happened.** Yes. Once phase 2 begins, the phase 1 area becomes recap. Once phase 3 begins, the phase 2 area also becomes recap.
**Mission overview → header row** See *header row* in the structure tree
**Promote `selectMission` to a real reducer** `selectMission` is toggled from the rhs cards and changes the whole mission story section
2. This adds onto step 1, also for the cause page design
3. The cause page details what phase each mission is in and has gone through.
4. ready to go
5-11. will focus on after 1-4

## BACKLOG
*Ordered least → most intensive. Tackle in order when blocked on the BUILD SEQUENCE above.*
**Remove upcoming decisions** from profile page
**Persist tiv & org choices** between to profile page choices table
**Vote weights**
**Side card locations**

### Tier 1 — Trivial (≤15 min, single file, no cross-cutting impact)
- **STRUCTURE.md "schema confusion" on voting types** — the helpfulness votes are inside the posts, not a problem. Delete the parenthetical "-- schema confusion" suffix so it doesn't keep triggering re-reviews.
- **GameMaster account** — make it a benefactor account with privileges. Single-row backend tweak.
- **`docs/posts.md`** — Good idea creating a document for all the post categories. Include all posts in the doc, including EN posts and org posts.
- **Pruning** (carry-over). Dead CSS in cause.html: `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS: `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. Currently guarded; safe to bulk-delete when list grows.

### Tier 2 — Small (contained UI or markup additions)
- **Element search box (STRUCTURE Phase-1 Active drawing "Search for an initiative").** Both. If no results, show empty and option to clear the search box.
- **`InitiativeRating` deletion ordering.** That's fine. Add `is_test` before deleting the ratings endpoint.
- **Mission ring** — basic version of the mission-progress ring widget. Create soon.

### Tier 3 — Medium (deferred until spec lands, or new widget)
- **Annulus election markers** — I'll do this after the next build. Backlogged for Jax drawing.
- **Filter sets** — initiative vs org tables have different filters. Backlogged for Jax spec.
- **Cause-page annulus election markers** — depends on Annulus election markers above.
- **Commiting ebx** Add ability to commit ebx in the tiv vote, which increases the share of your vote.

### Tier 4 — Large (cross-cutting; multiple files or schema impact)
- **Entity table** refinements:
  - (a) **collapsible** Once onclick entity functional, make collapsible.
  - (b) **Mission Start date** Replace the "next vote date" column in the table with "Vote date" which is either the missions start date, or the upcoming initiative vote date.
  - (c) **Organization table** Does not need cause column. Instead, the status column links to the mission page (if any). If it has no mission yet, it links to the org election phase on cause.html (if competing in an org election, option to nominate if not) or simply to the entity card on index.html.
  - (d) **filters** The organization table and entity tables will have different sets of filters.
  - (e) **Only future missions** Like we did on the cause page left cards, only phase-1 initiatives should be in the initiative table.
- **Pilot** Change cards depending on current phase. The missions start date (When the initiative was elected) should be coded into the pilot missions, and visible on all missions. Changed *new-mission* phase to *budget* phase to avoid naming confusion.
- **P0 — Vote-commit UI** There is no ability to commit ebx to an initiative. The entity card on index.html and the cause.html vote card need an option to commit/modify a desired amount of ebx to the voted-for tiv.
- **Remove old star-rating and review system** — drop `InitiativeRating` + `Review` tables; delete `crud.create_initiative_rating`, `routers/initiatives.py POST /rate`, `schemas.InitiativeRating*`. Sequenced after `is_test` ships.
