import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ, JSONB
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
    created_at = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
