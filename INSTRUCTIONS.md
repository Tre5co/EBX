## AI TUNING
@CLAUDE Stop process now if there are any lines in between here and ## BUILD SEQUENCE
## BUILD SEQUENCE
0. Resolve if any
- (a) **Errors**
**Admin ↔ p2 sync** Ensure admin mode is updating with the p2 vote logic (the new tally/candidacies/claims endpoints) — wiring the new p2 data in will do the trick.
- (b) **Blockers**
- (c) **Inconsistencies**
CLAUDE.md points to STRUCTURE.md, which doesn't exist in this folder.
- (d) **Not blocking** Acknowledge but do not attempt to fix yet.
~~**P2 Area** <phases> It doesn't seem to be updating.~~ ✅ Resolved 2026-07-07 (syncOrgTally now re-renders the phase-2 area).

1. **P2 Buildout** <expansion> ✅ Built 2026-07-07
Time for a large buildout to trim down later. Let's make mission.html.
Envision the org registration experience.

nominate → (register / claim) → elect. (election may happen before register/claim)

The mission page depends on these 3 booleans.

Org homepage / profile — a public page for a user, and an authenticated "org mode" for their org memberships.
 (roles: community / rep / executive / beneficiary)
Mission claim - the self-registration / onboarding flow by which a real organization enters the system, submits a mission statement to become a candidate, and claims a mission via the click-through legal agreement.
Charity status - Earthbux works with organizations to apply for legal status, making the users donations go farther.

An org can become a candidate and create posts without being approved. To receive votes, they have to submit a mission statement for a tiv. They can register for as many initiatives as they want, but need to be approved for each in order for the nonprofit application to begin. The application starts as soon as the election is won, and donations can not occur until the nonprofit status is achieved. Earthbux will help with this process.

Let orgs that register for a tiv show up in that election. When the org is not approved, display that the org is not approved. In the p2 area, mention that leading orgs will be approved or rejected soon. If your org was rejected, all your money is returned to you. The maximum amount of ebx someone can put on an unapproved org is 10 (1 vote).

A. Org nonprofit application / self-registration — ✅ POST /organizations/register (+ fuzzy duplicate detection, /organizations/match), application form on mission.html, entry points on index/cause.
B. Org membership account — ✅ MembershipCreate + GET/POST /organizations/{id}/memberships; profile.html org mode wired to real memberships; beneficiary surface scaffolded.
C. Org homepage / public profile — ✅ org.html + GET /organizations/{id}/profile bundle.
D. The claim gate — ✅ org_claims table + POST /missions/{id}/claim (attestation version + timestamp + ben); config-driven guaranteed-to-pool rates (unclaimed 20% → claimed 35%).
E. Candidacy → election polish — ✅ mission statement required to receive votes; unapproved cap 1 vote/10 EBX enforced server-side; P2-area refresh bug fixed. Block-vote (valence='harmful') UI still deferred by design.

2. **P1 recap** <phases> Some tweaks:
Remove "post recap" too. Seperate posts area into 3 rows.

3. **Posts** <discussion>
Table expanded columns need to be filterable by tiv (or by org when orgs are created)
Add helpful, hurtful, or neutral to these posts and option to reply, which takes us to the landing page discussion feed, where replies are displayed inside the posts.
Comments are classified as posts with a parent post.

Landing- All posts -> Stays on landing, users can continue discussion threads
home table- tiv-filtered -> onclick leads to landing
phase areas - cause-filtered -> onclick leads to home table expanded row
profile- user-filtered -> onclick leads to cause page

On the profile page ui, the choices table toggles the discussion area. If a user hasn't made any posts about that mission, display the leading posts from that mission.

Images - users should be able to attach images with their post - backlog this step but we will need it soon.

a. Posts EVERYWHERE need to display the date when they were posted and the initiative/organization which they regard, they should be colored based on what cause they are.

Refined model: it's the best context (cause-specific) post which wins the ebx reward from the p1 postvotes, and the best analysis (initiative-specific) which gets the reward for analysis, who wins the p2 postvotes. The best evaluation wins it in p3. This changes the timings of some of the releases.

