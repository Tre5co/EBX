## I start here
**Broad (ongoing changes)**
- [ ] Replace org/organization replace with "philanthropy"
- [ ] Replace misison support with "research"

**Specific (enactable now)**

**Specific (future)**
- Image attachments on posts —Image generation technology? Build an image search tool that finds/creates a good open source picture to represent the mission.

**Conceptual**
How a cause changes

The seven causes are meant to be hard to change — they are the standing subjects the whole system elects inside, so a week of enthusiasm should not move one. A challenger has to win the same window 7 weeks in a row. Lose a single week and the streak resets, and the swap date moves back by a full rotation.

A replacement is elected at least one full rotation (7+ weeks) before the ME.

Anyone can propose a cause. A cause worth standing up is a ubiquitously essential human experience

1. **CE**
Replace the cause election as an area on top of the election panel. It can persist across ME/OE. Design:
 _________________________________________________________________________
|      |    c                                                      |      |
|   a  |    f          g        h             i                    |  b   |
|      |    d                                                      |      |
|      |    e                                                      |      |
|______|___________________________________________________________|______|

a. We only need 1 column of 7 horizontal lines that get colored as the weeks go by
b. Show Cause Table
c. "Cause Election - ..." This row is good.
d. Keep [x] or replace with [y]
e. Clickthrough of possible causes
f. Nominate a Cause
g. Make your case
h. Commit
i. Cancel

note: the cause toggle in the CE is no longer necessary - it is toggled by the main page cause toggle (see below)

2. **More Election Page**
Move the ME/OE toggle from above to below the annulus, and remove the horizontal line to its right.

Move the 7-cause page toggle from the top of the page to in between the top of the annulus and the top cards. This will function as a toggle for the ME table and the CE panel as well as the election panel.

Move the just-elected mission from the lhs to the rhs top card. instead of "Winner of Forests: Invasive species removal in vermont. Elected Aug 25, 2026.", add a bar at the top of the card with "Winner of Forests" and a bar at the bottom with "Elected Aug 25, 2026."
Similarly, add a bar at the top of the budgeting card saying "Winner of Indiginous Land Title Fund" and a bar at the bottom saying "Elected <date>"

Add a new ME card below (top right side card), and shift each other card clockwise so that the upcoming ME election is now the top lhs card. Keep the orientation of the OE cards the same.

The "To vote" line should only be on the lhs top card. Make it say "Select a cause, and vote."

Replace the filter below the table with a button "Show all Initiatives"

For now, move the allocations panel to the very bottom of the page until its design is complete. The bottom of the side cards should now be flush with the top of the election panel.

Add the rays to the election annulus, but turn them into '<' symbols to indicate the direction of the dot & cards. 

Remove the rays from the Discussion page annulus, and reverse the direction the svg annulus sections are pointing.

Add to the discussion page above the annulus "Click on a cause to participate in the discussion."

Need a deselect or cancel button next to commit everywhere.


 — something nearly everyone lives through, that someone would donate to see optimized, and that is resistant to capture. Propose one, pick its colour, and make your case in the discussion: the cause election is on the Context page →
The fine print, in four lines

1, 2, 3, & 4 above correspond to a, b, c, & d in the drawing below. It would be helpful to have a better structural representation of both of these elements combined.
 __________________________________________________
|________________________k_           _____________| 
|______a_____|______b_____||_____c____||______d____| tabs
|                                                  |
|                       i                          |
|__________________________________________________|
|                       h                          |
|__________________________________________________|
|_______e________|_______f________|_______g________| tabs
|                      j                           |
|__________________________________________________|

