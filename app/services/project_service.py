"""Project service."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project operations."""

    @staticmethod
    async def create_project(
        db: AsyncSession, project_in: ProjectCreate, user_id: int
    ) -> Project:
        """Create a new project.

        Args:
            db: Database session
            project_in: Project creation schema
            user_id: Owner user ID

        Returns:
            Created project
        """
        project = Project(
            name=project_in.name,
            description=project_in.description,
            user_id=user_id,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
        """Get project by ID.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Project if found, None otherwise
        """
        result = await db.execute(select(Project).filter(Project.id == project_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_projects(db: AsyncSession, user_id: int) -> List[Project]:
        """Get all projects for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of projects
        """
        result = await db.execute(select(Project).filter(Project.user_id == user_id))
        return list(result.scalars().all())

    @staticmethod
    async def update_project(
        db: AsyncSession, project: Project, project_in: ProjectUpdate
    ) -> Project:
        """Update a project.

        Args:
            db: Database session
            project: Project to update
            project_in: Project update schema

        Returns:
            Updated project
        """
        if project_in.name is not None:
            project.name = project_in.name
        if project_in.description is not None:
            project.description = project_in.description

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete_project(db: AsyncSession, project: Project) -> None:
        """Delete a project.

        Args:
            db: Database session
            project: Project to delete
        """
        await db.delete(project)
        await db.commit()
