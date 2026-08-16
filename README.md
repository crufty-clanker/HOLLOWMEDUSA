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

## Documentation

- [Agents](./AGENTS.md) — Agent registry: harness × system prompt × model matrix
- [Design](./DESIGN.md) — System architecture and design decisions
- [Plan](./PLAN.md) — Implementation roadmap

## License

Private.
