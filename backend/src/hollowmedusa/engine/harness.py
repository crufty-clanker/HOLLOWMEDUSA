from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class HarnessResult(BaseModel):
    """Result from running a harness."""

    success: bool
    output: Any = None
    error: str | None = None
    validation_errors: list[str] = []


class Harness(ABC):
    """Base class for all pipeline step harnesses.

    A harness wraps an LLM call with validation, retry logic, and
    context injection specific to its step type.
    """

    name: str = "base"

    @abstractmethod
    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        """Execute the harness logic.

        Args:
            input_data: Input data for this step.
            context: Optional context injected from ContextManager.

        Returns:
            HarnessResult with success/failure status and output.
        """
        ...

    def validate(self, output: Any) -> list[str]:
        """Validate the output. Return list of error strings (empty = valid).

        Override in subclasses to add step-specific validation.
        """
        return []

    def retry(self, input_data: dict, context: dict, attempt: int) -> HarnessResult:
        """Retry with exponential backoff logic.

        Override in subclasses if custom retry behavior is needed.
        Default: just re-run without backoff.
        """
        return self.run(input_data, context)
