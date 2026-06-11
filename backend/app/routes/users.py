"""
users.py — user profile routes.

Allows the logged-in user to view and update their own profile.
All endpoints require authentication.
"""

from fastapi import APIRouter
from app.schemas.user import UserResponse, UpdateProfileRequest

router = APIRouter(prefix="/users", tags=["users"])


# Return the logged-in user's profile (name, bio, availability, etc.)
@router.get("/me", response_model=UserResponse)
def get_my_profile():
    return {"message": "not implemented yet"}


# Update the logged-in user's profile fields
@router.put("/me", response_model=UserResponse)
def update_my_profile(body: UpdateProfileRequest):
    return {"message": "not implemented yet"}
