# Implementation Plan — HollowMedusa

## Phase 0 — Project Scaffolding

| # | Task | Notes |
|---|------|-------|
| 0.1 | Initialize monorepo (Python backend + React frontend) | `pnpm workspaces` or separate `Makefile` targets |
| 0.2 | Set up Python project: `pyproject.toml`, venv, pre-commit hooks | Dependencies: `fastapi`, `uvicorn`, `langgraph`, `pydantic`, `sqlalchemy`, `alembic` |
| 0.3 | Set up React project: `vite`, TypeScript, Tailwind | Dependencies: `reactflow`, `@monaco-editor/react`, `zustand`, `react-query`, `socket.io-client` |
| 0.4 | Define shared types between frontend and backend | OpenAPI schema generation from FastAPI models → `openapi-typescript` for TS types |
| 0.5 | CI pipeline: lint + test on PR | GitHub Actions, `ruff` for Python, `eslint` + `tsc` for TS |

---

## Phase 1 — Core Pipeline Engine (Backend)

| # | Task | Priority |
|---|------|----------|
| 1.1 | Define `PipelineState` TypedDict with full schema | Foundation for everything |
| 1.2 | Implement `Harness` base class + `run()`, `validate()`, `retry()` | Abstract interface all harnesses extend |
| 1.3 | Implement 8 harness subclasses (Extract, Topology, Compile, Code, Merge, Test, Review, Doc) | One per pipeline step |
| 1.4 | Implement `ModelClient` interface + OpenAI, Anthropic, Ollama adapters | Provider-agnostic LLM calls |
| 1.5 | Implement `Agent` class: ties harness + model + system prompt together | The unit of execution |
| 1.6 | Build `AgentRegistry`: YAML-driven agent loading with hot-reload | `agents.yaml` → in-memory registry |
| 1.7 | Build `ModelRegistry`: provider config, fallback chains, rate limiting | `models.yaml` → client pool |
| 1.8 | Build `ContextManager`: named contexts, file management, per-step scoping | `contexts.yaml` + filesystem |
| 1.9 | Implement `PipelineRunner`: executes langgraph, captures traces | Core orchestration loop |
| 1.10 | Add prompt linting pass (contradiction detection, variable validation) | Quality gate |

**Deliverable:** CLI tool that can run a full pipeline end-to-end with YAML config.

---

## Phase 2 — API Server

| # | Task | Priority |
|---|------|----------|
| 2.1 | FastAPI app skeleton with router structure | `api/v1/` routes |
| 2.2 | `POST /runs` — start a pipeline execution | Triggers Phase 1 runner |
| 2.3 | `GET /runs/{id}` — get run status and state | Polling endpoint |
| 2.4 | `GET /runs/{id}/trace` — get execution trace for a step | Observability |
| 2.5 | `POST /runs/{id}/step/{step}/retry` — retry a failed step | Error recovery |
| 2.6 | `GET /agents` — list registered agents | Agent registry API |
| 2.7 | `PUT /agents/{id}` — update agent config (prompt, model) | Live reconfiguration |
| 2.8 | `GET /models` — list configured models/providers | Model config API |
| 2.9 | `PUT /models` — add/update/remove model config | Model management |
| 2.10 | `GET /contexts` / `POST /contexts` / `PUT /contexts/{id}` | Context CRUD |
| 2.11 | `GET /graph` / `PUT /graph` — read/write graph topology | Graph persistence |
| 2.12 | WebSocket: `ws://runs/{id}/events` — real-time trace stream | Live updates |
| 2.13 | Auth middleware (API key + optional JWT) | Security |
| 2.14 | SQLite storage layer (runs, traces, config) | Persistence |

**Deliverable:** Fully functional REST + WebSocket API.

---

## Phase 3 — Web Interface

