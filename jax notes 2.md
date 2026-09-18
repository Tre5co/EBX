## Instructions -> Notes & structure -> Instructions
The system relies on 3 elections.
Cause election - hard to change
Mission election - Conceptual election - seperate from individual entities
Organization election - Elect a group of humans who agree to be public.
Bens park money - Goal is to get it used up. 
Orgs park influence. Goal is to perform their stated purpose.
objective-based payout model
**Causes, Initiatives, Missions**

Anyone can propose a cause. A cause worth standing up is a ubiquitously essential human experience — something nearly everyone lives through, that someone would donate to see optimized, and that is resistant to capture. Propose one, pick its colour, and make your case in the discussion: the cause election is on the Context page →

**Organizations, Discussion, News**
- HEADLINES
- **PHL addition from cause.html** Users need to be able to suggest organizations even before the initiative has been decided. In this case, they do not need to be associated with any particular initiative or cause. This is so they can tailor their page depending on how they want to fit into our structure, without being forced to make commitments they don't yet understand. There will be links elsewhere to register/nominate an org. These will take you to profile page, but when nominating for a mission currently in OE, the whole experience stays in main.html.

**Profile, Donations**
General, Various missions, different membership types - access
Ebx = membership
  - You elevate yourself to higher roles in the organization though participation.
    - Valid posts, budget item approval, donation threshold, etc. 
- Page is sorted by recent activity. 
- Donations can ALWAYS be received.
- We need the page to be usable by an org rep and a personal profile. This is to emphasize that both share the same goal.

## ASCII MODELS
Moved to docs/structure.md 2026-09-18 — each page's **DRAWING** sits above its PAGE LAYOUT (Landing §4, Profile §5, Mission §6 target + as-built, Election §7, Newsfeed + discussion box §8, Admin §9).

## Unmanaged as of yet

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
