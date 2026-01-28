"""Test approval gates and artifact persistence."""
import asyncio

import pytest
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.epic import Epic
from app.models.run import Run, RunStatus
from app.models.story import Story
from app.services.agent_orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_approval_gates():
    """Test that approval gates are enforced."""
    async with AsyncSessionLocal() as db:
        # Create a test run
        run = Run(
            project_id=1,
            product_idea="Test product",
            status=RunStatus.PENDING,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        
        # Create orchestrator
        orchestrator = AgentOrchestrator(db=db, run_id=run.id)
        
        # Execute workflow
        state = {"product_idea": "Test product"}
        
        # Execute research node
        result = await orchestrator._research_node(state)
        assert "research" in result or "success" in result
        
        # Execute epic node
        result = await orchestrator._epic_node(state)
        assert result is not None
        
        # Check that epics were created
        epics_result = await db.execute(select(Epic).filter(Epic.run_id == run.id))
        epics = epics_result.scalars().all()
        
        # Verify epics are not approved by default
        if epics:
            assert all(not epic.is_approved for epic in epics), "Epics should not be approved by default"
        
        # Try to execute story node without approval
        result = await orchestrator._story_node(state)
        
        # If we have epics and they're not approved, we should get an error
        if epics and not all(epic.is_approved for epic in epics):
            assert "error" in result, "Stories should not generate without epic approval"
            assert "not approved" in result["error"].lower()
        
        print("✅ Approval gate test passed")


@pytest.mark.asyncio
async def test_artifact_persistence():
    """Test that artifacts are persisted correctly."""
    async with AsyncSessionLocal() as db:
        # Create a test run
        run = Run(
            project_id=1,
            product_idea="Test product for artifacts",
            status=RunStatus.PENDING,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        
        # Create orchestrator with database
        orchestrator = AgentOrchestrator(db=db, run_id=run.id)
        
        # Test artifact persistence
        await orchestrator._persist_artifact(
            "research",
            "Test Research Report",
            "This is a test research report content"
        )
        
        # Verify artifact was saved
        from app.models.artifact import Artifact
        result = await db.execute(
            select(Artifact).filter(Artifact.run_id == run.id)
        )
        artifacts = result.scalars().all()
        
        assert len(artifacts) > 0, "Artifacts should be persisted"
        assert artifacts[0].name == "Test Research Report"
        assert "test research" in artifacts[0].content.lower()
        
        print("✅ Artifact persistence test passed")


if __name__ == "__main__":
    asyncio.run(test_approval_gates())
    asyncio.run(test_artifact_persistence())
    print("\n✅ All tests passed!")
