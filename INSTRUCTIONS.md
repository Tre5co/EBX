## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
Some of the following steps depend on each other.

0. Resolve if any
- (a) **Errors**
*Vote shares dont add up to 1*
For some of the causes, the vote shares aren't adding up to 1. I'm not able to figure out why.
- (b) **Blockers**
- (c) **Inconsistencies**
- (d) **Not blocking** Acknowledge but do not attempt to fix yet.

1. **Home page overview/discussion** Instead of selected/news, toggle between overview and discussion. Overview is the same as the current selected, and discussion is a discussion board where users can read and post each of the possible post types. Discussions for initiatives are filtered by cause, and discussions for organizations are filtered by initiative.

2. **Phase 1** Redesign phase 1 area according to structure.
Note that selecting the re-balance on the home page should have the same effect as 'add' on the cause page

3. **Annulus 2** REDO
*Selected sector highlighted* Put back the outer ring as it was before.
*Inner pie-chart toggle* The inner pie chart changes depending on the phase of the selected mission. If it's in phase 2, it shows the orgs with votes. If in phase 1, it shows the initiatives.

4. **Org voting** Add org voting in the phase 2 area.

5. **Org profile** Switching to org mode should stay on profile.html. The pages resemble each other.

6. **Link pilot orgs to pilot tivs** For pilot initiatives that are past phase 2, link each to a pilot organization, and complete the phase 2 recap area. 

**Long-term** demo-ready core → initiative-vote pilot → mission/org layer → credits & cash → hardening & reach. 

## ROADBLOCKS
**Mount truncation** Do you have any suggestions to avoid this happening in the future?
**Registration proxy** We can auto approve them for now. Later we can add safeguards.
**Annulus 2** See build step 3
**Top card back face** Once we have the organization vote working, I can vote on an org for the active cause and we will have real data.

## BACKLOG
*Ordered least → most intensive. Tackle in order when blocked on the BUILD SEQUENCE above.*
**Org table filtering** Need a better filtering method than initiative. Idea - table still filters by cause, and any org with multiple initatives shows up in both tables. Possible sub-filter for initiatives within the cause.
**Vote weights**
**Side card locations**
**Org profile** - Place where orgs build a budget, a plan, interact with the community, post updates, communicate with EN, etc.
**Display incremental votes**


### Tier 1 — Trivial (≤15 min, single file, no cross-cutting impact)
- **GameMaster account** — make it a benefactor account with privileges. Single-row backend tweak.
- **`docs/posts.md`** Implement into workflow
- **Pruning** (carry-over). Dead CSS in cause.html: `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS: `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. Currently guarded; safe to bulk-delete when list grows.

### Tier 2 — Small (contained UI or markup additions)
- **Element search box (STRUCTURE Phase-1 Active drawing "Search for an initiative").** Both. If no results, show empty and option to clear the search box.
- **`InitiativeRating` deletion ordering.** That's fine. Add `is_test` before deleting the ratings endpoint.

### Tier 3 — Medium (deferred until spec lands, or new widget)
- **Annulus election markers** — I'll do this after the next build. Backlogged for Jax drawing.
- **Cause-page annulus election markers** — depends on Annulus election markers above.

### Tier 4 — Large (cross-cutting; multiple files or schema impact)
- **Entity table** refinements:
  - (a) **collapsible** Once onclick entity functional, make collapsible.
  - (b) **Mission Start date** Replace the "next vote date" column in the table with "Vote date" which is either the missions start date, or the upcoming initiative vote date.
  - (c) **Organization table** Does not need cause column. Instead, the status column links to the mission page (if any). If it has no mission yet, it links to the org election phase on cause.html (if competing in an org election, option to nominate if not) or simply to the entity card on index.html.
- **Pilot** Change cards depending on current phase. The missions start date (When the initiative was elected) should be coded into the pilot missions, and visible on all missions. Changed *new-mission* phase to *budget* phase to avoid naming confusion.
- **Remove old star-rating and review system** — drop `InitiativeRating` + `Review` tables; delete `crud.create_initiative_rating`, `routers/initiatives.py POST /rate`, `schemas.InitiativeRating*`. Sequenced after `is_test` ships.
