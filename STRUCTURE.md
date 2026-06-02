## UPDATE TASKS
@CLAUDE Stop process now if there are any lines in between here and ##SYSTEM
## SYSTEM
**Our goals** Root out wasteful and fraudulent charity organizations/players, reorient peoples media consumption towards meaningful things, focus charity efforts on the cause rather than sponsors, democratize charioty by finding the best idea rather than the most profitable one, rewarding thoughtful ideas, pooling donations to prevent redundant/competing charity missions. Provide unbiased and mission-oriented news coverage of every mission.
**Cause rotation - 7 weeks**
Atmosphere - Oceans - Land - Forests - Wildlife - Rights - Progress
**Voting**
1. Initiative voting - soft
Vote-split-economy - .1 division floor.
First vote from vote-entity on main page (or cause page), subsequently managed from cause page.
2. Organization voting - hard
1 vote 1 organization.
Vote from main page, cause page or mission page.
Benefactors can publicly buy votes & By doing so buy publicity.
**Committing**
1. Initiative
Vote weight amplified by contribution amount.
20% sent if your initiative wins, 10% if not.
2. Organization
Additional votes can be bought for increasing prices.
100% sent if your organization wins, 20% if not.

**Weekly missions - 4 phases**
1. Pre-Initiative-Election: weeks < 1
    - mission page (broad template) is created.
2. New-Initiative: weeks 1 - 8
3. New-Mission: weeks 9 - 16
4. Credit-Release: weeks 17 - 32
5. Resolution: weeks 33+
**EN** Earthbux News generates interactive content
- Benefactors and Organizations post content within each mission.
Benefactor posts: 
- Initiative ratings
- organization reviews
- mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed).
Org posts: 
- `mission proposals` (When competing for an org election)
- `mission_ideas`
- `mission updates`
- `feedback`
EBX posts: 
- `status-updates` on the mission metrics.
The app will eventually allow users to have constant location monitoring, and proximity-based selection of nearby missions or nearby mission opportunities.
Benefactors and organizations can both create ratings. When they do, they have the option to create a post alongside it, which can "help". Benefactor posts that help the most can earn earthbux to their poster. If an organization helps the won earthbux actually has to go to a benefactor within that org.
**Development**
`backlog management` Update structure and content of readme
`build` Is for making changes.

## BUILD SEQUENCE
0. **Errors** Resolve if any
1. **Scratch data before launch** create dummy missions Atm-Hpr 1001-1003 (21 total) that fill these slots and are hardcoded with dates in the past when they "won" elections. Simulate that my account (GameMaster) was the only participant in the votes and create dummy organizations (orgs 1-21) and assign (those past phase 2) to dummy initiatives (tivs 1-21). Do not use sample information. Change all sample tivs to "suggested".
1. **index.html**
- (a) Build **top and side cards**
    see 4 drawings in structure. Edit top card and side cards.

2. **cause.html.**

3. **Initiative-election backend + frontend wiring.**

4. **Ratings + Watch onto the backend.**

**6 · Pruning candidates (carry-over).** Dead CSS in cause.html — `.init-table-section`, `.cause-toggle-section`, `.org-register-section`, `.init-bridge-section`, `.cause-feed-section`, `.init-detail*`, `.feed-post*`, `.mission-table*`, `.mrow-*`, `.phase-badge-*`. Dead JS — `renderTable`, `filteredInits`, `showSelectedPanel`, `fmt`. All currently guarded; safe to delete.
    GOOD SYSTEM! KEEP CANDIDATES LIST UPDATED! Purge all at once when list is very long.
    

**7 · Long-term sequencing (carried over from STRUCTURE.md):**
0. Demo-ready core (now) — index.html, cause.html, m_indx.html look right; static demo link works.
1. Initiative-vote pilot — first 7 weekly votes with cofounder accounts + simulated money, real initiatives, simulated orgs.
2. Mission / organization layer — org registration → org-built mission pages → m_indx + org election → simulated org vote → mission annulus.
3. Credits & cash economy — real deposits, credit lifecycle, EN 5/16 cut, tax/redemption. Gate that makes the founding-49-EBX bonus relevant.
4. Hardening & reach — pytest / playwright, Postgres prod path, pagination, `cycleStart` from API, build-integrity check, static offline mode, Swift app.

