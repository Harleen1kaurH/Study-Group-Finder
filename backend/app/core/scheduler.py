"""
scheduler.py — the app's background alarm clock.

Each job is a one-off "run this exact function at this exact moment" alarm,
set at the moment the triggering event happens (proposing a session sets its
vote-summary alarm; confirming a slot sets its two reminder alarms) — not a
recurring loop that polls every session looking for something to do.

Uses SQLAlchemyJobStore (backed by the same Postgres database, in its own
"scheduled_jobs" table) instead of the default in-memory store, so alarms
survive an app restart. This matters in dev especially: `uvicorn --reload`
restarts the whole process on every file save, which would otherwise wipe
out any alarm that hadn't fired yet.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.core.config import settings

scheduler = BackgroundScheduler(
    jobstores={
        "default": SQLAlchemyJobStore(url=settings.DATABASE_URL, tablename="scheduled_jobs"),
    },
    timezone="UTC",
)
