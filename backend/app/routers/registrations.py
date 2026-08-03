import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.models import Event, Registration, RegistrationStatus, User
from app.schemas.common import Message
from app.schemas.event import EventOut
from app.schemas.registration import ParticipantOut, RegistrationOut
from app.services.counts import active_registration_count, attach_registered_counts

logger = logging.getLogger(__name__)
router = APIRouter(tags=["registrations"])


@router.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationOut,
    status_code=status.HTTP_201_CREATED,
)
def register_for_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register the current student for an event."""
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    existing = (
        db.query(Registration)
        .filter_by(user_id=current_user.id, event_id=event_id)
        .first()
    )
    if existing and existing.status == RegistrationStatus.registered:
        raise HTTPException(status_code=409, detail="Already registered")

    # Enforce capacity (0 means unlimited).
    if event.capacity and active_registration_count(db, event_id) >= event.capacity:
        raise HTTPException(status_code=400, detail="Event is full")

    if existing:
        existing.status = RegistrationStatus.registered  # re-activate a cancelled one
        registration = existing
    else:
        registration = Registration(user_id=current_user.id, event_id=event_id)
        db.add(registration)
    db.commit()
    db.refresh(registration)
    logger.info("User %s registered for event %s", current_user.email, event_id)
    return registration


@router.delete("/events/{event_id}/registrations", response_model=Message)
def cancel_registration(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel the current student's registration for an event."""
    registration = (
        db.query(Registration)
        .filter_by(user_id=current_user.id, event_id=event_id)
        .first()
    )
    if not registration or registration.status == RegistrationStatus.cancelled:
        raise HTTPException(status_code=404, detail="You are not registered")
    registration.status = RegistrationStatus.cancelled
    db.commit()
    logger.info("User %s cancelled registration for event %s", current_user.email, event_id)
    return Message(detail="Registration cancelled")


@router.get(
    "/events/{event_id}/registrations",
    response_model=list[ParticipantOut],
)
def list_participants(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Admin: list the students registered for an event."""
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    rows = (
        db.query(Registration, User)
        .join(User, Registration.user_id == User.id)
        .filter(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.registered,
        )
        .all()
    )
    return [
        ParticipantOut(
            registration_id=reg.id,
            user_id=user.id,
            name=user.name,
            email=user.email,
            status=reg.status,
            registered_at=reg.registered_at,
        )
        for reg, user in rows
    ]


@router.get("/me/registrations", response_model=list[EventOut])
def my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The events the current student is registered for."""
    regs = (
        db.query(Registration)
        .filter_by(user_id=current_user.id, status=RegistrationStatus.registered)
        .all()
    )
    event_ids = [r.event_id for r in regs]
    events = (
        db.query(Event).filter(Event.id.in_(event_ids)).all() if event_ids else []
    )
    attach_registered_counts(db, events)
    return events
