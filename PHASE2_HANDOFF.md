# Earthbux — Phase 2 Build Brief (Org Experience)

> **You are an advanced model tasked with building "Phase 2" of the Earthbux platform: the full birth of the organization experience.** You do **not** have the repository. This document is your complete context: the system model, the current code shapes, the existing gaps, and the work to do. Ask for a specific file's contents only if a decision genuinely depends on code not reproduced here. Prefer designing against the shapes given below.

---

## 0. What "Phase 2" means here (read this first)

The word "phase 2" is overloaded in this project. Be precise:

- **Mission lifecycle Phase 2** = the *organization election* — the domain step where the community picks *which organization* runs an already-elected initiative. (Lifecycle phases 1–5 are described in §3.)
- **Build Phase 2** (your job) = **standing up the entire organization side of the product** so that the lifecycle's Phase 2, and everything downstream of it, has real UI and real endpoints. Concretely:
  1. **Org homepage / profile** — a public page for an organization, and an authenticated "org mode" for its members.
  2. **Org membership account** — a person operating as an organization (roles: community / rep / executive / beneficiary), including how a benefactor account switches into org mode.
  3. **Org nonprofit application** — the self-registration / onboarding flow by which a real organization enters the system, submits a mission statement to become a candidate, and *claims* a mission via the click-through legal agreement.

These three are the deliverable. The backend already has most of the *data* primitives (Organization, Membership, MissionCandidacy, VoteP2); what's missing is the **application/claim/membership endpoints** and the **entire org-facing frontend**. See §7 for the precise gap list.

---

## 1. What Earthbux is

Earthbux is a **weekly charity pool elected by its community**. Each week a **mission** for one of seven rotating **causes** opens and runs a multi-phase lifecycle: an **initiative election** (which idea?), an **organization election** (who runs it?), **budgeting**, **credit release**, and **resolution**. **Earthbux News (EN)** — the in-house media agency — supervises, publicizes, and helps organize missions, funded by a fixed cut of each pool.

The seven causes rotate one decision per week: **Atmosphere · Oceans · Land · Forests · Wildlife · Human Rights · Human Progress**.

Core philosophy: pool donations to avoid redundant/competing charity efforts, expose wasteful or fraudulent actors, and democratize *which idea* and *which organization* gets funded — then report on the work independently through EN. **Earthbux never creates its own organizations**; the community selects the best *existing* organization for the elected initiative and votes.

---

## 2. Architecture & stack

```
Browser (static HTML + inline JS)          FastAPI app (backend/app/main.py)
 ┌───────────────────────────┐             ┌──────────────────────────────────────┐
 │ index / cause / mission /  │   HTTP      │ routers/ ── crud.py ── models.py (ORM) │
 │ profile / admin / en .html │◄──────────► │ auth.py (JWT)  scheduler.py  database  │
 │ resources/js/ebx_shared.js │             └──────────────────── │ ───────────────┘
 └───────────────────────────┘                                    ▼
        ▲ built by esbuild from                             SQLite (earthbucks.db)
        └ frontend/src/ebx_shared.ts                        Alembic-migrated
```

- **Backend** — FastAPI + SQLAlchemy 2.0 (typed `Mapped[...]` ORM) + SQLite, schema managed by Alembic. Run with `uvicorn app.main:app`. The same process also serves the static HTML/JS, so frontend and API share an origin.
- **Frontend** — plain HTML pages with inline `<script>` blocks, plus a shared engine compiled from TypeScript: `frontend/src/ebx_shared.ts` → (esbuild `npm run build`) → `resources/js/ebx_shared.js`, exposed as a global `EBX`. **A `.ts` edit ships nothing until `npm run build` regenerates the JS.**
- **Auth** — JWT bearer tokens via `/auth/login`. Accounts carry a `role` (`benefactor | employee | admin`); `employee`/`admin` (`is_staff`) unlock staff-only actions. Org authority is **not** a role — it is expressed through **Membership** rows (a person ↔ org link with an org-role).
- **Naming convention everywhere**: `ben` = benefactor, `tiv` = initiative, `org` = organization (all length-3). Class names stay descriptive (`BenefactorAccount`, `Initiative`, `Organization`); attributes/FKs use the short form (e.g. `tiv_id = ForeignKey("initiatives.id")`).

---

## 3. The mission lifecycle (5 phases)