## ROADBLOCKS
1. Seems to be set, but I can't tell behind the bugs.

2. Good progress.

3. Good.

4. Make table collapsable but still default to open.
The important thing here is that benefactors can vote on their chosen initiative from the main page. 

TOGGLE REDESIGNED.
5. good.
6. good.
7. This doesn't cause any operational problems so can be backlogged. 
8. Still open, priority is behind voting
9. Still open, priority is behind voting
10. Drawings are complete
11. See roadblocks 1.
12. Good.

## QUESTIONS & CONCEPTUAL BACKLOG
- (c) Fix the top-card / topbar alignment.
**Center contents**
**Top card expansion**
**Cause annulus markers** e.g. at the start and end of the active area mark "Initiative election" and "Organization election"
**Initiative ratings** Each initiative carries a rating that defaults to 0/5 and every benefactor can simply rate each initiative. By rating, initiative is added to a users watchlist. They can remove it from the watchlist however without nullifying thier rating.
**Watched initiatives** Displayed on profile page. Affects a users EN feed.
**`cyclestart` config endpoint** I want to run simulations and this will be necessary to understand. I will need to read the code.

## ERRORS
**Cause page bug** Only 1 of the causes has the new phase 1 voting applied.
**Entity area table link** The table items are not doing anything onclick. Putting in errors because Claude said this was complete (roadblocks 4).
## STRUCTURE (not updated)
- [ ] **Main page** (index.html) c
    - ✅ **annulus 1** - recolor - roygbiv
        - [ ] **Maximize annulus size for screen**
        - [ ] **Center of Annulus**
        Todays date, leading initiative for upcoming vote (next cause) - Once this is done, we'll figure out how to differentiate it from the top-right card. It will have details about the election and previous initiative... i dont know yet.
            - ✅ **glowy circle** Inner circle of "cause annulus* glows to represent the NEXT cause
            - [ ] **3D visual** backlog -
        - [ ] **Manipulate annulus & zoom** backlog -touchscreen
        - ✅ **`now` indicator** - UX aid for time-telling
            - ✅ **glowy marker** Glowy white vertical marker on top side of annulus. 
    - ✅ **Page toggle** Toggles whole page between upcoming org/tiv elections
        - [ ] **Location** Located below the annulus, in between the side cards, above the table.
        - [ ] **What it changes**
        - Flips all 7 cards between front (org mode) and back (tiv mode)
            - note that the top card will be the only thing on the page referencing an org while toggled to tiv mode.
        - Flips table between initiative table and organization table
            - flips between "propose an initiative" and "register an organization"
    - [ ] **Election Cards** switching to 2-sided
        - [ ] **Side cards** Note that we will be changing ebx counts instead of %s because that allows one to estimate the total pool size
            - ✅ **Location**
            - [ ] **front** upcoming *new-Mission*
            Yes, the cause name only needs to be on the back
            ____________________________________
            |tiv_name organization race    date*| *For the org election, this is the day at the END of the active cause window.
            |1. org_name                    #ebx|
            |2. org_name                    #ebx|
            |3._org_name____________________#ebx|
            |My choice - amnt_committed - | orgs|
            |choice_name_______________ % |_____|
            - [ ] **back** - upcoming *new-initiative*
            ____________________________________
            |cause_name mission i          date*| *We fixed the election decision date on cause.html. Fix it here too.
            |1. tiv_name                    #ebx|
            |2. tiv_name                    #ebx|
            |3._tiv_name____________________#ebx|
            |My choice - amnt_committed - | tivs|
            |choice_name_______________ % |_____|
        - [ ] **Top card** only card with 2 org-elections
        The front and back are the 2 consecutive org elections in the active cause.
            - [ ] **Glowy** top card glows white like now marker
            - ✅ **Location**
                Horizontal: In between the side cards
                Vertical: From the now marker all the way to the top of the display.
            - [ ] **front** Next vote
            ____________________________________
            |tiv_name organization race    date*| *For the org election, this is the day at the END of the active cause window.
            |1. org_name                    #ebx|
            |2. org_name                    #ebx|
            |3._org_name____________________#ebx|
            |My choice - amnt_committed - | orgs|
            |choice_name_______________ % |_____|
            - [ ] **back** This week - newest initiative
            ____________________________________
            |tiv_name organization race    date*| *For the org election, this is the day at the END of the active cause window.
            |1. org_name                    #ebx|
            |2. org_name                    #ebx|
            |3._org_name____________________#ebx|
            |My choice - amnt_committed - | orgs|
            |choice_name_______________ % |_____|
        In the future, the top card will include more information.
    - [ ] **Table** - 2 states
        - [ ] **rows** Each row selects a different entity card.
        - [ ] **Filters** For now, keep same filters for both states
        - ✅ **State 1 - Initiative Table** leading proposed initiatives
        search   -   filters      -       Propose an initiative
        Watch | Name | cause | my ebx committed | total ebx committed | status | next vote day
            - [ ] **propose an initiative**
            - cause
            - title
            - description
            handle/anonymous
            - [ ] **columns**
                - [ ] **status**
                show the phase of the initiative. If no ebx has been committed, status  is "suggested"
                - [ ] **watch** 
                users can bookmark ("watch") initiatives
        - ✅ **State 2 - Organization Table** leading organizations
        search   -   filters      -       Nominate an Organization
        Watch | Name | website_link | status | my ebx committed | total ebx committed | ring-mini
            - [ ] **Org registration** move "compete for this mission" here
                - [ ] **instructions**
                Call for charity organizations or for people to suggest charitys. We need recipients for our donations!
        - [ ] **Entity toggle** There will be a front and back of the entity card (below)
        Currently says selected and news. Switch to just front and back for now and move the toggle inside the card.
    - [ ] **Entity Card** - Entity = tiv or org
    Each tiv and org in the tables opens an organization/initiative (i.e. entity) card  Front and back eventually, for now we'll only be working on front. Defaults to the leading upcoming initiative (same as top right card back and center circle), or if "view organization elections" is toggled, it defaults to the leading organization on the front of the top card. Include vote option here. If the user has already voted and its the tiv vote, notify that they can split their vote and if they want to take them to the cause page. If it's an organization say that they have already voted for x and would they like to change their vote.
        - ✅ **Location** Fill area below table
        - [ ] **Vote** Both modes include a vote button
            - [ ] **Case first vote** If a benefactor has not yet voted
            Register the benefactors vote to the selected entity
            - [ ] **else**
            org: prompt to change vote or cancel.
            tiv: prompt to divide vote, if yes move to cause page vote area.
        - [ ] **case tiv**
            - [ ] **Initiative ratings.** 
            Posts tagged as a rating are factored into an initiative's overall rating.
        - [ ] **case org**
