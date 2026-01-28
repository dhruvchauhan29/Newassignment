"""Research agent for product research and analysis."""
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent


class ResearchAgent(BaseAgent):
    """Agent for conducting product research."""

    def __init__(self):
        """Initialize research agent."""
        super().__init__(name="ResearchAgent")
        self.llm = ChatOpenAI(model=self.model, temperature=0.7)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research on product idea.

        Args:
            input_data: Contains 'product_idea'

        Returns:
            Research findings
        """
        product_idea = input_data.get("product_idea", "")
        self.log(f"Researching product idea: {product_idea}")

        # Simplified research logic
        prompt = f"""
        Analyze the following product idea and provide:
        1. Market analysis
        2. Target audience
        3. Key features needed
        4. Technical considerations
        5. Potential challenges

        Product Idea: {product_idea}
        """

        try:
            response = await self.llm.ainvoke(prompt)
            research_findings = response.content

            return {
                "success": True,
                "research": research_findings,
                "product_idea": product_idea,
            }
        except Exception as e:
            self.log(f"Research failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
