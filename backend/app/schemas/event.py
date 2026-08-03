import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    location: str = ""
    start_time: datetime
    end_time: datetime
    capacity: int = Field(default=0, ge=0)  # 0 = unlimited


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    # Every field optional: send only the ones you want to change.
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    location: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    capacity: int | None = Field(default=None, ge=0)


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    banner_url: str | None
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    registered_count: int = 0  # how many students are currently registered
