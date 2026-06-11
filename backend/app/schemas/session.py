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
    vote_count: int  # computed field — number of votes this slot has received

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    id: uuid.UUID
    group_id: uuid.UUID
    status: SessionStatus
    voting_deadline: datetime
    confirmed_slot_id: uuid.UUID | None
    created_at: datetime
    slots: list[SessionSlotResponse]

    model_config = {"from_attributes": True}