k. Results of previous section - note design edit (assume we are post initiative election and pre philanthropy election for this example)- Whichever section has the most recent date should be connected to this area visually.
a. Cause confirmed
b. Mission open - when toggled, explain context in research and tiv case in reviews
c. Initiative elected - When toggled, explain investigation in research and phl case in reviews - also explain s/s/s in budgeting
d. Philanthropy elected - When toggled, explain analysis in research and evaluation in reviews - also explain budgeting in s/s/s
e. Research (Grayed until cause confirmed) (Context only in a-b, Context&Investigation in c, Context&Investigation&Analysis in d)
f. Reviews (tiv cases in a-b, phl cases in c, evaluations in d)
g. Budgeting (Grayed out until tiv elected) - Explain each of s/s/s
h. Explanation area - with the exception of budgeting, there is only 1 explanation per conbined-tab-toggle
i. Input dialogue
j. Leading post in that category for that mission

SECTIONS H + I DETAILED
 ____________________________________________________________
|  __c______________________________________________         |
| |                                                 |    e   |
| | d                                               |    f   |
| |                                                 |    g   |
| |                                                 |    h   |
| |_________________________________________________|    i   |
|______________________ b              ______________________|
|  _______________________________________________________   |
| |                                                       |  |
| |_______________________a_______________________________|  |
|____________________________________________________________|

a. about (including reward, voting)
b. Selection between different posts where applicable (Context/Investigation/Analysis)
c. Post title
d. Main post dialogue
e. Linked tivs
f. linked phls
g. linked budget items
h. linked media
i. external links

Context page should be called the "Election" page.

Swap the annuli between the election and discussion pages. Also move the page toggles across the top from the discussion to the eleciton page. 

Now the pie chart annulus is on the election page, which makes more sense. We can add pie-chart vote counting for the OE and CE. 

Maybe we should move the annulus from the discussion page onto the main page? Swap the 2 annuli? Move the 7 tabs also to the election page?

Dates in the cause cards are still wrong.

Seperating user choices from total tallies.

Ok. Major page swap incoming. Move the table to the profile page. This is the same as the choices table. Move the discussion to the main page. 

**News on discussion page** - Headlines on the election cards?
1. **Profile page buildout**
- You have your general profile, which is used to elect. You also have your mission profile, which gives you access to active missions.
  - You receive minted EBX when you receive org membership
  - You elevate yourself to higher roles in the organization though participation.
    - Valid posts, budget item approval, donation threshold, etc. 
- Token/EBX conversion hub
  - Tokens can be converted to EBX at rate. 
  - Any ongoing mission may receive ebx. Newer missions less likely to be funded.
  - That's okay because of projected app growth. 
- Globe with benefactor at center. Geolocate different initiatives/organizations.
- 1 mission at a time, always?
 - 1 at a time when in org mode
- Page is sorted by recent activity. 
- We need the page to be usable by an org rep and a personal profile. This is to emphasize that both share the same goal. Earthbux admin should also use these pages to build membership roles. Some of the user-specific items can be removed from the main page. 


- I need a better solution to deal with the possibility but not abuse of reallocation of tokens. Maybe: tokens can only be moved forward in time? Yes. I like this. So scrap the 3 total transactions, and we don't need to assign tokens with a date. Just a rule. You can only move tokens from newer to older causes and not the other way around. So yes, a user could, week after week, add every new dollar to a maturing mission. But they can't, even with purchased tokens, move them from a preexisting mission to a newly created one. We will be able to visualize this nicely with the election cards because of their arrangement by graying out those behind the selected card while the user is transferring tokens.

The issue with this is that all cash eventually ends up at the front mission, which gives unfair precedence to the oldest mission - the earliest mission automatically receives ridiculous amounts of money. BUT users are able to take money out of missions once they are into the budgeting stage, which will then be able to be put back into new missions. 


- The top card left area has room for a short description/instructions on how to vote. "Propose an initiative" should be removed from this area. The "Mission x was initiated..." should say "Winner of for1: x initiated y" and this chould be below the card. The description/instructions should be above the card. 
It should say. "To vote, select the election type, and click on one of the 7 cards. Then allocate your tokens."

- Main needs to indicate that this page is for the first 2 phases of the election, before the mission really starts. Instead of "Context" at the top, say "Voting phase"
- Admin should be able to remove initiatives, posts, orgs, etc. by the same mechanism which removes benefactors.

