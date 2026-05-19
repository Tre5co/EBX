## see backend/README.md

## Structure
- [ ] **Main page** (index.html)
    - [ ] **Cause Cards**
        - [ ] **Top card**
        A card for the active causes 2 hard (organization) elections, one upcoming and one whose initiative was just elected, a soft election. Move and repurpose banner as instructed in *bottom banner* 
            - [ ] **Visual** Largest card. Horizontally in between the side cards, and vertically from the now marker all the way to the top of the display.
            - [ ] **Contents**
            Right: Later hard election and organization, pool size (by people and vote), election date. Current org vote if applicable.
            Left:  Larger area with detailed metrics for upcoming hard election. Leaders with links to their mission page prorotypes, link to EN feed for discussion, display current votes and committments from `mission_indx`.
            - [ ] **Expansion** Scroll-triggered expand upward/outward - backlog.
            The organization election is the most important part so a lot of information here. 
        - [ ] **Bottom banner**
        Repurpose election banner which is replaced by *top card* to directly below the annulus, in between the left and right cause cards
            - [ ] **Upcoming Initiative Decision**
            That's what this banner is for. Change it to the color of the cause after the active cause and display the leader/metrics.
        - [ ] **Side  Cards** 
        Top section: "Initiative" 
                        leader - x % - Contribute ("Contribute" links to that cause page)
                        Total pool so far: x
        Bottom section: "Organization for [initiative]" (Note that this is the initiative for the previous cycle)
                        leader - x% - Contribute ("Contribute" links to that orgs mission page)
                        Total pool so far: x
        If there is no initiative/organization slotted in for a particular date, show "No votes yet"
    - [ ] **Cause annulus**
        - [ ] **Maximize display space**
        Keep inner circle at current size, maximize outer circle all the way to the inner edge of the cards. Lock left and right card edges to the edges of active card w light padding. Slide down on top of `now` bolt
        - [ ] **Cause label Visibility** Make annulus thicker so that cause titles are fully visible. Multi-word entries can take multiple lines.
        - [ ] **Center of Annulus**
        > Eventually, there will be a very cool 3d graphic in the middle. Hold that in the back of your mind because I'm not ready to create it yet. 
        
        - [ ] **Navigate and zoom**
        On mobile this will be important. There will be a zoom (And rotate) for users to select a particular sector and that will work well with touchscreens.
        - [ ] **`now`** 
        Additional marker incorrectly on this page needs to be relocated to the initiative annulus.
- [ ] **Mission Index page**
    - [ ] **Initiative Table**
        - [ ] **Columns** so far
        Name | Rating | Proposed-by | Credit (cause-color dot placeholder) | Pool share %
   - [ ] **Organization inputs** Organizations fill out mission pages for whatever initiative they want to apply for. Once the election is active everything becomes linked together by election widgets, and when it's over one organization gets to claim the mission. Every stage hass a success metric and a cash reward.
    - [ ] **News rankings**
    - [ ] **A big table** of every mission
    Information here is used on other pages
        - [ ] **Rows** Dates moving forward, one week at a time.
        The background color of upcoming mission rows (down on table) is different from ongoing missions (scroll to the top to find the first one.) The color of the missions with an initiative but no organization is the color of that cause (Middle, and middle of page when it opens)
            - [ ] **Indicate user join date**
        - [ ] **Columns** Everything, benefactors can edit their votes/committments/more here.
        pre-mission: "cause_name cycle_num"| mission_start_date | my_initiative_choice(s) (green/red if vote is over) | amt committed | my_org_choice(s) (also colored by win/loss, blank if no initiative yet.) | amt committed | pool_size
        - [ ] **Expandable** Rows are expandable 1 at a time. - useful for pulling this table from elsewhere.
            - [ ] **org side** Orgs have a slightly different table
            - [ ] **Admin side** Admins also have a different table. 
    - [ ] **Ring Mini** one of 3 cases
        - [ ] **Mission selected** The mission annulus, but with its stats expanded through the page so represented by small circle in corner.
        - [ ] **Mission not selected** 
            - [ ] **days left> 2** The cause annulus
            - [ ] **2 > days left** The initiative annulus for the upcoming cause
