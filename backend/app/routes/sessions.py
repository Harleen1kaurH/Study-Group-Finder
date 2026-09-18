"""
sessions.py — study session routes.

Sessions belong to a group and follow a state machine:
  voting → scheduled → completed (or cancelled at any point).
The owner proposes time slots; members vote; the owner confirms one slot.
"""

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from apscheduler.jobstores.base import JobLookupError

from app.db import get_db
from app.dependencies import get_current_user
from app.models.group import Group, GroupMember
from app.models.session import Session as StudySession, SessionSlot, SlotVote, SessionStatus
from app.models.user import User
from app.services.notifications import notify_group
from app.core.scheduler import scheduler
from app.services.scheduled_notifications import send_vote_summary, send_session_reminder


def _reminder_job_ids(session_id: uuid.UUID) -> list[str]:
    # Deterministic job IDs for a session's alarms, used for replace_existing
    # and for cleanup on cancel.
    return [f"vote_summary_{session_id}", f"reminder_24h_{session_id}", f"reminder_1h_{session_id}"]
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


def build_session_response(session: StudySession, db: Session, is_owner: bool, current_user_id: uuid.UUID) -> SessionResponse:
    """Helper — build SessionResponse. Vote counts are owner-only (per design
    decision): non-owners get vote_count=None for every slot instead of the
    real number. voted_by_me is different, since it's always populated for
    whoever is asking, as it only reveals the asker's own vote."""
    slots = []
    for slot in session.slots:
        vote_count = db.query(SlotVote).filter(SlotVote.slot_id == slot.id).count() if is_owner else None
        voted_by_me = db.query(SlotVote).filter(
            SlotVote.slot_id == slot.id,
            SlotVote.user_id == current_user_id,
        ).first() is not None
        slots.append(SessionSlotResponse(
            id=slot.id,
            slot_date=slot.slot_date,
            start_time=slot.start_time,
            duration_minutes=slot.duration_minutes,
            location=slot.location,
            vote_count=vote_count,
            voted_by_me=voted_by_me,
        ))
    return SessionResponse(
        id=session.id,
        group_id=session.group_id,
        name=session.name,
        status=session.status,
        voting_deadline=session.voting_deadline,
        confirmed_slot_id=session.confirmed_slot_id,
        created_at=session.created_at,
        slots=slots,
    )


# Return all sessions for a group
@router.get("", response_model=list[SessionResponse])
def list_sessions(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify the group exists
    group = get_group_or_404(group_id, db)
    is_owner = group.owner_id == current_user.id

    sessions = db.query(StudySession).filter(StudySession.group_id == group_id).all()
    return [build_session_response(s, db, is_owner, current_user.id) for s in sessions]


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
        name=body.name,
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

    # Notify all group members that voting is open — name the group and
    # course so the notification is meaningful on its own, without the
    # member having to click through to figure out which session this is.
    notify_group(
        db,
        group_id=group_id,
        type="vote_open",
        message=f"Voting is open for '{session.name}' in {group.name} ({group.course.code})",
        payload={"group_id": str(group_id), "session_id": str(session.id)},
    )

    # Set the vote-summary alarm for exactly the voting deadline (spec Step 4).
    # This fires regardless of whether the owner confirms early; cancel_session
    # is what removes it, not an early confirm.
    scheduler.add_job(
        send_vote_summary,
        trigger="date",
        run_date=body.voting_deadline,
        args=[str(session.id)],
        id=f"vote_summary_{session.id}",
        replace_existing=True,
        misfire_grace_time=None,  # run it even if the server was down when this was due
    )

    return build_session_response(session, db, is_owner=True, current_user_id=current_user.id)


# Return details of a single session including its slots and vote counts
@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    group_id: uuid.UUID,
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = get_group_or_404(group_id, db)
    session = get_session_or_404(session_id, group_id, db)
    is_owner = group.owner_id == current_user.id
    return build_session_response(session, db, is_owner, current_user.id)


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

    # Voting window is exactly 24h from proposal time. Status stays "voting"
    # until the owner confirms or cancels (per spec), but no NEW votes are
    # accepted once the deadline has passed — checked live on every vote
    # attempt rather than via any background job.
    if datetime.now(timezone.utc) >= session.voting_deadline:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The voting deadline has passed")

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
        message=f"'{session.name}' has been confirmed in {group.name} ({group.course.code})",
        payload={"group_id": str(group_id), "session_id": str(session_id)},
    )

    # Set the T-24h and T-1h reminder alarms (spec Step 6), relative to the
    # confirmed slot's actual date/time, not the voting deadline. Skip any
    # that would fire in the past (e.g. confirming a slot less than 24h away).
    start_dt = datetime.combine(slot.slot_date, slot.start_time, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    for hours_before in (24, 1):
        run_date = start_dt - timedelta(hours=hours_before)
        if run_date > now:
            scheduler.add_job(
                send_session_reminder,
                trigger="date",
                run_date=run_date,
                args=[str(session.id), hours_before],
                id=f"reminder_{hours_before}h_{session.id}",
                replace_existing=True,
                misfire_grace_time=None,
            )

    return build_session_response(session, db, is_owner=True, current_user_id=current_user.id)


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
        message=f"'{session.name}' has been cancelled in {group.name} ({group.course.code})",
        payload={"group_id": str(group_id), "session_id": str(session_id)},
    )

    # Cancel any alarms still pending for this session, since a vote summary
    # or a reminder for a session that's been called off isn't useful.
    for job_id in _reminder_job_ids(session.id):
        try:
            scheduler.remove_job(job_id)
        except JobLookupError:
            pass  # already fired, or never got scheduled, so nothing to remove

    return build_session_response(session, db, is_owner=True, current_user_id=current_user.id)
