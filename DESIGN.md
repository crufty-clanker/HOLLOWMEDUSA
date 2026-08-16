# Design — HollowMedusa

> A langgraph-based development pipeline with specialized agent combinations per step, managed through a web interface.

---

## 1. Overview

HollowMedusa is a **multi-agent development orchestration system**. It decomposes software development into discrete, composable steps. Each step is executed by a dedicated agent configured with a specific harness, system prompt, and LLM model. The entire pipeline is represented as a **langgraph** and is configurable at runtime via a **web interface**.

### Core Principles

- **Step specialization** — no single model does everything; each step uses the best tool for the job.
- **Graph as source of truth** — the pipeline IS a langgraph; topology, state, and routing are first-class.
- **Runtime configurability** — models, prompts, contexts, and graph structure are editable without code changes.
- **Observability** — every invocation is traced, logged, and replayable.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Graph    │ │ Model    │ │ Prompt   │ │ Context   │  │
│  │ Editor   │ │ Config   │ │ Editor   │ │ Manager   │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
└──────────────────────────┬──────────────────────────────┘
                           │ REST / WebSocket
┌──────────────────────────▼──────────────────────────────┐
│                   API Server (FastAPI)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Pipeline Orchestrator                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │
│  │  │ Lang-   │ │ Agent   │ │ Harness │           │   │
│  │  │ graph   │ │ Registry│ │ Runner  │           │   │
│  │  └─────────┘ └─────────┘ └─────────┘           │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │  LLM Provider │ │  LLM Provider │ │  LLM Provider │
   │  (OpenAI)    │ │  (Anthropic)  │ │  (Local/Ollama)│
   └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 3. Langgraph Topology

The pipeline is a **langgraph `StateGraph`** where:

- **Nodes** = agents (each with its harness + model).
- **Edges** = data flow + conditional routing between steps.
- **State** = shared schema carrying artifacts through the pipeline.

### State Schema

```python
class PipelineState(TypedDict):
    requirements: dict           # Step 1 output
    architecture: dict           # Step 2 output
    prompts: dict[str, str]      # Step 3 output (per-node prompts)
    code: dict[str, str]         # Step 4 output (per-node source)
    test_results: list[dict]     # Step 6 output
    review: dict                 # Step 7 output
    documentation: str           # Step 8 output
    errors: list[str]            # accumulated errors
    metadata: dict               # run ID, timestamps, model used per step
```

### Graph Structure

```
[Start] → Requirements → Architecture → Prompt_Engineering
                                        ↓
                              Code_Generation → Integration
                                        ↓              ↓
                                      Testing ←──────┘
                                        ↓
                                    Review ──→ Documentation → [End]
```

Conditional edges allow skipping steps (e.g., skip Testing if code generation fails review) or looping back (e.g., re-generate code if tests fail).

---

## 4. Web Interface

### 4.1 Graph Editor

- Visual node-and-edge editor for the langgraph topology.
- Drag to add/remove/reorder nodes.
- Click an edge to set conditions (always, on_success, on_failure, custom).
- Live preview of the compiled graph.
- Export/import graph as JSON.

### 4.2 Model Configuration

- Per-node model selector with dropdown of configured providers.
- Fallback model chain configuration.
- Rate limit and timeout settings per provider.
- API key management (encrypted at rest).
- Provider-agnostic abstraction via a `ModelClient` interface (OpenAI, Anthropic, Ollama, vLLM, etc.).

### 4.3 Prompt Editor

- Per-node system prompt editor with markdown preview.
- Variable interpolation (`{{requirements}}`, `{{architecture}}` etc.).
- Prompt versioning — every edit is saved as a version; rollback supported.
- Prompt linting — detects contradictions, dead variables, format violations.

### 4.4 Context Manager

- Named context collections (e.g., "Python backend", "React frontend").
- Contexts inject relevant files, schemas, and examples into the agent's context window.
- Per-step context scoping — only relevant contexts are loaded.
- File upload and management for context assets.

### 4.5 Pipeline Runner

- Start / pause / resume / stop pipeline execution.
- Step-by-step execution with manual approval gates.
- Real-time execution trace viewer (prompt → response → validation → next step).
- Replay any step with modified parameters.

### 4.6 Observability

- Token usage and cost tracking per run.
- Latency heatmap per step.
- Error log with full prompt/response capture.
- Export traces as JSONL for offline analysis.

---

## 5. Configuration

All configuration is stored as YAML/JSON and live-editable from the web UI:

```
config/
├── graph.yaml          # Graph topology (nodes, edges, conditions)
├── agents.yaml         # Agent registry (harness, prompt, model per node)
├── models.yaml         # LLM provider configurations
├── contexts.yaml       # Named context collections
└── runs/               # Execution history
    └── {run-id}/
        ├── state.json
        ├── traces.jsonl
        └── artifacts/
```

---

## 6. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Langgraph as core** | Native support for stateful, conditional, cyclic graphs. Rich ecosystem. |
| **Harness pattern** | Decouples agent logic from execution concerns (validation, retry, tracing). |
| **Web UI for all config** | Non-developers can operate the pipeline; version control stays in YAML. |
| **Stateless providers** | Each LLM call is self-contained; state lives in the graph, not the provider. |
| **Prompt versioning** | Prompts drift; versioning enables rollback and A/B comparison. |
| **Context scoping** | Only load what each step needs — controls cost and reduces noise. |

---

## 7. Technology Stack

| Layer | Technology |
|-------|-----------|
| Pipeline | Python, langgraph, langchain |
| API | FastAPI |
| Web UI | React + Vite, React Flow (graph editor), Monaco Editor (prompt editor) |
| Storage | SQLite (dev), PostgreSQL (prod) |
| LLM Providers | OpenAI, Anthropic, Ollama, vLLM (extensible) |
| Auth | API keys (env), optional JWT for web UI |

---

## 8. Future Directions

- **Multi-pipeline support** — run several graph variants in parallel.
- **Collaborative editing** — real-time multi-user graph/prompt editing via WebSocket.
- **Prompt marketplace** — share and import prompt templates.
- **Auto-evaluation** — LLM-as-judge for output quality scoring.
- **CI/CD integration** — trigger pipelines from git webhooks.
