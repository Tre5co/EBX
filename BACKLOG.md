# Earthbucks — Backlog

Deferred items captured during planning. Roughly ordered by priority.

## Soon

- [ ] **Founding 49-EBX bonus.** First 100 BenefactorAccount signups should receive 49 EBX automatically. Implement as either (a) a startup hook that grants on signup if `id <= 100`, or (b) a one-time admin script after the first 100 register. Decide which.
- [ ] **Real vote tally.** Add a `Vote` model (`benefactor_id`, `organization_id`, `cause_id`, `cycle_num`) and a `/causes/{id}/votes` endpoint. Replace the deterministic mock in `EBX.Votes.forCause`.
- [ ] **Initiative ratings.** `Initiative.rating` exists on the model but no endpoint to update it. Add `POST /initiatives/{id}/ratings`.
- [ ] **Organization logos.** Add `logo_url` to `Organization`. Until logos are uploaded, render a colored circle with the org's initials. Logos serve as a verification layer when the team approves orgs.
- [ ] **Mission logos.** Add `logo_url` to `Mission` for the credit-coin badge. Initials placeholder until set.

## Verification & perks

- [ ] **Blue-check via vote participation.** Below a donation threshold, a benefactor must have participated in at least one org vote to unlock the colored credit-badge perk. Add `verified_via_vote: bool` to `BenefactorAccount`, set after first vote.
- [ ] **Donation threshold.** Define and store the threshold amount (env var or config row). Compute on the fly per benefactor.

## UI / annulus

- [ ] **Outer-ring color polish.** Currently leader=cause-color, runners-up fade toward white. Revisit once real initiatives populate.
- [ ] **Connection between active segment and election panel.** Iterate on the visual link (currently: empty outer ring + chevron on panel).
- [ ] **Improve "go to benefactor or org home" flow.** The 7-sector ring currently sends users to `cause.html`. Eventually it should branch by user type (benefactor vs. org rep).

## Profile / accounts

- [ ] **Profile badge.** Same geometry as the credit badge but shows benefactor initials in the center and segments filled per contributions across causes.
- [ ] **Credit badge.** One segment filled per credit-coin issued, mission logo (or initials) in the center.
- [ ] **Org-account flow.** Auto-create an OrgAccount when a benefactor receives a credit coin, and prompt them to upgrade if they're an org employee.

## Infra

- [ ] **Postgres path.** Stay on SQLite for dev; pick Postgres for prod and document the env-var swap.
- [ ] **Pagination on /posts and /initiatives.** Current `limit` only.
- [ ] **Vote model migration.** Generate via `alembic revision --autogenerate` once Vote is added.

## Polish / not blocking

- [ ] **About page.** Linked from footer but doesn't exist yet.
- [ ] **Org page.** A view for an Organization's profile (missions, reviews, members).
- [ ] **Search across initiatives + orgs + causes.** The old `stats.html` had a stub for this; a real version belongs on its own page.
- [ ] **Tests.** No test suite yet. Pick pytest for backend, vitest or playwright for frontend smoke.
