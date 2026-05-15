# Earthbucks — Backlog

## Changelog
- **2026-05-15** — Fixed main page alignment (see below). Logged notes on wildlife chart, propose-login bug, and cycle model.
- **2026-05-15 (auto)** — Three bugs fixed (see notes below). Also repaired a silent corruption in `frontend/src/ebx_shared.ts` where duplicate code had been appended after the build sentinel — this was blocking all TS builds.
- **2026-05-15 (auto, pass 2)** — Added "now" glowing white line to the cause wheel annulus. Removed separate Vote button from initiative detail panel — Commit is now the single action (it IS the vote). Fixed `n===1` label position in the wildlife pie chart (label now shows at 12 o'clock instead of bottom of ring). Rebuilt JS bundle successfully.

## Structure
- [ ] **Main page**
    - [ ] **Cause annulus** is here, Claude was right
        - [ ] **Glowy white now marker** - Marker from previous edit is on wrong page. This was supposed to be on the initiative annulus, which is on cause.html. Oops!
        - [ ] **Maximize display space**
        Keep inner circle at current size, maximize outer circle all the way to the inner edge of the cards. Lock left and right card corners to the bottom corners of active card w light padding.
            - [ ] **Size and dimensions of annulus**
        - [ ] **Navigate and zoom**
        On mobile this will be important. There will be a zoom (And rotate) for users to select a particular sector and that will work well with touchscreens.
- [ ] **Cause/Initiative page**
    - [ ] **Initiative annulus**
        - [ ] **Glowy white now marker**
        which circumnavigates the annulus once every 7 weeks.
    - [ ] **Initiative vote cards**
        - [ ] **Option to vote without committing anything**
        Explain the algorithm - (1 + %of_the_pool_from_b) * b_committment_value_ebx
        - [ ] **Dialog** sign something convert_to_ebx
        Voting is important, you are in charge of determining and electing the fate of the planet, so don't f around.
        - ✅ **Vote/Commit unified (2026-05-15 auto):** Removed separate "Vote" button from initiative detail panel. "Commit EBX" is now the single action and its dialog explains the mechanics. Full multi-initiative allocation dialog (see Initiatives → Committing UX) is still pending.
- [ ] **Credits** a credit is 1 ebx
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


        
- [ ] **NEWSFEED**
    - [ ] **Rename** Rename feed everywhere to newsfeed.

- [ ] **Profile page** Each of the 7 choices on profile page should link to their respective initiative or mission page.

- [ ] **Mission Page**
   Nothing yet

- [ ] **Feed Page**
   Nothing yet

## Cause Page
- [ ] **Initiative proposal** Asking "Are you logged in?" When I am logged in. Wiring this up will help me learn about databases.
- [ ] **Page design**
Good for now.
EBX                                                                        profile
___Leading initiatives___  [cause] decision - [date] ___Past/Ongoing Initiatives___
|                        | Select upcoming mission*  |                             |
|________________________|       Cause               |_____________________________|
                                 Wheel**                                                         **see cause wheel item
   ____________________________________________________________________________________       
   - Selected initiative area - Remove the numbered "click to jump" section
   Flows seamlessly into feed - ONLY posts directly related to selected initiativwe
   If no initiative is selected display all feed info for cause
   Remove header from feed section for clean flow from initiative above
Vote for x - Commit donation - contribute to the discussion
   _____________________________________________________________________________________
   __________________________Initiatives table__________________________________________
Search                                                         Propose an Initiative

   And the bottom section contains more detailed information about the initiative, including ratings, posts/comments/user feedback, history (it might have been edited/improved), budget, org backing, etc.



## Initiatives
- [ ] **Propose initiative problem** I can't propose initiatives, it 

- [ ] **Cards** Top section: "Initiative" 
                              leader - x % - Contribute ("Contribute" links to that cause page)
                              Total pool so far: x
               Bottom section: "Organization for [initiative]" (Note that this is the initiative for the previous cycle)
                              leader - x% - Contribute ("Contribute" links to that orgs mission page)
                              Total pool so far: x
  If there is no initiative/organization slotted in for a particular date, show "No votes yet"

- [ ] **Committing** Each benefactor has a baseline vote share that does not require any money to be committed. The weight of your vote share is multiplied by 1 + your_committment / total_pool_not_including_your_committment. You can split your vote share between multiple initiatives however you want to divide it. This way, larger committments will have a smaller impact the more people vote.

- [ ] **Committing UX** Eliminate "Vote" option from initiative cards. "Commit" will open a dialog where you see all current committments, and are prompted for the % of your vote share you want to commit to each. Enforce that it adds up to 100% by rounding and notifying what was rounded.

- [ ] **Selection day** Before selection day, you can move around your vote shares as much as you want. You can add, withdraw, and move around committments. 24 hours before selection is when voting locks for counting. The pool also locks and the mission page is created.

- [ ] **Winner** Whichever initiative has the largest vote share gets moved to the organization election slot for the next cycle. A mission page is created for the initiative, and for the next 8 weeks each organization that wants the donation uses this page for debate and outreach.

- [ ] **Data** Add "cycles" to database. These are organizaed by the cause and cycle number, and will be populated with the initiative, organization, and contextual information.

- [ ] **Initiative ratings.** Posts tagged as a rating are factored into an initiative's overall rating.

- [ ] **Admin** Admin can remove initiatives, other tasks.

- [ ] **Initiative Logos** One half of the credit coin. Contains all the information on the initiative side, like what the initiative is and how it garnered all its support.

## Missions
- [ ] **Initiatives first** Finalize initiative process before starting working on missions.
- [ ] **Progress report** The missions 7-12 step progress report is prominent on the mission page. This consists of a benefactor-moderated comparison of the organization's progress reporting and Earthbucks parallel report.
- [ ] **Mission Annulus** Each mission gets its own ring widget. Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins. Flow from homepage to mission page. Will increase in complexity. 7-12 steps which can just be labeled 1-12 and will all link to the mission page. This will beome the 3rd outer annulus on the cause page.

- [ ] **Organization inputs** Organizations fill out mission pages for whatever initiative they want to apply for. Once the election is active everything becomes linked together by election widgets, and when it's over one organization gets to claim the mission..

- [ ] **UX**
_______________________________________________________________


## Organizations
- [ ] **Organization logos.** Add `logo_url` to `Organization`. Until logos are uploaded, render a colored circle with the org's initials. Logos serve as a verification layer when the team approves orgs. This is 1/2 of the credit coin.
- [ ] **Profile page** Organization profile pages are very similar to benefactor profile pages. Organizations do most of their work on the mission page. Once approved as a candidate, they put all important information on a mission page which continues if they win and is frozen and linked from their profile if not.

## Profile / accounts
- [ ] **UI/UX**
Good 4 now.
EBX                                                Profile badge        
   _____  _______________________________________     ______________
   | a  | |_________________b____________________| |       d      |   
   |____|                                          |              |  
   | c  |                   e                      |              |
   |____|                                          |______________|

a. Same handle-card as current 
b. [Upcoming Cause] - [User initiative choice] - [ebx committed] - [timer countdown] | [Upcoming Initiative] - [User organization choice] - [ebx committed] - [timer countdown]
c. wallet - remove the ebx balance, replace with the credit portfolio because it is the same thing. Benefactors will be able to click on each credit coin to see their stake in that mission.
d. Table with the user choices for each cause. Toggle between initiatives and organizations, linked to the cause (initiative) or mission (organization) page.
e. History of feed content posted by the user.

- [ ] **Dropdown dialog** Credit badge has dropdown dialog when logged in where users can log out, view wallet, or switch to an organization account.
- [ ] **Flow** To create an account should be easy. Account will have things like : Wallet, Missions, Reviews/Rating, messages, current votes and commits for each of the 7 causes, org memberships, etc.
- [ ] **Credit badge.** mission logo (or initials) in the center. Annulus fills with the cause color throughout first 49 days of mission. Turns to permanant state upon completion.
- [ ] **Org-account flow.** Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org employee.
- [ ] **Logo colorization via vote participation.** Below a donation threshold, a benefactor must have participated in the org vote to unlock the colored perk for that weeks sector. Add `verified_via_vote: bool` to `BenefactorAccount`, set after first vote.
- [ ] **Security** For now all posts, initiatives, org inputs, votes, commits, etc will automaticaally be valid and public. Later we'll determine which elements to protect.

## UI / Annulus
- [ ] **Cause label Visibility** Make annulus thicker so that cause titles are fully visible. Multi-word entries can take multiple lines.

## Credit
- [ ] **Coin generation** Coins and mission are created when org is elected. Coins have same geometry as annulus but their cause segment is the only one highlighted and the relative value to when it was created in the middle.
- [ ] **Coin details** The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission...
- [ ] **Review/rating awards** Benefactors are awarded credit coins from a mission if their posts are highly related and deemed "Helpful"
- [ ] **Transactional logic** Coins operate similarly to a cryptocurrency, can be exchanged for coins from other missions. All coins are donations, although can be removed which will be complex tax-law-wise.
- [ ] **Tax deductable** Benefactors need a seamless way to maximize their tax benefits from their donations. We do this by thinking of all earthbux as donations. Cash is only converted into Earthbux upon the election of the organization. If a benefactor wants to cash out their earthbux, then tax is applied.

## Feed
- [ ] **Types of post** Benefactor posts: Initiative ratings, organization reviews, mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed). Org posts: Mission ideas, mission updates, mission proposals (When competing for an org election), problems (asking users for feedback/ideas). EBX posts: Stories, status-updates on the mission metrics.
- [ ] **Filtered feeds** By applying filters to it, the feed improves the experience of many pages across earthbux.

