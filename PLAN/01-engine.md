# Phase 1 — Implementation Tasks

## Execution Order (Dependencies)

```
1.1 PipelineState (foundation)
    ↓
1.2 Harness base class
    ↓
1.3 Harness subclasses (8 total)
    ↓
1.4 ModelClient + adapters
    ↓
1.5 Agent class (uses Harness + ModelClient)
    ↓
1.6 AgentRegistry (uses Agent)
1.7 ModelRegistry (uses ModelClient)
    ↓
1.8 ContextManager
    ↓
1.9 PipelineRunner (uses AgentRegistry + ModelRegistry + ContextManager)
    ↓
1.10 Prompt Linting
```

---

## 1.1 — PipelineState

**File:** `backend/src/hollowmedusa/models/state.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StepResult(BaseModel):
    step: str
    status: str  # "succeeded", "failed", "skipped"
    output: dict | None = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


class PipelineState(BaseModel):
    """Shared state flowing through the langgraph pipeline."""
    requirements: dict | None = None
    architecture: dict | None = None
    prompts: dict[str, str] = Field(default_factory=dict)
    code: dict[str, str] = Field(default_factory=dict)
    test_results: list[dict] = Field(default_factory=list)
    review: dict | None = None
    documentation: str | None = None
    errors: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    # Runtime fields (not persisted)
    step_results: list[StepResult] = Field(default_factory=list)
    current_step: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def add_error(self, error: str):
        self.errors.append(error)

    def to_dict(self) -> dict:
        return self.model_dump(exclude={'step_results', 'current_step', 'started_at', 'completed_at'})
```

**Verification:**
```bash
cd backend && source .venv/bin/activate && python -c "
from hollowmedusa.models.state import PipelineState
s = PipelineState()
s.add_error('test error')
assert len(s.errors) == 1
print('✅ PipelineState works')
"
```

---

## 1.2 — Harness Base Class

**File:** `backend/src/hollowmedusa/engine/harness.py`

```python
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class HarnessResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    validation_errors: list[str] = []


class Harness(ABC):
    """Base class for all pipeline step harnesses."""

    name: str = "base"

    @abstractmethod
    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        """Execute the harness logic."""
        ...

    def validate(self, output: Any) -> list[str]:
        """Validate output. Return list of error strings (empty = valid)."""
        return []

    def retry(self, input_data: dict, context: dict, attempt: int) -> HarnessResult:
        """Retry with exponential backoff logic (override if needed)."""
        return self.run(input_data, context)
```

**Verification:**
```bash
python -c "
from hollowmedusa.engine.harness import Harness, HarnessResult
# Can't instantiate abstract class
try:
    h = Harness()
    assert False, 'Should fail'
except TypeError:
    print('✅ Harness is abstract')
"
```

---

## 1.3 — Harness Subclasses

**Files:**
- `backend/src/hollowmedusa/engine/harnesses/extract.py` — ExtractHarness (Requirements)
- `backend/src/hollowmedusa/engine/harnesses/topology.py` — TopologyHarness (Architecture)
- `backend/src/hollowmedusa/engine/harnesses/compile.py` — CompileHarness (Prompt Engineering)
- `backend/src/hollowmedusa/engine/harnesses/code.py` — CodeHarness (Code Generation)
- `backend/src/hollowmedusa/engine/harnesses/merge.py` — MergeHarness (Integration)
- `backend/src/hollowmedusa/engine/harnesses/test.py` — TestHarness (Testing)
- `backend/src/hollowmedusa/engine/harnesses/review.py` — ReviewHarness (Review & Refactor)
- `backend/src/hollowmedusa/engine/harnesses/doc.py` — DocHarness (Documentation)

**Example: ExtractHarness**
```python
from .harness import Harness, HarnessResult
import json
import re


class ExtractHarness(Harness):
    name = "extract"

    def run(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        text = input_data.get("text", "")
        # Try to parse as JSON first
        try:
            parsed = json.loads(text)
            return HarnessResult(success=True, output=parsed)
        except json.JSONDecodeError:
            pass

        # Fallback: extract key-value pairs
        parsed = {}
        for line in text.split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                parsed[key.strip()] = value.strip()

        return HarnessResult(success=True, output=parsed)

    def validate(self, output: Any) -> list[str]:
        errors = []
        if not isinstance(output, dict):
            errors.append("Output must be a dict")
        if "goal" not in output:
            errors.append("Missing required field: goal")
        return errors
```

