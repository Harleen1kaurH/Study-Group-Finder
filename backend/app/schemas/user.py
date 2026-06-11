"""
user.py — schemas for user profile endpoints.

UserResponse:         returned when reading a user's profile
UpdateProfileRequest: body for PUT /users/me (all fields optional)
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    bio: str | None
    availability: str | None
    email_notifications: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    # All fields are optional — only provided fields will be updated
    name: str | None = None
    bio: str | None = None
    availability: str | None = None
    email_notifications: bool | None = None
