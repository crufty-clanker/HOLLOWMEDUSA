from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StepResult(BaseModel):
    """Result from a single pipeline step."""
    step: str
    status: str  # "succeeded", "failed", "skipped"
    output: Any = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


class PipelineState(BaseModel):
    """Shared state flowing through the langgraph pipeline."""

    # Step outputs
    requirements: dict | None = None
    architecture: dict | None = None
    prompts: dict[str, str] = Field(default_factory=dict)
    code: dict[str, str] = Field(default_factory=dict)
    test_results: list[dict] = Field(default_factory=list)
    review: dict | None = None
    documentation: str | None = None

    # Error tracking
    errors: list[str] = Field(default_factory=list)

    # Metadata
    metadata: dict = Field(default_factory=dict)

    # Runtime fields (not persisted)
    step_results: list[StepResult] = Field(default_factory=list)
    current_step: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def add_error(self, error: str):
        """Add an error to the error list."""
        self.errors.append(error)

    def to_dict(self) -> dict:
        """Serialize to dict, excluding runtime fields."""
        excluded = {
            "step_results",
            "current_step",
            "started_at",
            "completed_at",
        }
        return self.model_dump(exclude=excluded)
