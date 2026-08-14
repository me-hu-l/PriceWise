.PHONY: backend-install backend-dev migrate seed frontend-install frontend-dev test

backend-install:
	cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt

backend-dev:
	cd backend && .venv/Scripts/uvicorn app.main:app --reload --port 8000

migrate:
	cd backend && .venv/Scripts/alembic upgrade head

seed:
	cd backend && .venv/Scripts/python -m app.seed.seed_database

test:
	cd backend && .venv/Scripts/pytest

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev
