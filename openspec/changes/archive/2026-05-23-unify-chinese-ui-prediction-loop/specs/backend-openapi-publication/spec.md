# backend-openapi-publication Specification

## Purpose

Define OpenAPI publication updates for prediction history, prediction details, prediction evaluation, source-quality scores, and DeepSeek mode metadata.

## ADDED Requirements

### Requirement: OpenAPI SHALL publish prediction-loop APIs
The generated OpenAPI document SHALL include protected operations for prediction history, prediction detail, and prediction evaluation.

#### Scenario: OpenAPI document is generated
- **WHEN** `openapi.json` is generated or served by the backend
- **THEN** it includes `GET /api/v1/market/news/prediction-history`, `GET /api/v1/market/news/predictions/{runId}`, and `GET /api/v1/market/news/predictions/{runId}/evaluate` with bearer authentication

### Requirement: OpenAPI SHALL describe enriched prediction metadata
The generated OpenAPI schemas SHALL describe run identifiers, prediction identifiers, DeepSeek thinking mode metadata, source-quality scores, history rows, detail payloads, and evaluation payloads.

#### Scenario: Prediction schema is inspected
- **WHEN** a client reads the prediction response schema
- **THEN** it can discover `runId`, `predictionId`, `thinkingType`, `reasoningEffort`, and source-quality score fields

#### Scenario: Evaluation schema is inspected
- **WHEN** a client reads the prediction evaluation schema
- **THEN** it can discover evaluation summary fields and per-prediction evaluation statuses

### Requirement: OpenAPI SHALL describe runtime capability states
The generated OpenAPI document SHALL describe capability inventory status as runtime product states instead of migration states.

#### Scenario: Capability schema is inspected
- **WHEN** a client reads the `Capability` schema
- **THEN** status values are `ready`, `limited`, or `disabled`
- **AND** the schema does not expose `migrated`, `skeleton`, `planned`, or placeholder response schemas
