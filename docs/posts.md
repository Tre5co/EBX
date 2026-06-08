# Post Categories — Election Commentary Design

## Overview

Each election phase (tiv vote, org vote) surfaces benefactor-supplied commentary in the phase area of `cause.html`. During the active phase, commentary lives in the voting dialog. After the election, it appears in the recap. The most helpful post in each supercategory is displayed prominently alongside its **helpfulness prize**.

Posts are voted on with: **Helpful / Neutral / Wrong**

---

## Benefactor Post Categories

### Shared (Tiv + Org elections)

**1. Context** — Background that helps voters understand what they're deciding on.
For the tiv vote: what is this initiative, who has tried it before, who would it help most, what are the main challenges.
For the org vote: what is this organization, what have they done before, how do they connect to this cause.
This is the catch-all educational supercategory. One featured post per election phase.

**2. Analysis** — Data-driven or expert takes.
Scientific/research backing for an initiative, independent assessment of an organization's financials or track record, criticism of a proposal or methodology.
Keeps commentary rigorous and separates opinion from evidence. One featured post per election phase.

---

### Tiv Vote–Specific

**3. Case** — "Why I voted for this initiative."
Replaces "ratings." This is the voter-perspective post: personal reasoning, values, stakes. Allows passionate advocacy without a numeric score muddying the signal.

---

### Org Vote–Specific

**4. Evaluation** — "Why I voted for this organization."
Replaces "reviews." Covers leadership, mission proposal quality, org content, credibility. Same idea as Case but targeted at the org race.

---

## Summary Table

| # | Name | Scope | Replaces |
|---|------|-------|----------|
| 1 | Context | Both | — |
| 2 | Analysis | Both | — |
| 3 | Case | Tiv vote | Initiative ratings |
| 4 | Evaluation | Org vote | Org reviews |

Featured slot in the phase area shows the top-voted post from each applicable category, plus the helpfulness prize earned by its author.

---

## Backlog

- **Remove star ratings.** Star ratings are unnecessary and create confusion alongside the voting system. The Helpful/Neutral/Wrong post votes and the tiv/org election votes are sufficient signal. Cut star ratings from both benefactor and org post flows.
- **More post categories** 
    - **`PostVote` cardinality on org-vote posts.** for analysis and context, the vote count should aggregate from phase 1 through phase 2.
    - **`POST /posts/{id}/vote` shape elaboration** A per-post sum of each, which aggregates into a score +1 for helpful or -1 for wrong. Neutral votes will play into the visibility of the post and allow people to add to the discussion
    post phase 2:
    - mission ideas (idea i.e. a thoughtful suggestion for how the org should proceed).
    Org posts: 
    - `mission proposals` (When competing for an org election)
    - `mission_ideas`
    - `mission updates`
    - `feedback`
    EBX posts: 
    - `status-updates` on the mission metrics.