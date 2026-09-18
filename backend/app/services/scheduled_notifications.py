"""
scheduled_notifications.py — functions APScheduler calls when an alarm fires.

These run outside any HTTP request (no request-scoped `db` session exists),
so each one opens and closes its own short-lived DB session.

All of these produce IN-APP notifications only (no email) — there is no
SendGrid integration in this project by design.
"""

import uuid
from app.db import SessionLocal
from app.models.session import Session as StudySession, SessionSlot, SlotVote, SessionStatus
from app.models.group import Group
from app.services.notifications import notify_user


def send_vote_summary(session_id: str):
    """Fires once, exactly at a session's voting_deadline (spec Step 4).
    Notifies the group owner with vote counts per slot and who voted for
    what. If the session was cancelled before this fired, the job is removed
    at cancel time (see routes/sessions.py) — a summary of a moot vote isn't
    useful, so this simply won't run for a cancelled session."""
    db = SessionLocal()
    try:
        session = db.get(StudySession, uuid.UUID(session_id))
        if session is None:
            return  # session (or its group) no longer exists

        group = db.get(Group, session.group_id)
        if group is None:
            return

        lines = []
        for slot in session.slots:
            votes = db.query(SlotVote).filter(SlotVote.slot_id == slot.id).all()
            voter_names = [v.user.name for v in votes]
            names_str = ", ".join(voter_names) if voter_names else "no one"
            lines.append(f"{slot.slot_date} {slot.start_time} — {len(votes)} vote(s): {names_str}")

        summary = "Voting closed for your session. " + " | ".join(lines)

        notify_user(
            db,
            user_id=group.owner_id,
            type="voting_summary",
            message=summary,
            payload={"group_id": str(group.id), "session_id": str(session.id)},
        )
    finally:
        db.close()


def send_session_reminder(session_id: str, hours_before: int):
    """Fires at T-24h or T-1h before a confirmed session's actual start time
    (spec Step 6). Only notifies members who voted for the confirmed slot.
    No-ops if the session was cancelled, or is no longer confirmed, by the
    time this fires."""
    db = SessionLocal()
    try:
        session = db.get(StudySession, uuid.UUID(session_id))
        if session is None or session.status != SessionStatus.scheduled or session.confirmed_slot_id is None:
            return

        slot = db.get(SessionSlot, session.confirmed_slot_id)
        if slot is None:
            return

        votes = db.query(SlotVote).filter(SlotVote.slot_id == slot.id).all()
        when = "1 hour" if hours_before == 1 else f"{hours_before} hours"
        location_note = f" at {slot.location}" if slot.location else ""
        message = f"Reminder: your study session starts in {when}{location_note}."

        for vote in votes:
            notify_user(
                db,
                user_id=vote.user_id,
                type="session_reminder",
                message=message,
                payload={"group_id": str(session.group_id), "session_id": str(session.id)},
            )
    finally:
        db.close()
