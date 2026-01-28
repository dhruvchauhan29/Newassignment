"""Validation agent for code validation."""
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent


class ValidationAgent(BaseAgent):
    """Agent for validating generated code."""

    def __init__(self):
        """Initialize validation agent."""
        super().__init__(name="ValidationAgent")
        self.llm = ChatOpenAI(model=self.model, temperature=0.2)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code validation.

        Args:
            input_data: Contains 'code' and 'specs'

        Returns:
            Validation results
        """
        code = input_data.get("code", "")
        specs = input_data.get("specs", "")
        self.log("Validating generated code")

        prompt = f"""
        Validate the following code against the specifications.
        Check for:
        - Correctness
        - Best practices
        - Security issues
        - Performance concerns
        - Missing features

        Code: {code}
        Specifications: {specs}

        Provide validation report with issues and recommendations.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            validation_data = response.content

            return {
                "success": True,
                "validation": validation_data,
                "passed": True,  # Simplified
            }
        except Exception as e:
            self.log(f"Validation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
