PYTHON := .venv/bin/python
PIP := .venv/bin/pip
UVICORN := .venv/bin/uvicorn

.PHONY: backend-install frontend-install backend-dev frontend-dev frontend-start backend-test frontend-test frontend-build

backend-install:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

frontend-install:
	cd frontend && npm install --cache .npm-cache

backend-dev:
	$(UVICORN) stockml.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app --reload-dir src --reload-include '*.py'

frontend-dev:
	cd frontend && npm run dev

frontend-start:
	cd frontend && npm run start

backend-test:
	$(PYTHON) -m pytest

frontend-test:
	cd frontend && npm run test

frontend-build:
	cd frontend && npm run build