The **Mission** is the spine: exactly one per `(cause, cycle)`. Phases are **server-authoritative**, advanced by `scheduler.py`; the frontend only *displays* phase. Every boundary is measured from `mission.started_at` (the day the cause's window opens).

| # | Phase (`current_phase`) | Window from start | What happens |
|---|---|---|---|
| 1 | Pre / Initiative (`pre`→`initiative`) | weeks <1 → ~week 7 | Benefactors propose & vote on initiatives |
| 2 | **Organization election** (still `initiative`) | ends ~week 8 (cause's final active day) | Benefactors **nominate / register / vote** on organizations |
| 3 | Budget (`budget`) | weeks 9–16 | Elected org budgets & plans; **EN verifies the org**; advance released |
| 4 | Credit-Release (`credit`) | weeks 17–32 | Credits released in stages; progress reports |
| 5 | Resolution (`resolution`) | weeks 33+ | Final distribution & impact summary |

Scheduler transitions: `finalize_p1` elects the winning tiv (mission stays `initiative` while the org race runs) → `finalize_p2` sets the winning org and advances to `budget` → `distribute_mission` advances to `resolution`.

**Phase 2 detail (the heart of your build):** an initiative is a *proposition*; an organization is a **counterparty** that must receive funds and do the work. So Phase 2 is three steps, not one: **nominate → (register / claim) → elect.**

- **Nomination & registration are both open, no gate.** Organizations can self-register at any time; benefactors can nominate any org as a candidate for any Phase-2 mission. Minimum candidacy requirement: **a name and a mission statement**. Nominating and voting are **free**.
- **An org is a single entity** — it can run multiple missions but is **never nominated twice** and never has separate pages. On nomination, warn on near-duplicate names ("did you mean an existing org?").
- **Claiming a mission is THE gate.** A real representative *claims* the mission → their account gains authority over the **budget and mission sequence**. Claiming requires a **click-through legal agreement** (representative attestation — already drafted in `mission.html`, see §6). This establishes the basis to litigate fraud.
- **Identity verification is EN's job, during Phase 3** — so EN verifies only one org per week (the week's single elected mission).
- **If no org claims:** the mission is *not* cancelled. Advances still send; the community executes as best it can; EN still reports. These end with smaller pools.
- **Guaranteed-to-pool rate:** an unclaimed/nominated mission has a set guaranteed-to-pool rate that is **bumped when an org claims** — rewarding orgs for showing up and protecting benefactors when none do.

---

## 4. Data model (the 15-table v2 schema)

The Mission spine holds phase state + singular winner pointers (`winning_tiv_id`, `winning_org_id`); candidates live on back-ref collections. All money movement and vote mutations are logged in one append-only **Transaction** ledger; **Pool** is a derived cache.

Tables: `causes, missions, initiatives, organizations, benefactor_accounts, memberships, mission_candidacies, votes_p1, votes_p2, pools, credit_coins, posts, post_votes, queries, transactions`.

### The org-relevant tables (verbatim shapes you must build against)

```python
class Organization(Base):            # a vetted org; logs in via Memberships, not directly
    id: str  (PK)                    # string id, e.g. "org_xxx"
    name: str
    description: str | None
    website_link: str | None
    founded_year: int | None
    founding_member_id: int | None   # FK benefactor_accounts.id
    joined_at: datetime | None
    verified: bool = False           # EN sets this during Phase 3
    score: float = 0.0
    logo_url: str | None
    # relationships: memberships[], candidacies[], posts[]
    # NOTE: an org's CAUSES are DERIVED (org -> candidacies -> missions -> cause);
    #       there is no organization_causes link table.

class Membership(Base):              # person <-> org link (association object)
    id: int (PK)
    ben_id: int                      # FK benefactor_accounts.id
    org_id: str                      # FK organizations.id
    role: str = "community"          # community | rep | executive | beneficiary
    joined_at: datetime
    # UNIQUE(ben_id, org_id)

class MissionCandidacy(Base):        # an org's BID to run a specific mission (replaces OrgRegistration)
    id: int (PK)
    mission_id: str                  # FK missions.id
    org_id: str                      # FK organizations.id
    mission_statement: str | None
    status: str = "pending"          # pending | approved | withdrawn | won | lost
    submitted_by_id: int | None      # ben who nominated/submitted
    approved_by_id: int | None       # the employee who approved
    p2_vote_tally: int = 0           # denormalised
    created_at: datetime
    # UNIQUE(mission_id, org_id)     # -> an org is never nominated twice per mission

class VoteP2(Base):                  # ORG election: 1 vote/1 org; extra votes bought at rising prices
    id: int (PK)
    ben_id: int
    mission_id: str
    org_id: str
    votes: int = 1                   # 1 (free) + bought
    ebx_spent: int = 0
    valence: str = "helpful"         # helpful=support | neutral | harmful(=block the org)
    committed: bool = False
    created_at: datetime
    # UNIQUE(ben_id, mission_id)     # one row per (ben, mission)

class BenefactorAccount(Base):       # the personal login; org access is via Membership
    id: int (PK)
    email, handle, pass_hash
    role: str = "benefactor"         # benefactor | employee | admin  (is_staff = role in (employee,admin))
    vvv: bool = False                # set true after first Phase-2 vote (unlocks a cause-color perk)
    watched_tiv_ids: str | None      # JSON list
    # relationships: memberships[], credit_coins[], votes_p1[], votes_p2[], posts[]
```

Supporting shapes you'll touch: `Mission` (`current_phase`, `winning_tiv_id`, `winning_org_id`, `started_at`, `cause_id`, `cycle_num`, `budget`, `spent`), `Post` (org-authored posts use `author_type='org'` + `org_author_id`; org-targeted posts like *evaluation* use `org_id`; `category` ∈ `case|context|analysis|evaluation|org_update|editorial|headline`), and `Transaction` (ledger; `type='transfer'` with `bucket ∈ pool|org|earthbux|evaluation|credit|refund` and `counterparty_org_id` when paid to an org).

---

## 5. Existing backend surface for orgs (what already works)

**Pydantic schemas** (Pydantic v2, `from_attributes=True`):
- `OrganizationCreate{ id, name, description?, website_link?, founded_year?, verified?, founding_member_id? }` → `OrganizationRead{ ...id, joined_at?, score, logo_url? }`
- `MembershipRead{ id, ben_id, org_id, role, joined_at }` — **no `MembershipCreate` exists yet.**
- `MissionCandidacyCreate{ mission_id, org_id, mission_statement? }` → `MissionCandidacyRead{ ...id, status, submitted_by_id?, approved_by_id?, p2_vote_tally, created_at }`
- `VoteP2Create{ org_id, votes>=1, ebx_spent>=0, valence }` → `VoteP2Read{...}`

**CRUD (`crud.py`) that exists:**
- `list_orgs(db, cause_id=None)` — cause filter joins through candidacies→missions.
- `get_org(db, org_id)`, `create_org(db, OrganizationCreate)`, `org_cause_ids(db, org_id)` (derived).
- `add_membership(db, ben_id, org_id, role="community")` (upsert), `list_memberships(db, ben_id=?, org_id=?)`.
- `create_candidacy(db, MissionCandidacyCreate, submitted_by_id=?)`, `list_candidacies(db, mission_id=?, org_id=?, status_filter=?)`, `approve_candidacy(db, candidacy_id, staff)` (staff-only → status `approved`).
- `cast_p2(db, ben_id, mission_id, org_id, votes=1, ebx_spent=0, valence="helpful")` (upsert; sets `vvv`), `commit_p2(db, ben_id, mission_id)`, `p2_tally(db, mission_id)` (net votes, blocks subtract), `finalize_p2(db, mission_id)`.

**Routers that exist:**
- `GET  /organizations` (opt `?cause_id=`), `GET /organizations/{id}`, `GET /organizations/{id}/causes` — **public reads**.
- `POST /organizations` — **staff-only** (`get_current_staff`). ← *this is the problem for self-registration; see §7.*
- `POST /candidacies` (authed benefactor), `GET /candidacies` (public, filterable), `POST /candidacies/{id}/approve` (staff).
- `GET /benefactors/me/memberships`, `.../credit-coins`, `.../watchlist`, `.../p1-votes`.
- Votes router: `PUT /missions/{id}/p1/votes`, `/p1/commit`, `/p1/tally`, `POST /missions/{id}/p2/vote`, `/p2/commit`, `/p2/tally`.

Error convention: domain errors raise `ValueError` (→ 4xx), permission errors raise `PermissionError` (→ 403); staff routes use the `get_current_staff` dependency, authed routes use `get_current_benefactor`.

**Phase-2 voting economics** (from the design docs — implement/confirm in `crud.cast_p2` pricing): one vote per benefactor, **no split** (contrast Phase 1 which splits shares). Extra votes are **bought on a steep curve**: 1st free, 2nd 10 EBX, 3rd 20, 4th 40 … i.e. `price(votes_held) = 10 × 2^(votes_held − 1)` EBX, spent outright (never committed to pool as a refundable). Eligibility is tied to having a stake in the mission (committed in Phase 1 / holds the mission's credit coin — *credits = membership*). Settlement: **100% of your commit is sent if your org wins, 20% if not.** Tallied on the cause's final active day.

---

## 6. Existing frontend for orgs (what's already on the page)

- `mission.html` — **skeleton exists.** It renders a "mission hub" card and, crucially, a **working click-through legal agreement modal** (`openOrgAgreement('claim'|'register')` → checkbox-gated → `acceptOrgAgreement()`). Right now acceptance is **client-side only** — there is a `// TODO: POST acceptance + claim/register to backend once the endpoint lands.` This is your hook for the claim/register flow.
- `profile.html` — benefactor profile exists (credit-coin wallet, choices table, settings) and has a **"Switch to Organization mode" toggle gated on holding a credit coin → membership picker**. The **organization profile itself is not built** (initiative coins, tasklist, memberships view, org ring). Staff also get a "Switch to admin mode" toggle that re-renders profile as the admin console.
- `cause.html` — the election surface; Phase-2 area (org election: evaluation/context/analysis + org pitch; nominate/register entry) is **partial**. There is a known bug: "P2 Area doesn't seem to be updating."
- `index.html`, `admin.html`, `en.html` — home, data console, and EN editorial layer (en.html is a skeleton).
- Shared engine `EBX` (global) exposes loaders (`loadCauses`, `loadOrganizations`, `loadMissions`, `loadInitiatives`, `loadFeed`), `initPage()`, `getParam()`, and `config`. **The old client-side election simulation has been fully removed** — the client no longer fabricates vote state; pages render honest empty states and read real v2 API shapes.

---

## 7. The gaps you must close (Build Phase 2 scope)

These are the concrete missing pieces between "data primitives exist" and "the org experience is alive."

### A. Org nonprofit application / self-registration
- **Problem:** `POST /organizations` is **staff-only**, but the design says *"organizations can self-register at any time, no gate."* Build a **public org application/registration endpoint** (authed benefactor becomes `founding_member_id`, auto-creates an `executive` **Membership** for the creator, generates the `org_id`, sets `joined_at`).
- **Duplicate detection:** on submit, run fuzzy name matching against existing orgs and surface "did you mean an existing org?" before creating. (Matching threshold tunable.)
- **UI:** a nonprofit application form (name, description, website, founded year, logo, mission focus). Entry points from `index.html` and `cause.html` nominate/register dialogs, and from `mission.html`'s "Register your organization" button.

### B. Org membership account (operating as an org)
- **Add `MembershipCreate` schema + endpoints** to create/list memberships (currently only `crud.add_membership` exists with no route, and `GET /benefactors/me/memberships` for reads). Needed: invite/add a member, set role (`community | rep | executive | beneficiary`), and the "switch to org mode" backing data.
- **Wire `profile.html`'s "Switch to Organization mode"** to a real org profile: initiative coins, mission tasklist, memberships list, org-authored posts. Respect org-roles (only `rep`/`executive` may edit the mission page/budget).
- **Beneficiary voice:** a beneficiary is a membership role with a **unique profile surface** and **a voice at the start of Phase 2** — scaffold where this renders.

### C. Org homepage / public profile
- Build the **public organization page** (read `GET /organizations/{id}` + derived `/causes` + its candidacies + its posts + score). This is distinct from the authenticated org-mode view. Design the org page to become the anchor an org grows into (later: budget, plan, progress reports live on `mission.html`, not here).

### D. The claim gate (wire the legal agreement to the backend)
- **Add org claim endpoints + an acceptance record** so `mission.html`'s `acceptOrgAgreement()` persists server-side. Claiming should: verify the actor is a `rep`/`executive` member of the org (or create that membership as part of claiming), record the click-through acceptance (attestation text version + timestamp + ben_id), and grant the org authority over the mission's budget/sequence. A **nominated (not self-registered) org has until the start of Phase 4 to claim.**
- **Guaranteed-to-pool rate:** store an unclaimed rate and **bump it on claim** (see pool math in §8). Rates are placeholders — make them config-driven.

### E. Candidacy → election polish
- Candidacy requires **name + mission statement** to *receive votes* (an org can be a candidate and post without approval, but must submit a mission statement for a tiv **before it is elected** to receive votes). Enforce this.
- Fix the **"P2 Area doesn't update"** bug on `cause.html` (org standings/vote widget not refreshing).
- Phase-2 negative/**block** votes (`valence='harmful'`) — schema exists, UI deferred but design it (reputationally sensitive; gate carefully).

---

## 8. Money model (only what Phase 2 touches)

Money is **never refunded**; a vote's "send rate" only sets the irrevocable-vs-returnable split computed later at credit release. 1 credit = 1 EBX ≈ $1.

- **Phase-1 → pool:** after Phase 1, every committed EBX lands in one of two buckets — **pool minimum sent** (20% if your initiative won, 10% if it lost) and **the remainder stays committed to the mission**. Holding a stake mints a **credit coin** (locked until end of Phase 3); *holding a credit coin = membership in that mission* and is the eligibility key for Phase-2 voting.
- **Phase-2 → org:** **100%** of your commit is sent if your org wins, **20%** if not. Extra org votes are bought outright on the `10 × 2^(n−1)` curve and go straight to the pool.
- **Phase-2 withdrawal (already implemented):** while the org race is open (after tiv elected, before `budget`), a benefactor may withdraw their Phase-1 commitment **minus the send** (20% if they backed the winning tiv, else 10%) via `POST /missions/{id}/p1/withdraw` → booked to the `refund` bucket; the send stays in the pool.
- **Guaranteed-to-pool rate (you build):** unclaimed missions guarantee a set fraction to the pool; claiming **bumps** it. This protects benefactors when no org shows up and rewards orgs that do.
- **Resolution split (context):** at resolution the pool is allocated in 32nds — EN 10/32, Org guaranteed 10/32 (the budgeting floor), post rewards 3/32, flexible remainder 9/32. Org's guaranteed 10/32 of today's pool is its budgeting **minimum**; the **maximum is uncapped** (guaranteed + flexible, both grow with new donations).
- **Phase-3 org-loss withdrawal is deferred** (80% withdrawable after acknowledging distrust of the winning org) — do **not** build it now; just don't block it.

---

## 9. Current DB / runtime state

- Genesis `2026-06-15`. First rotation: `atm0, oce0, lan0, for0, wil0, hmr0, hpr0`; cause *i* cycle *k* opens at `genesis + (i + 7k)·week`. Mission ids = `<prefix><cycle>` (atm/oce/lan/for/wil/hmr/hpr).
- Seeded: **7 causes · 4 accounts · 35 orgs · 55 initiatives (catalog) · 7 missions.** As of the last snapshot `atm0 = initiative (open)`, the rest `pre`, opening weekly through 2026-07-27.
- `scheduler.run_due()` advances due phases; it's throttled and wired into `GET /missions`, so reads keep the clock current (no separate cron).

---

## 10. How to run (for the environment that will execute your output)

```bash
cd backend
./.venv/bin/python -m alembic upgrade head                 # schema
./.venv/bin/python -m seed.port_v1                          # idempotent data port
./.venv/bin/python -c "from app.database import SessionLocal; from app import bootstrap; bootstrap.bootstrap(SessionLocal())"
./.venv/bin/uvicorn app.main:app --reload --port 8000       # pages + /admin + /docs
# Frontend engine rebuild after editing TS:
cd ../frontend && npm run build                             # ebx_shared.ts -> resources/js/ebx_shared.js
```

New Alembic migrations are required for any new columns (e.g. an acceptance/claim record, guaranteed-to-pool rate). Head migration is `a9f2c1b4d7e3` (the mission-centric rebuild).

---

## 11. Your deliverable

Produce, for Build Phase 2 (the org experience):

1. **Backend:** new/changed schemas (`MembershipCreate`, org application/claim bodies, acceptance record), CRUD functions, routers, and an Alembic migration for any new columns. Keep the `ben/tiv/org` naming and the `ValueError`/`PermissionError` error convention. Reuse `add_membership`, `create_candidacy`, `cast_p2`, `finalize_p2` where they already fit.
2. **Frontend:** the nonprofit application form, the public org page, the authenticated org-mode profile (wire `profile.html`'s existing toggle), and the wired claim flow on `mission.html` (replace the client-only `acceptOrgAgreement` TODO). Read real v2 API shapes; render honest empty states; no client-side simulation.
3. **Fixes:** the `cause.html` P2-area-not-updating bug and the candidacy "must have a mission statement to receive votes" rule.
4. **Respect invariants:** an org is a single entity (never duplicated), org authority flows through Membership roles (not the account `role`), the claim is the only gate, phases are server-authoritative, and money is never refunded.

Start by proposing the endpoint + schema + migration surface for **(A) nonprofit application**, **(B) membership creation**, and **(D) the claim gate**, then the three frontend surfaces. Ask for any specific file only if a decision depends on code not reproduced above.
