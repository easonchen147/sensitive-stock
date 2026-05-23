# Phase One Architecture Migration

The current architecture is a frontend/backend split rather than the old
Streamlit-style single process.

## Current Runtime

- Frontend: `frontend/` with Next.js App Router.
- Backend: `backend/` with Flask app factory at `backend/app/__init__.py`.
- Backend WSGI entrypoint: `backend/wsgi.py`.
- OpenSpec: `openspec/`.

## Backend Contract Boundary

The backend now publishes a global OpenAPI 3.1 contract:

- Runtime discovery: `GET /api/v1/openapi.json`
- Static artifact: `openapi.json`
- Generator:

```bash
cd backend
uv run python scripts/generate_openapi.py
```

The contract covers auth, capabilities, market data, AKQuant-backed backtests,
prediction-loop APIs, and the current screener, diagnosis, factors, and
portfolio capability endpoints.

The research capability families now have formal API routes:

- `POST /api/v1/screener/run`
- `POST /api/v1/diagnosis/run`
- `POST /api/v1/factors/analyze`
- `POST /api/v1/portfolio/optimize`

## Frontend Contract And Design Boundary

The frontend has been upgraded into a unified research workbench surface. The
active design direction is Quiet Capital
Terminal: dense, low-noise, status-forward layouts suited for A-share research
instead of marketing-style hero pages.

Frontend API consumption is now governed by `frontend/lib/openapi-client.ts`.
That binding table maps frontend route keys to the generated `openapi.json`,
and the Vitest suite verifies that major workbench endpoints stay covered.

## Backtesting Runtime

Backtests execute through `backend/app/services/backtests_akquant.py`, which
adapts the application request/response contract to the AKQuant runtime.
`backend/backtesting/*` remains a compatibility support area rather than the
main execution engine.

## Development Rule

New backend capability code should be added under `backend/app/api`,
`backend/app/schemas`, and `backend/app/services`, then surfaced through the
OpenAPI emitter before frontend integration.
