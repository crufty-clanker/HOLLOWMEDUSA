"""Context configuration dataclass."""

from dataclasses import dataclass, field


@dataclass
class ContextConfig:
    """Configuration for a named context collection."""

    id: str
    name: str
    description: str = ""
    files: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
