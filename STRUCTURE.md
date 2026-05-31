## UPDATE TASKS
@CLAUDE Stop process now if there are any lines in between here and ##SYSTEM
## SYSTEM
**Cause rotation - 7 weeks**
Atmosphere - Oceans - Land - Forests - Wildlife - Rights - Progress
**Weekly missions - 4 phases**
1. Pre-Initiative-Election: weeks < 1
The rankings are always visible in the 
2. New-Initiative: weeks 1 - 8
3. New-Mission: weeks 9 - 16
4. Credit-Release: weeks 17 - 32
5. Resolution: weeks 33+
**Voting**
1. Initiative voting
Can plit votes
2. Organization voting
Can only vote for 1 organization.
**Development**
`backlog management` Update structure and content of readme
`build` Is for making changes.
**index.html**
This page shows every past, present and future mission 
__________________________________________________________________________________________________
|You donate.          |                 Top card                            |             profile |
| We follow.          |                                                     |                     |
| ____________________|                                                     | ____________________| 
|| Side card 1       ||                                                     || Side card 6
||                   ||                                                     ||...
||                   ||                                                     ||...
||                   ||_____________________________________________________||...
||___________________|                          |                           ||____________________|
| ____________________                    `           '                     ||____________________
||  Side card 2      |             /                        \               ||
||                   |            |         Date             |              ||
||                   |              Upcoming initiative vote  ...
||                   |               Leader, ebx committed...
||___________________|...
| ____________________            |                          |...
||  Side card 3      |             \                        /...
||                   |                   .             ,...
||                   |             ...
||                   |      ________  ____  _________________...
||___________________|      |Filters| |for| |feed/initiatives|
|  Search initiatives _|cause dropdown|_|stage dropdown|_|rating dropdown|_____ + Propose an Initiative
| Name | Cause | EBX Committed | Status | Next vote date
| 12 rows_
|...;
|____________________________________________________________________________________________________
| News  | [selected_initiative] |
| Fill a set amount of space
|...;
|____________________________________________________________________________________________________
| ORGANIZE
| Do you and your company have the means to accomplish a mission?
| 1 - 2 - 3 - 4
| Register your organization ->
|_____________________________________________________________________________________________________
Earthbux                               Platform     Community
Collective action, measured by impact
Weekly pooled donations, insured by EN.

**Cause.html**
This page isolates a particular mission and cause
Whichever tab is selected persists color and information to the screen.
_____________________________________________________________________________________________________________________
ebx |              |              |              |              |              |              |              |profile|
    |              |              |              |              |              |              |              |
    |              |              |              |              |              |              |              |
    |              |              |              |              |              |              |              |
    |Atmosphere____|Oceans________|Land__________|Forests_______|Wildlife______|Rights________|Progress______|
        |Left - next initiative                                                     Right - 3 missions
        ||       leading     |             /                        \               ||mission currently in phase 2 |
        ||                   |            |      annulus 2           |              ||                             |
        ||                   |                ...                                   ||onclick changes page         |
        ||                   |              ...                                     ||_____________________________|
        ||___________________|...                                                   | _____________________________
        | ____________________            |                          |...           ||                             |
        ||       second      |                   .             ,...                 ||mission currently in stage 3 |
        ||                   |             ...                                      ||_____________________________|
        ||                   |  _____________  ____  ____________________ _________ | _____________________________
        ||___________________| |   Mission overview                               | ||Most recent stage 4 mission   |
                 third         |   Current phase                                  | ||______________________________|
        __________________     |__________________________________________________|  page through past missions<> - 147 days/page
|       Mission phase 1 recap or election card                                                                        |
|                                                                                                                     |
|_____________________________________________________________________________________________________________________
|       Mission phase 2 recap or election card                                                                        |
|                                                                                                                     |
|_____________________________________________________________________________________________________________________
|       Mission phase 3 recap or budget discussion                                                                    |
|                                                                                                                     |
|_____________________________________________________________________________________________________________________
|       Mission phase 4 plan                                                                                          |
|                                                                                                                     |
|                                                                                                                     |
|                                                                                                                     |
|                                                                                                                     |
|                                                                                                                     |
phase 5 will diverge between complete and incomplete

## BUILD SEQUENCE
0. Resolve Errors (if any)
1. _index.html_
- (a) **Propose-Initiative cause picker.** Proposed initiatives need to be linked to a cause. Users should select cause, title initiative, and describe it.
- (b) **MAIN TOGGLE → "View Initiative Elections" | "View Organization Elections"** See *Page toggle*  and revised *table*  section in structure. Do not replace Feed/Info toggle, but adapt it as described in structure.
- (c) **2-sided side cards and top card.** See *election cards*. Each card has a front and a back that is flippable from the page toggle.
- (d) **Center-of-annulus = NEXT cause cue.** If users vote for nothing else, they should vote for the next initiative. that is why it will be in the center. 
- (e) **Row click directs Feed/Info** The Feed/info section isolates a particular organization or initiative
2. _cause.html_
- (a) **Phase-1 card = initiative election.** see README
- (b) **Fix the initiative-election date.** see README.
- (c) **3 right cards and page flips** These cards allow the user to page through all historic missions in the selected cause. The left cards are already correctly phase 1, and the right cards show the previous 3 missions. Users can page back through all historic missions.
- (d) **Remove "now" and mini rotation arrow** This is redundant since the now marker has a working arrow.
- (e) **Connect mission-overview to the phase recaps.** See README

## QUESTIONS & CONCEPTUAL BACKLOG
1. Seeded successfully. What exactly does this do? Ran from backend this time, in the past I was instructed to run it from frontend.
2. The now marker is correct. Now we can remove "now c>" because the arrow does the job nicely
3. The top card is 2 sided. At the moment, both sides should be empty because no initiative elections have happened yet, therefore no organization elections are active yet. The front side of all election cards is actually blank. Pending functional voting system.
4. See answer below
5. Center should be an extension of the top-right side card.
6. Ratings described below.
7. Benefactor accounts store watched initiatives.

**Center redesign**
**Cause page now marker** We will be able to add more labels, for example at the start and end of the causes active area we can write "Initiative election" and "Organization election"
**Vote share** Users automatically use their entire vote share and when selecting more initiatives to vote for, they choose how to divide it.
**Initiative ratings** Each initiative carries a rating that defaults to 0/5 and every benefactor can simply rate each initiative. By rating, initiative is added to a users watchlist. They can remove it from the watchlist however without nullifying thier rating.
**Watched initiatives** Displayed on profile page. Affects a users EN feed.
**`cyclestart` config endpoint** I want to run simulations and this will be necessary to understand. I will need to read the code.
**Build-integrity check** It seems like we have this under control. What's IIFE?
**`tempfile + os.replace` write helper.** Another tool to get the build integrity under control
**Stage 2 toggle** Toggle "View Initiative Elections" and "View Organization Elections"
**Test fixtures** Will others be able to remotely access the site when I have the server running on my computer? Or do I need to get fly.io or some other server running? Otherwise, I can simply build the test accounts on my computer.

## LONG TERM
prune dead code
BYE-BYE M_INDX.html
BYE-BYE EN.html

0. Demo-ready core (now). The three public pages (index.html, cause.html, m_indx.html) look right and behave correctly, and the shareable link works for a static demo. Cleanup-level work, no new data model.

1. Initiative-vote pilot. Run the first 7 weekly initiative votes with cofounder accounts + simulated money on the existing sample initiatives/orgs (the test strategy already in this backlog). Requires the soft-vote flow to be solid end to end.

2. Mission / organization layer. The mission-page experience, in the order Jax sketched in STRUCTURE.md's CONVERSATION: (0) solidify concepts → (1) organization registration → (2) org-member mission-page creation → (3) link mission pages into m_indx + active organization election → simulate an org vote → (4) design the mission annulus.

3. Credits & cash economy. Replace "unlimited EBX" accounts with real deposits and the credit lifecycle (generic → cause → mission → org → live), the EN 5/16 cut, and tax/redemption logic. This is the gate that finally makes the founding-49-EBX bonus relevant (per Jax's Q1).

4. Hardening & reach. Tests (pytest / playwright), Postgres prod path, pagination, cycleStart from a config endpoint, build-integrity check, static offline mode, Swift mobile app.

## ERRORS
## STRUCTURE (not updated)
- [ ] **Main page** (index.html)
    - [ ] **annulus 1** - recolor - roygbiv
        - [ ] **Maximize annulus size for screen**
        - [ ] **Center of Annulus**
        Todays date, leading initiative for upcoming vote (next cause) - Once this is done, we'll figure out how to differentiate it from the top-right card. It will have details about the election and previous initiative... i dont know yet.
            - [ ] **glowy circle** Inner circle of "cause annulus* glows to represent the NEXT cause
            - [ ] **3D visual** backlog -
        - [ ] **Manipulate annulus & zoom** backlog -touchscreen
        - [ ] **`now` indicator** - UX aid for time-telling
            - ✅ **glowy marker** Glowy white vertical marker on top side of annulus. 
    - [ ] **Page toggle** Toggles whole page between upcoming org/tiv elections
        - [ ] **Location** Located below the annulus, in between the side cards, above the table.
        - [ ] **What it changes**
        - Flips all 7 cards between front (org mode) and back (tiv mode)
            - note that the top card will be the only thing on the page referencing an org while toggled to tiv mode.
        - Flips table between initiative table and organization table
            - flips between "propose an initiative" and "register an organization"
    - [ ] **Election Cards** switching to 2-sided
        - [ ] **Side cards**
            - ✅ **Location**
            - [ ] **front** upcoming *new-Mission*
            Predetermined initiative title
            leader - leader vote % - leader ring-mini
            choice - choice vote % - choice ring-mini
            Total pool so far              |discuss|
            My committment                  |Vote  |
            - [ ] **back** - upcoming *new-initiative*
            Cause name - date of mission (up to 7 weeks in future)
            choice - choice vote %
            leader - leader vote %
            second - second %
            third - third %          
            Total pool so far              |discuss|
            My committment                    |Vote|
        - [ ] **Top card** only card with 2 org-elections
            - [ ] **Glowy** top card glows white like now marker
            - ✅ **Location**
                Horizontal: In between the side cards
                Vertical: From the now marker all the way to the top of the display.
            - [ ] **front** Newest mission
            initiative title
            leader - leader vote % - leader ring-mini
            choice - choice vote % - choice ring-mini
            Total pool so far              |discuss|
            My committment                  |Vote  |
            Detailed election metrics
            - [ ] **back** This week - newest initiative
            next vote 7-8 weeks away
            various organization suggestions
            initiative info
    - [ ] **Table** - 2 states
        - [ ] **Filters** For now, keep same filters for both states
        - [ ] **State 1 - Initiative Table** leading proposed initiatives
        search   -   filters      -       Propose an initiative
        Watch | Name | cause | my ebx committed | total ebx committed | status | next vote day
            - [ ] **columns**
                - [ ] **status**
                show the phase of the initiative. If no ebx has been committed, status  is "suggested"
                - [ ] **watch** 
                users can bookmark ("watch") initiatives
        - [ ] **State 2 - Organization Table** leading organizations
        search   -   filters      -       Nominate an Organization
        Watch | Name | website_link | status | my ebx committed | total ebx committed | ring-mini
            - [ ] **Org registration** move "compete for this mission" here
                - [ ] **instructions**
                Call for charity organizations or for people to suggest charitys. We need recipients for our donations!
        - [ ] **Feed/info toggle** Does not depend on page toggle
    - [ ] **Feed/Info** - Either feed or info on selected tiv/org based on toggle at bottom of table
        - [ ] **State 1 - Initiative area** Fill area below table
        Users select a row in the table and this area expands
        - [ ] **State 2 - Feed** 
        Content from EN News
- [ ] **Cause page** (cause.html)
    - [ ] **Active missions bar**
    7 squares across the top of the screen that toggle between causes
        - [ ] **Add start dates**
    - [ ] **annulus 2**
    Center: Date, time until cause
    Tier 1 (center ring): Pie chart
    Tier 2: Highlight selected cause
    Tier 3 (Outside ring): Mission metrics
        - [ ] **Now marker**
            - [ ] **Arrow**
            good arrow, now remove circular "now" arrow
        - [ ] **Mission Progress annulus** Surrounds 2 inner sections.
        See mission section.
    - [ ] **Left Cards**
    Display options for the next initiative vote for the selected cause
    - [ ] **Right cards**
        - [ ] **Bottom** 
        Previous mission (in phase 3 or 4) of selected cause
        - [ ] **Middle** 
        Whatever mission is currently in phase 3 of selected cause
        - [ ] **Top** 
        Whatever mission is currently in phase 2 of selected cause
    - [ ] **mission story RENOVATED** there will actually be 4 different tables.
        - [ ] **New annulus** If a mission is selected, the annulus changes - backlog
        - [ ] **Top** Just below the annulus
            - [ ] **phase 1 recap**
            The vote shares and relevant posts that got the initiative elected
        - [ ] **slot below top**    
            - [ ] **if active**
            show election card
            - [ ] **else**
            Show how the people decided on the org, and mention the runners up.
        - [ ] **slot 2 below top**
            - [ ] **if active**
            benefactors and organization build an action plan
            
            phase 3 recap
            Here is where the organization (with the help of earthbux) is responsible for creating an impact
            - [ ] **phase 4 recap**
            this is where the community discusses the organizations impact
            - [ ] **phase 5** financial complexities - backlog
        - [ ] **rows** 
            - [ ] **Expandable** Rows are expandable 1 at a time.
            - [ ] **content** depends on phase
                - [ ] **mission** Each mission gets a row
                    - [ ] **phase 1** Bottom rows. White.
                    Leftmost columns populate. The bottom is 7 weeks out, which is under 6 weeks out, etc.
                    Cause_name cycle_num | decision date | your vote | your vote ratings | ebx committed | pool size | Leading initiative | second | third | ...
                    - [ ] **phase 2** Row in middle
                    Ring-mini | Cause_name| Initiative | Your pool contribution so far | org-election date | your vote | Reviews | ebx committed | pool size | Leaders
                    - [ ] **phase 3** Row above phase 2
                Ring-mini | Initiative | Organization | Your earthbucks | release date | credit | your intentions 
                    - [ ] **phase 4** Top rows. Green or red
                - [ ] **dates** join date, other dates
                backlog
                - [ ] **posts** may also be in table
                backlog
        - [ ] **columns**
            - [ ] **Ring Mini** A mini *cause annulus* is displayed next to each mission (if phase 1, it's empty). This will resemble the missions credit coin.
        - [ ] **Admin side** Admins have the full table. 
- [ ] **EN** Newsfeed
    - [ ] **Post** Post your own content.
            - [ ] **Types of post** Benefactor posts: Initiative ratings, organization reviews, mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed). Org posts: `mission proposals` (When competing for an org election), `mission_ideas`, `mission updates`, `feedback`. EBX posts: `status-updates` on the mission metrics.
    - [ ] **Rename** everything to EN (Earthbux News)
    Rename everything to "Earthbux News" or "EN" or .en if there is a space constraint.
    - [ ] **Feedback value** 
    Good posts can be awarded `cause_EBX`
    - [ ] **Filter** Everything is filtered and cropped`missionindx`. The feed improves the experience of many pages across earthbux.
- [ ] **About**
    - [ ] **Clarify core goals** Root out wasteful and fraudulent charity organizations/players, reorient peoples media consumption towards meaningful things, focus charity efforts on the cause rather than sponsors, democratize charioty by finding the best idea rather than the most profitable one, rewarding thoughtful ideas, pooling donations to prevent redundant/competing charity missions. Provide unbiased and mission-oriented news coverage of every mission.
    - [ ] **Financial structure** Committing to an initiative: 20% sent if your initiative wins, 10% if not. Committing to an organization: 100% if they win, 20% if not.
    - [ ]  **Information about how I founded the company...** My sstory. Get it working first
## MEMBERSHIPS
- [ ] **BENEFACTOR** A human who intends to vote in the election.
    - [ ] **Profile page** Benefactor profiles are mostly private
        - [ ] **Upcoming Decisions** 3 items: 
        Top: Initiative decision for cause x - link to initiative page for that cause
        Middle: Org decision for cause w - link to mission index with this expansion
        Bottom: Initiative and org for most recent mission. - links to mission page.
        - [ ] **Dropdown dialog** Credit badge has dropdown hover where users can (log in/register or) log out, view wallet, or switch to an organization account.
        - [ ] **Choices_Table** Snippet of mission index
    - [ ] **Cash flow**
    Users exchange cash for earthbucks. They can buy generic 1-cause earthbucks (can freely convert between causes), preminted ebx for a particular initiative (slight discount, less exchang freedom), or minted ebx for a determined mission in the 7-week initial period (usually a larger discount, much less mobility).
        - [ ] **Discounts** Earthbux fees are voided or discounted in certain cases
        - Benefactor committed to the winning initiative early
        - Benefactor committed to the winning organization early
        - Benefactor has achieved "Helpful" status on mission
        - Benefactor is willing to commit to a higher percentage being sent to the pool (maybe I should use "commit" here and replace previous usages of commit with "pledge"... thoughts?)
        - [ ] **Postmint** After 7-week period This will be complicated and is super backlog
    - [ ] **Verification & perks**
        - [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
        - [ ] **Credit badge colorization** Below a total donation threshold, a benefactor must have participated in the initiative and org vote to unlock the colored perk for that weeks sector. Add `vvv: bool` to `BenefactorAccount`, set after first vote.
            - [ ] **Automatic coloring threshold** threshold: $10
        - [ ] **Post visibility**
        Larger donations can unlock more visibility for your posts.
        - [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implementation: all id numbers below 100 get bonus.
- [ ] **ORGANIZATION** Organizations are mostly public, and work maximally on mission pages.
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

- [ ] **HUMAN**
backlog security questions
    - [ ] **Security** Any user of the app is verified to be a human/agent of Earthbux or an authorized organization.
## VOTES
- [ ] **Initiative vote** 
    Determines the initiative for the next mission
    Soft vote
    By contributing more, you get more vote share.
    Benefactors can split their vote down to shares of .1
        - [ ] **Initiative ratings.** 
        Posts tagged as a rating are factored into an initiative's overall rating.
        - [ ] **Committing** 
        Before adding money, one click sets a users vote to an initiaitve. Each benefactor has a vote that does not require any money to be committed.
            - [ ] **Selection day** 
            Before selection day, you can move around your vote shares as much as you want. You can add, withdraw, and move around committments. 24 hours before selection is when voting locks for counting. The pool also locks and the mission page is created.
                - [ ] **Winner** Winner of soft election enters 8-week hard election
                - [ ] **Mission page** and updated mission index
            - [ ] **Dialog** sign something convert_to_ebx
            Voting is important, you are in charge of determining and electing the fate of the planet, so don't f around.
            - [ ] **vote division** Benefactors can commit to multiple initiatives at once With every additional initiative, a benefactor is shown how they are spreading their vote share and decides how much vote to put on each initiative. Benefactors can not divide votes smaller than 0.1.
                - [ ] **Vote weight Algorithm** b is the benefactor
                Vote weight = 1 + b_contribution/(total_pool_not_including_b * n_total_votes*size_factor)
                    - [ ] **Vote division floor** 0.1
                    *"Benefactors can not divide votes smaller than 0.1."* Enforce in Commit dialog. Add to backlog → frontend Commit-dialog work + backend `Vote` validation.

- [ ] **Cause Vote**
Hard, users can only vote for one organization
Not weighted, although there are donation thresholds at which donors can buy a second, third, fourth etc. votes. These ramp up quickly though so it's still very democratic.

1. **`size_factor` in vote-weight formula.** 
optimized for a donation pool ideal size to be agreed upon later
8. **5/16 EN cut:**
    **1/16 evaluation reward.** README spells these out now. Combined ≈% of pool is non-mission.
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