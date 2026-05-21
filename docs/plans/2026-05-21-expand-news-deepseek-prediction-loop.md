# Expand News DeepSeek Prediction Loop Plan

## Problem Frame

The market workbench already ingests Jin10 news, derives rule-based keywords and
sector hints, and exposes AKQuant-backed backtests. The next optimization is to
turn that into a fuller prediction loop: collect more than one news channel,
normalize and deduplicate the feed, run a DeepSeek V4 Flash prediction pass when
configured, and hand predicted themes back into the research/backtest workflow.

## Scope

This plan covers backend ingestion, prediction, OpenAPI contract updates,
frontend binding/display updates, and a small backtest preset improvement that
helps validate event-driven predictions. It does not introduce persistent
storage, scheduled jobs, user portfolio state, or automated trading.

## Requirements Traceability

- Multi-source news: preserve the current Jin10 realtime path, then add more
  channel fetchers with per-channel status and warnings.
- Prediction: use the current DeepSeek OpenAI-compatible chat endpoint with
  `deepseek-v4-flash` as the default configured model.
- Degraded operation: run without a DeepSeek key by returning a transparent
  local heuristic prediction rather than pretending an LLM was called.
- Backtest loop: expose prediction-aware handoff metadata and add a preset that
  can validate event/theme momentum after prediction.
- Workflow: use OpenSpec plus Compound, no git stage or commit during the work.

## Key Decisions

1. Keep `Jin10NewsService` focused on Jin10 and add a multi-source aggregation
   layer around it.
   This avoids destabilizing the existing Jin10 pagination and cache behavior.

2. Treat DeepSeek as an optional provider behind a small service adapter.
   `BACKEND_DEEPSEEK_API_KEY` enables remote prediction. Without it, the backend
   returns heuristic predictions with `degraded: true` and warning metadata.

3. Add one new prediction endpoint instead of overloading every existing market
   endpoint.
   `GET /api/v1/market/news/predictions` can return items, channel metadata,
   keywords, sector hints, predictions, and a backtest handoff in one payload.

4. Make OpenAPI and frontend binding tests the guardrail for the new endpoint.
   The frontend must add the route binding and type surface at the same time the
   backend publishes the path.

## Implementation Units

### U1: OpenSpec Change Source

Files:
- `openspec/changes/expand-news-deepseek-prediction-loop/proposal.md`
- `openspec/changes/expand-news-deepseek-prediction-loop/design.md`
- `openspec/changes/expand-news-deepseek-prediction-loop/specs/**/spec.md`
- `openspec/changes/expand-news-deepseek-prediction-loop/tasks.md`

Approach:
- Capture multi-source news, DeepSeek prediction, OpenAPI, frontend, and
  backtest-loop requirements before implementation.

Verification:
- `openspec validate expand-news-deepseek-prediction-loop --strict`

### U2: Multi-Source News Aggregation

Files:
- `backend/app/services/news_intelligence.py`
- `backend/app/api/market.py`
- `backend/app/config.py`
- `backend/tests/test_news_intelligence_service.py`
- `backend/tests/test_news_cache_resilience.py`

Approach:
- Keep Jin10 as the primary source.
- Add extra fetchers for Eastmoney and Sina-style market news feeds.
- Deduplicate normalized items across channels.
- Return channel status, source count, warnings, and cache-backed degraded
  metadata.

Test Scenarios:
- Jin10, Eastmoney, and Sina items are merged and deduplicated.
- One failed channel does not fail the whole response.
- A fully failed refresh can reuse a still-valid cached aggregate.

Verification:
- `cd backend; uv run pytest tests/test_news_intelligence_service.py tests/test_news_cache_resilience.py -q`

### U3: DeepSeek V4 Flash Prediction Adapter

Files:
- `backend/app/services/deepseek_prediction.py`
- `backend/app/services/news_intelligence.py`
- `backend/app/config.py`
- `backend/.env.example`
- `backend/tests/test_deepseek_prediction_service.py`

