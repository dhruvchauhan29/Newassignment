"""Agent orchestrator using LangGraph with database persistence."""
import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.code import CodeAgent
from app.agents.epic import EpicAgent
from app.agents.research import ResearchAgent
from app.agents.spec import SpecAgent
from app.agents.story import StoryAgent
from app.agents.validation import ValidationAgent


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow using LangGraph with database persistence."""

    def __init__(self, db: Optional[AsyncSession] = None, run_id: Optional[int] = None):
        """Initialize the orchestrator.
        
        Args:
            db: Database session for persistence
            run_id: Run ID for artifact storage
        """
        self.db = db
        self.run_id = run_id
        self.research_agent = ResearchAgent()
        self.epic_agent = EpicAgent()
        self.story_agent = StoryAgent()
        self.spec_agent = SpecAgent()
        self.code_agent = CodeAgent()
        self.validation_agent = ValidationAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow.

        Returns:
            Compiled workflow graph
        """
        # Define the workflow
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("epic", self._epic_node)
        workflow.add_node("story", self._story_node)
        workflow.add_node("spec", self._spec_node)
        workflow.add_node("code", self._code_node)
        workflow.add_node("validation", self._validation_node)

        # Add edges
        workflow.set_entry_point("research")
        workflow.add_edge("research", "epic")
        workflow.add_edge("epic", "story")
        workflow.add_edge("story", "spec")
        workflow.add_edge("spec", "code")
        workflow.add_edge("code", "validation")
        workflow.add_edge("validation", END)

        return workflow.compile()

    async def _persist_artifact(self, artifact_type: str, name: str, content: str):
        """Persist an artifact to the database.
        
        Args:
            artifact_type: Type of artifact
            name: Name of the artifact
            content: Content of the artifact
        """
        if not self.db or not self.run_id:
            return
        
        from app.models.artifact import Artifact, ArtifactType
        
        artifact = Artifact(
            run_id=self.run_id,
            type=ArtifactType(artifact_type),
            name=name,
            content=content,
            created_at=datetime.utcnow(),
        )
        self.db.add(artifact)
        await self.db.commit()

    async def _persist_epics(self, epics_data: list):
        """Persist epics to the database.
        
        Args:
            epics_data: List of epic data dictionaries
        """
        if not self.db or not self.run_id:
            return
        
        from app.models.epic import Epic
        
        for epic_data in epics_data:
            epic = Epic(
                run_id=self.run_id,
                title=epic_data.get("title", ""),
                description=epic_data.get("description", ""),
                priority=epic_data.get("priority", 1),
                is_approved=False,
                created_at=datetime.utcnow(),
            )
            self.db.add(epic)
        await self.db.commit()

    async def _persist_stories(self, stories_data: list, epic_id: int):
        """Persist stories to the database.
        
        Args:
            stories_data: List of story data dictionaries
            epic_id: ID of the parent epic
        """
        if not self.db:
            return
        
        from app.models.story import Story
        
        for story_data in stories_data:
            story = Story(
                epic_id=epic_id,
                title=story_data.get("title", ""),
                description=story_data.get("description", ""),
                priority=story_data.get("priority", 1),
                is_approved=False,
                created_at=datetime.utcnow(),
            )
            self.db.add(story)
        await self.db.commit()

    async def _persist_specs(self, specs_data: list, story_id: int):
        """Persist specs to the database.
        
        Args:
            specs_data: List of spec data dictionaries
            story_id: ID of the parent story
        """
        if not self.db:
            return
        
        from app.models.spec import Spec
        
        for spec_data in specs_data:
            spec = Spec(
                story_id=story_id,
                component_name=spec_data.get("component_name", ""),
                technical_details=spec_data.get("technical_details", ""),
                api_endpoints=json.dumps(spec_data.get("api_endpoints", [])),
                data_models=json.dumps(spec_data.get("data_models", [])),
                is_approved=False,
                created_at=datetime.utcnow(),
            )
            self.db.add(spec)
        await self.db.commit()

    async def _research_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Research node with artifact persistence."""
        result = await self.research_agent.execute(state)
        state.update(result)
        
        # Persist research artifact
        if result.get("success") and result.get("research"):
            await self._persist_artifact(
                "research",
                "Research Report",
                result["research"]
            )
        
        return state

    async def _epic_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Epic node with database persistence."""
        result = await self.epic_agent.execute(state)
        state.update(result)
        
        # Persist epics
        if result.get("success") and result.get("epics"):
            epics_list = result["epics"] if isinstance(result["epics"], list) else []
            if epics_list:
                await self._persist_epics(epics_list)
        
        return state

    async def _story_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Story node with approval gate check."""
        # Check if epics are approved
        if self.db and self.run_id:
            from sqlalchemy import select
            from app.models.epic import Epic
            
            result = await self.db.execute(
                select(Epic).filter(Epic.run_id == self.run_id)
            )
            epics = result.scalars().all()
            
            if not epics or not all(epic.is_approved for epic in epics):
                state["error"] = "Cannot generate stories: Epics not approved"
                return state
        
        result = await self.story_agent.execute(state)
        state.update(result)
        
        # Persist stories
        if result.get("success") and result.get("stories") and self.db and self.run_id:
            from sqlalchemy import select
            from app.models.epic import Epic
            
            # Get first epic for simplicity (in real implementation, link properly)
            result_epic = await self.db.execute(
                select(Epic).filter(Epic.run_id == self.run_id).limit(1)
            )
            first_epic = result_epic.scalar_one_or_none()
            
            if first_epic:
                stories_list = result["stories"] if isinstance(result["stories"], list) else []
                if stories_list:
                    await self._persist_stories(stories_list, first_epic.id)
        
        return state

    async def _spec_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Spec node with approval gate check."""
        # Check if stories are approved
        if self.db and self.run_id:
            from sqlalchemy import select
            from app.models.epic import Epic
            from app.models.story import Story
            
            result = await self.db.execute(
                select(Story).join(Epic).filter(Epic.run_id == self.run_id)
            )
            stories = result.scalars().all()
            
            if not stories or not all(story.is_approved for story in stories):
                state["error"] = "Cannot generate specs: Stories not approved"
                return state
        
        result = await self.spec_agent.execute(state)
        state.update(result)
        
        # Persist specs
        if result.get("success") and result.get("specs") and self.db and self.run_id:
            from sqlalchemy import select
            from app.models.epic import Epic
            from app.models.story import Story
            
            # Get first story for simplicity
            result_story = await self.db.execute(
                select(Story).join(Epic).filter(Epic.run_id == self.run_id).limit(1)
            )
            first_story = result_story.scalar_one_or_none()
            
            if first_story:
                specs_list = result["specs"] if isinstance(result["specs"], list) else []
                if specs_list:
                    await self._persist_specs(specs_list, first_story.id)
        
        return state

    async def _code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Code node with approval gate check."""
        # Check if specs are approved
        if self.db and self.run_id:
            from sqlalchemy import select
            from app.models.epic import Epic
            from app.models.story import Story
            from app.models.spec import Spec
            
            result = await self.db.execute(
                select(Spec).join(Story).join(Epic).filter(Epic.run_id == self.run_id)
            )
            specs = result.scalars().all()
            
            if not specs or not all(spec.is_approved for spec in specs):
                state["error"] = "Cannot generate code: Specs not approved"
                return state
        
        result = await self.code_agent.execute(state)
        state.update(result)
        
        # Persist code artifact
        if result.get("success") and result.get("code"):
            await self._persist_artifact(
                "code",
                "Generated Code",
                json.dumps(result["code"])
            )
        
        return state

    async def _validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validation node with report persistence."""
        result = await self.validation_agent.execute(state)
        state.update(result)
        
        # Persist validation report
        if result.get("success") and result.get("validation_report"):
            await self._persist_artifact(
                "diagram",
                "Validation Report",
                json.dumps(result["validation_report"])
            )
        
        return state

    async def execute(
        self, product_idea: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the workflow with real-time progress.

        Args:
            product_idea: Product idea to process

        Yields:
            Progress updates with stage information
        """
        initial_state = {"product_idea": product_idea}

        # Define stages with detailed information
        stages = [
            ("research", "Conducting market research and analysis..."),
            ("epic", "Creating product epics with priorities..."),
            ("story", "Writing detailed user stories..."),
            ("spec", "Generating technical specifications..."),
            ("code", "Generating production code..."),
            ("validation", "Running validation and tests..."),
        ]

        try:
            # Execute each stage and yield progress
            for i, (stage_name, message) in enumerate(stages):
                progress = int((i / len(stages)) * 100)
                
                # Emit stage start
                yield {
                    "status": "running",
                    "stage": stage_name,
                    "current_step": stage_name,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
                # Simulate stage execution
                await asyncio.sleep(1)
            
            # Execute the actual workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Check for errors during execution
            if final_state.get("error"):
                yield {
                    "status": "failed",
                    "stage": "error",
                    "current_step": "error",
                    "progress": 0,
                    "message": final_state["error"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                yield {
                    "status": "completed",
                    "stage": "completed",
                    "current_step": "completed",
                    "progress": 100,
                    "message": "Workflow completed successfully",
                    "timestamp": datetime.utcnow().isoformat(),
                }
        except Exception as e:
            yield {
                "status": "failed",
                "stage": "error",
                "current_step": "error",
                "progress": 0,
                "message": f"Workflow failed: {str(e)}",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

