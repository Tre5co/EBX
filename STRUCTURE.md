## SYSTEM
- **Our goals** Motivation
Streamline and publicize charity missions. Expose wasteful or fraudulent organizations/players. Reorient media consumption towards meaningful efforts, focus charity on the cause, not the sponsors. Democratize ideas to find the best one, not the most profitable one by rewarding thoughtful ideas, pooling donations to prevent redundant/competing activities. Provide unbiased and mission-oriented news coverage independently.
- **7-Cause-Rotation** Each week, a mission focused on one of these causes begins.
Atmosphere - Oceans - Land - Forests - Wildlife - Human Rights - Human Progress
**Mission Phases** Missions have a detailed structure.
1. Pre-Initiative-Election: weeks < 1
2. New-Initiative: weeks 1 - 8
3. Budget: weeks 9 - 16
4. Credit-Release: weeks 17 - 32
5. Resolution: weeks 33+
**Phase 1** Initiative Voting
Vote-split-economy - .1 division floor.
Vote weight amplified by contribution amount.
20% sent if your initiative wins, 10% if not.
Vote tallied on the first day of its causes active period.
**Phase 2** Organization Voting
1 vote 1 organization.
Additional votes can be bought for increasing prices.
100% sent if your organization wins, 20% if not.
Vote occurs on the final day of its causes active period
**Phase 3** Budgeting
**Phase 4** Credit Release
**Phase 5** Resolution
**EN** Interactive content from benefactors, organizations, and Earthbux News.
## STRUCTURE
- [ ] **Profile page** Settings/Profile page for anybody on app (Benefactor/Organization/Admin)
    - [ ] **Design**
    ______________________________________________________
    | _____________                         ____  _______ |a. Profile badge
    ||CreditCoin   |                       | b  ||       ||b. Upcoming initiative decision
    ||Wallet       |                __     |____||   a   ||c. Upcoming organization decision
    ||_____________|           '           `     |_______||
    ||choices   |          '                  `     | c  ||
    || table    |                                   |____||
    ||          |    /                             \      |
    ||          |            Annulus 3                    |
    ||          |   |                                     |
    ||          |                                         |
    ||__________|    \                             /      |
    |                                                     |
    |                     .                     ,
    |                               __

    - [ ] **Annulus 3** Specific to each benefactor
    - [ ] **Choices_Table** All upcoming decisions (14)
        - ✅ **Toggle** between initiatives and orgs
        - [ ] **For multiple tiv selections** Only show the top one (temp)
        - [ ] **Expand** Choices table will eventually be more in depth, similar to a stock trading interface.
    - [ ] **Credit Badge**
        - [ ] **Colorization** Participating each week colorizes your credit badge for that weeks sector
        Below a total donation threshold, a benefactor must have participated in the initiative and org vote to unlock the colored perk for that weeks sector. Add `vvv: bool` to `BenefactorAccount`, set after first vote.
            - [ ] **Automatic coloring threshold** threshold: $10

    - [ ] **Org page** User profile to represent a specific org.
    Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org rep (the user automatically gets a benefactor profile too). Orgs build a mission page which continues if they win and is frozen and linked from their profile if not.
        - [ ] **Design** -backlog
        ______________________________________________________
        | _____________                         ____  _______ |
        ||             |                       | b  ||       ||
        ||             |                __     |____||   a   ||
        ||_____________|           '           `     |_______||
        ||          |          '                  `     | c  ||
        ||          |                                   |____||
        ||          |    /                             \      |
        ||          |            Annulus 4                    |
        ||          |   |                                     |
        ||          |                                         |
        ||__________|    \                             /      |
        |                                                     |
        |                     .                     ,
        |                               __
        - [ ] **Annulus 4** Specific to each organization
        - [ ] **Memberships** Page view and permissions depend on them
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
        - [ ] **Organization logos.** --backlog
        Color wheel idea
    - [ ] **Settings**
        - [ ] **Settings window scope elaboration**
        - [ ] **Testing**
            **`is_test` column.** Lets us test without using real ebx.
            **`cyclestart` config endpoint** I want to run simulations and this will be necessary to understand. I will need to read the code.
