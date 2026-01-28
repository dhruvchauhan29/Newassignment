"""Spec model."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Spec(Base):
    """Spec database model."""

    __tablename__ = "specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(Integer, ForeignKey("stories.id"), nullable=False)
    component_name: Mapped[str] = mapped_column(String, nullable=False)
    technical_details: Mapped[str] = mapped_column(Text, nullable=False)
    api_endpoints: Mapped[str] = mapped_column(Text, nullable=True)
    data_models: Mapped[str] = mapped_column(Text, nullable=True)
    dependencies: Mapped[str] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    story = relationship("Story", back_populates="specs")
