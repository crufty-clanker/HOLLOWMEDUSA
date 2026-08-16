# Phase 0 — Implementation Tasks

## Execution Order

```
0.1 Directory structure
0.2 Python backend setup
0.3 React frontend setup
0.4 Shared types
0.5 CI pipeline
```

---

## 0.1 — Directory Structure

**Create the monorepo layout:**

```
HOLLOWMEDUSA/
├── backend/
│   ├── pyproject.toml
│   ├── src/hollowmedusa/
│   ├── tests/
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
├── .github/workflows/ci.yml
├── Makefile
└── README.md
```

---

## 0.2 — Python Backend Setup

**Files:**
- `backend/pyproject.toml` — dependencies: fastapi, uvicorn, langgraph, pydantic, sqlalchemy, aiosqlite, httpx, python-jose, passlib, structlog
- `backend/.env.example` — OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_BASE_URL, DATABASE_URL, SECRET_KEY
- `backend/src/hollowmedusa/main.py` — FastAPI app skeleton with /health endpoint
- `backend/.pre-commit-config.yaml` — ruff hooks

**Verification:**
```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn hollowmedusa.main:app --reload --port 8000
# Should see: Uvicorn running on http://127.0.0.1:8000
```

---

## 0.3 — React Frontend Setup

**Files:**
- `frontend/package.json` — react, react-dom, react-router-dom, reactflow, @monaco-editor/react, @tanstack/react-query, socket.io-client, zustand
- `frontend/vite.config.ts` — Tailwind CSS, proxy to localhost:8000
- `frontend/tsconfig.json` — strict mode, path aliases
- `frontend/src/main.tsx` — QueryClient, BrowserRouter
- `frontend/src/App.tsx` — basic routing

**Verification:**
```bash
cd frontend && pnpm install
pnpm dev
# Should see: VITE v6.x ready in xxx ms
```

---

## 0.4 — Shared Types

**Files:**
- `backend/src/hollowmedusa/models/schemas.py` — Pydantic models (PipelineState, AgentConfig, ModelConfig, ContextConfig, Run)
- `frontend/src/types/api.ts` — TypeScript interfaces generated from Pydantic models

**Verification:**
```python
# Python
python -c "from hollowmedusa.models.schemas import PipelineState; print('✅')"

# TypeScript
cd frontend && pnpm exec tsc --noEmit
```

---

## 0.5 — CI Pipeline

**File:** `.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: cd backend && pip install -e ".[dev]"
      - run: cd backend && ruff check src/ tests/
      - run: cd backend && ruff format --check src/ tests/
      - run: cd backend && pytest tests/

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: cd frontend && pnpm install --frozen-lockfile
      - run: cd frontend && pnpm lint
      - run: cd frontend && pnpm typecheck
      - run: cd frontend && pnpm build
```

**Verification:**
```bash
# Backend
cd backend && ruff check src/ tests/
cd backend && pytest tests/

# Frontend
cd frontend && pnpm lint
cd frontend && pnpm typecheck
cd frontend && pnpm build
```

---

## Checklist

- [ ] `0.1` Directory structure created
- [ ] `0.2` Python venv, deps installed, server starts
- [ ] `0.3` Vite project, deps installed, dev server runs
- [ ] `0.4` Pydantic models + TS types defined
- [ ] `0.5` CI workflow committed, passes on main

## Deliverable

Working monorepo with backend + frontend, shared types, and CI pipeline.

```bash
make dev-backend  # Backend on :8000
make dev-frontend # Frontend on :5173
```