- [ ] **Cause/Initiative page** (cause.html)
    - [ ] **Initiative annulus**
    There will be a third tier around the outside which will track mission metrics.
        - [ ] **Now marker**
        Glowy white marker (currently incorrectly in index.html) that rotates around each cause annulus indicating how far now is from that causes active period. 
            - [ ] **Align** Match up the same-colored segments on the 2 annuli and use this to position the marker. On the main page, the annulus rotates, but on this page the marker rotates around the annulus.
        - [ ] **Handle when 1 or 0 initiatives have votes**
        - wildlife is not a special case and should not be treated as such.
        If only 1 or 0  initiatives has received votes, eliminate the pie chart and indicate in the middle of the annulus what case it is.
        - [ ] **Mission Progress annulus** Surrounds 2 inner sections.
        Backlog until mission progress interface is develped.
    - [ ] **Left Cards**
    Display upcoming initiative options. Currently shows the initiatives with the most of pool. 
    - [ ] **Right cards**
    Bottom: previous mission with status
    Middle: Active mission with status
    Top: Upcoming organization election with Initiative name and the benefactors current organization selection.
    - [ ] **Admin** 
    Admin can remove initiatives, other tasks.
    Works from mission index page
    - [ ] **Initiative vote** 
    Determines the initiative for the next mission
        - [ ] **Initiative ratings.** 
        Posts tagged as a rating are factored into an initiative's overall rating.
        - [ ] **Committing** 
        Before adding money, one click sets a users vote to an initiaitve. Each benefactor has a vote that does not require any money to be committed.
            - [ ] **Selection day** Before selection day, you can move around your vote shares as much as you want. You can add, withdraw, and move around committments. 24 hours before selection is when voting locks for counting. The pool also locks and the mission page is created.
                - [ ] **Winner** Winner of soft election enters 8-week hard election
                - [ ] **Mission page** and updated mission index
            - [ ] **Dialog** sign something convert_to_ebx
            Voting is important, you are in charge of determining and electing the fate of the planet, so don't f around.
            - [ ] **vote division** Benefactors can commit to multiple initiatives at once With every additional initiative, a benefactor is shown how they are spreading their vote share and decides how much vote to put on each initiative. Benefactors can not divide votes smaller than 0.1.
                - [ ] **Vote weight Algorithm** b is the benefactor
                Vote weight = 1 + b_contribution/(total_pool_not_including_b * n_total_votes*size_factor)
                    - [ ] **Vote division floor** 0.1
                    *"Benefactors can not divide votes smaller than 0.1."* Enforce in Commit dialog. Add to backlog → frontend Commit-dialog work + backend `Vote` validation.


    - [ ] **Feed**
    Content from EN News, if any, is shown with each initiative
        - [ ] **Filters**
        Moved to right sidebar, labeled "Filter". Sticky on desktop, collapses horizontal on mobile.
    - [ ] **Initiative Logos** One half of the credit coin. Contains all the information on the initiative side, like what the initiative is and how it garnered all its support.
- [ ] **Missions page**
When an initiative is decided, the mission page template is created. Each org builds their own. Like a profile page for them
    - [ ] **Data** Each mission is a row in `mission_indx`. populated with the initiative, organization, and more information.
        - [ ] **Progress reports** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
    - [ ] **Mission structure**
        - [ ] **Mission credit** Represented by a coin, value changes.
        For now, 1/16 total per week is released starting here. The value depends on how much benefactors like the progress and also by how much earthbux verifies their goodness combined with an efficiency metric.
        *"Once the mission begins, all committed money is locked for 7 weeks… After 7 weeks, 1/16 of the credits are released to the benefactors who provided the best contributions, and over the next 7 weeks, the money is released to a combination of the organizaion and the benefactors."* 
        *Mission goal is to win as much money as possible from the rules*
        - [ ] **Budget phase**
        Once the mission begins, all committed money is locked for 7 weeks. This is the early mission period, when the organization learns how they can best earn the full pool. 
        - [ ] **Evaluation Phase**
        After 7 weeks, 1/16 of the credits are releast to the benefactors who provided the best contributions (posting to the community or anonymously contacting EN) that helped the mission.
    - [ ] **Mission Annulus** 4 now just do a multi-sectored annulus.
    Each mission gets its own ring widget which is on the main page.. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from homepage to mission page. Will increase in complexity. 7-12 steps which can just be labeled 1-12 and will all link to the mission page. This will beome the 3rd outer annulus on the cause page.
- [ ] **Profile page** Focus on humans
    - [ ] **Benefactor**
        - [ ] **Upcoming Decisions** 3 items: 
        Top: Initiative decision for cause x - link to initiative page for that cause
        Middle: Org decision for cause w - link to mission index with this expansion
        Bottom: Initiative and org for most recent mission. - links to mission page.
        - [ ] **Dropdown dialog** Credit badge has dropdown dialog when logged in where users can log out, view wallet, or switch to an organization account.
        - [ ] **Credit badges** mission logo (or initials) in the center. Annulus fills with the color throughout first 49 days of mission.
        - [ ] **Choices_Table** Snippet of mission index
    - [ ] **Organization** representing...
        - [ ] **recent vote results** pool sizes.
        - [ ] **Org-account flow.** Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org employee.
