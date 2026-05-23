# openapi-driven-frontend-client Specification

## Purpose

Define frontend OpenAPI binding changes for prediction history, detail, evaluation, and expanded prediction metadata.

## ADDED Requirements

### Requirement: Frontend OpenAPI bindings SHALL include prediction-loop APIs
The frontend OpenAPI binding table SHALL include protected bindings for prediction history, prediction detail, and prediction evaluation APIs.

#### Scenario: Frontend contract tests inspect route bindings
- **WHEN** frontend OpenAPI binding tests compare bindings with `openapi.json`
- **THEN** `marketPredictionHistory`, `marketPredictionDetail`, and `marketPredictionEvaluation` map to existing protected OpenAPI operations

### Requirement: Frontend types SHALL expose prediction quality and evaluation fields
The frontend API types SHALL expose prediction `runId`, prediction ids, DeepSeek mode metadata, source-quality score fields, history rows, detail payloads, and evaluation result fields.

#### Scenario: Market workbench consumes prediction detail
- **WHEN** the market workbench renders prediction detail from the frontend API layer
- **THEN** TypeScript types include the detail payload fields without page-local ad hoc shapes

#### Scenario: Market workbench consumes evaluation
- **WHEN** the market workbench renders prediction evaluation
- **THEN** TypeScript types include evaluation summary and item status fields

### Requirement: Prediction request bindings SHALL support DeepSeek mode query overrides
The frontend client SHALL allow prediction requests to pass optional `thinking` and `reasoningEffort` query values while keeping default backend configuration when they are omitted.

#### Scenario: User selects non-thinking mode
- **WHEN** the market workbench requests predictions with non-thinking mode
- **THEN** the frontend request includes the expected query override and the returned metadata displays the actual backend mode