Voting no longer happens in EBX. It happens in tokens. We need to remove "EBX" everywhere from the voting area. It's confusing because votes and ebx appear to be seperate. (They kind of are, votes can carry more or less weight depending on how many tokens are behind them).

The OE race pool is not updating when I commit votes.

Allocations should be 
Allocations: 88 tokens - $8.80 - 



1. **CE Work** More updates in structure.md top card section.
2. **OE** It's starting to crystallize. Redesign and updates in structure.md main.html backlog.


- **PHL addition from cause.html** Users need to be able to suggest organizations even before the initiative has been decided. In this case, they do not need to be associated with any particular initiative or cause. This is so they can tailor their page depending on how they want to fit into our structure, without being forced to make commitments they don't yet understand. There will be links elsewhere to register/nominate an org. These will take you to profile page, but when nominating for a mission currently in OE, the whole experience stays in main.html.

A token is a vote, not yet a donation.
    Earthbucks are all identical and transferable — one Earthbux dime, worth 10¢, the same in anyone's hands. None of them is a donation until it is labelled with an organization.
Labelling it is called finalizing.
    Finalized money can be converted between missions; it cannot be exchanged back for cash. What you hold after that is a credit token, and it becomes a credit coin belonging to the winning organization once it is donated.
Backing the winner moves it automatically.
    If the organization that wins is the one you voted for, the coin moves on its own. If it isn't, you have 7 weeks to decide how much of your original share to commit — floor 10% of what you first committed.
So the worst case is small.
    Dislike both the cause and the organization that wins it, and the most you can lose is 10% twice. We audit these organizations as publicly as we can — that is the whole product. Give through us.

the organization — elected in phase 2, the pooled donation recipient the initiative — elected in phase 1, the mission it claims

        *make your case →*, then the race with a **%** on both sides, the
        suggestion pager, the seven windows abbreviated onto one row (ATM · OCE ·
        LAN · FOR · WIL · HR · HP, full name in the title attribute), the streak
        bars, and a one-line footer. Note (i) below is done: the paragraph is on
        the landing page.
 _______________________________________ _______________________________________
|+ Propose an initiative for oce1       | propose a cause to replace <a>        | a. oce2 if streak unbroken. else oce3
                                        | cause input   color     make your case| "make your case" links to the discussion where the user writes a case for the cause
                                        | vote - [oceans]<%> [<proposition>]<%> | % displays the percent of the vote each have
                                        | clickthrough and select other sugg.<%>| This row allows users to look at and vot on the causes others have proposed 
                                        | 7 causes toggle*                      | *Abbreviate so they all fit in one row
                                        | horizontal bars display               |
                                        |<i>____________________________________|i. ✅ 2026-08-10 — moved to `index.html#cause-change` ("How a cause changes"), which also clears the landing backlog's "Add cause change explanation". The card links to it.


     ______________________________________________________date_
    |winning_tiv Organization Election      |total fund   |     |         
    | ______________________ |  my_vote | my_commit     |vote  || This row shows which organization the logged-in benefactor has their vote going towards
p2  ||Leaderboards*         | _______  ______   _______        || *Not the recap, which it currently says. this is the organization race which will be elected at the date above
    ||                      ||sent   ||Limbo  ||wdrawn ||wdraw || *This row is all totals, not specific to benefactor
    ||                      ||_______||_______||_______||purchs||
    ||______________________|___________________________________|
    | evaluations of selected org or the one they are voting for| if none selected from leaderboard. Links to the expanded table row for that org.
    | Analysis for this mission                                 |
    |___________________________________________________________|
    _______________________________________________________date
    |"        *                "   |Posts recap:                | *As is
    | WINNER                       | best case for              |
p1* | ___my_vote. its_%_of_total__ | leading contex             | *recap
    || 2nd, 3rd, 4th.*            ||                            |* Only those 3. 
    ||                            ||                            |
    ||____________________________||                            |
    |______________________________|____________________________|

