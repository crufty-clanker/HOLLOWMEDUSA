.PHONY: dev-backend dev-frontend lint typecheck test setup

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
