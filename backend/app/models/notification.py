"""
Notification model — in-app notification stack per user.
Capped at 20 entries per user; on every insert the service deletes the oldest
rows beyond 20 (no DB trigger needed). The frontend fetches the full stack on
page load — no read/unread tracking, no filtering.

type values: vote_open, session_confirmed, session_cancelled,
             member_removed, voting_summary, session_reminder
payload (JSONB): optional deep-link data, e.g. { group_id, session_id }
"""

import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # vote_open, session_confirmed, etc.
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload = mapped_column(JSONB, nullable=True)              # e.g. { group_id, session_id }
    created_at = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
