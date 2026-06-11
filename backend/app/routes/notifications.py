"""
notifications.py — notification routes.

Returns the logged-in user's in-app notification feed.
Capped at 20 entries per user; newest first.
"""

from fastapi import APIRouter
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Return the logged-in user's notifications (newest first, max 20)
@router.get("", response_model=list[NotificationResponse])
def list_notifications():
    return {"message": "not implemented yet"}
