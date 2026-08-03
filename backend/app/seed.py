"""Idempotent seeding of the initial admin account.

Runs on startup. Because admins aren't creatable through the public
`/auth/register` endpoint (that only makes students), this bootstraps the
first privileged user from environment config.
"""
import logging

from app.config import settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def seed_admin() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == settings.admin_email).first():
            return  # already seeded
        admin = User(
            name=settings.admin_name,
            email=settings.admin_email,
            hashed_password=hash_password(settings.admin_password),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        logger.info("Seeded admin account: %s", settings.admin_email)
    finally:
        db.close()
