"""Anthropic LLM provider adapter."""

import os

from ..model_client import LLMResponse, ModelClient


class AnthropicClient(ModelClient):
    """Client for Anthropic's Claude API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=base_url,
        )

    async def generate(self, prompt: str, system_prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.messages.create(
            model=kwargs.get("model", "claude-sonnet-4-20250514"),
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        content = response.content[0].text if response.content else ""
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )

    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        # Extract system message if present
        system = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)

        response = await self.client.messages.create(
            model=kwargs.get("model", "claude-sonnet-4-20250514"),
            system=system,
            messages=filtered_messages,
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        content = response.content[0].text if response.content else ""
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        )
