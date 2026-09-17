# Earthbux ↔ Organization — Mission Agreement (DRAFT)

> Working draft of the claim-gate contract. This document describes Earthbux's
> relationship to the organization and to the mission. The click-through
> representative attestation on mission.html is the acceptance mechanism; each
> acceptance is recorded server-side (attestation version + timestamp + account,
> table `org_claims`). NOT LEGAL LANGUAGE YET — structure and substance first,
> counsel later.

## Parties & scope

- **Earthbux** — the platform and pool administrator; **Earthbux News (EN)** —
  its in-house media agency, funded by a fixed cut of each pool.
- **The Organization** — the entity whose authorized representative passes the
  claim gate for one specific **Mission** (one cause, one cycle).
- The agreement binds per-mission. An organization running several missions
  accepts once per mission.

## 1. Representative attestation

(As presented at the claim gate — v. `draft-2026-07`.)

1. The signer is an authorized representative of the organization, and the
   information provided about it is truthful and accurate.
2. EN will verify the organization's identity during the budgeting phase;
   misrepresentation is grounds for removal, public disclosure, and legal action.
3. The initial advance is released at the start of the budgeting phase; the full
   charity pool unlocks only after verification and against agreed budget and
   reporting obligations.
4. The organization will operate the mission in good faith — publish a budget,
   report progress honestly, and direct funds to the stated cause and beneficiary.
5. Accepting authority over the budget and mission sequence is a binding
   commitment; funds obtained through fraud may be recovered through litigation.

## 2. Reporting consent

By passing the claim gate, **the organization agrees to be reported on by
Earthbux** (EN): supervision, publicity, progress coverage, and a parallel EN
progress report alongside the organization's own, moderated by benefactors.

## 3. Money routing

- Earthbux agrees to **route untaxed money to the organization based on the
  socially selected service/supply suggestions** (the community-approved S/S/S
  picks recorded on the mission).
- Routing follows the mission's **step plan**: each release-phase STEP carries a
  **guaranteed** and a **potential** pool (no maximums), finalized by the end of
  the budgeting phase.
- Donations are routed through Earthbux to the organization or the community;
  most value remains in benefactor wallets as EBX. What benefactors keep as EBX
  (rather than converting/withdrawing) determines the pool available to budget.
- The guaranteed-to-pool rate rises when the mission is claimed (currently
  20% unclaimed → 35% claimed; config-driven placeholders).

## 4. Communication clause (both directions)

- **The available money declines if the organization fails to communicate with
  Earthbux** — missed progress reports, unanswered benefactor questions, or
  unreachable representatives reduce the releasable pool on a published
  schedule (schedule TBD).
- **Earthbux is bound symmetrically**: if Earthbux fails to meet its own
  communication and reporting obligations to the organization, Earthbux forfeits
  value on the same schedule. Both directions are part of this contract.

## 5. Resolutions & value

- The mission closes through **many small resolutions** (achieved suggestions
  and resolved steps), not a single resolution event. Each landed resolution
  grants its evaluation point and moves the mission's credit-coin value.
- Resolving steps **ahead of schedule earns a higher cash reward** (rate TBD).
- Realistically, missions can fail (bad-actor claims or extreme costs). Failure
  handling: unresolved steps' guaranteed pools, refund/return rules, and EN's
  closing report — TBD.

## 6. Nonprofit status

Earthbux works with the organization to apply for legal nonprofit status; the
application begins when the election is won, and **donations cannot flow to the
organization until nonprofit status is achieved**.

## 7. Enforcement & override

- Earthbux retains override authority (e.g. revoking a claim from a fraudulent
  or inactive representative).
- The recorded acceptance (version, timestamp, account) is the litigation basis.

---
*Open items: decline schedules (§4), early-resolution bonus rate (§5), failure
handling (§5), jurisdiction/governing law, beneficiary standing.*
