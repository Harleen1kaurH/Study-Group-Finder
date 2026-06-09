import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # e.g. CS101
    name: Mapped[str] = mapped_column(String, nullable=False)               # e.g. Intro to CS

    # Relationships
    groups = relationship("Group", back_populates="course")
