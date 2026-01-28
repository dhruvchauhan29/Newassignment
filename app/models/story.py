"""Story model."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Story(Base):
    """Story database model."""

    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    epic_id: Mapped[int] = mapped_column(Integer, ForeignKey("epics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    epic = relationship("Epic", back_populates="stories")
    specs = relationship("Spec", back_populates="story", cascade="all, delete-orphan")
