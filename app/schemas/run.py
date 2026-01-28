"""Run schemas."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Run status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunBase(BaseModel):
    """Base run schema."""

    product_idea: str = Field(..., min_length=10)


class RunCreate(RunBase):
    """Run creation schema."""

    project_id: int


class RunUpdate(BaseModel):
    """Run update schema."""

    status: Optional[RunStatus] = None
    current_step: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None


class RunInDB(RunBase):
    """Run database schema."""

    id: int
    project_id: int
    status: RunStatus
    current_step: Optional[str] = None
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Run(RunInDB):
    """Run response schema."""

    pass


class RunProgress(BaseModel):
    """Run progress update schema."""

    status: RunStatus
    current_step: str
    progress: int
    message: Optional[str] = None
