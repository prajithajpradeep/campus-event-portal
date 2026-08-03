import logging
import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.models import Event, User
from app.schemas.common import Page
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services.counts import attach_registered_counts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["events"])

# Only real image types are accepted for banners.
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


@router.get("", response_model=Page[EventOut])
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: str | None = Query(None, description="Search text in title/description"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    """Browse events. Supports a search term `q` and page/size pagination."""
    query = db.query(Event)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Event.title.ilike(like), Event.description.ilike(like))
        )
    total = query.count()
    events = (
        query.order_by(Event.start_time)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    attach_registered_counts(db, events)
    pages = (total + size - 1) // size if total else 0
    return Page(items=events, total=total, page=page, size=size, pages=pages)


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    attach_registered_counts(db, [event])
    return event


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    event = Event(**payload.model_dump(), created_by=admin.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    event.registered_count = 0
    logger.info("Event created: %s by %s", event.title, admin.email)
    return event


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: uuid.UUID,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    data = payload.model_dump(exclude_unset=True)  # only provided fields
    for field, value in data.items():
        setattr(event, field, value)
    if event.end_time <= event.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    db.commit()
    db.refresh(event)
    attach_registered_counts(db, [event])
    logger.info("Event updated: %s", event.id)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    logger.info("Event deleted: %s", event_id)
    return None


@router.post("/{event_id}/banner", response_model=EventOut)
def upload_banner(
    event_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Upload/replace an event's banner image. Saves the file and stores its URL."""
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    contents = file.file.read()
    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower() or ".png"
    filename = f"{event_id}{ext}"
    with open(os.path.join(settings.upload_dir, filename), "wb") as f:
        f.write(contents)

    event.banner_url = f"/uploads/{filename}"
    db.commit()
    db.refresh(event)
    attach_registered_counts(db, [event])
    logger.info("Banner uploaded for event %s", event_id)
    return event
