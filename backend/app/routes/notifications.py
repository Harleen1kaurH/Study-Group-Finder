"""
notifications.py — notification routes.

Returns the logged-in user's in-app notification feed.
Capped at 20 entries per user; newest first.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Return the logged-in user's notifications (newest first, max 20)
@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)  # only this user's notifications
        .order_by(Notification.created_at.desc())         # newest first
        .limit(20)                                         # cap at 20
        .all()
    )
    return notifications