- [x] **Cause election 'cause to replace'** — BUILT 2026-08-06. Toggle moved to the bottom under "Select cause to replace"; the threshold is now **7 weeks in a row** (one per streak column). Still framed — the ballot, the suggestions and the streak are local to the page until the cause vote has a backend (README §4).

a. Vote button for active cause
b. Vote button for alternative cause
c. << suggestions >> (page through alternative cause suggestions) (display eachs' vote share)
d. "Replace <cause> with <cause_suggestion> on <date>"
e. Dialogue for a user to suggest a cause. (Automatically populates c)
f. submit
g. 7 columns. The leftmost (active) has 1 horizontal line and the rightmost (previous) has 7. The lines glow the suggested new cause color as they win successive weeks. If they lose, the bars all turn to the current cause color, and <date> in d. gets pushed back by 7 weeks.
h. The 7 causes, toggle buttons for the card
i. Select cause to replace"

Cause Election Upgrade
 _______________________________________ _______________________________________
|+ Propose an initiative for oce1       | propose a cause to replace <a>        | a. oce2 if streak unbroken. else oce3
                                        | cause input   color     make your case| "make your case" links to the discussion where the user writes a case for the cause
                                        | vote - [oceans]<%> [<proposition>]<%> | % displays the percent of the vote each have
                                        | clickthrough and select other sugg.<%>| This row allows users to look at and vot on the causes others have proposed 
                                        | 7 causes toggle*                      | *Abbreviate so they all fit in one row
                                        | horizontal bars display               |
                                        |<i>____________________________________|i. The description at the bottom must be moved to the landing page.



Earthbux are voting tokens.

The benefactors should be encouraged to carry their earthbux through successive phases of the mission. 


The system relies on 3 elections.
Cause election - hard to change
Mission election - Conceptual election - seperate from individual entities
Organization election - Elect a group of humans who agree to be public. 

I've seeded with these causes.

Bens park money - Goal is to get it used up. 
Orgs park influence. Goal is to perform their stated purpose.

Bens decide which mission gets the money.
Orgs work for more money (over 1/4 just by winning election!) - objective-based payment model

Security reasoning- You cannot join just to vote on an org.

In order to deduct the taxes, you need to guarantee the spending of that money. This is optional, but possible by surrendering the money to earthbux (like a foundation).

The problem with good systems is that once they become corrupted, it stays that way. 
That's why you need to allocate resources towards a thick skin.
The cause needs to be a ubiquitously essential experience of humans that someone would donate to have optimized.


For each mission, diaplay 

Next things
- "Research" should replace "Mission Support"
- For the table vote splitters, they only have 10 votes. Cannot split your commit to more than 10 tivs.
-   - the weight of your vote is multiplied by (your commitment) / (sum of all commitments)
- Active missions also need to be shown in the main table. aand...
- Table 2 should not be a table of organizations. It should be a table of initiatives that are active. The table is different, but is still organizaed by the causes and initiative titles are still the titles. 
Landing - Show examples of 2 missions. Active and Upcoming. Active explains org vote and budgeting, upcoming shows initiative election and explains causes.
"
The system is carefully designed to maximize positive impact through democracy. Voters elect an initiative each week with a preassigned cause. (link to initial-causes justification and more information)*
This initiative becomes the mission, and voters spend the next 8 weeks electing the organization who will receive the funds for the mission.
After the organization is determined, voters each have a vote on budget items. 
"

*Where does cause-change logic and experience live?

P1 election:
The rows will also function as the leaderboard, because users will be able to sort them by their vote share.

- The winners of each post have created not only information but an exceptional discussion, and have cash that can be distributed to those who work hard. 

- The slider bar voting widget can be copied to profile.html. We will also integrate a vote-splitter in each row of the initiative table in the form of a text box that you can click to change the vote +/- 1 at a time if you want and a row at the top that is "uncommitted".
- 
- Below this, we have the discussion, in which 
- For phase 1, evaluation, Investigation, and analysis are grayed out. Evaluation is also grayed out through phase 2.

ststus (current votes, age, if_active, winning case, posts that WON (if applicable), org running it, key dates.).
- Can benefactors distribute their ebx at will?
- Center and large "Earthbux News" with subtitle-you donate, we follow". Landing page middle.
- OK. Rocking with missioncandidacy and orgclaim... The gate here is important. We need to really explain out the next step of the experience and how it is legal.

    Every benefactor has a summed yearly accumulation of donated money. This number accumulates as the organizaiton and earthbux receive their cut. They are notified that a large portion 
    A central mechanism of the Earthbux system is that benefactors, organizaitons, and ourselves are incentivized to put actual work into solving real problems, executing real missions. We do this by distributing various cash rewards.
    (most) Rewards come in the form of creditcoins (CC). (the case and evaluation rewards are not financial). Earthbux is paying mission members for their continued support.
    Let's change it - the initial value of EBX for each cause is 0. That way, the initial donation is deductable.
    The organization agrees to pay excess funds to the benefactors, by simply pouring it into the credit coin. This becomes convertible to cash and can be reinvested.
    This emphasizes the fact that missions can be COMPLETED, and that a noninfinite amount of money will maximize the efficiency.
    The amount of shares initially minted depends not on the total investments, but on the vote ownership. 
    If a mission is completed, 

    
    What is happening? The organizationagrees to pay Earthbux for consulting and research. Earthbux pays the benefactors as mission members/employees, which is legal, right?

- Let's also talk about funding. The first 5/8 of the pool is released equally to EN and the org. Earthbux budgets towards a background context report, an investigative report on the org, and a dedicated PR/relationship team for the  

- Fix the org election experience. It's ugly.
- The active cause active mission top card has many errors.

- [x] Context page profile is in a new line — FIXED 2026-08-10 (§5). Three
  columns wasn't enough: brand and page tag were both `auto`, so either could
  squeeze the badge cell to zero and wrap it. Now `auto auto minmax(0,1fr)` with
  `min-width:0` + `nowrap` on the badge. Also: `.ebx-home-mark` is fixed at
  top-left over the brand — hidden on this page.
- [x] main glowy marker pointing — already built 2026-08-05 (`.st-now`).
- [x] Colored sectors ray outwards. — already built 2026-08-05 (`rayGroup`).



Handling ties:
In the last election, I think I voted 5 each to make solar grids more efficient and global education access grid. What ended up happening was Global Education Access Grid won, and it says I committed 4.5 votes (not possible) and the total fund is 5 and I'm trying to figure out what to do. This issue will have to be resolved on a case by case basis and in the future it will be extremely rare.
Right now: org decisions: Human rights: sep 8 (correct) human progress: nov 3 (wrong) atmosphere: sep 22 (wrong)


### LANDING
    ___________________________________________________________________
    |EBX___________________________________________________profile_____|
    |                                                                  |
    |                                                                  |
    |                            a                                     |
    |                                                                  |  
    |                                                                  |
    ||_________________________________________________________________|
    ||                              | ___________ __________ _________ |
    ||                              ||          ||         ||         ||
    ||              b               ||    p1    ||   p2    ||   p3    || p1->main, p2->cause, p3->mission (links)
    ||                              ||          ||         ||         ||
    ||______________________________||__________||_________||_________||
    |                                                                  |
    a. "In 2023, Earthbux was created with one goal: Democratize and publicize charity. Capital warehouses of large private endowments hold trillions of dollars, incentivizing the most capable organizations to work for the richest grantmakers while ignoring the opinions of most people. Meanwhile, public charities fund professional fundraisers instead of the missions they allegedly support. (1) Earthbux operates ethically inside a system that doesn't require transparency by leveraging community engagement and independent news production to give donors control of their donations."
    b. "The System - 3 Phases - All Community-Controlled
    1 Initiative Election
    2 Organization Election
    3 Budgeting & Resolution"
    In 2026, the world seemed at risk of total destruction.
    Earthbux was invented to give us control so we save it.
    A public forum to direct pooled philanthropic missions.
    An independent research team to publicize their impact.
    ------------------------------------------------------
    Earthbux gives donors ability to be real benefactors with a say in the budget and execution of missions.
    The system relies on your voting and participation in weekly elections of the pooled donation recipient.
    This organization claims an elected initiative and undertakes the mission alongside the whole community.
    Your role as an Earthbux Community Member:
    The weekly recipient of the pool is an organizaiton fully determined by the voters.
    3/32 of the total funds are used to compensate researchers from our community. The rest is donated.
    Each mission gets a credit coin, which changes based on their credability and determines the amount of allocations available to them at any moment.

### CONTEXT
- [ ] **Side cards** Note that we will be changing ebx counts instead of %s because that allows one to estimate the total pool size
    - ✅ **Location**
    - [ ] **back** upcoming phase 3
    ____________________________________
    |a              b                 c |
    |f                                  |
    |d                                  |
    | [vote]      [orgs]      [discuss] |
    |___________________________________|
a. "<days> d left"
b. "<tiv_title>"
c. "<election_date>"
f. "<total_pool> -> <leading_org> (<percent>%)"
d. "<user_commit_amount> -> <user_org_vote> (<user_org_percent_of_total_pool>%)"
[orgs] -> mission.html for this initiative

    - [ ] **front**
    ____________________________________
    |a              b                 c |
    |f                                  |
    |d                                  |
    |   e                               |
    | [vote]                  [discuss] |
    |___________________________________|
a. "<days> d left"
b. "<cause> <number>"
c. "<election_date>"
f. "<total_pool> -> <leading_tiv> (<percent>%)"
d. "<user_top_commit_amount> -> <user_top_tiv> (<user_top_tiv_percent_of_total_pool>%)"
e. "<user_amount> of votes to other initiatives or uncommitted."


- [ ] **Top card**
    - [ ] **right** upcoming phase 3
    ____________________________________
    |tiv_name                      date*| *Last day of current active window
    |1. org_name                  #votes|
    |2. org_name                  #votes|
    |3._org_name__________________#votes|
    |My choice - choice_name     |ebx   |
    |My committment_-_x_ebx______|pool__|
    - [ ] **left** Most recent phase 2
    ____________________________________
    |tiv_name                      date*| *Last day of NEXT active window (in 7-8 weeks)
    |1. org_name                  #votes|
    |2. org_name                  #votes|
    |3._org_name__________________#votes|
    |My choice - choice_name     |ebx   |
    |My committment_-_x_ebx______|pool__|

Active missions table:
Top row: org voting dialog
<cause#> | <tiv_name> | <org> (or phase 2) | <pool> | <pool_spent> | <credit_value>

### MISSION
 _________________________________________________________________________________________
|                  |                                                  |                  |
|       a          |                   g                              |         b        |
|__________________|                                                  |__________________|
|                   \                      ____                      /                   |
|                     \                                            /                     |
|                       \                                        /                       |
|                         \ /                                \ /                         |
|                          |                                  |                          |
|         c                                  e                                 d         |
|                                                                                        |
|                          |                                  |                          |
|                         / \                                / \                         |
|                       /                                        \                       |
|                     /                    _____                   \                     |
|___________________/                                                \___________________|
|                                                                                        |
|      f                                                                                 |
|                                                                                        |
|                                                                                        |
|________________________________________________________________________________________|

a. mission toggle left<>right with a search bar that users can look up initiatives, which all have their own page.
b. profile and membership status (if mission is active, all users have a membership status)
c. Stream of most recent posts in one of the 3 categories for the specific initiative/mission. Toggle the 3 categories at the bottom.
d. Dated log of updates in mission progress. For example "Finished <rank> in <cause>", "Advanced to P2 with <amount> EBX", "Approved <budget-item> for <cost>"
e. Circle displaying the current phase and status of the initiative. Ultimately this will be a 3d globe.
f.Information about how much money is in the pool, how much is committed, & how much has been withdrawn.
g. Name and core info about the initiative.