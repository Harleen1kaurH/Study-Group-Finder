"""
Session, SessionSlot, and SlotVote models — the voting and scheduling core.

Session: one voting/scheduling event within a group. Status follows a strict
state machine (voting → scheduled → completed, or either → cancelled). All
status writes go through SessionService.update_status(), never directly.

SessionSlot: the 2–4 time options proposed by the group owner for a session.
Each slot has a date, start time, duration, and optional location.

SlotVote: junction table between users and session_slots (many-to-many).
Composite PK (slot_id, user_id) prevents double votes at the DB level.
Changing a vote = delete existing votes for that session, insert new ones.

Circular FK note: sessions.confirmed_slot_id → session_slots.id, while
session_slots.session_id → sessions.id. Resolved with use_alter=True so
Alembic can generate the migration without a dependency error.
"""

import uuid
import enum
from sqlalchemy import String, Integer, Date, Time, ForeignKey, CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.db import Base


class SessionStatus(str, enum.Enum):
    voting = "voting"
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(SAEnum(SessionStatus, name="session_status"), nullable=False, default=SessionStatus.voting)

    # Circular FK: sessions.confirmed_slot_id -> session_slots.id
    # use_alter=True tells SQLAlchemy to add this FK after both tables are created
    confirmed_slot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("session_slots.id", use_alter=True, name="fk_sessions_confirmed_slot"),
        nullable=True
    )
    voting_deadline = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    group = relationship("Group", back_populates="sessions")
    slots = relationship("SessionSlot", back_populates="session", foreign_keys="SessionSlot.session_id")
    confirmed_slot = relationship("SessionSlot", foreign_keys=[confirmed_slot_id])


class SessionSlot(Base):
    __tablename__ = "session_slots"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_slots_duration"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    slot_date: Mapped[Date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    session = relationship("Session", back_populates="slots", foreign_keys=[session_id])
    votes = relationship("SlotVote", back_populates="slot")


class SlotVote(Base):
    """Junction table — composite PK (slot_id, user_id) prevents double votes."""
    __tablename__ = "slot_votes"

    slot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("session_slots.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    voted_at = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    slot = relationship("SessionSlot", back_populates="votes")
    user = relationship("User", back_populates="slot_votes")
