"""Application entrypoint: builds the FastAPI app and wires everything together."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.logging_config import configure_logging
from app.routers import (
    announcements,
    auth,
    dashboard,
    events,
    registrations,
    users,
)
from app.seed import seed_admin

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: make sure the uploads folder exists, create tables (dev 
    convenience — Alembic migrations are the production path), seed admin."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    seed_admin()
    logger.info("%s started in %s mode", settings.app_name, settings.environment)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Campus Event Management Portal API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""Serve uploaded banner images. check_dir=False so import doesn't fail if the
   folder isn't created yet (it's created on startup)."""
app.mount(
    "/uploads",
    StaticFiles(directory=settings.upload_dir, check_dir=False),
    name="uploads",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Last-resort handler: log the stack trace, return a generic 500 so we
    never leak internals to the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}


"""Wire up every feature. Each router already declares its own path prefix
  (e.g. /events), and here we add the shared /api prefix in front."""
for module in (auth, events, registrations, users, announcements, dashboard):
    app.include_router(module.router, prefix=settings.api_prefix)
