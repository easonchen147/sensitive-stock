## Why

The current system already uses AkShare and AKQuant, but it still underuses AKQuant's latest execution controls and relies on a narrow market-data fallback surface. This change strengthens the research loop by adding TickFlow-backed market data resilience, upgrading AkShare, and exposing richer backtest diagnostics from AKQuant through backend APIs and the frontend workbench.

## What Changes

- Upgrade the backend AkShare dependency to the latest confirmed version and add TickFlow as an optional market-data dependency.
- Add a TickFlow historical OHLCV provider to the shared market-data contract, with explicit source order and degraded diagnostics.
- Add optional TickFlow quote fallback when a TickFlow API key is configured.
- Extend the structured backtest request contract with AKQuant-supported execution, fee, and risk controls.
- Pass supported advanced controls into AKQuant and collect runtime event summaries.
- Add data-quality, execution-quality, risk-diagnostic, and engine-event sections to each backtest result.
- Update OpenAPI, frontend types, the回测页面 payload, and the回测报告 UI so the new contract is visible and callable.
- Document which `daily_stock_analysis` ideas are adopted now and which require separate future changes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `akshare-market-data-orchestration`: add TickFlow historical/quote fallback behavior, source diagnostics, and AkShare version update expectations.
- `akquant-runtime-adapter`: expose additional AKQuant runtime parameters, strategy-level risk controls, and stream event summary collection.
- `backtest-execution-and-reporting`: extend request and response contracts with advanced execution, fee, risk, data-quality, execution-quality, and risk-diagnostic sections.
- `backend-openapi-publication`: publish the expanded backtest request and response diagnostic fields in the global OpenAPI document.
- `openapi-driven-frontend-client`: require the frontend payload builder, TypeScript types, and回测页面 to use the expanded OpenAPI-backed contract.

## Impact

- Backend dependencies: `backend/pyproject.toml`, `backend/poetry.lock`, `backend/uv.lock`.
- Backend configuration: TickFlow-related environment variables in `backend/app/config.py` and `backend/.env.example`.
- Backend runtime code: `backend/backtesting/data.py`, `backend/app/services/market_data.py`, `backend/app/schemas/backtests.py`, `backend/app/services/backtests_akquant.py`, `backend/app/openapi.py`.
- Frontend runtime code: `frontend/types/api.ts`, `frontend/lib/backtests.ts`, `frontend/components/backtest-console.tsx`.
- Static API contract: `openapi.json`.
- Tests: backend provider, market API, backtest API/reporting/OpenAPI tests, and frontend backtest payload tests.
- Documentation: `README.md`, `backend/README.md`, and a durable solution note.