| # | Task | Priority |
|---|------|----------|
| 3.1 | App shell: sidebar nav, top bar, main content area | Layout foundation |
| 3.2 | **Graph Editor** page | |
| 3.2.1 | React Flow canvas with langgraph nodes | Visual topology |
| 3.2.2 | Drag-to-add node, click-to-edit, edge routing | Interaction |
| 3.2.3 | Edge condition editor (always / on_success / on_failure / custom) | Conditional edges |
| 3.2.4 | Compile graph → validate → sync to backend | Round-trip |
| 3.3 | **Model Config** page | |
| 3.3.1 | Provider list with add/edit/delete | CRUD |
| 3.3.2 | API key input (masked, encrypted) | Security |
| 3.3.3 | Per-agent model assignment table | Mapping |
| 3.4 | **Prompt Editor** page | |
| 3.4.1 | Monaco Editor with markdown preview pane | Editing |
| 3.4.2 | Variable autocomplete (`{{requirements}}` etc.) | DX |
| 3.4.3 | Version history + rollback | Versioning |
| 3.5 | **Context Manager** page | |
| 3.5.1 | Context list with file upload | Management |
| 3.5.2 | Per-step context assignment | Scoping |
| 3.6 | **Pipeline Runner** page | |
| 3.6.1 | Start / pause / resume / stop controls | Execution |
| 3.6.2 | Step-by-step progress with approval gates | Control |
| 3.6.3 | Real-time trace viewer (WebSocket) | Observability |
| 3.7 | **Observability** page | |
| 3.7.1 | Token/cost tracking dashboard | Metrics |
| 3.7.2 | Latency heatmap per step | Performance |
| 3.7.3 | Error log with full prompt/response capture | Debugging |
| 3.7.4 | Export traces as JSONL | Analysis |

**Deliverable:** Fully interactive web UI.

---

## Phase 4 — Polish & Hardening

| # | Task | Priority |
|---|------|----------|
| 4.1 | Add PostgreSQL support (drop-in replacement for SQLite) | Production readiness |
| 4.2 | Add prompt A/B testing (run same step with two prompts, compare) | Quality |
| 4.3 | Implement CI/CD trigger endpoint (webhook from GitHub) | Automation |
| 4.4 | Add rate-limiting + quota tracking per provider | Operations |
| 4.5 | Write integration tests for full pipeline | Reliability |
| 4.6 | Add Docker Compose for one-command deployment | DevEx |
| 4.7 | Add `docker-compose.prod.yml` with reverse proxy, TLS | Production |
| 4.8 | Write user documentation (README, setup guide, API docs) | Docs |
| 4.9 | Performance profiling: trace latency, optimize hot paths | Optimization |
| 4.10 | Add dark mode to web UI | UX |

---

## Implementation Order Summary

```
Phase 0 (scaffolding)     → 1 week
Phase 1 (pipeline engine) → 2-3 weeks
Phase 2 (API server)      → 2 weeks
Phase 3 (web UI)          → 3-4 weeks
Phase 4 (polish)          → 1-2 weeks
─────────────────────────────────────
Total estimate            → 9-12 weeks
```

### Recommended Execution Order

1. **Phase 0** — get the project building on both sides.
2. **Phase 1** — build the engine first so the API has something to serve.
3. **Phase 2** — API lets you test the engine with curl/Postman before UI work.
4. **Phase 3** — build UI pages in dependency order: Graph Editor → Model Config → Prompt Editor → Context Manager → Runner → Observability.
5. **Phase 4** — hardening once everything works end-to-end.

### Key Risks

| Risk | Mitigation |
|------|-----------|
| Langgraph API changes | Pin versions; write adapter layer between langgraph and our runner |
| LLM provider rate limits | Fallback chains + queuing + backoff in ModelClient |
| Prompt drift / inconsistency | Versioning + linting + diff view in UI |
| State schema complexity | Strict Pydantic models; schema migration tests |
| WebSocket scalability | Start with single-process; add Redis pub/sub later if needed |
