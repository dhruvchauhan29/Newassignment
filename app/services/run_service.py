"""Run service."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.run import Run, RunStatus
from app.schemas.run import RunCreate, RunUpdate


class RunService:
    """Service for run operations."""

    @staticmethod
    async def create_run(db: AsyncSession, run_in: RunCreate) -> Run:
        """Create a new run.

        Args:
            db: Database session
            run_in: Run creation schema

        Returns:
            Created run
        """
        run = Run(
            project_id=run_in.project_id,
            product_idea=run_in.product_idea,
            status=RunStatus.PENDING,
            progress=0,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        return run

    @staticmethod
    async def get_run(db: AsyncSession, run_id: int) -> Optional[Run]:
        """Get run by ID.

        Args:
            db: Database session
            run_id: Run ID

        Returns:
            Run if found, None otherwise
        """
        result = await db.execute(select(Run).filter(Run.id == run_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_project_runs(db: AsyncSession, project_id: int) -> List[Run]:
        """Get all runs for a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            List of runs
        """
        result = await db.execute(select(Run).filter(Run.project_id == project_id))
        return list(result.scalars().all())

    @staticmethod
    async def update_run(db: AsyncSession, run: Run, run_in: RunUpdate) -> Run:
        """Update a run.

        Args:
            db: Database session
            run: Run to update
            run_in: Run update schema

        Returns:
            Updated run
        """
        if run_in.status is not None:
            run.status = run_in.status
        if run_in.current_step is not None:
            run.current_step = run_in.current_step
        if run_in.progress is not None:
            run.progress = run_in.progress
        if run_in.error_message is not None:
            run.error_message = run_in.error_message

        if run_in.status == RunStatus.COMPLETED:
            run.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(run)
        return run
