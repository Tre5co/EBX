## UPDATE TASKS
@CLAUDE Stop process now if there are any lines in between here and ##SYSTEM
## BUILD SEQUENCE
For nontrivial steps, check with Jax before confirming completion and moving on to the next.
0. 
- (a) **Errors** Resolve if any
- (b) **Blockers** Internalize roadblocks, and ensure that none of the items in questions & conceptual backlog are blocking the step before beginning it.
- (c) **Inconsistencies** Point out any sections in STRUCTURE.md that are confusing or contradictory.

1. **Cause page navigability**
- Implement onclick from the right-cards which changes the whole page to that mission. So if the missions past phase 1, the election card should not show. 
- **Vote splitting redesign** Other initiative options are only visible from index.html. Otherwise central area is news.

create dummy missions Atm-Hpr 1001-1003 (21 total) that fill these slots and are hardcoded with dates in the past when they "won" elections. Simulate that my account (GameMaster) was the only participant in the votes and create dummy organizations (orgs 1-21) and assign (those past phase 2) to dummy initiatives (tivs 1-21). Do not use sample information. Change all sample tivs to "suggested".
- GameMaster is the account I use, it's a benefactor account with privilidges.

2. **index.html top and side cards**
    see 4 drawings in structure. Edit top card and side cards.

3. **Entity table collapsible** Once onclick entity functional, make collapsible.
I choose nouns. Close Q4.

4. **Cause.html**
- (a) Change the Mission overview to a header for the phases rather than a card below the annulus.
- (b) **Cause-page annulus election markers.**
    - 
5. **Frontend swap to backend** (votes / ratings / watch). Drop localStorage as primary read. Wire a real Rating ★ dropdown. `getWatched`/`setWatched` → `/benefactors/me/watch`.
- Not immediately imperative

6. **Pruning** (carry-over). Dead CSS in cause.html: `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS: `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. Currently guarded; safe to bulk-delete when list grows.  

7. **Long-term** demo-ready core → initiative-vote pilot → mission/org layer → credits & cash → hardening & reach. 

## ROADBLOCKS (Jaxs response to readme)
1. That looks correct. Whichever phase is in its active decision cycle should render the election information (similarly to its display on the index.html election card). 
However, it should not display all suggested initiatives, only the ones currently selected with the option to withdraw or modify vote share. On the cause.html phase 1 card, only the leading tivs and the voted-for tivs should display. The most helpful post will also display, as well as options for users to review and discuss.
- **Single-vote-default dialog.** This shipped, but only for the one cause. May need to re-create and re-seed.

2. Looks correct. Dispose of any outdated/unused code

3. Is this doable?

4. Great, ready to go

5. Making table collapsible is its own small task

6. Yes, let's nail this down conceptually and add the endpoints.

7. This doesn't cause any operational problems so can be backlogged.

8. pending
9. pending bulk purge. Alert when ready.
10. Excellent

## QUESTIONS & CONCEPTUAL BACKLOG
**Q4** Yes. Recommended is already active.
**Q8** LAN only
**Q10** Server only
**Q11** Real `BenefactorAccount` row with `is_test=True`.
**Q12**

**Remote-access for the pilot.** LAN only for now.
**top-card / topbar alignment.**
**Cause annulus markers** e.g. at the start and end of the active area mark "Initiative election" and "Organization election"
**`cyclestart` config endpoint** I want to run simulations and this will be necessary to understand. I will need to read the code.
- Should I do this before starting the pilot?

## ERRORS
**Cause page bug** See roadblocks 1
**Entity area table link** See roadblocks 2