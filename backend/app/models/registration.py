import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.types import GUID


class RegistrationStatus(str, enum.Enum):
    registered = "registered"
    cancelled = "cancelled"


class Registration(Base):
    __tablename__ = "registrations"
    # A user can hold at most one registration row per event. Cancelling flips
    # `status` rather than deleting, so history/analytics stay intact while this
    # constraint still blocks duplicate active sign-ups.
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("events.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(RegistrationStatus, name="registration_status"),
        default=RegistrationStatus.registered,
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
