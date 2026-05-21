---
module: backend/frontend market intelligence
date: 2026-05-21
problem_type: architecture_pattern
component: service_object
severity: medium
applies_when:
  - "market news comes from multiple unreliable external feeds"
  - "LLM predictions should enrich research without becoming a hard dependency"
  - "prediction output needs a backtest handoff rather than trading actions"
tags: [market-intelligence, deepseek, openapi, backtesting, degraded-mode]
---

# Multi-source news plus DeepSeek prediction loop

## Context

The market workbench started with Jin10 ingestion, rule-based keywords, sector
hints, and AKQuant-backed backtests. That was a useful foundation, but it left
three gaps: one primary news channel could dominate the view, prediction was not
available through a formal contract, and news-driven predictions were not tied
back to validation through backtests.

## Guidance

Keep the prediction loop layered:

- `Jin10NewsService` stays focused on Jin10 pagination, normalization, fallback,
  and cache behavior.
- `MultiSourceNewsService` wraps Jin10 plus additional channel fetchers,
  deduplicates normalized items, and returns per-channel status.
- `DeepSeekMarketPredictionService` owns model calls and local heuristic
  fallback. It defaults to `deepseek-v4-flash`, uses the OpenAI-compatible
  `/chat/completions` shape, and never lets model failure break the market page.
- `MarketNewsIntelligenceService` orchestrates latest news, keywords, sector
  hints, predictions, and `backtestHandoff`.
- OpenAPI and frontend binding tests must be updated in the same change as the
  endpoint, because prediction output is consumed directly by the Next.js
  workbench.

The important product boundary is that predictions are research hints. The API
returns `riskNotes` and a backtest handoff to `event_theme_momentum`; it does not
return trading instructions.

## Why This Matters

External news feeds and LLM APIs fail independently. If either is treated as a
single hard dependency, the market page becomes brittle or misleading. The
stable pattern is to surface provenance and degradation explicitly:

- channel failures appear in `channels` and `warnings`;
- missing or failing DeepSeek credentials produce `provider: local_heuristic`;
- remote model success is identified by `provider: deepseek` and the configured
  model;
- candidate themes can be validated by AKQuant instead of being accepted as
  model truth.

## When to Apply

- The product needs market/news intelligence from multiple upstream feeds.
- A model provider enriches analysis but should not block core workflows.
- The frontend depends on generated or static OpenAPI route coverage.
- Prediction output should feed research validation, not automated execution.

## Examples

The backend route should remain one combined research contract:

```text
GET /api/v1/market/news/predictions?limit=60&symbols=000001,600000
```

The response should include both prediction and validation handoff:

```json
{
  "predictionMetadata": {
    "provider": "deepseek",
    "model": "deepseek-v4-flash",
    "degraded": false,
    "warnings": []
  },
  "predictions": [
    {
      "targetType": "sector",
      "target": "AI infrastructure",
      "direction": "bullish",
      "confidence": 0.73,
      "drivers": ["AI", "cooling"]
    }
  ],
  "backtestHandoff": {
    "endpoint": "/api/v1/backtests/run",
    "suggestedPreset": "event_theme_momentum"
  }
}
```

## Related

- `backend/app/services/news_intelligence.py`
- `backend/app/services/deepseek_prediction.py`
- `backend/backtesting/presets.py`
- `backend/app/openapi.py`
- `frontend/components/market-workbench.tsx`
- `openspec/specs/jin10-news-intelligence-pipeline/spec.md`
- `openspec/specs/backend-openapi-publication/spec.md`
- `openspec/specs/openapi-driven-frontend-client/spec.md`
