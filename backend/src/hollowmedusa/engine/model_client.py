from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Response from an LLM provider."""
    content: str
    model: str
    usage: dict = {}


class ModelClient(ABC):
    """Base interface for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str, **kwargs) -> LLMResponse:
        """Generate a response from a prompt."""
        ...

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        """Chat with the model using a message list."""
        ...
