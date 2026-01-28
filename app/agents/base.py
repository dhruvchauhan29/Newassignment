"""Base agent class."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, model: str = "gpt-4-turbo-preview"):
        """Initialize the agent.

        Args:
            name: Agent name
            model: LLM model to use
        """
        self.name = name
        self.model = model

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task.

        Args:
            input_data: Input data for the agent

        Returns:
            Output data from the agent
        """
        pass

    def log(self, message: str, level: str = "info") -> None:
        """Log a message.

        Args:
            message: Message to log
            level: Log level
        """
        print(f"[{self.name}] {level.upper()}: {message}")
