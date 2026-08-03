"""End-to-end API tests.

These run against a lightweight throwaway SQLite database (no PostgreSQL or
Docker needed) so they're fast and easy to run:  `pytest`
They walk through the real user journeys: register, login, create an event,
register for it, view participants, cancel, and check the dashboard.
"""
import os

# Point the app at a test database BEFORE importing it.
os.environ["DATABASE_URL"] = "sqlite:///./test_campus.db"
os.environ["UPLOAD_DIR"] = "./test_uploads"
os.environ["JWT_SECRET"] = "test-secret"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402

API = settings.api_prefix


@pytest.fixture(scope="module")
def client():
    # Start fresh each run.
    if os.path.exists("./test_campus.db"):
        os.remove("./test_campus.db")
    with TestClient(app) as c:  # triggers startup: create tables + seed admin
        yield c


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get(f"{API}/health").json() == {"status": "ok"}


def test_register_and_login_student(client):
    r = client.post(
        f"{API}/auth/register",
        json={"name": "Asha", "email": "asha@campus.edu", "password": "secret123"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["role"] == "student"

    # Duplicate email is rejected.
    dup = client.post(
        f"{API}/auth/register",
        json={"name": "Asha", "email": "asha@campus.edu", "password": "secret123"},
    )
    assert dup.status_code == 409

    login = client.post(
        f"{API}/auth/login",
        json={"email": "asha@campus.edu", "password": "secret123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def admin_token(client) -> str:
    r = client.post(
        f"{API}/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def student_token(client) -> str:
    r = client.post(
        f"{API}/auth/login",
        json={"email": "asha@campus.edu", "password": "secret123"},
    )
    return r.json()["access_token"]


def test_requires_auth(client):
    # No token -> 401/403 (not allowed to browse without logging in).
    assert client.get(f"{API}/events").status_code in (401, 403)


def test_only_admin_creates_events(client):
    body = {
        "title": "Robotics Workshop",
        "description": "Hands-on robotics",
        "location": "Lab 2",
        "start_time": "2030-01-01T10:00:00Z",
        "end_time": "2030-01-01T12:00:00Z",
        "capacity": 2,
    }
    # Student is forbidden.
    forbidden = client.post(
        f"{API}/events", json=body, headers=auth_header(student_token(client))
    )
    assert forbidden.status_code == 403

    # Admin succeeds.
    created = client.post(
        f"{API}/events", json=body, headers=auth_header(admin_token(client))
    )
    assert created.status_code == 201, created.text
    assert created.json()["registered_count"] == 0


def test_full_registration_flow(client):
    admin = admin_token(client)
    student = student_token(client)

    # Find the event we created.
    events = client.get(f"{API}/events", headers=auth_header(student)).json()
    assert events["total"] >= 1
    event_id = events["items"][0]["id"]

    # Search works.
    found = client.get(f"{API}/events?q=Robotics", headers=auth_header(student)).json()
    assert found["total"] >= 1

    # Register, then a second attempt is a conflict.
    reg = client.post(
        f"{API}/events/{event_id}/registrations", headers=auth_header(student)
    )
    assert reg.status_code == 201, reg.text
    again = client.post(
        f"{API}/events/{event_id}/registrations", headers=auth_header(student)
    )
    assert again.status_code == 409

    # Appears in "my registrations".
    mine = client.get(f"{API}/me/registrations", headers=auth_header(student)).json()
    assert any(e["id"] == event_id for e in mine)

    # Admin sees the participant.
    participants = client.get(
        f"{API}/events/{event_id}/registrations", headers=auth_header(admin)
    ).json()
    assert len(participants) == 1
    assert participants[0]["email"] == "asha@campus.edu"

    # Dashboard reflects one active registration.
    stats = client.get(f"{API}/admin/stats", headers=auth_header(admin)).json()
    assert stats["active_registrations"] >= 1

    # Cancel, and it drops out of active counts.
    cancel = client.delete(
        f"{API}/events/{event_id}/registrations", headers=auth_header(student)
    )
    assert cancel.status_code == 200
    stats_after = client.get(f"{API}/admin/stats", headers=auth_header(admin)).json()
    assert stats_after["active_registrations"] == stats["active_registrations"] - 1


def test_announcements(client):
    admin = admin_token(client)
    student = student_token(client)
    created = client.post(
        f"{API}/announcements",
        json={"title": "Welcome", "body": "Semester starts Monday"},
        headers=auth_header(admin),
    )
    assert created.status_code == 201
    listed = client.get(f"{API}/announcements", headers=auth_header(student)).json()
    assert any(a["title"] == "Welcome" for a in listed)
