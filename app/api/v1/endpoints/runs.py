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
    """Execute run in background with database persistence."""
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            orchestrator = AgentOrchestrator(db=db, run_id=run_id)
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


# Artifact Retrieval Endpoints

@router.get("/{run_id}/epics")
async def get_run_epics(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get all epics for a run."""
    from sqlalchemy import select
    from app.models.epic import Epic
    
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
    
    result = await db.execute(select(Epic).filter(Epic.run_id == run_id))
    epics = result.scalars().all()
    
    return [
        {
            "id": epic.id,
            "title": epic.title,
            "description": epic.description,
            "priority": epic.priority,
            "is_approved": epic.is_approved,
            "created_at": epic.created_at.isoformat(),
        }
        for epic in epics
    ]


@router.get("/{run_id}/stories")
async def get_run_stories(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get all stories for a run."""
    from sqlalchemy import select
    from app.models.epic import Epic
    from app.models.story import Story
    
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
    
    # Get stories through epics
    result = await db.execute(
        select(Story).join(Epic).filter(Epic.run_id == run_id)
    )
    stories = result.scalars().all()
    
    return [
        {
            "id": story.id,
            "epic_id": story.epic_id,
            "title": story.title,
            "description": story.description,
            "is_approved": story.is_approved,
            "created_at": story.created_at.isoformat(),
        }
        for story in stories
    ]


@router.get("/{run_id}/specs")
async def get_run_specs(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get all specs for a run."""
    from sqlalchemy import select
    from app.models.epic import Epic
    from app.models.story import Story
    from app.models.spec import Spec
    
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
    
    # Get specs through stories and epics
    result = await db.execute(
        select(Spec).join(Story).join(Epic).filter(Epic.run_id == run_id)
    )
    specs = result.scalars().all()
    
    return [
        {
            "id": spec.id,
            "story_id": spec.story_id,
            "component_name": spec.component_name,
            "technical_details": spec.technical_details,
            "is_approved": spec.is_approved,
            "created_at": spec.created_at.isoformat(),
        }
        for spec in specs
    ]


@router.get("/{run_id}/artifacts")
async def get_run_artifacts(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get all artifacts for a run."""
    from sqlalchemy import select
    from app.models.artifact import Artifact
    
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
    
    result = await db.execute(select(Artifact).filter(Artifact.run_id == run_id))
    artifacts = result.scalars().all()
    
    return [
        {
            "id": artifact.id,
            "type": artifact.type.value,
            "name": artifact.name,
            "content": artifact.content,
            "created_at": artifact.created_at.isoformat(),
        }
        for artifact in artifacts
    ]


# Approval Endpoints

@router.post("/{run_id}/epics/{epic_id}/approve")
async def approve_epic(
    run_id: int,
    epic_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Approve an epic."""
    from sqlalchemy import select
    from app.models.epic import Epic
    
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
    
    result = await db.execute(select(Epic).filter(Epic.id == epic_id, Epic.run_id == run_id))
    epic = result.scalar_one_or_none()
    
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found",
        )
    
    epic.is_approved = True
    await db.commit()
    
    return {"message": "Epic approved", "epic_id": epic_id}


@router.post("/{run_id}/stories/{story_id}/approve")
async def approve_story(
    run_id: int,
    story_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Approve a story."""
    from sqlalchemy import select
    from app.models.epic import Epic
    from app.models.story import Story
    
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
    
    result = await db.execute(
        select(Story).join(Epic).filter(Story.id == story_id, Epic.run_id == run_id)
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found",
        )
    
    story.is_approved = True
    await db.commit()
    
    return {"message": "Story approved", "story_id": story_id}


@router.post("/{run_id}/specs/{spec_id}/approve")
async def approve_spec(
    run_id: int,
    spec_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Approve a spec."""
    from sqlalchemy import select
    from app.models.epic import Epic
    from app.models.story import Story
    from app.models.spec import Spec
    
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
    
    result = await db.execute(
        select(Spec).join(Story).join(Epic).filter(Spec.id == spec_id, Epic.run_id == run_id)
    )
    spec = result.scalar_one_or_none()
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spec not found",
        )
    
    spec.is_approved = True
    await db.commit()
    
    return {"message": "Spec approved", "spec_id": spec_id}


# Traceability Matrix Endpoint

@router.get("/{run_id}/traceability")
async def get_traceability_matrix(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Get traceability matrix for a run."""
    import json
    from sqlalchemy import select
    from app.models.epic import Epic
    from app.models.story import Story
    from app.models.spec import Spec
    from app.models.artifact import Artifact
    
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
    
    # Build traceability matrix
    matrix = {
        "run_id": run_id,
        "product_idea": run.product_idea,
        "traceability": []
    }
    
    # Get epics
    epics_result = await db.execute(select(Epic).filter(Epic.run_id == run_id))
    epics = epics_result.scalars().all()
    
    for epic in epics:
        epic_trace = {
            "epic_id": epic.id,
            "epic_title": epic.title,
            "stories": []
        }
        
        # Get stories for this epic
        stories_result = await db.execute(select(Story).filter(Story.epic_id == epic.id))
        stories = stories_result.scalars().all()
        
        for story in stories:
            story_trace = {
                "story_id": story.id,
                "story_title": story.title,
                "specs": []
            }
            
            # Get specs for this story
            specs_result = await db.execute(select(Spec).filter(Spec.story_id == story.id))
            specs = specs_result.scalars().all()
            
            for spec in specs:
                story_trace["specs"].append({
                    "spec_id": spec.id,
                    "component_name": spec.component_name,
                })
            
            epic_trace["stories"].append(story_trace)
        
        matrix["traceability"].append(epic_trace)
    
    # Get artifacts
    artifacts_result = await db.execute(select(Artifact).filter(Artifact.run_id == run_id))
    artifacts = artifacts_result.scalars().all()
    
    matrix["artifacts"] = [
        {
            "id": artifact.id,
            "type": artifact.type.value,
            "name": artifact.name,
        }
        for artifact in artifacts
    ]
    
    return matrix
