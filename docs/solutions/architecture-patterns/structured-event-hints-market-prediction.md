---
title: Structured event hints for market prediction
date: 2026-05-24
category: architecture-patterns
module: sensitive-stock market intelligence
problem_type: architecture_pattern
component: service_object
severity: medium
applies_when:
  - "news and disclosures are already ingested but prediction still treats them as plain text"
  - "official announcements should influence prediction and backtest handoff"
  - "frontend should display only backend-supported market intelligence"
related_components:
  - backend/app/services/news_intelligence.py
  - backend/app/services/deepseek_prediction.py
  - backend/app/services/prediction_history.py
  - frontend/components/market-workbench.tsx
tags: [event-hints, disclosures, prediction, openapi, backtesting]
---

# Structured event hints for market prediction

## Context

Multi-source news aggregation and CNInfo official disclosures were already in
place, but the prediction pipeline still relied mainly on keywords and sector
hints. That made official announcements useful only as plain text evidence.
The missing layer was a compact, structured event contract that prediction,
history, OpenAPI, frontend, and backtest handoff could all share.

## Guidance

Add event intelligence as a first-class field beside keywords and sector hints.

- Extract `eventHints` in `MarketNewsIntelligenceService`, not inside the model
  adapter. The event layer should be reusable by intelligence, predictions, and
  frontend rendering.
- Keep the first version rule-based. Titles, content, tags, CNInfo security
  codes, security names, and announcement type names are enough for a useful
  initial classifier.
- Use a stable shape: `eventType`, `label`, `signal`, `score`, `count`,
  `relatedSymbols`, `relatedNames`, `sourceIds`, and `matchedTitles`.
- Pass `eventHints` into `DeepSeekMarketPredictionService.predict()` and include
  them in the JSON context sent to the remote model.
- Make local heuristic prediction prioritize strong event hints before sector
  hints and keywords.
- Preserve `eventHints` in prediction history so historical detail pages can
  show the same evidence that produced the prediction.
- When a prediction request omits `symbols`, use high-priority event hint
  `relatedSymbols` to populate `backtestHandoff.symbols`. If the user supplies
  symbols, keep user input authoritative.
- Update OpenAPI, `openapi.json`, frontend TypeScript types, and market page UI
  in the same change. Otherwise the UI can silently drift from the backend
  contract.

## Why This Matters

Event-driven market research needs different handling from ordinary keyword
counts. A shareholder increase, inquiry letter, buyback, penalty, or delisting
risk can be more actionable than a broad sector keyword. Making events
structured gives the system useful properties:

- event direction is explicit through `signal`;
- related stock codes can flow directly into backtest validation;
- model context becomes explainable and compact;
- frontend users can see why a symbol was suggested;
- tests can validate event extraction without relying on a live LLM.

## Example

An official disclosure can become both a prediction driver and a backtest
handoff suggestion:

```json
{
  "eventHints": [
    {
      "eventType": "shareholder_increase",
      "label": "股东增持",
      "signal": "bullish",
      "score": 5.6,
      "count": 1,
      "relatedSymbols": ["000792"],
      "relatedNames": ["盐湖股份"],
      "sourceIds": ["cninfo-1"],
      "matchedTitles": ["关于控股股东增持公司股份计划的公告"]
    }
  ],
  "backtestHandoff": {
    "endpoint": "/api/v1/backtests/run",
    "suggestedPreset": "event_theme_momentum",
    "symbols": ["000792"]
  }
}
```

## Validation Pattern

Cover the contract at every boundary:

- service tests for rule extraction, related symbol/name extraction, and
  automatic handoff;
- prediction adapter tests for remote context and heuristic prioritization;
- history tests for persistence;
- API tests for response payload shape;
- OpenAPI publication tests for `MarketEventHint` and `eventHintCount`;
- frontend tests/build for TypeScript and page contract safety;
- `openspec validate --all --strict` before archiving.

## Related

- `docs/solutions/architecture-patterns/multi-source-news-deepseek-prediction-loop-2026-05-21.md`
- `docs/solutions/architecture-patterns/deepseek-prediction-reliability-explainability-2026-05-21.md`
- `openspec/changes/archive/2026-05-24-structure-event-hints-for-market-prediction/`
