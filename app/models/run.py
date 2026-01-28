"""Run model."""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RunStatus(str, PyEnum):
    """Run status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Run(Base):
    """Run database model."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus), default=RunStatus.PENDING, nullable=False
    )
    product_idea: Mapped[str] = mapped_column(Text, nullable=False)
    current_step: Mapped[str] = mapped_column(String, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="runs")
    artifacts = relationship("Artifact", back_populates="run", cascade="all, delete-orphan")
    epics = relationship("Epic", back_populates="run", cascade="all, delete-orphan")
    traceability_matrix = relationship("TraceabilityMatrix", back_populates="run", cascade="all, delete-orphan", uselist=False)

