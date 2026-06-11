"""
group.py — schemas for study group endpoints.

CreateGroupRequest: body for POST /groups
UpdateGroupRequest: body for PUT /groups/{group_id} (all fields optional)
GroupResponse:      returned when reading a group
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str
    course_id: uuid.UUID
    # max_size must be at least 2 (enforced in DB too, but validated here first)
    max_size: int = Field(..., ge=2)


class UpdateGroupRequest(BaseModel):
    # All fields optional — only provided fields will be updated
    name: str | None = None
    max_size: int | None = Field(default=None, ge=2)


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    course_id: uuid.UUID
    owner_id: uuid.UUID
    max_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
