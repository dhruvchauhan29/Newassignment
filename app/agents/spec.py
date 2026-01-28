"""Spec agent for creating technical specifications."""
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent


class SpecAgent(BaseAgent):
    """Agent for creating technical specifications."""

    def __init__(self):
        """Initialize spec agent."""
        super().__init__(name="SpecAgent")
        self.llm = ChatOpenAI(model=self.model, temperature=0.5)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute spec creation.

        Args:
            input_data: Contains 'stories'

        Returns:
            Technical specifications
        """
        stories = input_data.get("stories", "")
        self.log("Creating technical specifications")

        prompt = f"""
        Based on the following user stories, create detailed technical specifications.
        For each component, provide:
        - Component name
        - Technical details
        - API endpoints
        - Data models
        - Dependencies

        User Stories: {stories}

        Format as JSON array.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            specs_data = response.content

            return {
                "success": True,
                "specs": specs_data,
            }
        except Exception as e:
            self.log(f"Spec creation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
