"""Agent orchestrator using LangGraph."""
import asyncio
from typing import Any, AsyncGenerator, Dict

from langgraph.graph import END, StateGraph

from app.agents.code import CodeAgent
from app.agents.epic import EpicAgent
from app.agents.research import ResearchAgent
from app.agents.spec import SpecAgent
from app.agents.story import StoryAgent
from app.agents.validation import ValidationAgent


class AgentOrchestrator:
    """Orchestrates the multi-agent workflow using LangGraph."""

    def __init__(self):
        """Initialize the orchestrator."""
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

    async def _research_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Research node."""
        result = await self.research_agent.execute(state)
        state.update(result)
        return state

    async def _epic_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Epic node."""
        result = await self.epic_agent.execute(state)
        state.update(result)
        return state

    async def _story_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Story node."""
        result = await self.story_agent.execute(state)
        state.update(result)
        return state

    async def _spec_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Spec node."""
        result = await self.spec_agent.execute(state)
        state.update(result)
        return state

    async def _code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Code node."""
        result = await self.code_agent.execute(state)
        state.update(result)
        return state

    async def _validation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validation node."""
        result = await self.validation_agent.execute(state)
        state.update(result)
        return state

    async def execute(
        self, product_idea: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the workflow.

        Args:
            product_idea: Product idea to process

        Yields:
            Progress updates
        """
        initial_state = {"product_idea": product_idea}

        # Simulate streaming execution
        steps = [
            ("research", "Conducting market research..."),
            ("epic", "Creating product epics..."),
            ("story", "Writing user stories..."),
            ("spec", "Generating technical specifications..."),
            ("code", "Generating code..."),
            ("validation", "Validating output..."),
        ]

        for i, (step, message) in enumerate(steps):
            progress = int((i + 1) / len(steps) * 100)
            yield {
                "status": "running",
                "current_step": step,
                "progress": progress,
                "message": message,
            }
            await asyncio.sleep(1)  # Simulate processing time

        # Execute the actual workflow (simplified)
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            yield {
                "status": "completed",
                "current_step": "completed",
                "progress": 100,
                "message": "Workflow completed successfully",
                "result": final_state,
            }
        except Exception as e:
            yield {
                "status": "failed",
                "current_step": "error",
                "progress": 0,
                "message": f"Workflow failed: {str(e)}",
                "error": str(e),
            }