**Verification:**
```bash
python -c "
from hollowmedusa.engine.harnesses.extract import ExtractHarness
h = ExtractHarness()
result = h.run({'text': 'goal: build an app\nscope: web'})
assert result.success
assert result.output['goal'] == 'build an app'
print('✅ ExtractHarness works')
"
```

**Create all 8 harness files** (skeletons with `run()` and `validate()` methods).

---

## 1.4 — ModelClient + Adapters

**Files:**
- `backend/src/hollowmedusa/engine/model_client.py` — Base interface
- `backend/src/hollowmedusa/engine/llm_providers/openai_client.py`
- `backend/src/hollowmedusa/engine/llm_providers/anthropic_client.py`
- `backend/src/hollowmedusa/engine/llm_providers/ollama_client.py`

**Base interface:**
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: dict = {}


class ModelClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str, **kwargs) -> LLMResponse:
        ...

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        ...
```

**OpenAI adapter:**
```python
from .model_client import ModelClient, LLMResponse
from openai import AsyncOpenAI
import os


class OpenAIClient(ModelClient):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
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
```

**Verification:**
```python
# Requires OPENAI_API_KEY set
python -c "
import asyncio
from hollowmedusa.engine.llm_providers.openai_client import OpenAIClient

async def test():
    client = OpenAIClient()
    resp = await client.generate('Hello', 'You are helpful.')
    assert resp.content
    print(f'✅ OpenAI client works: {resp.model}')

asyncio.run(test())
"
```

---

## 1.5 — Agent Class

**File:** `backend/src/hollowmedusa/engine/agent.py`

```python
from .harness import Harness, HarnessResult
from .model_client import ModelClient, LLMResponse
from ..config import AgentConfig


class Agent:
    """Ties a harness + model + system prompt together."""

    def __init__(self, config: AgentConfig, harness: Harness, model_client: ModelClient):
        self.config = config
        self.harness = harness
        self.model_client = model_client

    async def execute(self, input_data: dict, context: dict | None = None) -> HarnessResult:
        """Run the agent: inject prompt → call LLM → run harness → validate."""
        # 1. Build the prompt from system prompt + input
        prompt = self._build_prompt(input_data, context)

        # 2. Call LLM
        llm_response = await self.model_client.generate(
            prompt=prompt,
            system_prompt=self.config.system_prompt,
            model=self.config.primary_model,
        )

        # 3. Run harness
        harness_result = self.harness.run(
            input_data={"llm_output": llm_response.content, **input_data},
            context=context,
        )

        # 4. Validate
        validation_errors = self.harness.validate(harness_result.output)
        if validation_errors:
            harness_result.validation_errors = validation_errors
            harness_result.success = False

        return harness_result

    def _build_prompt(self, input_data: dict, context: dict | None) -> str:
        """Inject context variables into the prompt."""
        prompt_parts = [self.config.system_prompt, "\n\nInput:\n"]
        for key, value in input_data.items():
            if key != "llm_output":
                prompt_parts.append(f"{key}: {value}\n")
        if context:
            prompt_parts.append(f"\nContext:\n{context}")
        return "\n".join(prompt_parts)
```

**Verification:**
```python
# Mock test
python -c "
from unittest.mock import AsyncMock, MagicMock
from hollowmedusa.engine.agent import Agent
from hollowmedusa.engine.harness import Harness
from hollowmedusa.engine.model_client import ModelClient
from hollowmedusa.config import AgentConfig

# Mock harness
harness = MagicMock(spec=Harness)
harness.run.return_value = MagicMock(success=True, output={'test': 'data'})
harness.validate.return_value = []

# Mock model client
model_client = AsyncMock(spec=ModelClient)
model_client.generate.return_value = MagicMock(content='test output')

# Create agent
config = AgentConfig(
    id='test', step='requirements', harness='extract',
    system_prompt='You are a test agent.', primary_model='gpt-4o-mini'
)
agent = Agent(config, harness, model_client)

# Run
result = asyncio.run(agent.execute({'input': 'test'}))
assert result.success
print('✅ Agent works')
"
```

---

## 1.6 — AgentRegistry

**File:** `backend/src/hollowmedusa/config/agent_registry.py`

```python
from dataclasses import dataclass
from typing import dict
import yaml
from pathlib import Path


@dataclass
class AgentConfig:
    id: str
    step: str
    harness: str
    system_prompt: str
    primary_model: str
    fallback_models: list[str] = []
    context_ids: list[str] = []


