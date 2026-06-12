"""
sessions.py — study session routes.

Sessions belong to a group and follow a state machine:
  voting → scheduled → completed (or cancelled at any point).
The owner proposes time slots; members vote; the owner confirms one slot.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.group import Group, GroupMember
from app.models.session import Session as StudySession, SessionSlot, SlotVote, SessionStatus
from app.models.user import User
from app.services.notifications import notify_group
from app.schemas.session import (
    CreateSessionRequest,
    VoteRequest,
    ConfirmSlotRequest,
    SessionResponse,
    SessionSlotResponse,
)

router = APIRouter(prefix="/groups/{group_id}/sessions", tags=["sessions"])


def get_group_or_404(group_id: uuid.UUID, db: Session):
    """Helper — fetch group or raise 404."""
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


def get_session_or_404(session_id: uuid.UUID, group_id: uuid.UUID, db: Session):
    """Helper — fetch session, verify it belongs to this group, or raise 404."""
    session = db.get(StudySession, session_id)
    if session is None or session.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


def is_member(group_id: uuid.UUID, user_id: uuid.UUID, db: Session) -> bool:
    """Helper — check if a user is a member of a group."""
    return db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
    ).first() is not None


def build_session_response(session: StudySession, db: Session) -> SessionResponse:
    """Helper — build SessionResponse with vote counts for each slot."""
    slots = []
    for slot in session.slots:
        vote_count = db.query(SlotVote).filter(SlotVote.slot_id == slot.id).count()
        slots.append(SessionSlotResponse(
            id=slot.id,
            slot_date=slot.slot_date,
            start_time=slot.start_time,
            duration_minutes=slot.duration_minutes,
            location=slot.location,
            vote_count=vote_count,
        ))
    return SessionResponse(
        id=session.id,
        group_id=session.group_id,
        status=session.status,
        voting_deadline=session.voting_deadline,
        confirmed_slot_id=session.confirmed_slot_id,
        created_at=session.created_at,
        slots=slots,
    )


# Return all sessions for a group
@router.get("", response_model=list[SessionResponse])
def list_sessions(group_id: uuid.UUID, db: Session = Depends(get_db)):
    # Verify the group exists
    get_group_or_404(group_id, db)

    sessions = db.query(StudySession).filter(StudySession.group_id == group_id).all()
    return [build_session_response(s, db) for s in sessions]


# Create a new session with proposed time slots — owner only
@router.post("", response_model=SessionResponse)
def create_session(
    group_id: uuid.UUID,
    body: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = get_group_or_404(group_id, db)

    # Only the group owner can create sessions
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can create sessions")

    # Create the session with status=voting
    session = StudySession(
        group_id=group_id,
        voting_deadline=body.voting_deadline,
        status=SessionStatus.voting,
    )
    db.add(session)
    db.flush()  # get session.id before creating slots

    # Create each proposed time slot
    for slot_in in body.slots:
        slot = SessionSlot(
            session_id=session.id,
            slot_date=slot_in.slot_date,
            start_time=slot_in.start_time,
            duration_minutes=slot_in.duration_minutes,
            location=slot_in.location,
        )
        db.add(slot)

    db.commit()
    db.refresh(session)

    # Notify all group members that voting is open
    notify_group(
        db,
        group_id=group_id,
        type="vote_open",
        message="Voting is open for a new study session",
        payload={"group_id": str(group_id), "session_id": str(session.id)},
    )
    return build_session_response(session, db)


# Return details of a single session including its slots and vote counts
@router.get("/{session_id}", response_model=SessionResponse)
def get_session(group_id: uuid.UUID, session_id: uuid.UUID, db: Session = Depends(get_db)):
    get_group_or_404(group_id, db)
    session = get_session_or_404(session_id, group_id, db)
    return build_session_response(session, db)


# Cast or change the logged-in user's vote for a time slot
@router.post("/{session_id}/vote")
def vote_on_slot(
    group_id: uuid.UUID,
    session_id: uuid.UUID,
    body: VoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_group_or_404(group_id, db)
    session = get_session_or_404(session_id, group_id, db)

    # Only group members can vote
    if not is_member(group_id, current_user.id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only group members can vote")

    # Session must be in voting status
    if session.status != SessionStatus.voting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voting is closed for this session")

    # The slot must belong to this session
    slot = db.get(SessionSlot, body.slot_id)
    if slot is None or slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to this session")

    # Delete any existing votes by this user for this session (allows changing vote)
    existing_votes = (
        db.query(SlotVote)
        .join(SessionSlot)
        .filter(SessionSlot.session_id == session_id, SlotVote.user_id == current_user.id)
        .all()
    )
    for v in existing_votes:
        db.delete(v)

    # Cast the new vote
    vote = SlotVote(slot_id=body.slot_id, user_id=current_user.id)
    db.add(vote)
    db.commit()
    return {"message": "Vote recorded"}


# Confirm a slot and move session to scheduled — owner only
@router.post("/{session_id}/confirm", response_model=SessionResponse)
def confirm_slot(
    group_id: uuid.UUID,
    session_id: uuid.UUID,
    body: ConfirmSlotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = get_group_or_404(group_id, db)
    session = get_session_or_404(session_id, group_id, db)

    # Only the owner can confirm a slot
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can confirm a slot")

    # Session must be in voting status to confirm
    if session.status != SessionStatus.voting:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is not in voting status")

    # The slot must belong to this session
    slot = db.get(SessionSlot, body.slot_id)
    if slot is None or slot.session_id != session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot does not belong to this session")

    # Confirm the slot and move to scheduled
    session.confirmed_slot_id = body.slot_id
    session.status = SessionStatus.scheduled
    db.commit()
    db.refresh(session)

    # Notify all group members that the session has been scheduled
    notify_group(
        db,
        group_id=group_id,
        type="session_confirmed",
        message="A study session has been confirmed",
        payload={"group_id": str(group_id), "session_id": str(session_id)},
    )
    return build_session_response(session, db)


# Cancel a session — owner only
@router.post("/{session_id}/cancel", response_model=SessionResponse)
def cancel_session(
    group_id: uuid.UUID,
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = get_group_or_404(group_id, db)
    session = get_session_or_404(session_id, group_id, db)

    # Only the owner can cancel a session
    if group.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can cancel a session")

    # Cannot cancel a session that is already completed or cancelled
    if session.status in (SessionStatus.completed, SessionStatus.cancelled):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a session with status '{session.status}'",
        )

    session.status = SessionStatus.cancelled
    db.commit()
    db.refresh(session)

    # Notify all group members that the session was cancelled
    notify_group(
        db,
        group_id=group_id,
        type="session_cancelled",
        message="A study session has been cancelled",
        payload={"group_id": str(group_id), "session_id": str(session_id)},
    )
    return build_session_response(session, db)
