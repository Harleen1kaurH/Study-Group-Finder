"""
dependencies.py — shared FastAPI dependencies.

get_db:           yields a DB session for the duration of a request
get_current_user: validates the JWT from the HttpOnly cookie and returns the logged-in User

Usage in a route:
    from app.dependencies import get_current_user, get_db
    from fastapi import Depends

    def my_route(db = Depends(get_db), current_user = Depends(get_current_user)):
        ...
"""

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import decode_access_token
from app.models.user import User


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    # No cookie present — not logged in
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Decode the JWT and extract the user ID
    user_id = decode_access_token(access_token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Fetch the user from the DB
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
