import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.registration import RegistrationStatus


class RegistrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_id: uuid.UUID
    user_id: uuid.UUID
    status: RegistrationStatus
    registered_at: datetime


class ParticipantOut(BaseModel):
    """One row in an event's participant list (admin view)."""

    registration_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    email: EmailStr
    status: RegistrationStatus
    registered_at: datetime
