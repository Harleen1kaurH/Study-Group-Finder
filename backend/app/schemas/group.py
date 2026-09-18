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
    course_code: str  # e.g. CS101 — backend will look up the course by code
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
    # Only populated by the list endpoint (whether the CURRENT user is a
    # member of this group) — defaults False elsewhere since it's unused there.
    is_member: bool = False

    model_config = {"from_attributes": True}


class GroupMemberResponse(BaseModel):
    user_id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class GroupDetailResponse(GroupResponse):
    """Used only by GET /groups/{id} — bundles the member list into the
    response so the frontend doesn't need a second request (per the
    locked-in decision that group details return all nested data at once)."""
    members: list[GroupMemberResponse]
