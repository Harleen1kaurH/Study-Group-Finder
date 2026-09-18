"""
users.py — user profile routes.

Allows the logged-in user to view and update their own profile, and to list
their own upcoming (confirmed) study sessions across every group they belong
to, for the dashboard's "Upcoming Sessions" box.
All endpoints require authentication.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.course import Course
from app.models.session import Session as StudySession, SessionSlot, SessionStatus
from app.schemas.user import UserResponse, UpdateProfileRequest
from app.schemas.session import UpcomingSessionResponse

router = APIRouter(prefix="/users", tags=["users"])


# Return the logged-in user's profile (name, bio, availability, etc.)
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    # get_current_user already fetched the user from the DB, just return it
    return current_user


# Update the logged-in user's profile fields
@router.put("/me", response_model=UserResponse)
def update_my_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only update fields that were actually provided (not None)
    if body.name is not None:
        current_user.name = body.name

    if body.bio is not None:
        current_user.bio = body.bio

    if body.availability is not None:
        current_user.availability = body.availability

    if body.email_notifications is not None:
        current_user.email_notifications = body.email_notifications

    # Save changes to the DB
    db.commit()

    # Refresh so the returned object reflects what's now in the DB
    db.refresh(current_user)

    return current_user



# Return the logged-in user's upcoming CONFIRMED sessions (status='scheduled')
# across every group they belong to (owner or member: owners are always
# auto-added as members, so one membership join covers both), soonest first.
# Sessions still in voting, or with no confirmed slot yet, are not "events"
# and are left out, matching how the rest of the app treats "scheduled" as
# the only status with a real, confirmed date/time.
@router.get("/me/upcoming-sessions", response_model=list[UpcomingSessionResponse])
def get_my_upcoming_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)

    rows = (
        db.query(StudySession, SessionSlot, Group, Course)
        .join(GroupMember, GroupMember.group_id == StudySession.group_id)
        .join(SessionSlot, SessionSlot.id == StudySession.confirmed_slot_id)
        .join(Group, Group.id == StudySession.group_id)
        .join(Course, Course.id == Group.course_id)
        .filter(
            GroupMember.user_id == current_user.id,
            StudySession.status == SessionStatus.scheduled,
        )
        .all()
    )

    upcoming = []
    for session, slot, group, course in rows:
        start_dt = datetime.combine(slot.slot_date, slot.start_time, tzinfo=timezone.utc)
        if start_dt <= now:
            continue  # already happened, so not "upcoming"
        upcoming.append(UpcomingSessionResponse(
            session_id=session.id,
            session_name=session.name,
            group_id=group.id,
            group_name=group.name,
            course_code=course.code,
            slot_date=slot.slot_date,
            start_time=slot.start_time,
            duration_minutes=slot.duration_minutes,
            location=slot.location,
        ))

    upcoming.sort(key=lambda u: (u.slot_date, u.start_time))
    return upcoming
