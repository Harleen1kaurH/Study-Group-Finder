import uuid
from sqlalchemy import String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

    # Relationships
    owned_groups = relationship("Group", back_populates="owner", foreign_keys="Group.owner_id")
    group_memberships = relationship("GroupMember", back_populates="user")
    slot_votes = relationship("SlotVote", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
