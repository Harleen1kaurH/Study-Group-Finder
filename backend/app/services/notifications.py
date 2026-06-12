"""
notifications.py — notification service.

Provides two helper functions for creating notifications:
  - notify_user:  send a notification to one specific user
  - notify_group: send a notification to all members of a group

Both functions enforce the 20-notification cap per user by deleting
the oldest notifications when the limit is exceeded.

Notification types:
  vote_open          — a new session is open for voting
  session_confirmed  — a session slot has been confirmed
  session_cancelled  — a session was cancelled
  member_added       — user was added to a group
  member_removed     — user was removed from a group
"""

import uuid
from sqlalchemy.orm import Session

from app.models.group import GroupMember
from app.models.notification import Notification

# Maximum notifications stored per user
MAX_NOTIFICATIONS = 20


def _create_notification(
    db: Session,
    user_id: uuid.UUID,
    type: str,
    message: str,
    payload: dict | None = None,
):
    """
    Internal helper — create one notification for one user.
    Deletes the oldest notification if the user already has 20.
    """
    # Count how many notifications this user already has
    count = db.query(Notification).filter(Notification.user_id == user_id).count()

    # If at the cap, delete the oldest one to make room
    if count >= MAX_NOTIFICATIONS:
        oldest = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.asc())
            .first()
        )
        if oldest:
            db.delete(oldest)

    # Create the new notification
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        payload=payload,
    )
    db.add(notification)


def notify_user(
    db: Session,
    user_id: uuid.UUID,
    type: str,
    message: str,
    payload: dict | None = None,
):
    """Send a notification to one specific user."""
    _create_notification(db, user_id, type, message, payload)
    db.commit()


def notify_group(
    db: Session,
    group_id: uuid.UUID,
    type: str,
    message: str,
    payload: dict | None = None,
):
    """Send a notification to every member of a group."""
    # Fetch all members of the group
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

    # Create one notification per member
    for member in members:
        _create_notification(db, member.user_id, type, message, payload)

    db.commit()
