"""Story agent for creating user stories."""
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent


class StoryAgent(BaseAgent):
    """Agent for creating user stories."""

    def __init__(self):
        """Initialize story agent."""
        super().__init__(name="StoryAgent")
        self.llm = ChatOpenAI(model=self.model, temperature=0.7)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute story creation.

        Args:
            input_data: Contains 'epics'

        Returns:
            List of user stories
        """
        epics = input_data.get("epics", "")
        self.log("Creating user stories from epics")

        prompt = f"""
        Based on the following epics, create detailed user stories.
        For each story, provide:
        - Title
        - User story (As a... I want... So that...)
        - Acceptance criteria
        - Priority

        Epics: {epics}

        Format as JSON array.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            stories_data = response.content

            return {
                "success": True,
                "stories": stories_data,
            }
        except Exception as e:
            self.log(f"Story creation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
