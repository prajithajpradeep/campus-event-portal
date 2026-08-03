"""Database engine and session management.

`get_db` is a FastAPI dependency: it opens a session per request and always
closes it, even if the handler raises. This is the standard unit-of-work
pattern and keeps connection handling out of the route code.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings

# pool_pre_ping avoids "server closed the connection" errors after the DB
# container restarts by validating a connection before it is used.
# SQLite (used only in tests) needs check_same_thread disabled for the test client.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)
engine = create_engine(
    settings.database_url, pool_pre_ping=True, connect_args=_connect_args
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
