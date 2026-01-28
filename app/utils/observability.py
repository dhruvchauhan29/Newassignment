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
                from langfuse.callback import CallbackHandler

                self.langfuse = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
                self.callback_handler = CallbackHandler(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
            except ImportError:
                self.enabled = False
                self.langfuse = None
                self.callback_handler = None
        else:
            self.langfuse = None
            self.callback_handler = None

    def get_callback_handler(self):
        """Get Langfuse callback handler for LLM calls.
        
        Returns:
            CallbackHandler if available, None otherwise
        """
        return self.callback_handler if self.enabled else None

    def trace_llm_call(
        self,
        agent_name: str,
        model: str,
        input_prompt: str,
        output: str,
        tokens_used: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Trace an LLM call.

        Args:
            agent_name: Name of the agent making the call
            model: Model name (e.g., "gpt-4")
            input_prompt: Input prompt sent to LLM
            output: Output from LLM
            tokens_used: Token usage dictionary
            metadata: Additional metadata
        """
        if not self.enabled or not self.langfuse:
            return

        try:
            trace = self.langfuse.trace(
                name=f"{agent_name}_llm_call",
                metadata=metadata or {},
            )
            
            generation = trace.generation(
                name=f"{agent_name}_generation",
                model=model,
                input=input_prompt,
                output=output,
            )
            
            if tokens_used:
                generation.update(
                    usage={
                        "promptTokens": tokens_used.get("prompt_tokens", 0),
                        "completionTokens": tokens_used.get("completion_tokens", 0),
                        "totalTokens": tokens_used.get("total_tokens", 0),
                    }
                )
        except Exception as e:
            print(f"Failed to trace LLM call: {str(e)}")

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
            trace = self.langfuse.trace(name=agent_name, metadata=metadata or {})
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
