## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
Progress is being made.

1. **Small top card tweak** Switch top election card front with back.
2. **Different Accounts - Different Votes** Currently, every account retains the current committments of my GameMaster account. Each account needs its own wallet and independent voting. Is there no backend for seperate data in seperate accounts?
3. **Simulated past vote dates** - Each of the pilot missions should have a unique set of past election dates that lines up with the current state of their cause. Currently they all say they started on the same date. The official mission start date is the date of the phase 1 election, when the initiative is elected. 
4. **Election Functionality and phase shift** It's June 11, so the forests active window just began. I expected my votes for the phase 1 land election to be finalized. Unfortunately, the rhs cards did not shift, the phase 1 election did not convert to recap, and my votes did not reset. 
5. **Phase 2 confusion** The phase 2 pilot org missions have orgs wired in, but phase 2 is before the org election. Only missions phase 3 and onward have united initiatives with organizations
6. **Vote UX**The slider bars should not have any initiatives that the user has not voted for unless they are currently selected.

0. Resolve if any
- (a) **Errors**
*Vote not registered.* It's june 11, and the active cause just switched to land. We had the CAFO initiative winning, but the program hasn't shifted the phases. It still has land pilot 0003 in phase 2, and all the rhs cards are the same as they were before. Shift the phases for each initiative on its vote day and organization. In fact, no data i sdifferent between accounts. I think I already mentioned this... I'm gonna go eat some steak. Is this because of the 1 day counting period? I guess I need to figure this out todsy to stay on track.

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
**Make 1 vote 10 Earthbux.** This slight change will globalize nicely
Change the background color within the text boxes to creamy white
1. When proposing an initiative, users should also be able to look through preexisting initiatives. 
1. The leaders section is showing 0 no matter how many ebx I commit.
1. Phase 1 doesn't need the initiative-suggested section
1. Phase 1-2 timing
- When the phase 1 election has not yet happened, the phase 2 area should still be in the "pre" mode.
- When the phase 1 election happens the header should change to phase 2, and the phase 1 area should switch to recap mode.
1. Update register/nominate organization
- When nominating, allow se