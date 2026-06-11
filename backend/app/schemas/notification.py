"""
notification.py — schemas for notification endpoints.

NotificationResponse: returned when listing a user's notifications
"""

import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str        # e.g. vote_open, session_confirmed, session_cancelled
    message: str
    payload: dict | None  # optional deep-link data e.g. { group_id, session_id }
    created_at: datetime

    model_config = {"from_attributes": True}
