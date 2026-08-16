import asyncio
from unittest.mock import AsyncMock, MagicMock
from hollowmedusa.engine.agent import Agent
from hollowmedusa.engine.harness import Harness
from hollowmedusa.engine.model_client import ModelClient
from hollowmedusa.config.agent_config import AgentConfig


def test_agent_execution():
    harness = MagicMock(spec=Harness)
    harness.run.return_value = MagicMock(
        success=True, output={"test": "data"}, validation_errors=[]
    )
    harness.validate.return_value = []

    model_client = AsyncMock(spec=ModelClient)
    model_client.generate.return_value = MagicMock(content="test output")

    config = AgentConfig(
        id="test",
        step="requirements",
        harness="extract",
        system_prompt="test",
        primary_model="openai/gpt-4o-mini",
    )
    agent = Agent(config, harness, model_client)
    result = asyncio.run(agent.execute({"input": "test"}))
    assert result.success
