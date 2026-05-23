# backend-openapi-publication Specification

## Purpose
Define the global OpenAPI publication surface for the Flask backend, including runtime discovery, generated artifact validation, shared components, and route coverage expectations.
## Requirements
### Requirement: Backend SHALL publish a global OpenAPI contract for all formal APIs
The system SHALL generate and publish a global OpenAPI document that describes every formal backend API exposed under the versioned platform boundary, including the migrated screener, diagnosis, factor, and portfolio APIs.

#### Scenario: Client requests the published OpenAPI document
- **WHEN** a client requests the backend OpenAPI discovery route or generated artifact
- **THEN** the system returns a valid OpenAPI document that covers the formal auth, market, backtest, screener, diagnosis, factor, and portfolio APIs, including the migrated `/screener/run`, `/diagnosis/run`, `/factors/analyze`, and `/portfolio/optimize` operations

### Requirement: OpenAPI publication SHALL be validated as part of backend verification
The system SHALL validate the generated OpenAPI document during backend verification so drift between routes, schemas, and published contracts is caught automatically.

#### Scenario: Route or schema drift breaks the OpenAPI output
- **WHEN** a route, schema, or shared component no longer matches the generated OpenAPI contract
- **THEN** the backend verification flow fails instead of silently publishing a stale or invalid OpenAPI document

### Requirement: OpenAPI SHALL publish market prediction contracts
The generated OpenAPI document SHALL include the market-news prediction endpoint,
query parameters, response schemas, bearer-auth security declaration, source
quality metadata, dedupe metadata, and enriched prediction operational metadata.

#### Scenario: OpenAPI document is generated
- **WHEN** `openapi.json` is generated or served by the backend
- **THEN** it includes `GET /api/v1/market/news/predictions` with protected bearer authentication

#### Scenario: Prediction response schema is inspected
- **WHEN** a client reads the prediction response schema
- **THEN** it can discover prediction metadata, prediction rows, channel metadata, source-quality metadata, dedupe metadata, risk notes, and backtest handoff fields

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
