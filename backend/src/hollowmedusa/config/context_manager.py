"""ContextManager — manages named context collections."""

from pathlib import Path

import yaml

from .context_config import ContextConfig


class ContextManager:
    """Load and manage context collections for pipeline steps."""

    def __init__(self, config_path: Path | None = None, store_dir: Path | None = None):
        self.contexts: dict[str, ContextConfig] = {}
        self.config_path = config_path or Path("config/contexts.yaml")
        self.store_dir = store_dir or Path("context_store")
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        """Load contexts from YAML config file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            for ctx_data in data.get("contexts", []):
                config = ContextConfig(**ctx_data)
                self.contexts[config.id] = config

    def create(self, config: ContextConfig):
        """Create a new context."""
        self.contexts[config.id] = config
        self._save()

    def get(self, context_id: str) -> ContextConfig | None:
        """Get context by ID."""
        return self.contexts.get(context_id)

    def list_contexts(self) -> list[ContextConfig]:
        """List all contexts."""
        return list(self.contexts.values())

    def get_context_for_step(self, step: str) -> dict[str, str]:
        """Load all context files for a given step.

        Returns a dict with 'context' key containing concatenated file contents.
        """
        context_text = ""
        for ctx in self.contexts.values():
            if step in ctx.steps:
                for file_path in ctx.files:
                    full_path = self.store_dir / file_path
                    if full_path.exists():
                        context_text += f"\n=== {file_path} ===\n"
                        context_text += full_path.read_text()
        return {"context": context_text}

    def _save(self):
        """Save contexts to YAML config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"contexts": [c.__dict__ for c in self.contexts.values()]}
        self.config_path.write_text(yaml.dump(data, default_flow_style=False))
