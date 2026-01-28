"""Export endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.services.project_service import ProjectService
from app.services.run_service import RunService
from app.utils.export import export_to_markdown, generate_pdf_report

router = APIRouter()


@router.get("/run/{run_id}/pdf")
async def export_run_pdf(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Export run results as PDF."""
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

    # Generate PDF
    report_data = {
        "title": f"Run Report - {project.name}",
        "sections": [
            {
                "title": "Product Idea",
                "content": run.product_idea,
            },
            {
                "title": "Status",
                "content": f"Status: {run.status.value}\nProgress: {run.progress}%",
            },
        ],
    }

    pdf_buffer = generate_pdf_report(report_data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=run_{run_id}_report.pdf"},
    )


@router.get("/run/{run_id}/markdown")
async def export_run_markdown(
    run_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Export run results as Markdown."""
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

    # Generate Markdown
    report_data = {
        "title": f"Run Report - {project.name}",
        "sections": [
            {
                "title": "Product Idea",
                "content": run.product_idea,
            },
            {
                "title": "Status",
                "content": f"Status: {run.status.value}\nProgress: {run.progress}%",
            },
        ],
    }

    markdown = export_to_markdown(report_data)

    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=run_{run_id}_report.md"},
    )
