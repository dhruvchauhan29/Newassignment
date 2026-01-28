"""Run endpoints."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.core.dependencies import get_current_active_user
from app.db.session import AsyncSessionLocal, get_db
from app.models.run import RunStatus
from app.models.user import User
from app.schemas.run import Run, RunCreate
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.project_service import ProjectService
from app.services.run_service import RunService

router = APIRouter()


@router.post("/", response_model=Run, status_code=status.HTTP_201_CREATED)
async def create_run(
    run_in: RunCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Run:
    """Create a new run."""
    # Verify project ownership
    project = await ProjectService.get_project(db, run_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    run = await RunService.create_run(db, run_in)
    return run


@router.get("/{run_id}", response_model=Run)
async def get_run(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Run:
    """Get a specific run."""
    run = await RunService.get_run(db, run_id)

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )

    # Verify project ownership
    project = await ProjectService.get_project(db, run.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return run


@router.get("/project/{project_id}", response_model=List[Run])
async def list_project_runs(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> List[Run]:
    """List all runs for a project."""
    # Verify project ownership
    project = await ProjectService.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    runs = await RunService.get_project_runs(db, project_id)
    return runs


@router.post("/{run_id}/start")
async def start_run(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Start a run execution (async)."""
    run = await RunService.get_run(db, run_id)

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )

    # Verify project ownership
    project = await ProjectService.get_project(db, run.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    if run.status != RunStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run is not in pending status",
        )

    # Update status to running
    from app.schemas.run import RunUpdate
    update_data = RunUpdate(status=RunStatus.RUNNING, current_step="initialization")
    await RunService.update_run(db, run, update_data)
    
    # Start execution in background
    import asyncio
    asyncio.create_task(_execute_run(run_id, run.product_idea))
    
    return {"message": "Run started", "run_id": run_id}


async def _execute_run(run_id: int, product_idea: str):
    """Execute run in background."""
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            orchestrator = AgentOrchestrator()
            async for progress in orchestrator.execute(product_idea):
                run = await RunService.get_run(db, run_id)
                if run:
                    from app.schemas.run import RunUpdate
                    update_data = RunUpdate(
                        status=RunStatus(progress.get("status", "running")),
                        current_step=progress.get("current_step", ""),
                        progress=progress.get("progress", 0),
                    )
                    await RunService.update_run(db, run, update_data)
        except Exception as e:
            print(f"Error executing run {run_id}: {e}")
            run = await RunService.get_run(db, run_id)
            if run:
                from app.schemas.run import RunUpdate
                update_data = RunUpdate(
                    status=RunStatus.FAILED,
                    error_message=str(e),
                )
                await RunService.update_run(db, run, update_data)


@router.get("/{run_id}/progress")
async def get_run_progress(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get real-time progress via SSE."""
    run = await RunService.get_run(db, run_id)

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )

    # Verify project ownership
    project = await ProjectService.get_project(db, run.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    async def event_generator():
        """Generate SSE events for run progress."""
        import asyncio
        import json
        
        while True:
            # Fetch current run status
            async with AsyncSessionLocal() as session:
                current_run = await RunService.get_run(session, run_id)
                if current_run:
                    progress_data = {
                        "status": current_run.status.value,
                        "current_step": current_run.current_step or "",
                        "progress": current_run.progress,
                        "error_message": current_run.error_message or "",
                    }
                    
                    yield {
                        "event": "progress",
                        "data": json.dumps(progress_data),
                    }
                    
                    # Stop streaming if run is completed or failed
                    if current_run.status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
                        break
            
            await asyncio.sleep(1)  # Poll every second

    return EventSourceResponse(event_generator())
