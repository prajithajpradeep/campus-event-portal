import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.models import User
from app.schemas.common import Page
from app.schemas.user import UserOut, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """View my profile."""
    return current_user


@router.patch("/users/me", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update my profile (currently just the display name)."""
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/users", response_model=Page[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    """Admin: paginated list of all users (feeds the dashboard)."""
    query = db.query(User)
    total = query.count()
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    pages = (total + size - 1) // size if total else 0
    return Page(items=users, total=total, page=page, size=size, pages=pages)
