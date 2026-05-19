## See backend/README.md to implement

## Structure
- [ ] **Main page** (index.html)
    - [ ] **Cause Cards**
        - [ ] **Top card**
        A card for the active causes 2 organization elections, one upcoming and one whose initiative was just decided. Move and repurpose banner as instructed in *bottom banner*
            - [ ] **Visual** Largest card. Horizontally in between the side cards, and vertically from the now marker all the way to the top of the display.
            - [ ] **Contents**
            Right: Smaller area titled with the newly elected initiative name and organization, pool size, election date. Current org vote if applicable.
            Left:  Larger area with detailed metrics for the organization election that will be decided this week. Leaders with links to their mission page prorotypes, link to EN feed for discussion, display current votes and committments.
            - [ ] **Expansion** Scroll-triggered expand upward/outward - backlog.
            The organization election is the most important part so a lot of information here. 
        - [ ] **Bottom banner**
        Relocate this banner to directly below the annulus, in between the left and right cause cards
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
        Keep inner circle at current size, maximize outer circle all the way to the inner edge of the cards. Lock left and right card corners to the bottom corners of active card w light padding.
            - [ ] **Center of Annulus**
            > Eventually, there will be a very cool 3d graphic in the middle. Hold that in the back of your mind because I'm not ready to create it yet. 
        - [ ] **Navigate and zoom**
        On mobile this will be important. There will be a zoom (And rotate) for users to select a particular sector and that will work well with touchscreens.
        - [ ] **Glowy white now marker** 
        Additional marker incorrectly on this page needs to be relocated to the initiative annulus.
- [ ] **Cause/Initiative page** (cause.html)
    - [ ] **Initiative annulus**
    There will be a third tier around the outside which will track mission metrics.
        - [ ] **Now marker**
        Glowy white marker (currently incorrectly in index.html) that rotates around each cause annulus indicating how far now is from that causes active period. 
            - [ ] **Align** Match up the same-colored segments on the 2 annuli and use this to position the marker. On the main page, the annulus rotates, but on this page the marker rotates around the annulus.
        - [ ] **Handle when 1 or 0 initiatives have votes**
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
            - [ ] **Vote weight Algorithm** b is the benefactor
            Vote weight = 1 + b_contribution/(total_pool_not_including_b * n_total_votes)
        - [ ] **Multiple choices** Benefactors can commit to multiple initiatives at once
            - [ ] **vote division** With every additional initiative, a benefactor is shown how they are spreading their vote share and decides how much vote to put on each initiative. Benefactors can not divide votes smaller than 0.1.
        - [ ] **Dialog** sign something convert_to_ebx
        Voting is important, you are in charge of determining and electing the fate of the planet, so don't f around.
        - [ ] **Winner** Whichever initiative has the largest vote share gets moved to the organization election slot for the next cycle. A mission page is created for the initiative, and for the next 8 weeks each organization that wants the donation uses this page for debate and outreach.
    - [ ] **Initiative Table**
        - [ ] **Columns**
        Name | Rating | Proposed-by | Credit (cause-color dot placeholder) | Pool share %
    - [ ] **Feed**
    Content from EN News, if any, is shown with each initiative
        - [ ] **Filters**
        Moved to right sidebar, labeled "Filter Newsfeed". Sticky on desktop, collapses horizontal on mobile.
    - [ ] **Initiative Logos** One half of the credit coin. Contains all the information on the initiative side, like what the initiative is and how it garnered all its support.
- [ ] **Missions**
    When an initiative is decided, the mission page template is created. Each org builds their own.
    - [ ] **Progress report** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
    - [ ] **Mission Annulus** Each mission gets its own ring widget. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from homepage to mission page. Will increase in complexity. 7-12 steps which can just be labeled 1-12 and will all link to the mission page. This will beome the 3rd outer annulus on the cause page.
    - [ ] **Organization inputs** Organizations fill out mission pages for whatever initiative they want to apply for. Once the election is active everything becomes linked together by election widgets, and when it's over one organization gets to claim the mission..
