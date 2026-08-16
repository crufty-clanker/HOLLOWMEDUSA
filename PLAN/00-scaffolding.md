# Phase 0 — Implementation Tasks

## 0.1 — Directory Structure

Create the monorepo layout:

```
HOLLOWMEDUSA/
├── backend/                 # Python FastAPI + langgraph engine
│   ├── pyproject.toml
│   ├── src/
│   │   └── hollowmedusa/
│   │       ├── __init__.py
│   │       ├── main.py              # FastAPI app entry
│   │       ├── config/              # YAML config loading
│   │       ├── engine/              # Pipeline engine (Phase 1)
│   │       ├── api/                 # FastAPI routes (Phase 2)
│   │       └── models/              # Pydantic models
│   ├── tests/
│   └── .env.example
├── frontend/                # React + Vite + TS
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/              # Zustand state
│   │   ├── lib/                 # API client, utils
│   │   └── types/               # Generated TS types
│   └── public/
├── .gitignore
├── Makefile                   # Unified dev commands
└── README.md
```

---

## 0.2 — Python Backend Setup

### 0.2.1 — `backend/pyproject.toml`

```toml
[project]
name = "hollowmedusa"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "langgraph>=0.2",
    "langchain-openai>=0.2",
    "langchain-anthropic>=0.2",
    "langchain-ollama>=0.2",
    "pydantic>=2.9",
    "pydantic-settings>=2.5",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
    "sqlalchemy>=2.0",
    "aiosqlite>=0.20",          # SQLite async driver
    "httpx>=0.27",              # Async HTTP for LLM clients
    "python-jose[cryptography]>=3.3",  # JWT
    "passlib[bcrypt]>=1.7",     # Password hashing
    "python-multipart>=0.0.9",  # File uploads
    "structlog>=24.4",          # Structured logging
    "pydantic-ai-slim[openai,anthropic]>=0.4",  # prompt linting
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "ruff>=0.6",
    "mypy>=1.13",
    "httpx>=0.27",              # for TestClient
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 0.2.2 — Initialize Python project

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 0.2.3 — `backend/.env.example`

```env
# LLM Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# App
DATABASE_URL=sqlite+aiosqlite:///./hollowmedusa.db
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=http://localhost:5173

# Defaults
DEFAULT_MODEL=openai/gpt-4o-mini
DEFAULT_CONTEXT=python-backend
```

### 0.2.4 — `backend/src/hollowmedusa/main.py` (minimal skeleton)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HollowMedusa", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

### 0.2.5 — Ruff config + pre-commit

```bash
# backend/.pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

---

## 0.3 — React Frontend Setup

### 0.3.1 — Create Vite project

```bash
cd frontend
pnpm create vite@latest . --template react-ts
cd frontend
pnpm install
```

### 0.3.2 — Install dependencies

```bash
pnpm add reactflow zustand @tanstack/react-query socket.io-client
pnpm add @monaco-editor/react react-router-dom
pnpm add -D @types/reactflow tailwindcss @tailwindcss/vite
```

### 0.3.3 — `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

### 0.3.4 — `frontend/src/main.tsx`

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1 } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
```

### 0.3.5 — Tailwind setup

```bash
pnpm tailwindcss init
```

```css
/* frontend/src/index.css */
@import "tailwindcss";
```

---

## 0.4 — Shared Types

### 0.4.1 — Define types in Python (source of truth)

```python
# backend/src/hollowmedusa/models/schemas.py

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class PipelineState(BaseModel):
    requirements: Optional[dict] = None
    architecture: Optional[dict] = None
    prompts: dict[str, str] = Field(default_factory=dict)
    code: dict[str, str] = Field(default_factory=dict)
    test_results: list[dict] = Field(default_factory=list)
    review: Optional[dict] = None
    documentation: Optional[str] = None
    errors: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AgentConfig(BaseModel):
    id: str
    step: str
    harness: str
    system_prompt: str
    primary_model: str
    fallback_models: list[str] = Field(default_factory=list)
    context_ids: list[str] = Field(default_factory=list)


class ModelConfig(BaseModel):
    id: str                    # e.g. "openai/gpt-4o"
    provider: str              # "openai", "anthropic", "ollama"
    model_name: str            # "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 60


class ContextConfig(BaseModel):
    id: str
    name: str
    description: str = ""
    files: list[str] = Field(default_factory=list)  # file paths in context store
    steps: list[str] = Field(default_factory=list)  # which steps use this context
```

### 0.4.2 — Generate TypeScript types

```bash
# Install: pip install openapi-python-client
# Or manually write them. Add script to Makefile:
# generate-types:
#   openapi-python-client generate --path http://localhost:8000/openapi.json --output ../frontend/src/types
```

Alternatively, hand-write a minimal `frontend/src/types/api.ts`:

```typescript
export type StepStatus = 'pending' | 'running' | 'succeeded' | 'failed' | 'skipped'
export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'stopped'

export interface PipelineState {
  requirements?: Record<string, any>
  architecture?: Record<string, any>
  prompts: Record<string, string>
  code: Record<string, string>
  test_results: any[]
  review?: Record<string, any>
  documentation?: string
  errors: string[]
  metadata: Record<string, any>
}

export interface AgentConfig {
  id: string
  step: string
  harness: string
  system_prompt: string
  primary_model: string
  fallback_models: string[]
  context_ids: string[]
}

export interface ModelConfig {
  id: string
  provider: 'openai' | 'anthropic' | 'ollama'
  model_name: string
  api_key?: string
  base_url?: string
  rate_limit?: number
  timeout: number
}

export interface ContextConfig {
  id: string
  name: string
  description: string
  files: string[]
  steps: string[]
}

export interface Run {
  id: string
  status: RunStatus
  state: PipelineState
  created_at: string
  updated_at: string
}
```

---

## 0.5 — CI Pipeline

### 0.5.1 — `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: ruff check src/ tests/
      - run: ruff format --check src/ tests/
      - run: pytest tests/

  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck
      - run: pnpm build
```

### 0.5.2 — `Makefile` (root)

```makefile
.PHONY: dev-backend dev-frontend lint test

dev-backend:
	cd backend && source .venv/bin/activate && uvicorn hollowmedusa.main:app --reload --port 8000

dev-frontend:
	cd frontend && pnpm dev

lint:
	cd backend && ruff check src/ tests/
	cd frontend && pnpm lint

typecheck:
	cd frontend && pnpm typecheck

test:
	cd backend && pytest tests/

setup:
	cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
	cd frontend && pnpm install
```

---

## 0.6 — Git Setup

```bash
git init
echo "# HollowMedusa" > README.md
git add .
git commit -m "init: project scaffolding"
```

---

## Checklist

- [ ] `0.2.1` pyproject.toml written
- [ ] `0.2.2` Python venv created, packages installed
- [ ] `0.2.3` .env.example committed
- [ ] `0.2.4` main.py runs (`uvicorn hollowmedusa.main:app --reload`)
- [ ] `0.2.5` ruff + pre-commit configured
- [ ] `0.3.1` Vite project created
- [ ] `0.3.2` All frontend deps installed
- [ ] `0.3.3` vite.config.ts with proxy configured
- [ ] `0.3.4` main.tsx renders
- [ ] `0.3.5` Tailwind compiles
- [ ] `0.4.1` Pydantic models defined
- [ ] `0.4.2` TypeScript types written
- [ ] `0.5.1` CI workflow committed
- [ ] `0.5.2` Makefile works (`make dev-backend`, `make dev-frontend`)
- [ ] `0.6` Git repo initialized, first commit
