"""User schemas."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User roles."""

    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """User database schema."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """User response schema."""

    pass


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: Optional[int] = None
