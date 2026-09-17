"""Public community stats — the two numbers the landing page is allowed to say.

Added 2026-08-18 (build-seq §1). structure.md §1c asks the landing page to
"Display #Activeusers" and to draw the funding runway as
`total funds / user count = weeks`. Before this endpoint existed index.html
guessed both: it summed `voter_count` across every mission's phase-1 tally and
treated the total as a member count, which double-counts anyone who votes in
more than one mission and counts vote ROWS rather than people. On the current
database that guess reads 19 where the answer is 4.

Deliberately public and deliberately thin: two counts and one total, no
identities, nothing a scraper could turn into a member list. The staff console
(`/admin/accounts`) remains the only surface that names anybody.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, union
from sqlalchemy.orm import Session

from .. import wallet
from ..database import get_db
from ..models import BenefactorAccount, VoteP1, VoteP2

router = APIRouter(prefix="/stats", tags=["stats"])

# 1 EBX = 10c. Fixed by the model, not by configuration — the grant is "ten
# dimes a week" and the landing page says so in those words.
EBX_CENTS = 0.10
WEEKLY_GRANT_EBX = 10


@router.get("", response_model=dict)
def community_stats(db: Session = Depends(get_db)) -> dict:
    """Members, active members, and the money they have committed.

    members         — live non-staff accounts.
    active_members  — those of them carrying at least one vote row in either
                      election. This is the divisor in the runway chart: every
                      active member is granted 10 EBX (= $1) a week.
    committed_tokens — what MEMBERS have put behind a decision, read out of the
                      wallet: committed tokens plus the EBX they have minted
                      into plus what has already crossed as a donation. Every
                      state except unallocated, because every one of them is
                      money that is no longer free.

    §0a (2026-09-08) — **this endpoint was adding two things that are not the
    same and missing a third.** It summed the legacy float `VoteP1.ebx_committed`
    and then `VoteP2.ebx_spent`, which is not a phase-2 stake at all: it is
    `p2_vote_cost`, the price of EXTRA votes, and `p2_vote_cost(1)` is 0 by
    design. Nobody has ever bought an extra vote, so the phase-2 term was
    identically zero and the whole organization-election side of the platform —
    72 tokens standing in live races — counted as nothing. The phase-1 term was
    the retired unit, carrying the un-roundable legacy 1.7142857 with it, so the
    landing page published a **fractional token count** (152.7143), which the
    model cannot express.

    It also mixed its scopes: `members` and `active_members` count live
    benefactors, while the money summed EVERY vote row in the table, staff
    included. The GameMaster admin account holds 111 of those 152 tokens, so
    three quarters of the published "committed" belonged to an account the
    membership count deliberately excludes, and the runway divided one
    population by another.

    All three are one fix: ask `wallet.read_wallet` — the module that is
    already the single reader of a benefactor's money — once per live member,
    and add up what it says. No second opinion, and the unit is whatever the
    wallet says it is.
    """
    members = db.scalar(
        select(func.count(BenefactorAccount.id)).where(
            BenefactorAccount.is_active.is_(True),
            BenefactorAccount.role == "benefactor",
            BenefactorAccount.is_test.is_(False),   # bots are not members
        )
    ) or 0

    live_ben_ids = select(BenefactorAccount.id).where(
        BenefactorAccount.is_active.is_(True),
        BenefactorAccount.role == "benefactor",
            BenefactorAccount.is_test.is_(False),   # bots are not members
    )
    voters = union(
        select(VoteP1.ben_id).where(VoteP1.ben_id.in_(live_ben_ids)),
        select(VoteP2.ben_id).where(VoteP2.ben_id.in_(live_ben_ids)),
    ).subquery()
    active_members = db.scalar(select(func.count()).select_from(voters)) or 0

    behind_ct = 0
    for (ben_id,) in db.execute(live_ben_ids).all():
        try:
            w = wallet.read_wallet(db, int(ben_id))
        except ValueError:
            continue
        # 2026-09-16 — `donated_ct` is final-so-far, an overlay on committed +
        # minted, so it is not added again.
        behind_ct += int(w.committed_ct) + int(w.minted_ct)
    committed_tokens = behind_ct / 100.0

    weekly_cost_usd = active_members * WEEKLY_GRANT_EBX * EBX_CENTS
    committed_usd = committed_tokens * EBX_CENTS

    return {
        "members": int(members),
        "active_members": int(active_members),
        "committed_tokens": round(committed_tokens, 2),
        "committed_ct": behind_ct,
        "committed_usd": round(committed_usd, 2),
        "weekly_grant_ebx": WEEKLY_GRANT_EBX,
        "ebx_cents": EBX_CENTS,
        "weekly_cost_usd": round(weekly_cost_usd, 2),
        # weeks the committed money could keep granting every active member
        # their 10 EBX — structure.md §1c's "total funds / user count = weeks".
        "runway_weeks": int(committed_usd // weekly_cost_usd) if weekly_cost_usd else 0,
    }
