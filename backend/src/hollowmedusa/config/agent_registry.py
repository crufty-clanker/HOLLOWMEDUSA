"""AgentRegistry — loads and manages agent configurations."""

from pathlib import Path

import yaml

from .agent_config import AgentConfig


class AgentRegistry:
    """Load agents from YAML config and provide lookup."""

    def __init__(self, config_path: Path | None = None):
        self.agents: dict[str, AgentConfig] = {}
        self.config_path = config_path or Path("config/agents.yaml")
        self._load()

    def _load(self):
        """Load agents from YAML config file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            for agent_data in data.get("agents", []):
                config = AgentConfig(**agent_data)
                self.agents[config.id] = config

    def get(self, agent_id: str) -> AgentConfig | None:
        """Get agent config by ID."""
        return self.agents.get(agent_id)

    def list_agents(self) -> list[AgentConfig]:
        """List all registered agents."""
        return list(self.agents.values())

    def register(self, config: AgentConfig):
        """Register a new agent."""
        self.agents[config.id] = config

    def get_by_step(self, step: str) -> list[AgentConfig]:
        """Get all agents for a specific step."""
        return [a for a in self.agents.values() if a.step == step]
