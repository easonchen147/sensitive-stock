## Why

The market-news prediction endpoint now exists, but it needs stronger reliability
and explainability before it can be treated as a dependable research surface.
DeepSeek JSON output should be governed by an explicit schema prompt, repeated
equivalent requests should avoid unnecessary remote calls, and users need to see
source quality and evidence behind the prediction payload.

## What Changes

- Harden the DeepSeek V4 Flash adapter with an explicit JSON output contract,
  prompt/schema versioning, and richer prediction metadata.
- Add prediction-result TTL caching keyed by normalized input digest, model, and
  schema version.
- Add source-quality and dedupe metadata to multi-source news and prediction
  responses.
- Publish the new metadata through OpenAPI and frontend TypeScript types.
- Render prediction cache/model state, source quality, dedupe count, and evidence
  in the market workbench.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `jin10-news-intelligence-pipeline`: prediction and multi-source news responses
  gain reliability metadata, source-quality summaries, dedupe explainability,
  and an explicit DeepSeek JSON output contract.
- `backend-openapi-publication`: OpenAPI publishes enriched prediction,
  source-quality, and dedupe metadata fields.
- `openapi-driven-frontend-client`: frontend types and market workbench display
  the enriched prediction explainability fields.

## Impact

- Backend services: `backend/app/services/deepseek_prediction.py`,
  `backend/app/services/news_intelligence.py`, `backend/app/config.py`.
- Backend contract: `backend/app/openapi.py`, `openapi.json`, market API tests.
- Frontend: `frontend/types/api.ts`, `frontend/components/market-workbench.tsx`,
  frontend OpenAPI/client verification.
- No database migration, no persistent cache, and no trading/order behavior.
