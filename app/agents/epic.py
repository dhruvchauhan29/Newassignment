"""Epic agent for creating epics."""
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent


class EpicAgent(BaseAgent):
    """Agent for creating product epics."""

    def __init__(self):
        """Initialize epic agent."""
        super().__init__(name="EpicAgent")
        self.llm = ChatOpenAI(model=self.model, temperature=0.7)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute epic creation.

        Args:
            input_data: Contains 'product_idea' and 'research'

        Returns:
            List of epics
        """
        product_idea = input_data.get("product_idea", "")
        research = input_data.get("research", "")

        self.log(f"Creating epics for: {product_idea}")

        prompt = f"""
        Based on the following product idea and research, create 3-5 high-level epics.
        For each epic, provide:
        - Title
        - Description
        - Acceptance Criteria
        - Priority (1-5)

        Product Idea: {product_idea}
        Research: {research}

        Format as JSON array.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            # Simplified - in production, parse JSON properly
            epics_data = response.content

            return {
                "success": True,
                "epics": epics_data,
                "product_idea": product_idea,
            }
        except Exception as e:
            self.log(f"Epic creation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
