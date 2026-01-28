"""Authentication service."""
from datetime import timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user.

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            User if authenticated, None otherwise
        """
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        """Create a new user.

        Args:
            db: Database session
            user_in: User creation schema

        Returns:
            Created user
        """
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role=user_in.role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    def create_token(user_id: int) -> str:
        """Create access token.

        Args:
            user_id: User ID

        Returns:
            Access token
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(subject=user_id, expires_delta=access_token_expires)
