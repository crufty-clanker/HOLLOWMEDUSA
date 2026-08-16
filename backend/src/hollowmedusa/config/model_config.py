"""Model configuration dataclass."""

from dataclasses import dataclass


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
