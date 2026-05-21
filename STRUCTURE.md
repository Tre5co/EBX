## README.md

## UPDATE TASKS
@CLAUDE Stop process now if there are any lines in between this one and the most recent pass
## 8:30 5/21/26 (pass 4)
**Q1** Pending application. I've already donte this but it won't be relevant until users accounts don't have unlimited ebx and need to deposit money, which is super-backlogged for now.
**Q2** Nothing was wrong. My bad, I forgot to remove that.
**Q3** I see, the same initiative won 2 cycles in a row because they both used the same sample data. Everything is fine as it is because it will work when actual voting begins. 
**Q4** Top card is ok for now.
## 4:50 5/20/26 (pass 3)
**Q1** I was hoping it could actually go up into the topbar. Is that possible? Maybe it would need to be a seperate thing in the topbar that connects to the rest of the page? I want the bottom next-initiative banner to be aligned with the bottom of the side cards, and push the top card upwards.
**Q2** Should be all set. Is there something missing?
## 3:45 5/20/26 (pass 2)
**Q20** Top card: In pass 1, my instructions for the bottom card were incorrectly interpreted as top card instructions, and now the structure does not reflect the design. Please revert back to the structure described in structure tree. (A slight change from what it was before)
**Q21** Bottom card: Implement 1 row ticker here.
**Q22** Satisfactory
**Q23** Done, seeded successfully.
## 10:45 5/20/26 (pass 1)
**Q17**
I think there was some damage caused by me stopping processes while partially complete.
**Q18**
Probably same issue as q17, pre-commit hook that fails on a second `EBX_TAIL_SENTINEL` occurrence is a good idea. Let's make it happen.
**Q20** See structure tree

**Q21** Yes, 

**Q22** No, side cards should be designed at the maximum size and be compressed for smaller displays in the future. Expand annulus wherever possible. 

## CONVERSATION (For backlog management)
I think the truncation issues are happening when I scroll within the claude app as you are executing tasks. I'll refrain from doing that.
You say that it's already substantially built, and I can see that, but the link is not working. Do I need to do some building commands?

Yes, building out the mission experience is complex and will need a precisely planned design.
I want to make sure we do these mission pages right. I'll propose steps.
0. Discuss details and solidify concepts and plan, cut off loose ends.
1. Create organization registration.
- I suggest we 
2. Mission page creation by org members.
3. Link mission pages to mission index
 - *Active organization election*
3. simulate vote
4. Design mission annulus

## BUILD SEQUENCE (For build)
0. Resolve Errors
1. **Dont jump on click** Minor problem in cause.html
2. **Side card update** on index.html per updated structure
3. **m_indx.html build-out** See conversation
 - Columns and rows
 - color code, expand
4. **Mission page buildout**
mission.html - the org-side mission page for them to work on their mission. Information: mission.html -> m_indx.html
5. **Implement Voting** 
6. **Credits** if id <= 100, mint 49 generic EBX credits into wallet.
    - Pretend each credit is worth $1
    - This will actually allow the process to begin.
## ERRORS
None, Good!

## STRUCTURE
- [ ] **Main page** (index.html)
    - [ ] **Cause Cards**
        - [ ] **Top card**
            - [ ] **Contents** 
            2 current organization elections for the active cause.
            This week upcoming upcoming on left
            7-8 weeks away (newest) on rightBacklog finalization
                - [ ] **Location**
                Horizontal: In between the side cards
                Vertical: From the now marker all the way to the top of the display.
                - [ ] **Right** This week - newest initiative
                Pool size, election date...
                - [ ] **Left** Newest mission
                Larger area with detailed metrics for upcoming hard election. Leaders with links to their mission page prorotypes, link to EN feed for discussion, display current votes and committments from `mission_indx`.
            - [ ] **Expansion** - backlog interface
            Scroll-triggered expand upward/outward.
            The upcoming organization election is the most important moment at any given time so a lot of information here. 
        - [ ] **Bottom banner**
        Directly below the annulus, in between the left and right cause cards
        Ideally we can make it a 1-row display that can be immediately digested as quickly as possible -
        benefactor experience: see initiative I committed for with it's standing among other initiatives, may toggle to the leading initiative somehow. Those should be the only words on the page, everything else should be widgets/diagramatic/visual - quickly digestible.
            - [ ] **Upcoming Initiative Decision**
            That's what this banner is for. Change it to the color of the cause after the active cause and display the leader/metrics.
        - [!] **Side  Cards** Pass 1 edit
        Top section: Your Initiative -- Your Initiatives current vote share (spill to multiline just for this top row)
                        leading initiative - leading %  |Vote  |
                        second - second %               |  or  |
                        third - third %                 |Commit|
                        Total pool so far: x            
        Bottom section: [initiative] - ring-mini
                        your organization -- your organization vote share
                        leader - leader % - leader ring-mini
                        Total pool so far: x
        If there is no initiative/organization slotted in for a particular date, show "No votes yet"
    - [ ] **Cause annulus**
        - [ ] **Maximize display space**
        Keep inner circle at current size, maximize outer circle all the way to the inner edge of the cards. Lock left and right card edges to the edges of active card w light padding. Slide down on top of `now` mark
        - [ ] **Cause label Visibility** Make annulus thicker so that cause titles are fully visible. Multi-word entries can take multiple lines.
        - [ ] **Center of Annulus**
        > Eventually, there will be a very cool 3d graphic in the middle. Hold that in the back of your mind because I'm not ready to create it yet. 
    
        - [ ] **Navigate and zoom**
        On mobile this will be important. There will be a zoom (And rotate) for users to select a particular sector and that will work well with touchscreens.
        - [ ] **`now`** Glowy
    - [ ] **Active missions bar**
    Links to the 7 active missions (1 cycle ahead of the organization elections)
        - [ ] **Add start dates**
    - [ ] **Feed snippet**
    - [ ] **About snippet**
        - [ ] **Update** Make up to date with current readme
        - [ ] **Combine** Combine "Put your profile to work" section into the same snippet
    - [ ] **Need orgs!!**
    Replace "Put your profile to work" section with a call for charity organizations or for people to suggest charitys. We need people to be the recipients of the donations!
