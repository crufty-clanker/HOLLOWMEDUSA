# HollowMedusa

A langgraph-based development pipeline with specialized agent combinations per step, managed through a web interface.

## Quick Start

```bash
# Setup
make setup

# Run backend (port 8000)
make dev-backend

# Run frontend (port 5173)
make dev-frontend
```

## Architecture

- **Backend**: Python, FastAPI, langgraph, SQLAlchemy
- **Frontend**: React, Vite, TypeScript, React Flow, Tailwind CSS
- **Pipeline**: Multi-step agent orchestration with configurable models, prompts, and contexts

## Features

- **Graph Editor**: Visual langgraph topology editor
- **Model Config**: Manage LLM providers (OpenAI, Anthropic, Ollama)
- **Prompt Editor**: Monaco editor with markdown preview
- **Context Manager**: Named context collections with file upload
- **Pipeline Runner**: Real-time execution with WebSocket updates
- **Observability**: Token usage, latency, error tracking

## API

- `POST /api/v1/runs/` — Start pipeline execution
- `GET /api/v1/runs/{id}` — Get run status
- `GET /api/v1/agents/` — List agents
- `PUT /api/v1/models/` — Configure models
- `WS /runs/{id}/events` — Real-time updates

## Development

```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn hollowmedusa.api.main:app --reload

# Frontend
cd frontend && pnpm dev

# Tests
cd backend && pytest tests/
cd frontend && pnpm test
```

## Deployment

```bash
docker-compose up -d
# Access UI at http://localhost:3000
```

## Documentation

- [Agents](./AGENTS.md) — Agent registry
- [Design](./DESIGN.md) — System architecture
- [Plan](./PLAN.md) — Implementation roadmap

## License

This project is licensed as [MIT](LICENSE)
