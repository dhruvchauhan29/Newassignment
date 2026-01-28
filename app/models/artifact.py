"""Artifact model."""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ArtifactType(str, PyEnum):
    """Artifact types."""

    RESEARCH = "research"
    EPIC = "epic"
    STORY = "story"
    SPEC = "spec"
    CODE = "code"
    DIAGRAM = "diagram"


class Artifact(Base):
    """Artifact database model."""

    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("runs.id"), nullable=False)
    type: Mapped[ArtifactType] = mapped_column(Enum(ArtifactType), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_data: Mapped[str] = mapped_column(Text, nullable=True)  # Renamed from metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    run = relationship("Run", back_populates="artifacts")
