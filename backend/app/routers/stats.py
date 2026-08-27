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
    committed_ebx   — what benefactors have actually put behind a decision:
                      phase-1 EBX plus phase-2 EBX. Uncommitted draft rows are
                      excluded from phase 1 (a slider someone is still dragging
                      is not funding).
    """
    members = db.scalar(
        select(func.count(BenefactorAccount.id)).where(
            BenefactorAccount.is_active.is_(True),
            BenefactorAccount.role == "benefactor",
        )
    ) or 0

    live_ben_ids = select(BenefactorAccount.id).where(
        BenefactorAccount.is_active.is_(True),
        BenefactorAccount.role == "benefactor",
    )
    voters = union(
        select(VoteP1.ben_id).where(VoteP1.ben_id.in_(live_ben_ids)),
        select(VoteP2.ben_id).where(VoteP2.ben_id.in_(live_ben_ids)),
    ).subquery()
    active_members = db.scalar(select(func.count()).select_from(voters)) or 0

    p1 = db.scalar(
        select(func.coalesce(func.sum(VoteP1.ebx_committed), 0.0)).where(
            VoteP1.committed.is_(True)
        )
    ) or 0.0
    p2 = db.scalar(select(func.coalesce(func.sum(VoteP2.ebx_spent), 0.0))) or 0.0
    committed_ebx = float(p1) + float(p2)

    weekly_cost_usd = active_members * WEEKLY_GRANT_EBX * EBX_CENTS
    committed_usd = committed_ebx * EBX_CENTS

    return {
        "members": int(members),
        "active_members": int(active_members),
        "committed_ebx": round(committed_ebx, 4),
        "committed_usd": round(committed_usd, 2),
        "weekly_grant_ebx": WEEKLY_GRANT_EBX,
        "ebx_cents": EBX_CENTS,
        "weekly_cost_usd": round(weekly_cost_usd, 2),
        # weeks the committed money could keep granting every active member
        # their 10 EBX — structure.md §1c's "total funds / user count = weeks".
        "runway_weeks": int(committed_usd // weekly_cost_usd) if weekly_cost_usd else 0,
    }
