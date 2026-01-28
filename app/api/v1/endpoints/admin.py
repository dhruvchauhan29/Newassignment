"""Admin endpoints."""
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("/users", response_model=List[UserSchema])
async def list_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_admin_user)],
) -> List[User]:
    """List all users (admin only)."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return list(users)


@router.get("/stats")
async def get_system_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_admin_user)],
):
    """Get system statistics (admin only)."""
    from app.models.project import Project
    from app.models.run import Run

    # Count users
    user_result = await db.execute(select(User))
    user_count = len(list(user_result.scalars().all()))

    # Count projects
    project_result = await db.execute(select(Project))
    project_count = len(list(project_result.scalars().all()))

    # Count runs
    run_result = await db.execute(select(Run))
    run_count = len(list(run_result.scalars().all()))

    return {
        "users": user_count,
        "projects": project_count,
        "runs": run_count,
    }