class AgentRegistry:
    def __init__(self, config_path: Path | None = None):
        self.agents: dict[str, AgentConfig] = {}
        self.config_path = config_path or Path("config/agents.yaml")
        self._load()

    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            for agent_data in data.get("agents", []):
                config = AgentConfig(**agent_data)
                self.agents[config.id] = config

    def get(self, agent_id: str) -> AgentConfig | None:
        return self.agents.get(agent_id)

    def list_agents(self) -> list[AgentConfig]:
        return list(self.agents.values())

    def register(self, config: AgentConfig):
        self.agents[config.id] = config
```

**Verification:**
```bash
# Create a test agents.yaml
cat > /tmp/test_agents.yaml << 'EOF'
agents:
  - id: requirements_agent
    step: requirements
    harness: extract
    system_prompt: "You are a product analyst."
    primary_model: openai/gpt-4o-mini
EOF

python -c "
from pathlib import Path
from hollowmedusa.config.agent_registry import AgentRegistry
registry = AgentRegistry(Path('/tmp/test_agents.yaml'))
assert len(registry.list_agents()) == 1
assert registry.get('requirements_agent').step == 'requirements'
print('✅ AgentRegistry works')
"
```

---

## 1.7 — ModelRegistry

**File:** `backend/src/hollowmedusa/config/model_registry.py`

```python
from dataclasses import dataclass
from typing import dict
import yaml
from pathlib import Path
from ..engine.model_client import ModelClient
from ..engine.llm_providers import OpenAIClient, AnthropicClient, OllamaClient


@dataclass
class ModelConfig:
    id: str
    provider: str
    model_name: str
    api_key: str | None = None
    base_url: str | None = None
    rate_limit: int | None = None
    timeout: int = 60


