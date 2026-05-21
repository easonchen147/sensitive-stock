## ADDED Requirements

### Requirement: Frontend OpenAPI bindings SHALL include market prediction
The frontend OpenAPI binding table SHALL include the market-news prediction
endpoint and keep its public/protected security flag aligned with the backend
OpenAPI document.

#### Scenario: Frontend contract tests run
- **WHEN** frontend OpenAPI binding tests compare route bindings with `openapi.json`
- **THEN** the market-news prediction endpoint is covered with the correct path, method, and protected security metadata

### Requirement: Market workbench SHALL display prediction metadata
The market workbench SHALL render prediction provider, degraded state, prediction
items, drivers, confidence, and backtest handoff metadata from the backend
prediction endpoint.

#### Scenario: Prediction endpoint returns degraded heuristic predictions
- **WHEN** DeepSeek is not configured and the prediction endpoint returns local heuristic predictions
- **THEN** the market workbench displays the degraded prediction state and still renders the prediction rows