The best case gets an upgraded membership with their organization which includes privelidges like (I'm spitballing) veto rights, communication lines, early information from earthbux, etc. No cash reward for a case.

Post voting should be possible from all areas... cause page issue persisting.

⚠ Category author-permission rules now live in §4b — apply them when building this section.

4. **Money, S/S/S & Resolutions** <reorientation — refined & consolidated 2026-07-07>

*Vocabulary*
- **Service** — something we can send people to DO.
- **Supply** — WHAT those people need to do it.
- **Support** — assurance that the issue is being resolved honestly.
- (S/S/S are the key objects of Earthbux reporting.)
- **Resolution** — a small, mission-tied outcome we can reasonably assume was successfully accomplished; when it lands, its evaluation point is given and it moves the mission's credit-coin value. Phase 5 is removed as a phase: a mission closes through MANY tiny resolutions, not one resolution event.
- **Mission membership** — new name for org memberships, everywhere. All mission members hold credit coins.

a. **Credit coin entity**
- Real CreditCoin entity with a coin icon; the icon displays ONLY next to real financial transactions.
- Every benefactor who voted gets coins — possibly a tiny amount (e.g. just the 10% send from a lost commit followed by a withdrawal).
- Funding source arrives later with donations: money is routed through Earthbux to the org, or returned to the donor.
- The amount people keep as EBX (rather than converting/withdrawing) determines the pool available to budget with.
- Design for failure: realistically, many missions will fail — the coin model must tolerate that.
- Resolutions (see vocabulary) move credit-coin value.

b. **Posts reoriented to services & supplies** (category author-permission rules)
- **Context** = suggesting S/S/S. Cost analysis is CONTEXT, not analysis. Posted by mission members AND non-members.
- **Analysis** = real analysis, never cost-based. Mission members only.
- **Evaluation** = non-members only.
- **Case** = both.
- Organizations and users generate itemized, mission-funded budget plans for their supply chains: orgs post itemized cost lists; users vote on popular suggestions; benefactors select the services/supplies they approve.
- The socially selected picks drive the money routing (see c) and are key aspects of Earthbux reporting.

c. **Claim-gate contract** (draft started: CONTRACT_DRAFT.md)
- By passing the claim gate, the organization agrees to be reported on by Earthbux.
- Earthbux agrees to route untaxed money to the organization based on the socially selected service/supply suggestions.
- Communication clause: the available money declines if the organization fails to communicate with Earthbux — and Earthbux can lose money the same way. Both directions go in the contract.

d. **Release phase structure**
- The release phase has a projected MISSION LENGTH.
- Each STEP has a guaranteed and a potential pool attached, finalized by the end of the budgeting phase.

e. **Org admin mode**
- Org members who have been assigned to a mission get their own admin mode (access credentials will be provided) — the community conversation flows directly into the ears of the organization.

*Open questions (resolve before building §4)*
- "Non-members post evaluation": non-members of the ORG, presumably — but if every voting benefactor holds a credit coin and credits=membership, define precisely who is excluded from evaluation.
- Where do resolutions render once phase 5 is gone (cause-page phase blocks, mission hub, both)?
- Does a resolution move only that mission's coin value, or feed a global coin value too?
- Rename scope: does "Mission membership" replace the Membership table naming, the UI copy, or both?

## CONVERSATION
I can pledge to BE the funds for Earthbux, up to $500/week. That's how I earn my money.
In p1, bens can change tiv votes at will until the final count. They can even sell back any additional purchased votes, but only for a strict $0.10 per vote, the additional cost of additional voting power is sent to the pool.

All money sent is converted to earthbucks.

To post, you must have a user id. How do I go in and assign/edit relationships in the database?
At the end of phase 1, a pool is created. Benefactors each need a balance. Earthbux also needs a balance. Orgs need a payout. How does this make sense in the database?

## BACKLOG (for backlog management - ignore this section during build task)
*Order least → most intensive. Tackle in order when blocked on the BUILD SEQUENCE above.*
**Landing page** <ux> Activate post voting
**Election card ui** I need to make the differences between the 2 sides of the election card more obvious to viewers
**Apache infra** I'm probably going to use some apache software like Kafka, Flink, Airflow, and Cassandra in the future. Lets add that to infra.
**Start date everywhere** The cause page rhs cards should have the start date as well.
**Org table filtering** Need a better filtering method than initiative. Idea - table still filters by cause, and any org with multiple initatives shows up in both tables. Later - sub-filter for initiatives within the cause.
**Org profile** - Place where orgs build a budget, a plan, interact with the community, post updates, communicate with EN, etc. Cause page becomes mission page
Change the background color within the text boxes to creamy white
**Initiative proposal** When proposing an initiative, users should also be able to look through preexisting initiatives.
**Org registration/nomination**
*Find orgs* In the registration/nomination dialog, there needs to be a way to paruse/search/scroll through all orgs that are in the db.
*Home page* The dialog should be the same from the home page button as well
**Remove** onclick from annulus 1 to cause page.
**Admin Vote visualization** Add mission-specific election overview in admin
**Voting acts like it works when not logged in** The phase 1 and 2 voting interface pretends to work when not logged in, even when the voting doesn't actually do anything. This is a minor issue, but makes the experience a bit confusing. We need 'log in to vote' on this page like it is on the home page. It should not be possible to do any voting at all when not logged in. Currently, it shows a different count whether im in account 1, account 2, or logged out. I think the issue may be connected with an inability to divide votes into shares of less than 1, and an inability to withdraw votes in the backend.