class ModelRegistry:
    PROVIDERS = {
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
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            for model_data in data.get("models", []):
                config = ModelConfig(**model_data)
                self.models[config.id] = config

    def get_client(self, model_id: str) -> ModelClient:
        if model_id not in self.clients:
            config = self.models.get(model_id)
            if not config:
                raise ValueError(f"Model {model_id} not found")
            provider_cls = self.PROVIDERS.get(config.provider)
            if not provider_cls:
                raise ValueError(f"Unknown provider: {config.provider}")
            self.clients[model_id] = provider_cls(
                api_key=config.api_key,
                base_url=config.base_url,
            )
        return self.clients[model_id]

    def list_models(self) -> list[ModelConfig]:
        return list(self.models.values())
```

**Verification:**
```python
python -c "
from pathlib import Path
from hollowmedusa.config.model_registry import ModelRegistry
registry = ModelRegistry()  # No config file = empty registry
assert len(registry.list_models()) == 0
print('✅ ModelRegistry works')
"
```

---

## 1.8 — ContextManager

**File:** `backend/src/hollowmedusa/config/context_manager.py`

```python
from dataclasses import dataclass
from typing import dict
import yaml
from pathlib import Path


@dataclass
class ContextConfig:
    id: str
    name: str
    description: str = ""
    files: list[str] = []
    steps: list[str] = []


class ContextManager:
    def __init__(self, config_path: Path | None = None, store_dir: Path | None = None):
        self.contexts: dict[str, ContextConfig] = {}
        self.config_path = config_path or Path("config/contexts.yaml")
        self.store_dir = store_dir or Path("context_store")
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
            for ctx_data in data.get("contexts", []):
                config = ContextConfig(**ctx_data)
                self.contexts[config.id] = config

    def create(self, config: ContextConfig):
        self.contexts[config.id] = config
        # Save config
        self._save()

    def get(self, context_id: str) -> ContextConfig | None:
        return self.contexts.get(context_id)

    def list_contexts(self) -> list[ContextConfig]:
        return list(self.contexts.values())

    def get_context_for_step(self, step: str) -> dict[str, str]:
        """Load all context files for a given step."""
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
        data = {"contexts": [c.__dict__ for c in self.contexts.values()]}
        self.config_path.write_text(yaml.dump(data, default_flow_style=False))
```

**Verification:**
```bash
python -c "
from pathlib import Path
from hollowmedusa.config.context_manager import ContextManager, ContextConfig
cm = ContextManager()
ctx = ContextConfig(id='test', name='Test Context', steps=['requirements'])
cm.create(ctx)
assert len(cm.list_contexts()) == 1
print('✅ ContextManager works')
"
```

---

## 1.9 — PipelineRunner

**File:** `backend/src/hollowmedusa/engine/pipeline_runner.py`

```python
from .agent import Agent
from .harness import Harness
from ..config.agent_registry import AgentRegistry
from ..config.model_registry import ModelRegistry
from ..config.context_manager import ContextManager
from ..models.state import PipelineState, StepResult
import asyncio
import uuid
from datetime import datetime


class PipelineRunner:
    def __init__(
        self,
        agent_registry: AgentRegistry,
        model_registry: ModelRegistry,
        context_manager: ContextManager,
    ):
        self.agent_registry = agent_registry
        self.model_registry = model_registry
        self.context_manager = context_manager
        self.agents: dict[str, Agent] = {}

    def build_agents(self):
        """Instantiate all agents from registry."""
        for agent_config in self.agent_registry.list_agents():
            # Find matching harness
            from . import harnesses
            harness_cls = getattr(harnesses, f"{agent_config.harness.capitalize()}Harness", None)
            if not harness_cls:
                raise ValueError(f"Unknown harness: {agent_config.harness}")

            # Get model client
            model_client = self.model_registry.get_client(agent_config.primary_model)

            # Create agent
            agent = Agent(agent_config, harness_cls(), model_client)
            self.agents[agent_config.id] = agent

    async def run(self, state: PipelineState, graph: dict) -> PipelineState:
        """Execute the pipeline according to the graph topology."""
        state.started_at = datetime.now()

        # Topological sort of graph
        nodes = self._topological_sort(graph)

        for node_id in nodes:
            state.current_step = node_id
            agent = self.agents.get(node_id)
            if not agent:
                state.add_error(f"Agent not found: {node_id}")
                continue

            try:
                # Get context for this step
                context = self.context_manager.get_context_for_step(node_id)

                # Execute agent
                result = await agent.execute(state.to_dict(), context)

                # Record step result
                step_result = StepResult(
                    step=node_id,
                    status="succeeded" if result.success else "failed",
                    output=result.output,
                    error=result.error,
                )
                state.step_results.append(step_result)

                if not result.success:
                    state.add_error(f"Step {node_id} failed: {result.validation_errors}")

            except Exception as e:
                state.add_error(f"Step {node_id} error: {str(e)}")

        state.completed_at = datetime.now()
        state.current_step = None
        return state

    def _topological_sort(self, graph: dict) -> list[str]:
        """Simple topological sort of graph nodes."""
        visited = set()
        order = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for neighbor in graph.get(node, {}).get("depends_on", []):
                visit(neighbor)
            order.append(node)

        for node in graph:
            visit(node)

        return order
```

**Verification:**
```python
# Integration test with mocked agents
python -c "
import asyncio
from hollowmedusa.engine.pipeline_runner import PipelineRunner
from hollowmedusa.models.state import PipelineState

# This would need full setup, but structure is correct
state = PipelineState()
print('✅ PipelineRunner structure OK')
"
```

---

## 1.10 — Prompt Linting

**File:** `backend/src/hollowmedusa/engine/prompt_linter.py`

```python
import re
from typing import list


class PromptLinter:
    """Validate prompts for common issues."""

    def __init__(self):
        self.errors = []

    def lint(self, prompt: str, variables: list[str] | None = None) -> list[str]:
        self.errors = []

        # Check for empty prompt
        if not prompt.strip():
            self.errors.append("Prompt is empty")

        # Check for undefined variables
        if variables:
            defined_vars = set(variables)
            found_vars = re.findall(r'\{\{(\w+)\}\}', prompt)
            for var in found_vars:
                if var not in defined_vars:
                    self.errors.append(f"Undefined variable: {{{{ {var} }}}}")

        # Check for contradictory instructions
        if "always" in prompt.lower() and "never" in prompt.lower():
            self.errors.append("Prompt contains contradictory 'always' and 'never' instructions")

        # Check for excessive length (>10k chars)
        if len(prompt) > 10000:
            self.errors.append("Prompt exceeds 10,000 characters")

        return self.errors
```

**Verification:**
```python
python -c "
from hollowmedusa.engine.prompt_linter import PromptLinter
linter = PromptLinter()

# Test empty prompt
errors = linter.lint('')
assert len(errors) == 1
assert 'empty' in errors[0].lower()

# Test undefined variable
errors = linter.lint('Use {{undefined_var}}', ['defined_var'])
assert len(errors) == 1
assert 'undefined' in errors[0].lower()

print('✅ PromptLinter works')
"
```

---

## 1.11 — Unit Tests

**Files:**
- `backend/tests/test_harnesses.py` — Test all 8 harnesses
- `backend/tests/test_agent.py` — Test Agent with mocked LLM
- `backend/tests/test_pipeline_runner.py` — Test full pipeline execution
- `backend/tests/test_prompt_linter.py` — Test prompt validation

**Test harnesses:**
```python
# backend/tests/test_harnesses.py
from hollowmedusa.engine.harnesses.extract import ExtractHarness
from hollowmedusa.engine.harnesses.topology import TopologyHarness
from hollowmedusa.engine.harnesses.compile import CompileHarness

def test_extract_harness():
    harness = ExtractHarness()
    result = harness.run({"text": "goal: build app"})
    assert result.success
    assert result.output["goal"] == "build app"

def test_topology_harness_no_cycles():
    harness = TopologyHarness()
    graph = {"nodes": [{"id": "a"}, {"id": "b"}], "edges": [{"source": "a", "target": "b"}]}
    result = harness.run({"graph": graph})
    assert harness.validate(result.output) == []

def test_compile_harness_substitution():
    harness = CompileHarness()
    result = harness.run({"prompts": {"node1": "You are a {{role}}"}, "role": "analyst"})
    assert result.output["node1"] == "You are an analyst"
```

**Test agent:**
```python
# backend/tests/test_agent.py
import asyncio
from unittest.mock import AsyncMock, MagicMock
from hollowmedusa.engine.agent import Agent
from hollowmedusa.engine.harness import Harness
from hollowmedusa.engine.model_client import ModelClient

def test_agent_execution():
    harness = MagicMock(spec=Harness)
    harness.run.return_value = MagicMock(success=True, output={"test": "data"}, validation_errors=[])
    harness.validate.return_value = []

    model_client = AsyncMock(spec=ModelClient)
    model_client.generate.return_value = MagicMock(content="test output")

    agent = Agent(config, harness, model_client)
    result = asyncio.run(agent.execute({"input": "test"}))
    assert result.success
```

**Test pipeline runner:**
```python
# backend/tests/test_pipeline_runner.py
import asyncio
from hollowmedusa.engine.pipeline_runner import PipelineRunner
from hollowmedusa.models.state import PipelineState

def test_pipeline_runner():
    runner = PipelineRunner(agent_registry, model_registry, context_manager)
    runner.build_agents()

    state = PipelineState()
    graph = {"test_req": {"depends_on": []}}
    result_state = asyncio.run(runner.run(state, graph))
    assert len(result_state.step_results) == 1
    assert result_state.errors == []
```

**Test prompt linter:**
```python
# backend/tests/test_prompt_linter.py
from hollowmedusa.engine.prompt_linter import PromptLinter

def test_prompt_linter_empty():
    linter = PromptLinter()
    errors = linter.lint("")
    assert len(errors) == 1
    assert "empty" in errors[0].lower()

def test_prompt_linter_undefined_var():
    linter = PromptLinter()
    errors = linter.lint("Use {{undefined_var}}", ["defined_var"])
    assert len(errors) == 1
    assert "undefined" in errors[0].lower()
```

**Verification:**
```bash
cd backend && source .venv/bin/activate
pytest tests/ -v
# Should see: 4 passed
```

---

## Checklist

- [ ] `1.1` PipelineState defined and tested
- [ ] `1.2` Harness base class defined and tested
- [ ] `1.3` All 8 harness subclasses created and tested
- [ ] `1.4` ModelClient interface + 3 adapters (OpenAI, Anthropic, Ollama)
- [ ] `1.5` Agent class defined and tested
- [ ] `1.6` AgentRegistry with YAML loading
- [ ] `1.7` ModelRegistry with provider dispatch
- [ ] `1.8` ContextManager with file loading
- [ ] `1.9` PipelineRunner with topological execution
- [ ] `1.10` PromptLinter with validation rules
- [ ] `1.11` Unit tests for all components

## Deliverable

CLI tool that can run a full pipeline end-to-end:

```bash
cd backend && source .venv/bin/activate
python -m hollowmedusa.cli run --config config/pipeline.yaml
```

## CI Update

Add to `.github/workflows/ci.yml`:
```yaml
- run: cd backend && pytest tests/
```
