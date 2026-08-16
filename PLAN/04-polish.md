# Phase 4 — Implementation Tasks

## Execution Order

```
4.1 Integration tests (backend)
4.2 Frontend unit tests (Vitest + RTL)
4.3 E2E tests (Playwright)
    ↓
4.4 PostgreSQL support
4.5 Prompt A/B testing
4.6 CI/CD trigger endpoint
    ↓
4.7 Docker Compose
4.8 Documentation
4.9 Performance profiling
4.10 Dark mode
```

---

## 4.1 — Integration Tests (Backend)

**Problem:** NixOS missing `libstdc++.so.6` prevents async SQLAlchemy tests.

**Solution:** Use sync SQLAlchemy for tests or provide setup script.

**Files:**
- `backend/tests/conftest.py` — Test fixtures
- `backend/tests/test_api_runs.py` — Run CRUD
- `backend/tests/test_api_agents.py` — Agent management
- `backend/tests/test_api_models.py` — Model config
- `backend/tests/test_api_contexts.py` — Context CRUD
- `backend/tests/test_api_graph.py` — Graph topology
- `backend/tests/test_websocket.py` — WebSocket events

**Setup script:**
```bash
# backend/tests/setup.sh
#!/bin/bash
# Fix NixOS libstdc++ issue
export LD_PRELOAD=$(find /nix/store -name "libstdc++.so.6" 2>/dev/null | head -1)
exec "$@"
```

**Test fixtures:**
```python
# backend/tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hollowmedusa.storage.models import Base
from hollowmedusa.storage.database import get_db
from fastapi.testclient import TestClient
from hollowmedusa.api.main import app

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Test runs:**
```python
# backend/tests/test_api_runs.py
def test_create_run(client):
    resp = client.post("/api/v1/runs/", json={"graph_id": "default"})
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["status"] == "running"

def test_get_run_not_found(client):
    resp = client.get("/api/v1/runs/nonexistent")
    assert resp.status_code == 404

def test_get_run_trace(client, db_session):
    resp = client.post("/api/v1/runs/", json={})
    run_id = resp.json()["id"]
    resp = client.get(f"/api/v1/runs/{run_id}/trace")
    assert resp.status_code == 200
    assert "step_results" in resp.json()
```

**Verification:**
```bash
cd backend && bash tests/setup.sh pytest tests/ -v
# Should see: 6 passed
```

---

## 4.2 — Frontend Unit Tests

**Files:**
- `frontend/src/__tests__/GraphEditor.test.tsx`
- `frontend/src/__tests__/ModelConfig.test.tsx`
- `frontend/src/__tests__/PromptEditor.test.tsx`
- `frontend/src/__tests__/PipelineRunner.test.tsx`

**Setup:**
```bash
cd frontend
pnpm add -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Test example:**
```tsx
// frontend/src/__tests__/GraphEditor.test.tsx
import { render, screen } from '@testing-library/react'
import { GraphEditor } from '@/pages/GraphEditor'
import { describe, it, expect } from 'vitest'

describe('GraphEditor', () => {
  it('renders the canvas', () => {
    render(<GraphEditor />)
    expect(screen.getByTestId('react-flow')).toBeInTheDocument()
  })

  it('shows initial nodes', () => {
    render(<GraphEditor />)
    expect(screen.getByText('Requirements')).toBeInTheDocument()
    expect(screen.getByText('Architecture')).toBeInTheDocument()
  })
})
```

**Verification:**
```bash
cd frontend && pnpm test
# Should see: 4 passed
```

---

## 4.3 — E2E Tests

**Files:**
- `frontend/playwright.config.ts`
- `frontend/tests/e2e/graph-editor.spec.ts`
- `frontend/tests/e2e/pipeline-runner.spec.ts`
- `frontend/tests/e2e/model-config.spec.ts`

**Setup:**
```bash
cd frontend
pnpm add -D @playwright/test
npx playwright install
```

**Test example:**
```typescript
// frontend/tests/e2e/pipeline-runner.spec.ts
import { test, expect } from '@playwright/test'

test('start and monitor pipeline run', async ({ page }) => {
  await page.goto('/runner')
  await page.click('button:text("Start")')
  await expect(page.locator('.step-progress')).toBeVisible()
  await page.waitForSelector('.step-succeeded', { timeout: 30000 })
})

test('display run status', async ({ page }) => {
  await page.goto('/runner')
  await page.click('button:text("Start")')
  await page.waitForSelector('[data-testid="run-id"]')
  const runId = await page.locator('[data-testid="run-id"]').textContent()
  expect(runId).toBeTruthy()
})
```

**Verification:**
```bash
cd frontend && npx playwright test
# Should see: 3 passed
```

---

## 4.4 — PostgreSQL Support

**Files:**
- `backend/src/hollowmedusa/storage/postgres.py` — PostgreSQL engine
- `backend/.env.example` — Add POSTGRES_URL
- `docker-compose.yml` — PostgreSQL service

**PostgreSQL engine:**
```python
# backend/src/hollowmedusa/storage/postgres.py
from sqlalchemy.ext.asyncio import create_async_engine
import os

def create_postgres_engine():
    url = os.getenv("POSTGRES_URL", "postgresql+asyncpg://user:pass@localhost:5432/hollowmedusa")
    return create_async_engine(url, echo=False)
```