## About
- [ ] **Clarify core goals** Root out wasteful and fraudulent charity organizations/players, reorient peoples media consumption towards meaningful things, focus charity efforts on the cause rather than sponsors, democratize charioty by finding the best idea rather than the most profitable one, rewarding thoughtful ideas, pooling donations to prevent redundant/competing charity missions. Provide unbiased and mission-oriented news coverage of every mission.
- [ ] **Financial structure** Committing to an initiative: 20% sent if your initiative wins, 10% if not. Committing to an organization: 100% if they win, 20% if not.
- [ ]  **Information about how I founded the company...** My sstory. Get it working first

## Verification & perks
- [ ] **Donation threshold.** Define and store the threshold amount (env var or config row). Compute on the fly per benefactor. Threshold for initiative donations moderates logo colorization and for org donations it moderates user visibility/voice.
- [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implement as either (a) a startup hook that grants on signup if `id <= 100`, or (b) a one-time admin script after the first 100 register. Decide which.

## Build & dev tooling

- **TS build was silently broken (fixed 2026-05-15 auto).** The file `frontend/src/ebx_shared.ts` had duplicate corrupted code appended after the `// EBX_TAIL_SENTINEL` line — a second copy of the tail of `missionStrip()` and the `EBX` namespace object. esbuild failed with a syntax error (`Expected ";" but found ":"`) at line 1551. The sentinel grep check still passed (it was present twice), so the error only appeared when actually running `npm run build`. Cleaned up by truncating to line 1549.

  > **How to rebuild after any future JS edits, Jax:** From the `frontend/` folder, run `npm run build`. If you see `✘ [ERROR]` output, the TypeScript source has a syntax problem. You can also run `npm run typecheck` to catch type errors without building. The output always goes to `resources/js/ebx_shared.js`.

## Infra
- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only. What does this mean?
- [ ] **cycleStart from API.** Currently hardcoded in ebx_shared.ts — should come from a config endpoint so it can change without a rebuild.

## Cycle / process modeling
- [ ] **Dual-decision week.** Each cause has TWO per-cycle decisions a week apart: an initiative-decision (week N) for the incoming initiative followed by an org-election-decision for the outgoing initiative (week N+1). The current `Cycle` engine collapses both into one weekly tick; revisit when wiring real Vote/Initiative state through the race card's two halves.
  > **Architecture note (2026-05-15):** Based on the HTML comment at top of BACKLOG.md, here's how I understand the intended model — please confirm:
  > - **Each week, TWO decisions happen simultaneously for DIFFERENT causes:** the initiative decision for cause X (entering active window) AND the org decision for cause X-8 (which had its initiative decided 8 weeks ago).
  - Yes, Although I'd prefer if you called it "Mission x-8" because the causes repeat so I want to avoid confusion.

  > - **Initiative decision week (week N for cause X):** The winning initiative for that cause is selected. X's org election begins. 
  - Yes

  > - **Org election decision week (week N+8 for cause X):** The winning org for that initiative is selected. A mission page is created.
  - Yes, well, the mission page may have already been created by the org, but this is the point where one mission page becomes official for that particular mission.

  > - So at any given week, the "active cause" (in the annulus) is deciding its initiative, while simultaneously another cause (8 weeks behind) is deciding its org.
  - Exactly, although again I prefer the term mission. Each mission has a cause, cycle number, initiative, and organization.
  > 
  > **What this means for `Cycle.now()`:** It needs to return TWO active decisions per tick — `initiativeDecision: causeIndex` and `orgElectionDecision: (causeIndex + 8) % 7` (or some offset). The race card's two halves (Initiative row + Org election row) already anticipate this — the top row is the current initiative race, the bottom is the org race for the initiative that was selected earlier.
  - Exactly.
  > 


## Testing
- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke. (Right?)
- [ ] **Current strat** Me and my cofounders will each create a few accounts with simulated money. We will use real initiatives (probably the ones already in use) and simulate organizations (also probably the ones already in use). We will start with the first 7 initiative votes, and hopefully after those first 7 weeks we'll have the mission page locked in and be ready for the first organization votes.

## Non-conventional interfaces
- [ ] **Static off-line mode** Create an offline-mode that saves the current state of the project as an example so that I can download it on a hard drive and demonstrate it for someone without needing server access.
- [ ] **Swift** Create mobile version.