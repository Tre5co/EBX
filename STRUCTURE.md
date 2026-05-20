## README.md

## UPDATE TASKS
@CLAUDE Stop process now if there are any lines in between this one and the most recent pass
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

## BUILD SEQUENCE
0. Resolve Errors
1. **Answer top card question** Top card has the same initiative in both left and right. Should be different, but might be happening because we're using sample data. Let me know.
**Align bottom card** bottom of bottom card aligns with bottom of side cards, pushes annulus and top cards up.
2. **cause.html Now-marker** Better, but still wrong. I know how to do it. The correct marker will be in the same location around the circle no matter which cause is selected.
3. **100% or 0% vote share**
- Handle 0 or 1 initiative votes
    - Annulus needs to be divided by vote-share
    - We're actually handling an empty or 100% 1-way pool since partial-vote logic is not there yet.
3. **m_indx.html build-out** -- After cause.html reshuffle
 - Columns and rows
 - color code, expand
4. **Implement Voting** Seperate org vote from initiative vote.
5. **Credits** if id <= 100, mint 49 generic EBX credits into wallet.
    - Pretend each credit is worth $1
    - This will actually allow the process to begin.
## ERRORS
None, Good!

## JAX QUESTIONS
- I'm wondering why it sometimes takes a long time for updates to fully ship. Yesterday, I looked at the site 15 minutes after updating it and got a bunch of errors, but when I looked at it this morning it was fine. What's going on? I think it's multiple things at once.


## STRUCTURE
- [ ] **Main page** (index.html)
    - [ ] **Cause Cards**
        - [!] **Top card**
        2 current organization elections for the active cause.
        This week upcoming upcoming on left
        7-8 weeks away (newest) on right
            - [ ] **Contents** Backlog finalization
            Both sections should be titled with the initiative title.
                - [ ] **Location**
                Horizontal: In between the side cards
                Vertical: From the now marker all the way to the top of the display.
                - [ ] **Right** This week 
                Pool size (by people and vote), election date. Current org vote if applicable.
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
- [ ] **Mission Index page** (m_indx.html)
    - [ ] **Initiative Table** Each box will link somewhere different
        - [ ] **Columns** Different boxes populated for different scenarios.
            - [ ] **Pre Initiative Election** Leftmost columns populate
            Cause_name cycle_num | decision date | your vote | your vote ratings | ebx committed | pool size | Leading initiative | second | third | ...
            - [ ] **Post Initiative Election**
            Ring-mini | Cause_name| Initiative | Your pool contribution so far | org-election date | your vote | Reviews | ebx committed | pool size | Leaders
            - [ ] **Post organization election** Still working on this.
            Ring-mini | Initiative | Organization | Your earthbucks | release date | credit | your intentions 
            - [ ] **org side** Orgs have a slightly different table
            - [ ] **Admin side** Admins also have a different table. 
        - [ ] **Rows** Dates moving forward, one week at a time.
        The background color of upcoming mission rows (down on table) is different from ongoing missions (scroll to the top to find the first one.) The color of the missions with an initiative but no organization is the color of that cause (Middle, and middle of page when it opens)
            - [ ] **Expandable** Rows are expandable 1 at a time. - useful for pulling this table from elsewhere.
            - [ ] **Indicate user join date**
        - [ ] **Ring Mini** Mini annulus for one of 3 cases. Always links to a mission page.
            - [ ] **Mission selected** The mission annulus from the cause page, but with its stats expanded through the page so represented by small circle in corner.
            - [ ] **Mission not selected** 
                - [ ] **days left> 2** The cause annulus
                - [ ] **2 > days left** The initiative annulus for the upcoming cause
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
    - [ ] **Admin** 
    Admin can remove initiatives, other tasks.
    Works from mission index page
    - [ ] **Feed**
    Content from EN News, if any, is shown with each initiative
        - [ ] **Filters**
        Moved to right sidebar, labeled "Filter". Sticky on desktop, collapses horizontal on mobile.
    - [ ] **Initiative Logos** 
    One half of the credit coin. Contains all the information on the initiative side, like what the initiative is and how it garnered all its support.
- [ ] **Missions page**
When an initiative is decided, the mission page template is created. Each org builds their own. Like a profile page for them
    - [ ] **Data** Each mission is a row in `mission_indx`. populated with the initiative, organization, and more information.
        - [ ] **Progress reports** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
    - [ ] **Mission structure**
        - [ ] **Mission credit** Represented by a coin, value changes.
        For now, 1/16 total per week is released starting here. The value depends on how much benefactors like the progress and also by how much earthbux verifies their goodness combined with an efficiency metric.
        *"Once the mission begins, all committed money is locked for 7 weeks… After 7 weeks, 1/16 of the credits are released to the benefactors who provided the best contributions, and over the next 7 weeks, the money is released to a combination of the organizaion and the benefactors."* 
        *Accomplish mission goals to win as much money as possible*
        - [ ] **Budget phase**
        Once the mission begins, all committed money is locked for 7 weeks. This is the early mission period, when the organization learns how they can best earn the full pool. 
        - [ ] **Evaluation Phase**
        After 7 weeks, 1/16 of the credits are releast to the benefactors who provided the best contributions (posting to the community or anonymously contacting EN) that helped the mission.
    - [ ] **Organization inputs** Organizations fill out mission pages for whatever initiative they want to apply for. Once the election is active everything becomes linked together by election widgets, and when it's over one organization gets to claim the mission. Every stage hass a success metric and a cash reward.
    - [ ] **Mission Annulus** 4 now just do a multi-sectored annulus.
    Each mission gets its own ring widget which is on the cause page. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from ring minis on homepage or mission index to mission page. Will increase in complexity. 7-12 steps which can just be labeled 1-12 and will all link to the mission page. This will beome the 3rd outer annulus on the cause page.
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
    - [ ] **Verification & perks**
        - [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
        - [ ] **Credit badge colorization** Below a total donation threshold, a benefactor must have participated in the initiative and org vote to unlock the colored perk for that weeks sector. Add `vvv: bool` to `BenefactorAccount`, set after first vote.
            - [ ] **Automatic coloring threshold** threshold: $10
        - [ ] **Post visibility**
        Larger donations can unlock more visibility for your posts.
        - [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implementation: all id numbers below 100 get bonus.
- [ ] **ORGANIZATION** Organizations are mostly public, and work maximally on mission pages.
    - [ ] **Org-account flow.** 
    Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org employee. Once approved as a candidate, they put all important information on a mission page which continues if they win and is frozen and linked from their profile if not.
    - [ ] **Profile page** 
    Organization profile pages are very similar to benefactor profile pages. 
    - logo
    - missions
    - posts
    - [ ] **Member**
    A human representative of the weekly mission - Every org account is a member...
        - [ ] **Contributor**
        Benefactor who voted for org/possesses credits for mission
        - [ ] **Reporter**
        Person who can edit mission page for org
        - [ ] **Representative**
        Person responsible for submitting particular forms
        - [ ] **Beneficiary**
        Representative for the recipient of the charity effort (if applicable)
    - [ ] **Organization logos.** 1/2 of credit coin.

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
        - [ ] **Coin details** Coins are mini cause annuli their mission-specific cause solely highlighted  The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission from m_indx