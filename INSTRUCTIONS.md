## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
Great progress. There are some issues that I will point out, and some imperative steps have come to my attention, so I'm reordering the sequence. Focus on steps 0-4.

0. Resolve if any
- (a) **Errors**
*bug A - readme behavior* This is not causing any problems, but I should bring to your attention the few-hundred lines of null (unreadable to human) code that I just deleted from the end of the readme.
- (b) **Blockers**
- (c) **Inconsistencies**
- (d) **Not blocking** Acknowledge but do not attempt to fix yet.
*bug B - pool calculations* The total pool on the front and back of the cards is different. It is calculating the combined pool for one cycles org vote and the next cycles tiv vote. This is incorrect. the org vote pool adds the previous (phase 1) pool to the current (phase 2) pool for the same mission, and the tiv vote is only the current phase 1 pool. 

1. a. **Committments** Everywhere that a benefactor can vote there needs to be an option to commit EBX.
  b. **Vote weights** Races are measured in votes, not EBX. This needs to be changed throughout the platform.
2. **Table Filters**
  a. **Tivs filters** remove ratings and phases. only filter by cause
  b. **orgs filters** only filter by initiatives (orgs must register for an initiative)
3. **Table refinements**
  a. **Description** Instead of "Showing tivs/orgs competing for the next mission" Say "Select an initiative/organization (depending on page toggle state) to learn more"
  b. **remove status from initiatives** All are in phase 1
  c. **remove causes from orgs** orgs filter by initiative, not cause
4. **Cards**
  a. **onclick table filtering** clicking on a card filters the table
  b **multiline headers** Remove "org race" from headers and allow multiline for long initiative titles.


5. a. **P0 — Side cards front and back** *Refine*
Onclick, the side cards filter the table by cause (for initiatives) or by initiatives (for organizations)
2-line initiative titles. Also, "org race" is not necessary in the card header

Side card locations now may be edited. Spread them out to align them with their associated annulus sector. 
  b. **Top card front and back** Make

6. **P0 — Cause-page right-card navigability**

7. **P0 — Cause.html phase-1 & phase-2 UI** 
**Visible-tivs hardening (step 2).** - A benefactor sees in the recap how much of the vote was committed to the tiv they selected, as well as whether their vote won and the resulting amount of ebx they contributed.

8. **P0 — Pilot-mission card variants — first two phases**

9. **P1 — Settings window from profile**

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

### Tier 1 — Trivial (≤15 min, single file, no cross-cutting impact)
- **STRUCTURE.md "schema confusion" on voting types** — the helpfulness votes are inside the posts, not a problem. Delete the parenthetical "-- schema confusion" suffix so it doesn't keep triggering re-reviews.
- **GameMaster account** — make it a benefactor account with privileges. Single-row backend tweak.
- **`docs/posts.md`** — Good idea creating a document for all the post categories. Include all posts in the doc, including EN posts and org posts.
- **Pruning** (carry-over). Dead CSS in cause.html: `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS: `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. Currently guarded; safe to bulk-delete when list grows.

### Tier 2 — Small (contained UI or markup additions)
- **Element search box (STRUCTURE Phase-1 Active drawing "Search for an initiative").** Both. If no results, show empty and option to clear the search box.
- **`InitiativeRating` deletion ordering.** That's fine. Add `is_