"""
dependencies.py — shared FastAPI dependencies.

get_db:           yields a DB session for the duration of a request
get_current_user: validates the JWT and returns the logged-in User object

Usage in a route:
    from app.dependencies import get_current_user, get_db
    from fastapi import Depends

    def my_route(db = Depends(get_db), current_user = Depends(get_current_user)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import decode_access_token
from app.models.user import User

# Tells FastAPI to expect an "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    # Decode the JWT and extract the user ID
    user_id = decode_access_token(credentials.credentials)

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
