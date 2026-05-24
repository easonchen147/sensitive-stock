---
title: Keep market data provenance visible when extending AKQuant backtests
date: 2026-05-24
category: docs/solutions/architecture-patterns
module: backend market data and backtesting
problem_type: architecture_pattern
component: service_object
severity: medium
applies_when:
  - extending A-share market-data providers without changing default semantics
  - adding third-party backtest controls while keeping API consumers stable
  - exposing degraded external-data behavior through OpenAPI and frontend reports
tags: [akshare, tickflow, akquant, market-data, backtesting, diagnostics]
---

# Keep market data provenance visible when extending AKQuant backtests

## Context

The project needed stronger A-share data resilience and richer AKQuant backtest
controls. The tempting approach was to make every new provider or runtime feature
look like a direct capability upgrade, but that hides two important facts:
external data sources fail independently, and backtest outputs are only useful
when the report shows the data and execution assumptions behind the result.

## Guidance

Keep AkShare as the default normalized A-share source, add optional providers
behind explicit ordering, and make provider provenance part of the backend
contract.

In this repo the durable pattern is:

- `backend/backtesting/data.py` owns shared OHLCV provider behavior, including
  `AkshareProvider`, optional `TickflowProvider`, optional Tushare, and Sina
  direct fallback.
- `backend/app/services/market_data.py` returns provider diagnostics such as
  `sourceOrder`, `lastSuccessSource`, `providerErrors`, `skippedProviders`, and
  `providerCapabilities`.
- `backend/app/services/backtests_akquant.py` keeps AKQuant integration behind
  `AKQuantBacktestService`, uses stable strategy identity `signal_replay`, and
  serializes `dataQuality`, `executionQuality`, `riskDiagnostics`, and
  `engineEvents` instead of mixing these concerns into performance metrics.
- `backend/app/openapi.py`, root `openapi.json`, `frontend/types/api.ts`, and
  `frontend/components/backtest-console.tsx` move together so the frontend only
  renders controls and diagnostics that the backend actually supports.

Provider order should be an explicit product choice, not an accidental import
order. The default is:

```text
akshare -> tickflow -> tushare -> sina_direct
```

When a user intentionally wants TickFlow first, require configuration:

```text
BACKEND_MARKET_DATA_PREFER_TICKFLOW=true
```

TickFlow realtime quote fallback should stay gated by `TICKFLOW_API_KEY` or a
test-injected client because the free path is useful for historical day K data,
not as a universal realtime source.

## Why This Matters

Research users need to know whether a backtest ran against the primary feed, a
fallback feed, cached degraded data, or a provider that changed because of local
configuration. Without that provenance, a stronger provider chain can produce
less trustworthy analysis because failures become invisible.

Keeping diagnostics in named response objects also protects existing consumers:
existing `metrics`, `comparison`, `series`, `trades`, and `insights` remain
stable while new execution realism and risk details become available to clients
that understand them.

## When to Apply

- A new market-data provider is added to the A-share research stack.
- Provider priority, credentials, or free-tier limits can change output
  semantics.
- A third-party financial runtime exposes richer cost, volume, or risk controls.
- Frontend work depends on OpenAPI-generated or manually mirrored API types.

## Examples

Pin the integration through contract-focused tests rather than provider internals:

```text
backend/tests/test_data_provider_priority.py
backend/tests/test_market_data_resilience.py
backend/tests/test_market_api.py
backend/tests/test_backtest_engine_upgrade.py
backend/tests/test_backtest_reporting_contract.py
backend/tests/test_backtests_api.py
backend/tests/test_openapi_publication.py
frontend/lib/backtests.test.ts
```

The minimum verification loop for this pattern is:

```powershell
cd backend
poetry check
poetry run pytest tests -q
poetry run ruff check .
uv run python scripts/generate_openapi.py

cd ..\frontend
npm test
npm run build

cd ..
openspec validate --all --strict
```

## Related

- `docs/solutions/tooling-decisions/akquant-backtest-runtime-adapter-2026-05-21.md`
- `docs/solutions/tooling-decisions/global-openapi-contract-for-flask-backend-2026-05-21.md`
- `openspec/specs/akshare-market-data-orchestration/spec.md`
- `openspec/specs/akquant-runtime-adapter/spec.md`
- `openspec/specs/backtest-execution-and-reporting/spec.md`
- `openspec/specs/backend-openapi-publication/spec.md`
- `openspec/specs/openapi-driven-frontend-client/spec.md`
