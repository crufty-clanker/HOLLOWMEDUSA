"""OpenAI LLM provider adapter."""

import os

from ..model_client import LLMResponse, ModelClient


class OpenAIClient(ModelClient):
    """Client for OpenAI's chat completions API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url,
        )

    async def generate(self, prompt: str, system_prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            **{k: v for k, v in kwargs.items() if k != "model"},
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage=response.usage.model_dump() if response.usage else {},
        )

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=messages,
            **{k: v for k, v in kwargs.items() if k != "model"},
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage=response.usage.model_dump() if response.usage else {},
        )
