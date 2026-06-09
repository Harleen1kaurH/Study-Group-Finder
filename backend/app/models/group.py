"""
Group model — a study group tied to one course.
Many groups can belong to the same course. The owner (creator) can edit the
group, remove members, and delete it. max_size >= 2 is enforced at the DB level.

GroupMember is the junction table between users and groups (many-to-many).
The composite PK (group_id, user_id) prevents duplicate membership at the DB
level without needing a surrogate key.
"""

import uuid
from sqlalchemy import String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMPTZ
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from app.db import Base


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = (
        CheckConstraint("max_size >= 2", name="ck_groups_max_size"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    max_size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

    # Relationships
    course = relationship("Course", back_populates="groups")
    owner = relationship("User", back_populates="owned_groups", foreign_keys=[owner_id])
    members = relationship("GroupMember", back_populates="group")
    sessions = relationship("Session", back_populates="group")


class GroupMember(Base):
    """Junction table — composite PK prevents duplicate membership."""
    __tablename__ = "group_members"

    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    joined_at = mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")
