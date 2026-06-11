"""
auth.py — authentication routes.

Handles user registration, login, and logout.
JWT tokens are issued on login and must be sent with subsequent requests.
"""

from fastapi import APIRouter
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# Create a new user account with email, password, and name
@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest):
    return {"message": "not implemented yet"}


# Verify credentials and return a JWT access token
@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    return {"message": "not implemented yet"}


# Invalidate the current session / token
@router.post("/logout")
def logout():
    return {"message": "not implemented yet"}
