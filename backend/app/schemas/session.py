"""
session.py — schemas for session scheduling endpoints.

SlotIn:               one proposed time slot (used inside CreateSessionRequest)
CreateSessionRequest: body for POST /groups/{group_id}/sessions
VoteRequest:          body for POST /sessions/{session_id}/vote
ConfirmSlotRequest:   body for POST /sessions/{session_id}/confirm
SessionSlotResponse:  a slot with its current vote count
SessionResponse:      full session detail including slots
"""

import uuid
from datetime import date, time, datetime
from pydantic import BaseModel, Field
from app.models.session import SessionStatus


class SlotIn(BaseModel):
    slot_date: date
    start_time: time
    duration_minutes: int = Field(..., gt=0)
    location: str | None = None


class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1)
    voting_deadline: datetime
    # Must propose between 2 and 4 time slots
    slots: list[SlotIn] = Field(..., min_length=2, max_length=4)


class VoteRequest(BaseModel):
    slot_id: uuid.UUID


class ConfirmSlotRequest(BaseModel):
    slot_id: uuid.UUID


class SessionSlotResponse(BaseModel):
    id: uuid.UUID
    slot_date: date
    start_time: time
    duration_minutes: int
    location: str | None
    # Vote counts are owner-only (per design decision). None for non-owners.
    vote_count: int | None
    # Whether the CURRENT logged-in user has voted for this slot. Unlike
    # vote_count, this is always populated (for owner and members alike),
    # since showing someone their own vote doesn't leak anyone else's, so it
    # doesn't conflict with the owner-only vote-count decision.
    voted_by_me: bool

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    name: str
    status: SessionStatus
    voting_deadline: datetime
    confirmed_slot_id: uuid.UUID | None
    created_at: datetime
    slots: list[SessionSlotResponse]

    model_config = {"from_attributes": True}


class UpcomingSessionResponse(BaseModel):
    """One row in the logged-in user's upcoming-events list (dashboard box).
    Only confirmed (status='scheduled') sessions with a future date/time,
    built from a join across sessions -> confirmed slot -> group -> course,
    scoped to groups the current user belongs to."""
    session_id: uuid.UUID
    session_name: str
    group_id: uuid.UUID
    group_name: str
    course_code: str
    slot_date: date
    start_time: time
    duration_minutes: int
    location: str | None

    model_config = {"from_attributes": True}
