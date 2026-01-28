"""Observability utilities with Langfuse integration."""
from typing import Any, Dict, Optional

from app.core.config import settings


class ObservabilityManager:
    """Manager for observability and tracing."""

    def __init__(self):
        """Initialize observability manager."""
        self.enabled = bool(
            settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY
        )

        if self.enabled:
            try:
                from langfuse import Langfuse

                self.langfuse = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
            except ImportError:
                self.enabled = False
                self.langfuse = None
        else:
            self.langfuse = None

    def trace_agent_execution(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Trace an agent execution.

        Args:
            agent_name: Name of the agent
            input_data: Input to the agent
            output_data: Output from the agent
            metadata: Additional metadata
        """
        if not self.enabled or not self.langfuse:
            return

        try:
            trace = self.langfuse.trace(name=agent_name)
            trace.span(
                name=f"{agent_name}_execution",
                input=input_data,
                output=output_data,
                metadata=metadata or {},
            )
        except Exception as e:
            print(f"Failed to trace agent execution: {str(e)}")

    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Log an error.

        Args:
            error: Exception that occurred
            context: Context information
        """
        if not self.enabled or not self.langfuse:
            return

        try:
            self.langfuse.trace(
                name="error",
                metadata={
                    "error": str(error),
                    "type": type(error).__name__,
                    "context": context,
                },
            )
        except Exception as e:
            print(f"Failed to log error: {str(e)}")


# Global instance
observability = ObservabilityManager()
