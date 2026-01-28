"""Artifact schemas."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ArtifactType(str, Enum):
    """Artifact types."""

    RESEARCH = "research"
    EPIC = "epic"
    STORY = "story"
    SPEC = "spec"
    CODE = "code"
    DIAGRAM = "diagram"


class ArtifactBase(BaseModel):
    """Base artifact schema."""

    type: ArtifactType
    name: str
    content: str
    meta_data: Optional[str] = None  # Renamed from metadata


class ArtifactCreate(ArtifactBase):
    """Artifact creation schema."""

    run_id: int


class ArtifactInDB(ArtifactBase):
    """Artifact database schema."""

    id: int
    run_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Artifact(ArtifactInDB):
    """Artifact response schema."""

    pass
