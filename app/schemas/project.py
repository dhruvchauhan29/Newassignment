"""Project schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectInDB(ProjectBase):
    """Project database schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Project(ProjectInDB):
    """Project response schema."""

    pass
