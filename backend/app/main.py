"""
main.py — application entry point.

Creates the FastAPI app and registers all route modules.
Each router handles one resource (auth, users, courses, groups, sessions, notifications).
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, courses, groups, sessions, notifications
from app.core.scheduler import scheduler

# Set up logging so unexpected errors are printed to the terminal
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background alarm clock when the app boots, stop it on shutdown.
    # Jobs scheduled before a restart are persisted in Postgres (see
    # core/scheduler.py) and picked back up here.
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Study Group Finder", lifespan=lifespan)

# Allow the frontend dev server to call this API
# add your production URL here later when you deploy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_credentials=True,                   # allow cookies / auth headers
    allow_methods=["*"],                      # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                      # allow Authorization and other headers
)


# Global exception handler — catches any unexpected error and returns clean JSON
# HTTPExceptions (404, 403, etc.) are NOT caught here — FastAPI handles those normally
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the full traceback to the terminal for debugging
    logger.exception("Unhandled error: %s", exc)
    # Return a clean JSON response to the client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Authentication — register, login, logout
app.include_router(auth.router)

# User profile — view and update the logged-in user's profile
app.include_router(users.router)

# Course catalogue — browse available courses
app.include_router(courses.router)

# Study groups — create, browse, join, leave, and manage groups
app.include_router(groups.router)

# Sessions — schedule voting and confirmed study sessions within a group
app.include_router(sessions.router)

# Notifications — in-app notification feed for the logged-in user
app.include_router(notifications.router)


@app.get("/health")
def health():
    return {"status": "ok"}
