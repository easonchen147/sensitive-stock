# Harden Prediction Reliability And Explainability Plan

## Problem Frame

The system now aggregates multiple news sources and can call DeepSeek V4 Flash
for market predictions, but the prediction loop still needs stronger execution
quality before it is a dependable research workflow. The current adapter asks
for JSON output, yet the prompt does not provide a concrete schema example; the
response metadata does not expose enough operational details; repeated identical
requests can call the model repeatedly; and the frontend does not surface source
quality or prediction evidence clearly enough for research review.

## Scope

This plan covers the market-news prediction pipeline only: DeepSeek request
contract hardening, prediction result caching, source-quality and dedupe
explainability, OpenAPI/type updates, market workbench display updates, and
targeted tests. It does not add persistent storage, scheduled ingestion, model
fine-tuning, user portfolios, alerts, or trading actions.

## Requirements Traceability

- DeepSeek V4 Flash: preserve `deepseek-v4-flash` as the default model and use
  the OpenAI-compatible `/chat/completions` endpoint.
- JSON output: include `response_format: {"type": "json_object"}` and a strict
  prompt-level JSON example so the provider has an explicit output contract.
- Reliability: cache successful prediction payloads for repeated equivalent
  news/symbol contexts and return bounded metadata instead of duplicate remote
  calls.
- Explainability: attach source-quality metadata, dedupe counts, evidence
  coverage, and prompt/schema version to prediction responses.
- Frontend: render source-quality, cache/model state, schema version, and
  prediction evidence without treating degraded output as fully successful.
- Workflow: use OpenSpec plus Compound; no git stage or commit during this work.

## Key Decisions

1. Add reliability metadata to the existing prediction endpoint rather than a
   second endpoint.
   The current `/api/v1/market/news/predictions` response already aggregates the
   needed context, so a new route would increase frontend and OpenAPI surface
   without adding a new behavior boundary.

2. Cache at the prediction-adapter layer with a deterministic context hash.
   The cache key should be derived from normalized news item IDs/content,
   keywords, sector hints, symbols, model, and prompt schema version. This avoids
   leaking HTTP or Flask request details into business code.

3. Treat cache hits as non-degraded when they come from a prior successful
   DeepSeek prediction, but make `predictionMetadata.cached` and `cacheKey`
   explicit.
   Cache is an operational optimization, not a fallback failure path.

4. Keep heuristic fallback deterministic and transparent.
   If DeepSeek is unavailable, the system still returns local predictions, but
   metadata must show `provider: local_heuristic`, `degraded: true`, warning
   details, and the same prompt/schema version for consistent client handling.

5. Add source-quality summaries in the news aggregation layer.
   Prediction confidence should be inspectable against channel count, failed
   channel count, duplicate count, and source coverage.

## Implementation Units

### U1: OpenSpec Change Source

Files:
- `openspec/changes/harden-prediction-reliability-and-explainability/proposal.md`
- `openspec/changes/harden-prediction-reliability-and-explainability/design.md`
- `openspec/changes/harden-prediction-reliability-and-explainability/specs/**/spec.md`
- `openspec/changes/harden-prediction-reliability-and-explainability/tasks.md`

Approach:
- Define requirement deltas for the existing intelligence, OpenAPI, and
  frontend-client specs before implementation.

Verification:
- `openspec validate harden-prediction-reliability-and-explainability --strict`

### U2: DeepSeek JSON Contract And Prediction Cache

Files:
- `backend/app/services/deepseek_prediction.py`
- `backend/app/config.py`
- `backend/.env.example`
- `backend/tests/test_deepseek_prediction_service.py`

Approach:
- Add a prompt/schema version constant and explicit JSON example in the system
  prompt.
- Add a TTL cache for successful remote prediction payloads keyed by normalized
  context hash, model, and prompt/schema version.
- Publish metadata fields: `schemaVersion`, `cached`, `cacheKey`,
  `inputDigest`, `newsItemCount`, `keywordCount`, `sectorHintCount`,
  `symbolCount`, and `latencyMs` when a remote call is attempted.

