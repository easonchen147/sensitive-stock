# Expand News DeepSeek Prediction Loop

## Summary

Extend the market intelligence system from a Jin10-only rule-based feed into a
multi-source, prediction-aware research loop. The backend will aggregate
multiple news channels, derive keywords and sector hints, optionally call
DeepSeek V4 Flash for structured predictions, and expose a prediction endpoint
with OpenAPI and frontend bindings. The backtest preset catalog will gain an
event/theme momentum preset that helps validate predicted symbols or sectors.

## Motivation

The current market page is useful but still narrow:

- realtime news depends mainly on Jin10;
- intelligence is rule-based and stops at keyword/sector hints;
- prediction is not exposed through a formal API;
- backtesting is not clearly connected to news-driven predictions.

This change closes those gaps without introducing persistent jobs, a database,
or automated trading behavior.

## Scope

In scope:

- multi-source news aggregation with channel status and warnings;
- DeepSeek OpenAI-compatible prediction adapter using `deepseek-v4-flash`;
- deterministic local prediction fallback when DeepSeek is not configured;
- `GET /api/v1/market/news/predictions`;
- OpenAPI and frontend route binding updates;
- market workbench display for predictions;
- one prediction-validation backtest preset.

Out of scope:

- storing news or predictions in a database;
- scheduled ingestion;
- user-specific portfolios;
- live trading or order routing;
- replacing AKQuant again.

## Success Criteria

- News responses can include multiple normalized channels and still degrade
  gracefully when one source fails.
- Prediction responses clearly state provider, model, degraded state, warnings,
  prediction items, risk notes, and backtest handoff metadata.
- DeepSeek defaults to `deepseek-v4-flash` and is configurable by environment.
- Frontend OpenAPI binding tests cover the new endpoint.
- Backend tests cover multi-source aggregation, DeepSeek success/fallback, and
  the prediction endpoint.
- OpenSpec strict validation and affected backend/frontend tests pass.