- [ ] **Cause page** (cause.html)
    - ✅ **Active missions bar**
    7 squares across the top of the screen that toggle between causes
        - [ ] **Add start dates**
    - [ ] **annulus 2**
    Center: Date, time until cause
    Tier 1 (center ring): Pie chart
    Tier 2: Highlight selected cause
    Tier 3 (Outside ring): Mission metrics
        - ✅ **Now marker**
            - [ ] **Arrow**
            good arrow
        - [ ] **Mission Progress annulus** Surrounds 2 inner sections.
        See mission section.
    - ✅ **Left Cards**
    Display options for the next initiative vote for the selected cause
    - ✅ **Right cards**
        - [ ] **Bottom** 
        Previous mission (in phase 3 or 4) of selected cause
        - [ ] **Middle** 
        Whatever mission is currently in phase 3 of selected cause
        - [ ] **Top** 
        Whatever mission is currently in phase 2 of selected cause
    - [ ] **mission story RENOVATED** 5 sections that fill as the mission progresses, creating one big section.
        - [ ] **New annulus** If a mission is selected, the outer annulus changes - backlog
        - [ ] **Header row** Mission overview. Move card to connect with section below.
        - [ ] **Top** Just below the annulus
            - [ ] **phase 1 recap**
                - [ ] **if active**
                show election card and cause info
                Cause_name cycle_num | decision date | your vote | your vote ratings | ebx committed | pool size | Leading initiative | second | third | ...
                - [ ] **else**
                Show how the people decided on the tiv, and mention the runners up.
        - [ ] **slot below top**
            - [ ] **phase 2 recap**
            When an initiative wins an election, the mission page template is created. This populates phase 2 in cause.html with a discussion of the initiative and the potential organizations to run it. It must include a discussion option. Posts to a wall, comments, images, ratings, I don't know and I'm open to suggestions. There are definitely 2 main categories - posts meant to educate about the initiative, and posts meant to educate, advertise, or criticize organizations.    
                - [ ] **if active**
                show election card
                Ring-mini | Cause_name| Initiative | Your pool contribution so far | org-election date | your vote | Reviews | ebx committed | pool size | Leaders
                - [ ] **else**
                Show how the people decided on the org, and mention the runners up.
        - [ ] **slot 2 below top**
            - [ ] **if active**
            benefactors and organization build an action plan
            Ring-mini | Initiative | Organization | Your earthbucks | release date | credit | your intentions 
            - [ ] **else**
            phase 3 recap
            Here is where the organization (with the help of earthbux) is responsible for creating an impact
            - [ ] **phase 4 recap**
            this is where the community discusses the organizations impact
            - [ ] **phase 5** financial complexities - backlog
        - [ ] **items**
            - [ ] **Ring Mini** A mini *cause annulus* is displayed next to each mission (if phase 1, it's empty). This will resemble the missions credit coin.
        - [ ] **Admin side** Admins have the full table. 
## MEMBERSHIPS
- [ ] **BENEFACTOR** A human who intends to vote in the election.
    - [ ] **Profile page** Benefactor profiles are mostly private
        - [ ] **Upcoming Decisions** 3 items: 
        Top: Initiative decision for cause x - link to cause page phase 1 for that tiv
        Middle: Org decision for cause w - link to cause page phase 2 for that org
        Bottom: Initiative and org for most recent mission. - links to mission page.
        - [ ] **Dropdown dialog** Credit badge has dropdown hover where users can (log in/register or) log out, view wallet, or switch to an organization account.
        - [ ] **Choices_Table** All of a users upcoming decisions.
        - [ ] **Discounts** Earthbux fees are voided or discounted in certain cases
        - Benefactor committed to the winning initiative early
        - Benefactor committed to the winning organization early
        - Benefactor has achieved "Helpful" status on mission
        - Benefactor is willing to commit to a higher percentage being sent to the pool (maybe I should use "commit" here and replace previous usages of commit with "pledge"... thoughts?)
        - [ ] **Postmint** After 7-week period This will be complicated and is super backlog
    - [ ] **Verification & perks**
        - [ ] **Feedback value** 
        Good posts can be awarded `cause_EBX`
        - [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
        - [ ] **Credit badge colorization** Below a total donation threshold, a benefactor must have participated in the initiative and org vote to unlock the colored perk for that weeks sector. Add `vvv: bool` to `BenefactorAccount`, set after first vote.
            - [ ] **Automatic coloring threshold** threshold: $10
        - [ ] **Post visibility**
        Larger donations can unlock more visibility for your posts.
        - [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implementation: all id numbers below 100 get bonus.
- [ ] **ORGANIZATION** Organizations are mostly public, and work to build mission pages.
Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org employee. Once approved as a candidate, they put all important information on a mission page which continues if they win and is frozen and linked from their profile if not.
    - [ ] **Profile page** 
    Organization profile pages are very similar to benefactor profile pages. 
        - logo
        - missions
        - posts
        - [ ] **Memberships**
        Human representative of the weekly mission - Every org account is a member...
            - [ ] **Contributor**
            Benefactor who voted for org/possesses credits for mission
            credits=membership
            This will build a community.
            - [ ] **Representative**
            Person with permissions to edit mission page
            - [ ] **Executive**
            Highest level of member permission
            - [ ] **Beneficiary**
            Representative for the recipient of the charity effort
    - [ ] **Missions page**
    Home page for organizations.
        - [ ] **Mission registration**
        If an initiative is open (won one of the 7 causes) organizations can compete for that pool if they have a sufficiently developed page for that initiative. If they already have one, it becomes unfrozen when the initiative is elected.
        Organizations fill out mission pages for whatever initiative they want to apply for. Once the election is active everything becomes linked together by election widgets, and when it's over one organization gets to claim the mission. Every stage hass a success metric and a cash reward.
        - [ ] **Mission structure**
        Organizations accomplish mission goals to earn as much money as possible
            - [ ] **Budget phase**
            Once the mission begins, all committed money is locked for 7 weeks. This is the early mission period, when the organization learns how they can best earn the full pool. 
            - [ ] **Evaluation Phase**
            After 7 weeks, 1/16 of the credits are released to the benefactors who provided the best contributions, and for the weeks after that, the money is released to a combination of the organizaion and the benefactors. 
            - [ ] **Mission credit** Represented by a coin, value changes.
                - [ ] **Parameters**
                - Benefactor satisfaction
                - Earthbux satisfaction
                - Mission metric completeness
                - Budget adherance - efficiency
                - Transparency
                - Misc. accomplishments/failures
        - [ ] **Progress reports** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
        - [ ] **Mission Annulus** Backlog - 4 now just do a multi-sectored annulus.
        Each mission gets its own ring widget which is on the cause page. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from ring minis on homepage or mission index to mission page. Will increase in complexity. 7-12 steps which can just be labeled 1-12 and will all link to the mission page. This will beome the 3rd outer annulus on the cause page.
        - [ ] **Organization logos.** 1/2 of credit coin.
        Color wheel idea --backlog
## CREDITS
- [ ] **Credits** a credit is 1 EBX
Life cycle: Generic -> cause-tagged -> mission-tagged -> organization-tagged -> Live
    - [ ] **Conversion** $1 = 1 credit
        - [ ] **Coin value** Exactly 1 for the first 7 weeks
            EBX maintain a value of $1 7-weeks-post-mint
            Unminted EBX can be exchanged for cash. They are not tax deductable yet.
    - [ ] **Exchange** Non-donation exchanges
        - [ ] **Transactional logic** 
        Coins operate similarly to a cryptocurrency, can be exchanged for coins from other missions.
            - [ ] **Any gains are not tax deductable**
    - [ ] **Donation**
        - [ ] **Tax deductable**
        All minted credits are tax-redeemable. Only happens after it has been committed to a charity and converted.
        - [ ] **The rest is now in your wallet**
          - [ ] **EN Thresholds** We only take money if the pool is above $100. 
          - [ ] **5/16 EN Cut** Users are notified that 5/16 % of their money is going to Earthbux News (EN) and they/we go and help the mission in any way we can while reporting and chase them if we have to.
              - [ ] **1/16 to evaluation**  
              Included in Earthbux 5/16.
              - [ ] **1/4 to our side of the mission**
              We will create a budget.
    - [ ] **Badge**
    Users possessing the credit have it displayed on their profile. It is the ring-mini for that mission annulus.
        - [ ] **Coin visual** Coins are mini cause annuli their mission-specific cause solely highlighted  The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission from m_indx