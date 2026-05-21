## MODIFIED Requirements

### Requirement: Market workbench SHALL display prediction metadata
The market workbench SHALL render prediction provider, degraded state, cache
state, schema version, input digest, source-quality counts, dedupe counts,
prediction items, drivers, source evidence, confidence, and backtest handoff
metadata from the backend prediction endpoint.

#### Scenario: Prediction endpoint returns degraded heuristic predictions
- **WHEN** DeepSeek is not configured and the prediction endpoint returns local heuristic predictions
- **THEN** the market workbench displays the degraded prediction state and still renders the prediction rows

#### Scenario: Prediction endpoint returns cached DeepSeek predictions
- **WHEN** the backend returns a cached successful DeepSeek prediction payload
- **THEN** the market workbench displays the cache state without marking the prediction as failed or heuristic

#### Scenario: Prediction endpoint returns source-quality metadata
- **WHEN** the backend prediction payload contains source-quality and dedupe metadata
- **THEN** the market workbench displays compact source coverage and duplicate counts beside the prediction rows