- [ ] **Home page** (index.html)
    - ✅ **annulus 1** - recolor - roygbiv
        - [ ] **Maximize annulus size for screen**
        - [ ] **Center of Annulus** More refinements soon
            - ✅ **glowy circle** Inner circle of "cause annulus* glows to represent the NEXT cause
            - [ ] **3D visual** backlog -
        - [ ] **Manipulate annulus & zoom** backlog -touchscreen
        - ✅ **`now` indicator** - UX aid for time-telling
            - ✅ **glowy marker** Glowy white vertical marker on top side of annulus. 
    - ✅ **Page toggle** Toggles whole page between upcoming org/tiv elections
        - ✅ **Location** Located below the annulus, in between the side cards, above the table.
    - [ ] **Election Cards** switching to 2-sided
        - [ ] **Side cards** Note that we will be changing ebx counts instead of %s because that allows one to estimate the total pool size
            - ✅ **Location**
            - [ ] **front** upcoming phase 3
            ____________________________________
            |tiv_name                      date*| *Last day of cards upcoming active window
            |1. org_name                  #votes|
            |2. org_name                  #votes|
            |3._org_name__________________#votes|
            |My choice - My committment  |ebx   |
            |choice_name_____x_ebx_______|pool__|
            - [ ] **back** - upcoming phase 2
            ____________________________________
            |cause_name mission_num        date*| *First day of cards upcoming active window
            |1. tiv_name                  #votes|
            |2. tiv_name                  #votes|
            |3._tiv_name__________________#votes|
            |My choice - My committment -| ebx  |
            |choice_name______x_ebx______|pool__|
        - [ ] **Top card** only card with 2 org-elections
        The front and back are the 2 consecutive org elections in the active cause.
            - [ ] **Glowy** top card glows white like now marker
            - ✅ **Location**
                Horizontal: In between the side cards
                Vertical: From the now marker all the way to the top of the display.
            - [ ] **front** upcoming phase 3
            ____________________________________
            |tiv_name                      date*| *Last day of current active window
            |1. org_name                  #votes|
            |2. org_name                  #votes|
            |3._org_name__________________#votes|
            |My choice - My committment  |ebx   |
            |choice_name_____x_ebx_______|pool__|
            - [ ] **back** Most recent phase 2
            ____________________________________
            |tiv_name                      date*| *Last day of NEXT active window (in 7-8 weeks)
            |1. org_name                  #votes|
            |2. org_name                  #votes|
            |3._org_name__________________#votes|
            |My choice - My committment   |ebx  |
            |choice_name_____x_ebx________|pool_|
    - [ ] **Table** - 2 states
        - [ ] **Description** "Click on a row to interact"
        - ✅ **rows** Each row selects a different entity card.
        - [ ] **State 1 - Initiative Table** leading proposed initiatives
        Table only displays phase 1 tivs.
            - ✅ **Filters**
            - ✅ **propose an initiative**
            - cause
            - title
            - description
            handle/anonymous
            - [ ] **Design**
            search   -   filters      -       Propose an initiative
            Watch | Name | cause | my ebx committed | total ebx committed | tiv vote day
            - [ ] **column details** (some of them, more incoming)
                - [ ] **phase**
                show the phase of the initiative. If no ebx has been committed, status  is "suggested"
                - [ ] **watch** 
                users can bookmark ("watch") initiatives
        - [ ] **State 2 - Organization Table** leading organizations
            - [ ] **Filters** Mission, status, etc. idk yet
            - [ ] **Org registration** move "compete for this mission" here
                - [ ] **instructions**
                Call for charity organizations or for people to suggest charitys. We need recipients for our donations!
            - [ ] **Page design**
            search   -   filters      -       Nominate an Organization
            Watch | Name | website_link | status | my ebx committed | total ebx committed | ring-mini
            - [ ] **Column details** More to come.
        - [ ] **Entity toggle** There will be a front and back of the entity card (below)
        Currently says selected and news. Switch to just front and back for now and move the toggle inside the card.
    - [ ] **Entity Card** - Entity = tiv or org. Defaults to the leading upcoming initiative/the leading organization
        - [ ] **Front and back** Replaces News/selected. For now we'll only be working on front. 
        - ✅ **Location** Fill area below table
        - [ ] **Vote** Both modes include a vote button
            - [ ] **case org**
            - [ ] **case tiv**