- [ ] **EN** Newsfeed
    - [ ] **Post** Post your own content.
            - [ ] **Types of post** Benefactor posts: Initiative ratings, organization reviews, mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed). Org posts: `mission proposals` (When competing for an org election), `mission_ideas`, `mission updates`, `feedback`. EBX posts: `status-updates` on the mission metrics.
    - [ ] **Rename** everything to EN (Earthbux News)
    Rename everything to "Eerthbux News" or "EN" or .en if there is a space constraint.
    - [ ] **Feedback value** 
    Good posts can be awarded `cause_EBX`
    - [ ] **Filter** Everything is a filtered version of the `missionindx` to it, the feed improves the experience of many pages across earthbux.
- [ ] **About**
    - [ ] **Clarify core goals** Root out wasteful and fraudulent charity organizations/players, reorient peoples media consumption towards meaningful things, focus charity efforts on the cause rather than sponsors, democratize charioty by finding the best idea rather than the most profitable one, rewarding thoughtful ideas, pooling donations to prevent redundant/competing charity missions. Provide unbiased and mission-oriented news coverage of every mission.
    - [ ] **Financial structure** Committing to an initiative: 20% sent if your initiative wins, 10% if not. Committing to an organization: 100% if they win, 20% if not.
    - [ ]  **Information about how I founded the company...** My sstory. Get it working first
    - [ ] **Financial structure**
        1. **`size_factor` in vote-weight formula.** 
        optimized for a donation pool ideal size to be agreed upon later
        8. **5/16 EN cut:**
            **1/16 evaluation reward.** README spells these out now. Combined ≈% of pool is non-mission.
## MEMBERSHIPS
- [ ] **BENEFACTOR**
A human who intends to vote in the election.
    - [ ] **Verification & perks**
        - [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
        - [ ] **Logo colorization via vote participation.** Below a donation threshold, a benefactor must have participated in the org vote to unlock the colored perk for that weeks sector. Add `vvv: bool` to `BenefactorAccount`, set after first vote.
            - [ ] **Automatic coloring**
                Current threshold: $20
            - [ ] **Rewards** 
                - [ ] **Soft votes** Colorization
                - [ ] **Hard votes** Post Visibility/voice
        - [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implementation: all id numbers below 100 get bonus.
- [ ] **ORGANIZATION**
    A human representative of the weekly mission.
        -   -   -       -   -   -   -   member of organizaiton
        Person who uploads a particular set of documents
    - Membership to one organization
        - [ ] **Organization logos.** Add `logo_url` to `Organization`. Until logos are uploaded, render a colored circle with the org's initials. Logos serve as a verification layer when the team approves orgs. This is 1/2 of the credit coin.
        - [ ] **Profile page** Organization profile pages are very similar to benefactor profile pages. Organizations do most of their work on the mission page. Once approved as a candidate, they put all important information on a mission page which continues if they win and is frozen and linked from their profile if not.
- [ ] **HUMAN**
backlog security questions
    - [ ] **Security** Any user of the app is verified to be a human/agent of Earthbux or an authorized organization.
## CREDITS - LINKED TO A MISSION
- [ ] **Transactional logic** Coins operate similarly to a cryptocurrency, can be exchanged for coins from other missions. All coins are donations, although can be removed which will be complex tax-law-wise.

- [ ] **Credits** a credit is 1 EBX
    - [ ] **Description** A credit is an ebx token minted for all of the money converted to earthbucks 
    - [ ] **Conversion** 
        - [ ] **Coin details** Coins are mini cause annuli their mission-specific cause solely highlighted  The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission...
        - [ ] **Coin generation**  display value in middle (Exactly 1 for the first 7 weeks)
            - [ ] **EBX maintain a value of $1 7-weeks-post-mint**
            Unminted EBX can be exchanged for cash. They are not tax deductable.



    - [ ] **Donation**
        - [ ] **Tax deducted**
        All minted credits are tax-redeemable.
        - [ ] **The rest is now in your wallet** The number is gonna start off in dollars and , which only happens after it has been committed to a charity and converted.
          - [ ] **EN Thresholds** We only take money if the pool is above $100. 
          - [ ] **5/16 EN Cut** Users are notified that 5/16 % of their money is going to Earthbux News (EN) and they/we go and help the mission in any way we can while reporting and chase them if we have to.
              - [ ] **1/16 to evaluation**  
              Included in Earthbux 5/16.
              - [ ] **1/4 to our side of the mission**
              We will create a budget.