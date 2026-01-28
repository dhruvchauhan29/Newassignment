"""User model."""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, PyEnum):
    """User roles."""

    ADMIN = "admin"
    USER = "user"


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
