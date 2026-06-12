"""
main.py — application entry point.

Creates the FastAPI app and registers all route modules.
Each router handles one resource (auth, users, courses, groups, sessions, notifications).
"""

from fastapi import FastAPI
from app.routes import auth, users, courses, groups, sessions, notifications

app = FastAPI(title="Study Group Finder")

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
