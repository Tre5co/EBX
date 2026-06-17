"""Shared dependencies for v2 routers."""
from fastapi import Depends, HTTPException

from ..auth import get_current_benefactor
from ..models import BenefactorAccount


def get_current_staff(
    user: BenefactorAccount = Depends(get_current_benefactor),
) -> BenefactorAccount:
    """Gate employee-only routes (approvals, distribution, query console)."""
    if not getattr(user, "is_staff", False):
        raise HTTPException(status_code=403, detail="Earthbux employee account required")
    return user