- [ ] **Cause page** (cause.html)
    - ✅ **Active missions bar**
    7 squares across the top of the screen that toggle between causes
        - [ ] **Add start dates**
    - [ ] **annulus 2**
        - [ ] **Inner**
        Pie chart for initiative voting
        - [ ] **Outer**
        Pie chart for organization voting
        - ✅ **Now marker**
            - ✅ **Arrow**
    - ✅ **Left Cards**
    Display options for the next initiative vote for the selected cause
    - ✅ **Right cards**
    Onclick, each card changes the mission story section to its mission.
        - [ ] **Bottom** 
        Previous mission (in phase 3 or 4) of selected cause
        - [ ] **Middle** 
        Whatever mission is currently in phase 3 of selected cause
        - [ ] **Top** 
        Whatever mission is currently in phase 2 of selected cause
    - [ ] **mission story** 5 sections that fill as the mission progresses, creating one big section.
    *Note* for phase 1 and 2, "vote" appears 6 times. This refers to the helpful|neutral|wrong voting for discussion posts.
        - [ ] **Change annulus** If a mission is selected, the outer annulus changes - backlog
        - [ ] **Header row** right below the annulus, in between left and right cards.
        Just the cause name, and cycle number, or the mission title and organizaiton name if applicable.                ____________
        __________________________|Brief header|__________________________
        |Phase 1 area                                                    |
        - [ ] **Phase 1** Top card, below the header
            - [ ] **when Active** 
            _____________________________________________________________________
            | _________  _________   _______________|Discussion|_________________|
            ||Leaders  ||My votes | ||vote|Most_helpful/trending_case_____<>|post|
            ||         ||         | ||vote|Most_helpful/trending_context__<>|post|
            ||_________||_________| ||vote|Most_helpful/trending_analysis_<>|post|
            ||pool size||My commit|_|Search for an initiative____________________|
            | Display area for an initiative. Default to top vote. If none leader|
            | Slider vote bars (or just 'vote'), with new selected tiv option.   |
            |         discussion                                                 |
            |_|view initiatives|__|commit ebx|___________________________________|
            - [ ] **When Recap** Discussion locks after vote
            Show how the people decided on the tiv
            _____________________________________________________________________
            | _________  _________   _______________|Discussion|_________________|
            ||Winner   ||My votes | |Most_helpful_case______________________<>|go|
            ||2nd      ||         | |Winning intiative description               |
            ||3rd______||_________| |____________________________________________|
            ||pool size||My commit|_|See election details__v_____________________|
            |_______Election details dropdown-backlog____________________________|
        - [ ] **Phase 2** Below phase 1 card.
        When an initiative wins an election, the mission page template is created. This populates phase 2 in cause.html with a discussion of the initiative and the potential organizations to run it. It must include a discussion option. Posts to a wall, comments, images, ratings, I don't know and I'm open to suggestions. There are definitely 2 main categories - posts meant to educate about the initiative, and posts meant to educate, advertise, or criticize organizations.    
            - [ ] **Pre** Display 1-line "This phase is not yet active"
            - [ ] **When Active** Similar to phase 1 when active
            When the initiative is decided, organizations can compete for that pool. If they already have a page, it becomes unfrozen when the initiative is elected.
            One organization gets to claim the mission.
            _____________________________________________________________________
            | _________  _________   _______________|Discussion|_________________|
            ||Leaders  ||My vote  | ||vote|Most_helpful/trending_eval_____<>|post|
            ||         ||         | ||vote|Most_helpful/trending_context__<>|post|
            ||_________||_________| ||vote|Most_helpful/trending_analysis_<>|post|
            ||pool size||My commit|_|Search for an organization__________________|
            | Display area for an organization. Default to vote. If none leader. |
            | Show discussion and org supplied content                           |
            |                                                                    |
            |_|View organizations|_|Commit ebx|__________________________________|
            - [ ] **When Recap**
            _____________________________________________________________________
            | _________  _________   _______________|Discussion|_________________|
            ||Leaders  ||My vote  | |Most_helpful_evaluation________________<>|go|
            ||         ||         | |Winning organization mission statement      |
            ||_________||_________| |____________________________________________|
            ||pool size||My commit|_|See election details__v_____________________|
            |_______Election details dropdown-backlog____________________________|
        - [ ] **Phase 3** Budget phase
        Once the mission begins, all committed money is locked. Organization learns how they can earn the full pool. 
            - [ ] **Pre** Display 1-line "This phase is not yet active"
            - [ ] **when active**
            benefactors and organization build an action plan
            Ring-mini | Initiative | Organization | Your earthbucks | release date | credit | your intentions
            - [ ] **Recap**
        - [ ] **Phase 4** Evaluation phase
        After phase 3, 1/16 of the credits are released to the benefactors who provided the best contributions, and for the weeks after that, the money is released to a combination of the organizaion and the benefactors. 
            - [ ] **Pre** Display 1-line "This phase is not yet active"
            - [ ] **Progress reports** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
        - [ ] **items**
            - [ ] **Ring Mini** A mini *cause annulus* is displayed next to each mission (if phase 1, it's empty). This will resemble the missions credit coin.
        - [ ] **Admin side** Admins have the full table. 
- [ ] **Credit page** - in progress. Forms at phase 3
Note that this whole page is backlogged until after completion of phases 1 & 2.
    - [ ] **Mission Annulus** Backlog
    Each mission gets its own ring widget. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from ring minis on homepage or mission index to mission page. Will increase in complexity. 7-12 steps. This will beome the 3rd (outer) annulus on the cause page.
    - [ ] **Credits** a credit is 1 EBX
            - [ ] **Mission credit** Represented by a coin, value changes.
                - [ ] **Parameters**
                - Benefactor satisfaction
                - Earthbux satisfaction
                - Mission metric completeness
                - Budget adherance - efficiency
                - Transparency
                - Misc. accomplishments/failures
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

## STRUCTURE MISC.
    - [ ] **Verification & perks**
        - [ ] **Discounts** EBX is discounted in certain cases
            - Benefactor committed to the winning initiative early
            - Benefactor committed to the winning organization early
            - Benefactor has achieved "Helpful" status on mission
            - Benefactor is willing to commit to a higher