**Verification:**
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Test connection
python -c "
from hollowmedusa.storage.postgres import create_postgres_engine
engine = create_postgres_engine()
print('✅ PostgreSQL engine created')
"
```

---

## 4.5 — Prompt A/B Testing

**Files:**
- `backend/src/hollowmedusa/engine/ab_test.py` — A/B test runner
- `backend/src/hollowmedusa/api/routers/ab_test.py` — API endpoints
- `frontend/src/pages/AbTest.tsx` — A/B test UI

**A/B test runner:**
```python
# backend/src/hollowmedusa/engine/ab_test.py
class ABTestRunner:
    def __init__(self, agent_registry, model_registry, context_manager):
        self.agent_registry = agent_registry
        self.model_registry = model_registry
        self.context_manager = context_manager

    async def run_variant(self, variant_id: str, input_data: dict):
        """Run a single variant."""
        # TODO: Execute with specific variant config
        pass

    async def compare_variants(self, variant_a: str, variant_b: str, input_data: dict):
        """Run both variants and compare results."""
        result_a = await self.run_variant(variant_a, input_data)
        result_b = await self.run_variant(variant_b, input_data)
        return {"variant_a": result_a, "variant_b": result_b}
```

**Verification:**
```python
python -c "
from hollowmedusa.engine.ab_test import ABTestRunner
runner = ABTestRunner(agent_registry, model_registry, context_manager)
print('✅ A/B test runner created')
"
```

---

## 4.6 — CI/CD Trigger Endpoint

**Files:**
- `backend/src/hollowmedusa/api/routers/webhook.py` — Webhook handler
- `backend/src/hollowmedusa/engine/webhook_runner.py` — Webhook executor

**Webhook handler:**
```python
# backend/src/hollowmedusa/api/routers/webhook.py
from fastapi import APIRouter, Request, HTTPException
from ...engine.webhook_runner import WebhookRunner

router = APIRouter()

@router.post("/webhook/github")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event", "")

    if event == "push":
        # Trigger pipeline on push
        runner = WebhookRunner()
        run_id = await runner.trigger_pipeline(payload)
        return {"status": "triggered", "run_id": run_id}

    raise HTTPException(status_code=400, detail="Unsupported event")
```

**Verification:**
```bash
curl -X POST http://localhost:8000/api/v1/webhook/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"ref": "refs/heads/main"}'
```

---

## 4.7 — Docker Compose

**Files:**
- `docker-compose.yml` — Full stack
- `docker-compose.prod.yml` — Production with reverse proxy
- `Dockerfile.backend` — Backend image
- `Dockerfile.frontend` — Frontend image

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/hollowmedusa
    depends_on:
      - postgres

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=hollowmedusa
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Verification:**
```bash
docker-compose up -d
# Should see all services running
curl http://localhost:8000/health
```

---

## 4.8 — Documentation

**Files:**
- `README.md` — Updated with setup, architecture, API docs
- `docs/setup.md` — Detailed setup guide
- `docs/api.md` — API reference
- `docs/architecture.md` — Architecture deep dive

**README.md structure:**
```markdown
# HollowMedusa

A langgraph-based development pipeline with specialized agent combinations per step, managed through a web interface.

## Quick Start
...

## Architecture
...

## API Reference
...

## Development
...

## Testing
...

## Deployment
...
```

**Verification:**
```bash
cat README.md
# Should have all sections
```

---

## 4.9 — Performance Profiling

**Files:**
- `backend/src/hollowmedusa/utils/profiler.py` — Profiling utilities
- `backend/tests/test_performance.py` — Performance tests

**Profiler:**
```python
# backend/src/hollowmedusa/utils/profiler.py
import time
from functools import wraps

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__}: {end - start:.4f}s")
        return result
    return wrapper
```

**Verification:**
```python
python -c "
from hollowmedusa.utils.profiler import profile

@profile
def test_func():
    return sum(range(1000000))

test_func()
"
```

---

## 4.10 — Dark Mode

**Files:**
- `frontend/src/components/ThemeToggle.tsx` — Theme toggle button
- `frontend/src/lib/theme.ts` — Theme context
- `frontend/index.html` — Add dark mode class

**Theme toggle:**
```tsx
// frontend/src/components/ThemeToggle.tsx
import { useTheme } from '@/lib/theme'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button onClick={toggleTheme} className="p-2 rounded">
      {theme === 'light' ? '🌙' : '☀️'}
    </button>
  )
}
```

**Verification:**
```tsx
// Manual test
// Click toggle button
// Verify UI switches between light/dark
```

---

## Checklist

- [ ] `4.1` Integration tests (backend)
- [ ] `4.2` Frontend unit tests (Vitest + RTL)
- [ ] `4.3` E2E tests (Playwright)
- [ ] `4.4` PostgreSQL support
- [ ] `4.5` Prompt A/B testing
- [ ] `4.6` CI/CD trigger endpoint
- [ ] `4.7` Docker Compose
- [ ] `4.8` Documentation
- [ ] `4.9` Performance profiling
- [ ] `4.10` Dark mode

## Deliverable

Production-ready application with tests, docs, and deployment configs.

```bash
# Run all tests
make test

# Deploy
docker-compose up -d

# Access UI
open http://localhost:3000
```

## CI Update

Add to `.github/workflows/ci.yml`:
```yaml
- run: cd backend && bash tests/setup.sh pytest tests/ -v
- run: cd frontend && pnpm test
- run: cd frontend && npx playwright test
```
