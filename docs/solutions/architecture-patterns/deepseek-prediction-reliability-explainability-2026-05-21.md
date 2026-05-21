---
title: DeepSeek prediction reliability and explainability contract
date: 2026-05-21
category: architecture-patterns
module: sensitive-stock market intelligence
problem_type: architecture_pattern
component: service_object
severity: medium
applies_when:
  - "LLM predictions are part of a research workflow but must not become a hard dependency"
  - "Repeated equivalent prediction requests can waste remote model calls"
  - "Prediction consumers need source-quality and evidence metadata"
related_components:
  - backend/app/services/deepseek_prediction.py
  - backend/app/services/news_intelligence.py
  - frontend/components/market-workbench.tsx
tags: [deepseek, prediction-cache, explainability, openapi, openspec]
---

# DeepSeek prediction reliability and explainability contract

## Context

The first prediction loop established multi-source news aggregation, DeepSeek V4
Flash prediction, heuristic fallback, and AKQuant backtest handoff. The next
gap was trustworthiness: clients could see a prediction, but not enough about
the model contract, input digest, cache state, source quality, or duplicate
pressure behind that prediction.

## Guidance

Treat LLM prediction as a versioned research contract, not a raw model call.

- Keep the business endpoint stable: `/api/v1/market/news/predictions`.
- Add `predictionMetadata.schemaVersion` and include it in the prompt, cache key,
  OpenAPI schema, and frontend type.
- Use DeepSeek JSON Output with `response_format: {"type": "json_object"}` and
  put a concrete JSON example in the system prompt.
- Cache only successful remote model payloads. Do not cache heuristic fallbacks;
  they are cheap and should preserve fresh warning metadata.
- Include `cached`, `cacheKey`, `inputDigest`, `newsItemCount`, `keywordCount`,
  `sectorHintCount`, and `symbolCount` in `predictionMetadata`.
- Add `sourceQuality` and `dedupeMetadata` at the news aggregation layer, then
  preserve those fields through intelligence and prediction responses.
- Render model/cache/source/evidence metadata in the market workbench so users
  can inspect prediction quality before using the AKQuant handoff.

## Why This Matters

Prediction systems fail quietly when the provider output contract, input
context, and source reliability are hidden. A versioned metadata contract makes
failures reviewable and testable:

- prompt/schema changes invalidate old cache keys by design;
- repeated equivalent requests avoid duplicate remote calls;
- degraded heuristic predictions remain visible as degraded;
- source failures and duplicate news are not mistaken for high-confidence
  model insight;
- OpenAPI and frontend tests catch contract drift.

## When to Apply

- Use this pattern for optional LLM enrichment in research or analytics flows.
- Use it when an endpoint can continue with deterministic local fallback.
- Use it when frontend users need to understand why a prediction was produced.
- Avoid it for workflows that require durable audit logs; those need persistent
  storage rather than in-memory TTL caching.

## Examples

The prediction metadata should stay compact but diagnostic:

```json
{
  "predictionMetadata": {
    "provider": "deepseek",
    "model": "deepseek-v4-flash",
    "degraded": false,
    "cached": true,
    "schemaVersion": "market-prediction-json-v1",
    "cacheKey": "a1b2c3d4e5f6a7b8",
    "inputDigest": "f1e2d3c4b5a69788",
    "newsItemCount": 30,
    "keywordCount": 20,
    "sectorHintCount": 8,
    "symbolCount": 3
  }
}
```

The news aggregation metadata should explain source quality:

```json
{
  "sourceQuality": {
    "queriedChannels": 3,
    "succeededChannels": 2,
    "degradedChannels": 0,
    "failedChannels": 1,
    "totalItems": 42,
    "uniqueItems": 36,
    "duplicateItems": 6,
    "sourceCoverage": ["eastmoney_stock_news", "jin10"]
  },
  "dedupeMetadata": {
    "strategy": "source-url-or-normalized-title-content",
    "originalCount": 42,
    "uniqueCount": 36,
    "duplicateCount": 6
  }
}
```

## Related

- `docs/solutions/architecture-patterns/multi-source-news-deepseek-prediction-loop-2026-05-21.md`
- `docs/solutions/architecture-patterns/harden-nextjs-openapi-smoke-and-degraded-cache-2026-05-21.md`
- `openspec/changes/archive/2026-05-21-harden-prediction-reliability-and-explainability/`
