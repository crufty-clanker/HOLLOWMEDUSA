"""Configuration dataclasses."""

from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Configuration for a single agent."""

    id: str
    step: str
    harness: str
    system_prompt: str
    primary_model: str
    fallback_models: list[str] = field(default_factory=list)
    context_ids: list[str] = field(default_factory=list)


@dataclass
class ModelConfig:
    """Configuration for an LLM model/provider."""

    id: str
    provider: str  # "openai", "anthropic", "ollama"
    model_name: str
    api_key: str | None = None
    base_url: str | None = None
    rate_limit: int | None = None
    timeout: int = 60


@dataclass
class ContextConfig:
    """Configuration for a named context collection."""

    id: str
    name: str
    description: str = ""
    files: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
