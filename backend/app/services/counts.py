"""Small reusable query helpers for registration counts."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Registration, RegistrationStatus


def attach_registered_counts(db: Session, events: list) -> list:
    """Set `registered_count` on each event using a single grouped query
    (avoids one query per event)."""
    if not events:
        return events
    ids = [e.id for e in events]
    rows = (
        db.query(Registration.event_id, func.count(Registration.id))
        .filter(
            Registration.event_id.in_(ids),
            Registration.status == RegistrationStatus.registered,
        )
        .group_by(Registration.event_id)
        .all()
    )
    counts = {event_id: count for event_id, count in rows}
    for event in events:
        event.registered_count = counts.get(event.id, 0)
    return events


def active_registration_count(db: Session, event_id) -> int:
    return (
        db.query(func.count(Registration.id))
        .filter(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.registered,
        )
        .scalar()
        or 0
    )
