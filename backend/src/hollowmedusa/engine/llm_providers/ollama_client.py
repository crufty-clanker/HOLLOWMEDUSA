"""Ollama LLM provider adapter."""

import os

from ..model_client import LLMResponse, ModelClient


class OllamaClient(ModelClient):
    """Client for local Ollama instances."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        from ollama import AsyncClient

        self.client = AsyncClient(
            host=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )

    async def generate(self, prompt: str, system_prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.generate(
            model=kwargs.get("model", "llama3"),
            prompt=prompt,
            system=system_prompt,
            options={k: v for k, v in kwargs.items() if k in ("num_predict", "temperature")},
        )
        return LLMResponse(
            content=response.get("response", ""),
            model=response.get("model", "unknown"),
            usage={"total_tokens": response.get("eval_count", 0)},
        )

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        response = await self.client.chat(
            model=kwargs.get("model", "llama3"),
            messages=messages,
            options={k: v for k, v in kwargs.items() if k in ("num_predict", "temperature")},
        )
        return LLMResponse(
            content=response.get("message", {}).get("content", ""),
            model=response.get("model", "unknown"),
            usage={"total_tokens": response.get("eval_count", 0)},
        )