- [ ] **Mission Index page** (m_indx.html)
    - [ ] **Initiative Table** Each box will link somewhere different   
        - [ ] **Rows** Dates moving forward, one week at a time.
        Each mission is a row in `mission_indx`. populated with the initiative, organization, and more information.     
        The background color of upcoming mission rows (down on table) is different from ongoing missions (scroll to the top to find the first one.) The color of the missions with an initiative but no organization is the color of that cause (Middle, and middle of page when it opens)
            - [ ] **Expandable** Rows are expandable 1 at a time.
            - [ ] **Indicate user join date**
                - [ ] **Active organization elections**
                For the 8 active elections at any given time, the row expands into a whole table with all the organizations who are trying to win the pool.
        - [ ] **Columns** Different boxes populated for different scenarios. Time flows from left to right
            - [ ] **Pre Initiative Election** Leftmost columns populate
            Cause_name cycle_num | decision date | your vote | your vote ratings | ebx committed | pool size | Leading initiative | second | third | ...
            - [ ] **Post Initiative Election**
            Ring-mini | Cause_name| Initiative | Your pool contribution so far | org-election date | your vote | Reviews | ebx committed | pool size | Leaders
            - [ ] **Post organization election** Still working on this.
            Ring-mini | Initiative | Organization | Your earthbucks | release date | credit | your intentions 
            - [ ] **Ring Mini** Mini annulus. Links to a mission page. Display in corner of m_indx toggled by current selection.
                - [ ] **Mission selected** The mission annulus from the cause page, but with its stats expanded through the page so represented by small circle in corner.
                - [ ] **Mission not selected** 
                    - [ ] **days left> 2** The cause annulus
                    - [ ] **2 > days left** The initiative annulus for the upcoming cause
        - [ ] **Admin side** Admins have a different table. 
- [ ] **Cause/Initiative page** (cause.html)
    - [ ] **Initiative annulus**
    Center: Date, time until cause
    Tier 1 (center ring): Pie chart
    Tier 2: Highlight selected cause
    Tier 3 (Outside ring): Mission metrics
        - [!] **Now marker**
        Marker is currently rotating in the wrong direction.
            - [ ] **Indicate motion direction**
            with a little arrow
        - [ ] **Handle when vote is 100% or no votes yet**
        If only 1 or 0  initiatives has received votes, Drop pie chart and add text to center.
        - [ ] **Mission Progress annulus** Surrounds 2 inner sections.
        See mission section.
    - [ ] **Left Cards**
    Display options for the next initiative vote for the selected cause
    - [ ] **Right cards**
        - [ ] **Bottom** 
        Previous mission in selected cause, 0-7 weeks into funds release
        - [ ] **Middle** 
        Most recent mission (initiative and organization) for selected cause, approaching funds release
        - [ ] **Top** 
        Upcoming organization election for selected cause with Initiative name and the benefactors current organization selection.
        Links to m_indx because no mission page yet.
        Also links to organization page on feed.
    - [ ] **Initiative cards**
    Expand when their initiative is selected in table
        - [!] **Don't jump on click** Small bug - the initiative cards and the cards left of the annulus on cause.html are jumping/scrolling to the feed on click. Remove this.
        - [ ] **Table** Shows all initiatives for that cause
        Name | proposal_link | conception date | ebx committed |
    - [ ] **Feed**
    Content from EN News, if any, is shown with each initiative
        - [ ] **Filters**
        Moved to right sidebar, labeled "Filter". Sticky on desktop, collapses horizontal on mobile.
    - [ ] **Initiative Logos** 
    One half of the credit coin. Contains all the information on the initiative side, like what the initiative is and how it garnered all its support.
    - [ ] **Admin** 
    Admin can remove initiatives, other tasks.
    Works from mission index page
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