# Backlog

> Loose ideas and deferred work. Order roughly least → most intensive.
> Promote items into `structure.md` / `mission_lifecycle.md` as they firm up.

## Phase 2 / organizations
- [ ] Org claim flow wired to backend (authority transfer + acceptance record).
- [ ] Duplicate-org detection on nominate (fuzzy name match + "did you mean?").
- [ ] Guaranteed-to-pool rate: set unclaimed rate, bump on claim.
- [ ] EN verification queue (one org/week) + revoke authority control.
- [ ] Beneficiary voice surface at the start of phase 2.
- [ ] Negative/block (`harmful`) org votes — schema exists; UI deferred (reputationally sensitive).

## Cause / election UI
- [ ] Election-card nav buttons: View (jump to table row) · Explore (cause page) · Vote.
- [ ] Move overview into the table; clicking a row expands it and filters discussion.
- [ ] Pool metrics: "guaranteed pool" vs "committed pool".
- [ ] Vote visualization (count + relative commit size per vote).
- [ ] Start dates on every mission card; show future dates after the cause shift.
- [ ] "Log in to vote" gating on the cause page (no phantom voting when signed out).

## Profiles
- [ ] Organization profile (initiative coins, tasklist, annulus 4, memberships).
- [ ] Beneficiary profile page.
- [ ] Credit-badge colorization perk (participation threshold $10; `vvv` flag).
- [ ] Profile ring sticky to the rhs with badge in the corner (design on backburner).

## Discussion / EN
- [ ] Post category routing (Case/Context/Analysis/Evaluation) by phase & scope.
- [ ] Post rewards (EBX for most-helpful) and visibility tied to donation size.
- [ ] EN feed layout + parallel progress reports.

## Credit page / money (backlogged until phases 1–2 complete)
- [ ] Mission annulus / ring widget (deadlines, 7–12 steps).
- [ ] Credit lifecycle: generic → cause → mission → org → live; coin value parameters.
- [ ] Exchange (non-donation) + donation/tax-deductibility flow; EN $100 pool threshold.

## Infra / admin / testing
- [ ] Admin event log (vote_events) + duplicate/invalid-vote flags + CSV export.
- [ ] `is_test` column + `cyclestart` config endpoint for simulations.
- [ ] Apache stack (Kafka/Flink/Airflow/Cassandra) — future.
- [ ] v2-compatible seeder (pilot/seed are stale against the current schema).
- [ ] Working-tree corruption: avoid concurrent writers (mount sync vs uvicorn --reload); commit often.

## Founding
- [ ] First 100 BenefactorAccount signups receive 49 EBX automatically (id < 100).
