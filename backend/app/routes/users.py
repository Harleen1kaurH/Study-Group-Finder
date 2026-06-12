"""
users.py — user profile routes.

Allows the logged-in user to view and update their own profile.
All endpoints require authentication.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UpdateProfileRequest

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
