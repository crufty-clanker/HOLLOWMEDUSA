"""ModelRegistry — loads model configs and dispatches to provider clients."""

from pathlib import Path

import yaml

from ..engine.llm_providers import AnthropicClient, OllamaClient, OpenAIClient
from ..engine.model_client import ModelClient
from .model_config import ModelConfig


class ModelRegistry:
    """Load model configurations and provide client instances."""

    PROVIDERS: dict[str, type[ModelClient]] = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
        "ollama": OllamaClient,
    }

    def __init__(self, config_path: Path | None = None):
        self.models: dict[str, ModelConfig] = {}
        self.clients: dict[str, ModelClient] = {}
        self.config_path = config_path or Path("config/models.yaml")
        self._load()

    def _load(self):
        """Load models from YAML config file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            for model_data in data.get("models", []):
                config = ModelConfig(**model_data)
                self.models[config.id] = config

    def get_client(self, model_id: str) -> ModelClient:
        """Get or create a model client for the given model ID."""
        if model_id not in self.clients:
            config = self.models.get(model_id)
            if not config:
                raise ValueError(f"Model {model_id} not found in registry")

            provider_cls = self.PROVIDERS.get(config.provider)
            if not provider_cls:
                raise ValueError(f"Unknown provider: {config.provider}")

            self.clients[model_id] = provider_cls(
                api_key=config.api_key,
                base_url=config.base_url,
            )

        return self.clients[model_id]

    def list_models(self) -> list[ModelConfig]:
        """List all registered models."""
        return list(self.models.values())

    def register(self, config: ModelConfig):
        """Register a new model."""
        self.models[config.id] = config
