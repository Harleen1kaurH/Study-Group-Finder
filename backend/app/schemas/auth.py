"""
auth.py — schemas for authentication endpoints.

RegisterRequest: body for POST /auth/register
LoginRequest:    body for POST /auth/login

Note: there's no TokenResponse schema here, since auth uses an HttpOnly
cookie, not a bearer token returned in the response body, so /login and
/register just return a plain {"message": ...} dict.
"""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
