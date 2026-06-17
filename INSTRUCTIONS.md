## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
Time to clean up our SQL.

0. Resolve if any
- (a) **Errors**
- (b) **Blockers**
- (c) **Inconsistencies**
- (d) **Not blocking** Acknowledge but do not attempt to fix yet.

1. **Admin** <Backend> Good start. The page needs to cover everything, not just votes. Need more lists.

There are all kinds of things that need to happen.

This page is essentially a frontend for the api and search interface for all its data.

I think it'll halp me learn how backend development works.

Top level datasets:
- Users
- Missions
- Events

Events: EVERYTHING. Literally everything that causes a new line in the terminal (what are these?)

This is hard to organizae, because every entity has lots of different attributes.


- Users - ID
- Missions - 


- Organizations - 
- Initiatives
- Posts
- Vote/commit log




- It should be sorted by mission i.e. "Oceans 6".
- Within each mission, there are 2 elections (so far). 

I'm confused by a lot of what was created. Let's get down and dirty with it. 

Let's build an admin page where we can: 
- Search by user
- Filter by election
- Filter by organization
- Export CSV
- Sort by timestamp

Summary views so we can sort votes by users, elections, or targets.
Checks to flag duplicate votes, votes without users, and invalid elections.

Instead of overwriting rows, create an event log
vote_events
-----------
id
user_id
election_id
action (CAST/UPDATE/REMOVE)
old_value
new_value
created_at

`/Admin/Votes` endpoint 

2. **Models/Schemas** <Backend> Remove "missionmetric, review, initiativerating" from models. I also notice that on schemas, there is a causevote but no orgvote. On models, there is just "vote". Identify other stale code in the backend.


## CONVERSATION


## BACKLOG (for backlog management - ignore this section during build task)
*Order least → most intensive. Tackle in order when blocked on the BUILD SEQUENCE above.*



1. **1 vote - 10 ebx split** <EBX> This will negate the need for floating point vote shares.
2. **Per-account wallets/votes** <Backend> (shipped, refine). Each account needs a fully independent wallet and ballot.
*Vote withdrawal* Withdrawing a vote does not persist to the pool.
3. **Phase shift & rollover.** <Backend> On a cause's vote day, finalize phase-1 votes, convert the phase-1 card to recap, shift the rhs cards, and reset the user's votes. Bug: a just-elected-initiative vote currently mutates the phase-2 card instead of accruing to the next mission's phase-1 period.

**Remove sample voting data** Remove all sample voting data from all orgs. I want to create it myself by actually executing the process.

4. **Simulated past vote dates** <Admin> (shipped, refine). Each pilot mission's past election dates must line up with its cause's real position in the rotation. Mission start date = the day its initiative was elected. So missions in phase 1 will show future dates.
 - Do I really need this? 

5. **Overview into the table.** <UI> Remove the Overview/Discussion toggle (discussion only). Clicking a table row expands it to show the overview and filters discussion by that cause / initiative / organization.
6. **Election-card navigation.** <UI> Add three buttons to each card: **View** (jump to that entity's expanded table row), **Explore** (link to the cause page), **Vote** (link to the phase-1 or phase-2 voting dialog, matching the card face clicked).
- Add orgs election cards to cause page lhs
1. **Election cards to navigate.** At the bottom of each election card, add 3 buttons. 1. (Left) "View" 
-Filters the table too-
which jumps down to the expanded row of whatever initiative or organization card it came from. 2. (Middle) "Explore" Which links to the cause page. 3. (Right) "Vote" Which links users directly to the cause page voting dialog in the phase 1 or 2 area (depending on which side of the card they click from).
1. **Move overview to table** Remove the overview/discussion toggle. Now it it only discussion. Add on-click expansion for the table rows that has them expand to display the overview when you click on them. Clicking will also filter the discussion by cause, initiative, or organization.
**Election card ui** I need to make the differences between the 2 sides of the election card more obvious to viewers
**Pool metrics** Your commmittment stays in the system until you decide to pull it out. There should be statistics for "Guaranteed pool" and "Committed pool". These include both your personal votes and the overall votes
**Phase 2 cause.html experience** When a phase 2 mission is selected, the lhs cards should show potential orgs instead of the next-phase tivs.
**Apache infra** I'm probably going to use some apache software like Kafka, Flink, Airflow, and Cassandra in the future. Lets add that to infra.
**Start date everywhere** The cause page rhs cards should have the start date as well.
**Profile ring** - My goal was to have a large ring sticky to the rhs of the page, and have the profile badge in the top right corner. I know this is difficult because at certain sizes it would be hard for them to not overlap. I think it would look cool and futuristic that way. We don't need to implement this yet but I'm keeping the design on the backburner. 
**Cause page flip** Let's flip the phases on the cause page so phase 1 is at the bottom and phase 5 is just below the header. So during phase 1, there are 4 "This phase is not yet active" rows and the bottom row shows the initiative election.
**Org table filtering** Need a better filtering method than initiative. Idea - table still filters by cause, and any org with multiple initatives shows up in both tables. Later - sub-filter for initiatives within the cause.
**Org profile** - Place where orgs build a budget, a plan, interact with the community, post updates, communicate with EN, etc. Cause page becomes mission page
Change the background color within the text boxes to creamy white
**Initiative proposal** When proposing an initiative, users should also be able to look through preexisting initiatives.
**Org registration/nomination** 
*Find orgs* In the registration/nomination dialog, there needs to be a way to paruse/search/scroll through all orgs that are in the db.
*Home page* The dialog should be the same from the home page button as well
**Phase 1** Doesn't need the initiative-suggested section
a. *pre mode* When a phase has not yet begun, it and all future phases need to display the pre text - not phase 1 but the rest
*redesign* Move the "share remaining" to a different location. This whole thing needs to look better. The lhs section in the phase area can be removed. It's taking up unnecessary space. 
**Posting to the right categories**
- Context/Analysis - cause-specific with optional tiv-tag for phase 1 election, tiv-specific with optional org-tag for phase 2 election.
- Case - must be cause and tiv specific
- Evaluation - must be org specific, tiv optional
*Seperate discussion categories* There will be a precise description of how users navigate the discussion. This is after we move the overview into the table. 
**Remove** onclick from annulus 1 to cause page.
**When no next-initiative votes** Allow users to click "Show next mission" and do phase 1 experience on cause page.
**Active cause and center focus** The 2 upcoming votes need to capture the users attention. This shold be the case on all pages. Maybe - A glowy now marker or just a highlighted block on the cause page showing which is in the org section and which is the next tiv vote. 
**Vote visualization** Add ability to see how many votes and the general size of each vote's commit.
**Voting acts like it works when not logged in** The phase 1 and 2 voting interface pretends to work when not logged in, even when the voting doesn't actually do anything. This is a minor issue, but makes the experience a bit confusing. We need 'log in to vote' on this page like it is on the home page. It should not be possible to do any voting when not logged in. Currently, it shows a different count whether im in account 1, account 2, or logged out. I think the issue may be connected with an inability to divide votes into shares of less than 1, and an inability to withdraw votes in the backend.
**Show future dates for each mission** These should be made visible. This will come when the page state changes upon cause 3 shift.
**View initiatives cause card link**