- [ ] **Mission Index** REPLACE Initiatives.html with mission_index.html and Initiatives.html can be deleted and replaced with the Mission Index
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
- [ ] **Profile page** Focus on humans
    - [ ] **Upcoming Decisions** 3 items: 
    Top: Initiative decision for cause x - link to initiative page for that cause
    Middle: Org decision for cause w - link to mission index with this expansion
    Bottom: Initiative and org for most recent mission. - links to mission page.
    - [ ] **Choices_Table** Snippet of mission index
    - [ ] **Logo colorization via vote participation.** Below a donation threshold, a benefactor must have participated in the org vote to unlock the colored perk for that weeks sector. Add `verified_via_vote: bool` to `BenefactorAccount`, set after first vote.
- [ ] **EN** Newsfeed
    - [ ] **Rename** everything to EN (Earthbux News)
    Rename everything to "Eerthbux News" or "EN" if there is a space constraint.
    - [ ] **Types of post** Benefactor posts: Initiative ratings, organization reviews, mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed). Org posts: Mission ideas, mission updates, mission proposals (When competing for an org election), problems (asking users for feedback/ideas). EBX posts: Stories, status-updates on the mission metrics.
    - [ ] **Feedback value** Good posts can be awarded EBX
    - [ ] **Filtered feeds** By applying filters to it, the feed improves the experience of many pages across earthbux.

## MEMBERSHIPS

**BENEFACTOR**
A human who intends to vote in the election.

**ORGANIZATION**
A human representative of the weekly mission.
    -   -   -       -   -   -   -   member of organizaiton
    Person who uploads a particular set of documents
 - Membership to one organization
    - [ ] **Organization logos.** Add `logo_url` to `Organization`. Until logos are uploaded, render a colored circle with the org's initials. Logos serve as a verification layer when the team approves orgs. This is 1/2 of the credit coin.
    - [ ] **Profile page** Organization profile pages are very similar to benefactor profile pages. Organizations do most of their work on the mission page. Once approved as a candidate, they put all important information on a mission page which continues if they win and is frozen and linked from their profile if not.

**HUMAN**
- [ ] **Security** Any user of the app is verified to be a human or the authorized AI agent of Earthbux or an authorized organization.

## CREDITS
- [ ] **Coin generation** Coins and mission are created when org is elected. Coins have same geometry as annulus but their cause segment is the only one highlighted and the relative value to when it was created in the middle.
- [ ] **Coin details** The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission...
- [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
- [ ] **Transactional logic** Coins operate similarly to a cryptocurrency, can be exchanged for coins from other missions. All coins are donations, although can be removed which will be complex tax-law-wise.
- [ ] **Tax deductable** Benefactors need a seamless way to maximize their tax benefits from their donations. We do this by thinking of all earthbux as donations. Cash is only converted into Earthbux upon the election of the organization. If a benefactor wants to cash out their earthbux, then tax is applied.
- [ ] **Credits** a credit is 1 EBX
    - [ ] **Description** A credit is an ebx token minted for all of the money converted to earthbucks 
    - [ ] **Conversion** 
        - [ ] **EBX maintain a value of $1 pre-mint**
        Unminted EBX can be exchanged for cash. They are not tax deductable. This initial step is to make the next step easier.    
    - [ ] **Donation**
        - [ ] **Tax deducted**
        All minted credits are tax-redeemable.
        - [ ] **Mission structure**
            - [ ] **Budget phase**
            Once the mission begins, all committed money is locked for 7 weeks. This is the early mission period, when the organization learns how they can best earn the full pool. 
            - [ ] **Evaluation Phase**
            After 7 weeks, 1/16 of the credits are releast to the benefactors who provided the best contributions (posting to the community or anonymously contacting EN) that helped the mission.
        - [ ] **The rest is now in your wallet** The number is gonna start off in dollars and , which only happens after it has been committed to a charity and converted.
          - [ ] **EN cut thresholds** If your donation brings the threshold over $1000, we take 4/16, $800 3/16, $600 2/16, and anything else 1/16.

          - [ ] **5/16 EN Cut** Users are notified that 5/16 % of their money is going to Earthbux News (EN) and they/we go and help the mission in any way we can while reporting and chase them if we have to.
              - [ ] **1/16 to evaluation**  