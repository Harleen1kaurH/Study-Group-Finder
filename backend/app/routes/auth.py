"""
auth.py — authentication routes.

Handles user registration, login, and logout.
JWT tokens are issued on login and must be sent with subsequent requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# Create a new user account with email, password, and name
@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user with hashed password
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return a token so the user is logged in immediately
    return TokenResponse(access_token=create_access_token(str(user.id)))


# Verify credentials and return a JWT access token
@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    # Look up user by email
    user = db.query(User).filter(User.email == body.email).first()

    # Use the same error for wrong email or wrong password (don't reveal which)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(access_token=create_access_token(str(user.id)))


# Logout is stateless — client discards the token, nothing to do server-side
@router.post("/logout")
def logout():
    return {"message": "logged out"}
