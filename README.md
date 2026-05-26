# StockML Local Web App

StockML is now a two-app local product:

- `FastAPI` is the real backend API.
- `Next.js` is the real web frontend.
- The older Flask app is legacy code and is not part of the default run path.

The local experience is:

1. start the FastAPI backend
2. start the Next.js frontend
3. open the website in a browser
4. submit a stock ticker
5. review metrics, predictions, and charts

## Architecture

### Backend

- `src/stockml/`
  Core settings, logging, ML pipeline, services, and schemas.
- `app/api/`
  FastAPI router composition and HTTP endpoints.
- `tests/`
  Backend unit and integration tests.

### Frontend

- `frontend/src/app/`
  Next.js App Router entrypoints and global styles.
- `frontend/src/components/`
  UI, forms, charts, and dashboard components.
- `frontend/src/hooks/`
  React Query integration.
- `frontend/src/stores/`
  Zustand form state.

## Prediction Flow

The website submits `POST /api/v1/predictions/` with:

- `symbol`
- optional `start_date`
- optional `end_date`

The backend response includes:

- normalized stock window metadata
- engineered feature columns
- model metrics
- historical price points
- validation predictions
- anomaly-day context with same-day news when enabled
- response metadata

Identical prediction requests are cached in-memory for the running FastAPI process so repeat local requests do not retrain unnecessarily during the same session.

## Prerequisites

- Python `3.12+`
- Node.js `20+`
- npm

Python `3.14.5` and Node `26.0.0` were used during local verification in this workspace.

## Installation

### Option A: Use the Makefile

```bash
make backend-install
make frontend-install
```

### Option B: Run commands manually

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
cd frontend && npm install --cache .npm-cache
```

## Environment Setup

Backend defaults are already safe for local development, but you can create env files if you want explicit configuration:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Important local defaults:

- backend API: `http://127.0.0.1:8000`
- frontend app: `http://localhost:3000`
- backend docs: `http://127.0.0.1:8000/docs`

The frontend defaults to `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`, so `frontend/.env.local` is optional unless you want to change the backend origin.

To enable anomaly-day news context, add your Tavily key to the backend `.env`:

```bash
STOCKML_NEWS__TAVILY_API_KEY=your_tavily_key_here
```

Then restart the backend server.

## Run Locally

Open two terminals from the project root.

### Terminal 1: backend

```bash
make backend-dev
```

Manual equivalent:

```bash
.venv/bin/uvicorn stockml.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app --reload-dir src --reload-include '*.py'
```

Expected output:

- Uvicorn startup logs
- `Application startup complete`
- backend available on port `8000`
- reloads only when Python files under `app/` or `src/` change

### Terminal 2: frontend

```bash
make frontend-dev
```

Manual equivalent:

```bash
cd frontend && npm run dev
```

Expected output:

- Next.js dev server startup logs
- local frontend URL on port `3000`

If your machine reports `EMFILE` watch errors while running `next dev`, use the built frontend server instead:

```bash
make frontend-build
make frontend-start
```

### Open the app

Visit:

- `http://localhost:3000`

Try a ticker such as:

- `AAPL`
- `MSFT`
- `NVDA`
- `^GSPC`

If Tavily is configured, large validation misses can now render same-day news context directly in the results UI.

## Test Commands

### Backend

Run the full backend suite:

```bash
make backend-test
```

Or:

```bash
.venv/bin/python -m pytest
```

### Frontend

Run the frontend smoke test:

```bash
make frontend-test
```

Or:

```bash
cd frontend && npm run test
```

Run the production build check:

```bash
make frontend-build
```

Or:

```bash
cd frontend && npm run build
```

## Verified Commands

These commands were run successfully in this workspace:

- `.venv/bin/python -m pytest tests/integration/test_predictions.py -q`
- `.venv/bin/python -m pytest tests/integration/test_health.py -q`
- `cd frontend && npm run test`
- `cd frontend && npm run build`

## Common Failure Points

### `pytest` not found

You are probably not using the project virtual environment yet. Install backend dependencies first and run tests with `.venv/bin/python -m pytest`.

### `npm install` cache permission errors

Use the workspace-local cache:

```bash
cd frontend && npm install --cache .npm-cache
```

### Frontend cannot reach the backend

Check that:

- the backend is running on `127.0.0.1:8000`
- `NEXT_PUBLIC_API_BASE_URL` points to the same origin
- you are opening the frontend from `localhost:3000` or `127.0.0.1:3000`

### Next.js dev server shows `EMFILE`

This machine hit file watcher limits while running `npm run dev`. The app still started, but if you want a quieter path use:

```bash
make frontend-build
make frontend-start
```

### Prediction request returns validation or training errors

Possible causes:

- invalid ticker symbol
- date window too small for rolling features
- no market data returned by `yfinance`
- Yahoo Finance timed out before returning the requested daily history

If needed, retry with a larger date range or omit custom dates.

### Anomaly news does not appear

Check that:

- `STOCKML_NEWS__TAVILY_API_KEY` is present in the root `.env`
- you restarted `make backend-dev` after adding it
- the run actually produced anomaly days in the selected validation window
- Tavily was reachable from your machine when the request was made

## Why This Architecture Is Correct

- The backend API is the single source of truth for prediction logic.
- Endpoint handlers stay thin by delegating to typed services.
- The frontend consumes one clean response contract instead of rebuilding backend logic.
- React Query manages async request state cleanly.
- Zustand is limited to local UI form state, which keeps concerns separated.
- The existing ML pipeline is reused without a disruptive redesign.
- FastAPI and Next.js can now run independently, which is the right foundation for future scaling.
