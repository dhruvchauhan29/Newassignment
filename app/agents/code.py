"""Code agent for generating code."""
from typing import Any, Dict

from langchain_openai import ChatOpenAI

from app.agents.base import BaseAgent


class CodeAgent(BaseAgent):
    """Agent for generating code."""

    def __init__(self):
        """Initialize code agent."""
        super().__init__(name="CodeAgent")
        self.llm = ChatOpenAI(model=self.model, temperature=0.3)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation.

        Args:
            input_data: Contains 'specs'

        Returns:
            Generated code
        """
        specs = input_data.get("specs", "")
        self.log("Generating code from specifications")

        prompt = f"""
        Based on the following technical specifications, generate production-ready code.
        Include:
        - File structure
        - Implementation code
        - Tests
        - Documentation

        Specifications: {specs}

        Provide code with proper structure and best practices.
        """

        try:
            response = await self.llm.ainvoke(prompt)
            code_data = response.content

            return {
                "success": True,
                "code": code_data,
            }
        except Exception as e:
            self.log(f"Code generation failed: {str(e)}", "error")
            return {"success": False, "error": str(e)}
