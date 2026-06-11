"""
auth.py — schemas for authentication endpoints.

RegisterRequest: body for POST /auth/register
LoginRequest:    body for POST /auth/login
TokenResponse:   returned on successful login (JWT access token)
"""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