Test Scenarios:
- DeepSeek request includes JSON output mode and prompt schema example.
- Two identical successful DeepSeek requests use the cached result on the second
  call without a second HTTP request.
- Changing requested symbols changes the cache key.
- No-key and malformed-output fallbacks include the same schema version and
  input summary metadata.

Verification:
- `cd backend; uv run pytest tests/test_deepseek_prediction_service.py -q`

### U3: Source Quality And Dedupe Explainability

Files:
- `backend/app/services/news_intelligence.py`
- `backend/tests/test_multisource_news_service.py`
- `backend/tests/test_news_intelligence_service.py`

Approach:
- Return `sourceQuality` with queried, succeeded, degraded, failed, item,
  duplicate, unique, and source-coverage counts.
- Return `dedupeMetadata` explaining duplicates removed and dedupe strategy.
- Include the same metadata in prediction responses so model output can be read
  alongside source reliability.

Test Scenarios:
- Overlapping multi-source stories report a positive duplicate count.
- Failed channels are reflected in `sourceQuality.failedChannels` and warnings.
- Prediction responses preserve `sourceQuality` and `dedupeMetadata`.

Verification:
- `cd backend; uv run pytest tests/test_multisource_news_service.py tests/test_news_intelligence_service.py -q`

### U4: OpenAPI And Frontend Types

Files:
- `backend/app/openapi.py`
- `backend/tests/test_openapi_publication.py`
- `openapi.json`
- `frontend/types/api.ts`
- `frontend/lib/openapi-client.test.ts`

Approach:
- Add schema components for `sourceQuality`, `dedupeMetadata`, and enriched
  `predictionMetadata`.
- Regenerate `openapi.json`.
- Update TypeScript API types and keep frontend OpenAPI binding tests aligned.

Test Scenarios:
- OpenAPI publishes the new metadata fields.
- Frontend contract tests still pass against regenerated OpenAPI.

Verification:
- `cd backend; uv run pytest tests/test_openapi_publication.py -q`
- `cd backend; uv run python scripts/generate_openapi.py --output ..\openapi.json`
- `cd frontend; npm test`

### U5: Market Workbench Explainability Display

Files:
- `frontend/components/market-workbench.tsx`
- `frontend/types/api.ts`

Approach:
- Render prediction cache/model state, schema version, source quality, duplicate
  count, and prediction evidence/source IDs.
- Keep degraded state visually distinct from successful remote model output.

Test Scenarios:
- Frontend typecheck/build succeeds with enriched prediction metadata.
- Smoke path still loads the market workbench after login.

Verification:
- `cd frontend; npm run build`
- `cd frontend; npm run test:smoke`

### U6: Final Verification, Archive, And Learning

Files:
- `openspec/specs/**/spec.md`
- `openspec/changes/archive/**`
- `docs/solutions/**`

Approach:
- Run targeted and whole-project verification.
- Archive the completed OpenSpec change after specs are synced.
- Record a Compound learning for prediction reliability and explainability.

Verification:
- `cd backend; uv run pytest -q`
- `cd backend; uv run ruff check app tests scripts`
- `cd frontend; npm test`
- `cd frontend; npm run build`
- `openspec validate --all --strict`
- `git diff --check`

## Risks And Mitigations

- DeepSeek model names and capabilities can drift. The default remains
  configurable by environment, and tests assert the configured value rather than
  hard-coding business behavior around one provider.
- Prediction caching can hide model changes. The key includes model and schema
  version, and cache metadata is explicit in responses.
- Additional metadata can bloat frontend cards. The UI should show compact
  summary metrics first and keep evidence lists short.
- Source-quality counts are runtime diagnostics, not truth guarantees. Risk
  notes must still remind users to validate with AKQuant and broader data.

## Verification Strategy

Use targeted backend tests for the prediction adapter first, then aggregation
metadata tests, OpenAPI generation/tests, frontend unit/build/smoke checks, and
final strict OpenSpec validation. Do not stage or commit as part of this work.