Approach:
- Add a small OpenAI-compatible chat completion adapter using
  `BACKEND_DEEPSEEK_BASE_URL`, `BACKEND_DEEPSEEK_MODEL`, and
  `BACKEND_DEEPSEEK_API_KEY`.
- Default the model to `deepseek-v4-flash`.
- Parse JSON predictions defensively.
- Fall back to deterministic local predictions when no key exists or the remote
  call fails.

Test Scenarios:
- With no API key, prediction returns heuristic degraded metadata.
- With a fake DeepSeek response, prediction parses structured JSON.
- Malformed or failing DeepSeek responses fall back with warnings.

Verification:
- `cd backend; uv run pytest tests/test_deepseek_prediction_service.py -q`

### U4: Prediction API And OpenAPI Contract

Files:
- `backend/app/schemas/market.py`
- `backend/app/api/market.py`
- `backend/app/openapi.py`
- `backend/tests/test_market_api.py`
- `backend/tests/test_openapi_publication.py`
- `openapi.json`

Approach:
- Add `GET /api/v1/market/news/predictions`.
- Reuse `MarketNewsQuery` with optional `symbols`.
- Publish prediction schemas and update static `openapi.json`.

Test Scenarios:
- The endpoint returns predictions, channel metadata, and backtest handoff.
- OpenAPI includes the new path and schema components.
- Protected-route security stays aligned with the rest of market APIs.

Verification:
- `cd backend; uv run pytest tests/test_market_api.py tests/test_openapi_publication.py -q`
- `cd backend; uv run python scripts/generate_openapi.py --output ..\openapi.json`

### U5: Frontend Prediction Binding And Display

Files:
- `frontend/lib/openapi-client.ts`
- `frontend/lib/openapi-client.test.ts`
- `frontend/lib/api.ts`
- `frontend/types/api.ts`
- `frontend/components/market-workbench.tsx`

Approach:
- Add the prediction route binding and typed client helper.
- Show prediction provider/degraded state, predicted themes, confidence, drivers,
  and the backtest handoff preset in the market workbench.

Test Scenarios:
- OpenAPI binding test covers the new endpoint.
- Market workbench can render empty, degraded, and populated prediction payloads.

Verification:
- `cd frontend; npm test`

### U6: Backtest Prediction Validation Preset

Files:
- `backend/backtesting/presets.py`
- `backend/tests/test_backtest_reporting_contract.py`

Approach:
- Add an event/theme momentum preset designed to validate predicted sectors or
  symbols after news-driven signals.
- Keep the preset implemented through the existing AKQuant signal replay
  adapter.

Test Scenarios:
- Preset catalog exposes the new preset and metadata.
- The preset includes grouped parameter schema suitable for frontend rendering.

Verification:
- `cd backend; uv run pytest tests/test_backtest_reporting_contract.py -q`

### U7: Final Verification, Archive, And Learning

Files:
- `openspec/specs/**/spec.md`
- `openspec/changes/archive/**`
- `docs/solutions/**`

Approach:
- Run backend and frontend targeted checks, strict OpenSpec validation, archive
  the completed change, then capture the reusable pattern using
  `ce-compound mode:headless`.

Verification:
- `cd backend; uv run pytest -q`
- `cd backend; uv run ruff check app tests scripts`
- `cd frontend; npm test`
- `openspec validate --all --strict`
- `git diff --check`

## Risks And Mitigations

- External news endpoints may change shape. Fetchers must fail closed per
  channel and report warnings without breaking the aggregate.
- DeepSeek credentials may be unavailable in local development. Prediction
  metadata must state whether the provider is `deepseek` or `local_heuristic`.
- LLM output may be malformed. JSON parsing must be defensive and fall back to
  deterministic predictions.
- Predictions are research context, not investment advice. The response should
  include risk notes and a backtest handoff rather than trading actions.

## Verification Strategy

Use test-first implementation for the new services and endpoint, regenerate the
OpenAPI document after backend changes, then run frontend contract tests and a
final whole-repo validation sweep. Do not stage or commit as part of this work.
