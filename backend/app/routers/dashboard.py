import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.database import get_db
from app.models import Event, Registration, RegistrationStatus, User
from app.schemas.common import DashboardStats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Admin dashboard: high-level counts for users, events and registrations."""
    now = datetime.now(timezone.utc)
    return DashboardStats(
        total_users=db.query(func.count(User.id)).scalar() or 0,
        total_events=db.query(func.count(Event.id)).scalar() or 0,
        upcoming_events=db.query(func.count(Event.id))
        .filter(Event.start_time >= now)
        .scalar()
        or 0,
        total_registrations=db.query(func.count(Registration.id)).scalar() or 0,
        active_registrations=db.query(func.count(Registration.id))
        .filter(Registration.status == RegistrationStatus.registered)
        .scalar()
        or 0,
    )
