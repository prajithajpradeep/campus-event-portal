from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A single page of results. `pages` is the total number of pages."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class DashboardStats(BaseModel):
    total_users: int
    total_events: int
    upcoming_events: int
    total_registrations: int
    active_registrations: int


class Message(BaseModel):
    detail: str
