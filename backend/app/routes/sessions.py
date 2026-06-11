"""
sessions.py — study session routes.

Sessions belong to a group and follow a state machine:
  voting → scheduled → completed (or cancelled at any point).
The owner proposes time slots; members vote; the owner confirms one slot.
"""

from fastapi import APIRouter
from app.schemas.session import (
    CreateSessionRequest,
    VoteRequest,
    ConfirmSlotRequest,
    SessionResponse,
)

router = APIRouter(prefix="/groups/{group_id}/sessions", tags=["sessions"])


# Return all sessions for a group
@router.get("", response_model=list[SessionResponse])
def list_sessions(group_id: str):
    return {"message": "not implemented yet"}


# Create a new session with proposed time slots — owner only
@router.post("", response_model=SessionResponse)
def create_session(group_id: str, body: CreateSessionRequest):
    return {"message": "not implemented yet"}


# Return details of a single session including its slots and votes
@router.get("/{session_id}", response_model=SessionResponse)
def get_session(group_id: str, session_id: str):
    return {"message": "not implemented yet"}


# Cast or change the logged-in user's vote for a time slot
@router.post("/{session_id}/vote")
def vote_on_slot(group_id: str, session_id: str, body: VoteRequest):
    return {"message": "not implemented yet"}


# Confirm a slot and move session status to scheduled — owner only
@router.post("/{session_id}/confirm", response_model=SessionResponse)
def confirm_slot(group_id: str, session_id: str, body: ConfirmSlotRequest):
    return {"message": "not implemented yet"}


# Cancel a session — owner only
@router.post("/{session_id}/cancel", response_model=SessionResponse)
def cancel_session(group_id: str, session_id: str):
    return {"message": "not implemented yet"}
