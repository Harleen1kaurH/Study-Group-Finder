"""
auth.py — authentication routes.

Handles user registration, login, and logout.
Tokens are issued as HttpOnly cookies — JavaScript cannot read them.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


# Create a new user account with email, password, and name
@router.post("/register")
def register(body: RegisterRequest, response: Response, db: Session = Depends(get_db)):
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

    # Set the token as an HttpOnly cookie — JavaScript cannot read this
    token = create_access_token(str(user.id))
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return {"message": "registered"}


# Verify credentials and set an HttpOnly cookie with the JWT
@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # Look up user by email
    user = db.query(User).filter(User.email == body.email).first()

    # Use the same error for wrong email or wrong password (don't reveal which)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Set the token as an HttpOnly cookie — JavaScript cannot read this
    token = create_access_token(str(user.id))
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return {"message": "logged in"}


# Clear the auth cookie on logout
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "logged out"}
