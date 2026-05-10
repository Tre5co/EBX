# Earthbucks — Backlog

Deferred items captured during planning. Roughly ordered by priority.

---
<!-- NEXT -->
<!--
Profile page and cause page each need "EBX" in top left of page.
-->
---
## Organizations
- [ ] **Organization logos.** Add `logo_url` to `Organization`. Until logos are uploaded, render a colored circle with the org's initials. Logos serve as a verification layer when the team approves orgs. This is 1/2 of the credit coin.

## Cause/Initiative page
- [ ] **Mission updates.** Replace filler information in "Current Cycle" Panel with "Vote week dayx - dayy", and a row with the current mission title (Organization -> Initiative) linked to the mission page.

- [ ] **Initiative ratings.** `Initiative.rating` exists on the model but no endpoint to update it. Add `POST /initiatives/{id}/ratings`. 

- [ ] **Cause Annulus** Annulus pie chart showing the leading initiatives for the upcoming vote.

- [ ] **Page Structure** Default page structure sorts the initiatives with the leaders at the top. There will eventually be other ways to sort (trending, date proposed, search).

- [ ] **Initiative Logos** The other half of the credit coin. Will be complicated to define/create credit coins

- [ ] **Home navigation** EBX logo takes you home.

## Mission page

- [ ] **Mission Annulus** Deadlines. Budget submission, beneficiary approval/outreach, issue resolution (for example, a response to donor questions), Earthbux check-ins

## Credit
- [ ] **Coin generation** Coins and mission are created when org is elected. Coins have same geometry as annulus but their cause segment is the only one highlighted and the relative value to when it was created in the middle.

- [ ] **Coin details** The coin can be expanded to show details like "Pool for this mission", "Value donated", Transaction history for this mission...

- [ ] **Transactional logic** Coins operate similarly to a cryptocurrency, can be exchanged for coins from other missions. All coins are donations, although can be removed which will be complex tax-law-wise.

## Profile / accounts
- [ ] **Home navigation** EBX logo takes you home.
- [ ] **Profile badge.** Same geometry as the main annulus and credit badge but shows benefactor initials in the center and segments filled per contributions across causes.
- [ ] **Credit badge.** mission logo (or initials) in the center. Annulus fills with the cause color throughout first 49 days of mission.
- [ ] **Org-account flow.** Auto-create an OrgAccount when a benefactor receives a credit coin, or help them create one if they're an org employee.
- [ ] **Logo colorization via vote participation.** Below a donation threshold, a benefactor must have participated in the org vote to unlock the colored perk for that weeks sector. Add `verified_via_vote: bool` to `BenefactorAccount`, set after first vote.

## Feed
- [ ] **Types of post** Benefactor posts: Initiative ratings, organization reviews, mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed). Org posts: Mission ideas, mission updates, mission proposals (When competing for an org election), problems (asking users for feedback/ideas). EBX posts: Stories, status-updates on the mission metrics.

## About us
- [ ] **Better access point** Will fill in after rest of UI is in order.

## Verification & perks

- [ ] **Donation threshold.** Define and store the threshold amount (env var or config row). Compute on the fly per benefactor. Threshold for initiative donations moderates logo colorizaton and for org donations it moderates user visibility/voice.
- [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implement as either (a) a startup hook that grants on signup if `id <= 100`, or (b) a one-time admin script after the first 100 register. Decide which.

## UI / annulus
- [ ] **Real vote tally.** Add a `Vote` model (`benefactor_id`, `organization_id`, `cause_id`, `cycle_num`) and a `/causes/{id}/votes` endpoint. Replace the deterministic mock in `EBX.Votes.forCause`.

## Infra

- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only.
- [ ] **Vote model migration.** Generate via `alembic revision --autogenerate` once Vote is added.

## Polish / not blocking

- [ ] **About page.** Linked from footer but doesn't exist yet.
- [ ] **Org page.** A view for an Organization's profile (missions, reviews, members).
- [ ] **Search across initiatives + orgs + causes.** The old `stats.html` had a stub for this; a real version belongs on its own page. From feed
- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke.

## Annulus extensions

- [ ] **Mission-progress annulus.** Each mission gets its own ring widget showing progress vs. budget over its execution window. Distinct from the homepage cycle annulus. Flow from homepage to mission page. Will increase in complexity

## Cycle / process modeling

- [ ] **Dual-decision week.** Each cause has TWO per-cycle decisions a week apart: an initiative-decision (week N) followed by an org-election-decision (week N+1). That means in any given calendar week a single cause may show two distinct active initiatives — one outgoing (currently in org-vote) and one incoming (just won initiative debate). The current `Cycle` engine collapses both into one weekly tick; revisit when wiring real Vote/Initiative state through the race card's two halves.
