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
    - [ ] **Benefactor Profile**
        - [ ] **Design**
            ______________________________________________________
            | _____________                         ____  _______ |
            ||CreditCoin   |                       | b  ||       ||
            ||<   Wallet  >|                __     |____||   a   ||
            ||_____________|           '           `     |_______||
            ||choices   |          '                  `     | c  ||
            || table    |                                   |____||
            ||          |    /                             \      |
            ||          |            Annulus 3                    |
            ||          |   |         front/back toggle     |     |
            ||          |                                         |
            ||__________|    \                             /      |
            |                                                     |
            |                     .                     ,
            |                               __
        - [ ] **Annulus 3** Specific to each benefactor
            Empty for now
        - ✅ **Choices_Table** All upcoming decisions (14)
            - ✅ **Toggle** between initiatives and orgs
            - ✅ **Selections** All of a benefactors current votes are displayed here. Each links to its respective cause page.
                - ✅ **For multiple tiv selections** Only show the top one for now
            - [ ] **Expand** Backlog - Choices table will eventually be more in depth, similar to a stock trading interface.
        - [ ] **Top Right section**
            - [ ] **Credit Badge** a - Username and annulus
                - [ ] **Colorization** Participating each week colorizes your credit badge for that weeks sector
                Below a total donation threshold, a benefactor must have participated in the initiative and org vote to unlock the colored perk for that weeks sector. Add `vvv: bool` to `BenefactorAccount`, set after first vote.
                    - [ ] **Automatic coloring threshold** threshold: $10
            - ✅ **Settings** - b
            - ✅ **Switch to Organization mode** - c
            If a benefactor has the credit coin, they have access to org mode for that mission
            If they do not, every org page is still linked from it's cause page mission
        - [ ] **CreditCoin Wallet**
            - [ ] **Contents**
            Each mission will have a unique logo, which becomes the credit coin. They will link from the wallet to the Mission page. Backlogged because logos are still a concept
            - ✅ **Design** 
            Contains all missions a benefactor has contributed to. Scrolls left-right
    - [ ] **Organization Profile** User profile to represent a specific org.
    Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org rep (the user automatically gets a benefactor profile too). Orgs build a mission page which continues if they win and is frozen and linked from their profile if not.
        - [ ] **Design** 
            ______________________________________________________
            | _____________                         ____  _______ |
            ||Initiative   |                       | b  ||       ||
            || Coins       |                __     |____||   a   ||
            ||_____________|           '           `     |_______||
            ||Tasklist  |          '                  `     | c  ||
            ||          |                                   |____||
            ||          |    /                             \      |
            ||          |            Annulus 4                    |
            ||          |   |         front/back toggle           |
            ||          |                                         |
            ||__________|    \                             /      |
            |                                                     |
            |                     .                     ,
            |                               __
        - [ ] **Annulus 4** Almost identical to Annulus 3.
            Empty for now
        - [ ] **Top right section** 
            - [ ] **Settings** - b
            - [ ] **Switch to Benefactor mode** - c
        - [ ] **Tasklist**
        - ✅ **Initiative coins** Every initiative that the org has ever registered for produces a coin which toggles the page.
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
            Representative for the recipients of the charity effort
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
            - [ ] **back** upcoming phase 3
            ____________________________________
            |tiv_name                      date*| *Last day of cards upcoming active window
            |1. org_name                  #votes|
            |2. org_name                  #votes|
            |3._org_name__________________#votes|
            |My choice - choice_name     |ebx   |
            |My committment_-_x_ebx______|pool__|
            - [ ] **front** - upcoming phase 2
            ____________________________________
            |cause_name mission_num        date*| *First day of cards upcoming active window
            |1. tiv_name                  #votes|
            |2. tiv_name                  #votes|
            |3._tiv_name__________________#votes|
            |My choice - choice_name     |ebx   |
            |My committment_-_x_ebx______|pool__|
        - [ ] **Top card** only card with 2 org-elections
        The front and back are the 2 consecutive org elections in the active cause.
            - [ ] **Glowy** top card glows white like now marker
            - ✅ **Location**
                Horizontal: In between the side cards
                Vertical: From the now marker all the way to the top of the display.
            - [ ] **back** upcoming phase 3
            ____________________________________
            |tiv_name                      date*| *Last day of current active window
            |1. org_name                  #votes|
            |2. org_name                  #votes|
            |3._org_name__________________#votes|
            |My choice - choice_name     |ebx   |
            |My committment_-_x_ebx______|pool__|
            - [ ] **front** Most recent phase 2
            ____________________________________
            |tiv_name                      date*| *Last day of NEXT active window (in 7-8 weeks)
            |1. org_name                  #votes|
            |2. org_name                  #votes|
            |3._org_name__________________#votes|
            |My choice - choice_name     |ebx   |
            |My committment_-_x_ebx______|pool__|
    - [ ] **Table** - 2 states
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
        One sector highlighted denoting selected cause
        - ✅ **Now marker**
            - ✅ **Arrow**
    - ✅ **Left Cards**
    Display options for the next initiative vote for the selected cause
        - [ ] **Pagination** Page through all initiatives with votes for that cause
        - [ ] **Links** Link to home page area for that initiative
    - ✅ **Right cards**
    Onclick, each card changes the mission story section to its mission.
        - [ ] **Top** 
        Whatever mission is currently in phase 2 of selected cause
        - [ ] **Middle** 
        Previous mission
        - [ ] **Bottom** 
        Mission before that
        - [ ] **Subsequent pages**
        Every past mission in chronological order.
    - [ ] **mission story** 5 sections that fill as the mission progresses, creating one big section.
    *Note* for phase 1 and 2, "vote" appears 6 times. This refers to the helpful|neutral|wrong voting for discussion posts.
        - [ ] **Header row** right below the annulus, in between left and right cards.
        Just the cause name, and cycle number, or the mission title and organizaiton name if applicable.                ____________
        __________________________|Brief header|__________________________
        |Phase 1 area                                                    |
        - [ ] **Phase 1** Bottom section
            - [ ] **when Active**
                        "Organization voting begins when the initiative is elected"
             __________________________________________________________________________________
            |    | ____________  ______________________________________________________________|
            | 1. ||Leaders     || Selected post                                           |   ||
            |ini-||            ||                                                         | a || a: 3-way toggle between leading case, context, and analysis for this mission.
            |tia-|| List up to ||_________________________________________________________|___||
            |tive||   10 and   | _____________________________________________________________ |
            |ele-|| each ebx   || Slider voting. Top row: uncommitted                         ||
            |cti-|| share      ||                                                             ||
            |on -||            ||                                                             ||
            |    ||            ||                                                             ||
            |sta-||            ||                                                             ||
            |rt  ||            ||                                                             ||
            |date||            ||                                                             ||
            | -  ||            ||Bottom Row: Selected tiv "split vote" if not yet committed   ||
            |end ||____________||_____________________________________________________________||
            |date| _____  _____  ______________________  _________  ___________________________|
            |    ||Pool ||My   ||Purchase xxxebx <rate>|||Convert||| Selected tiv title & link||
            | *  ||_____||comit||______________________||_________||__________________________|| * Make text sideways
            |____|_____________________________________________________________________________|
            - [ ] **When Recap** Discussion locks after vote
            Show how the people decided on the tiv
            _____________________________________________________________________
            | _________  _________   _______________|Discussion|_________________|
            ||Winner   ||My votes | |Most_helpful_case______________________<>|go|
            ||2nd      ||         | |Winning intiative description               |
            ||3rd______||_________| |____________________________________________|
            ||pool size||My commit|_|See election details__v_____________________|
            |_______Election details dropdown-backlog____________________________|
        - [ ] **Phase 2** Above phase 1 card.
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
            |__|View organizations|_|Commit ebx|_________________________________|
            - [ ] **When Recap**
            _____________________________________________________________________
            | _________  _________   _______________|Discussion|_________________|
            ||Leaders  ||My vote  | |Most_helpful_evaluation________________<>|go|
            ||         ||         | |Winning organization mission statement      |
            ||_________||_________| |____________________________________________|
            ||pool size||My commit|_|See election details__v_____________________|
            |_______Election details dropdown-backlog____________________________|
        - [ ] **Phase 3** Budget phase - Above phase 2
        Once the mission begins, all committed money is locked. Organization learns how they can earn the full pool. 
            - [ ] **Pre** Display 1-line "This phase is not yet active"
            - [ ] **when active**
            ________________________________________________________________
            |           |   Phase 3 Info                      |             |             
            |           |                                     |
            |           |                                     |
            |           |_____________________________________|                 
            |       \                 _________                   /
            |           \           /             \            /     
            |               \                               /         
            |                 \ /                     \ /            
            |         in       |      Annulus4         |     out   
            |                  |                       |             
            |                  / \                     / \            
            |              /                                \        
            |           /           \  __________  /            \
            |      /                                                \
            - [ ] **Recap**
        - [ ] **Phase 4** Evaluation phase - Above phase 3
        After phase 3, 1/16 of the credits are released to the benefactors who provided the best contributions, and for the weeks after that, the money is released to a combination of the organizaion and the benefactors. 
            - [ ] **Pre** Display 1-line "This phase is not yet active"
            - [ ] **Progress reports** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
        - [ ] **Phase 5** Resolution just below header.
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
            - Benefactor is willing to commit to a higher percentage being sent to the pool
        - [ ] **Post rewards** Benefactors are awarded ebx if they contributed the most helpful post.
        - [ ] **Post visibility**
        Larger donations can unlock more visibility for your posts.
        - [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implementation: all id numbers below 100 get bonus.