# openapi-driven-frontend-client Specification

## Purpose
Define the frontend client layer that binds frontend API helpers, BFF proxy paths, and server helpers to the generated backend OpenAPI contract.
## Requirements
### Requirement: Frontend SHALL consume backend APIs through an OpenAPI-governed client layer
The system SHALL consume backend APIs through a client layer whose types and endpoint bindings are generated from or aligned to the published OpenAPI contract.

#### Scenario: Frontend calls a backend API covered by OpenAPI
- **WHEN** a frontend page, server helper, or BFF route consumes a backend API described by the published OpenAPI contract
- **THEN** the frontend uses the OpenAPI-governed type and client binding instead of hand-maintained drifting request or response shapes

#### Scenario: Backend contract changes
- **WHEN** the published OpenAPI contract changes
- **THEN** the frontend client/type layer surfaces the delta during regeneration or verification instead of silently continuing with stale field assumptions

### Requirement: Frontend OpenAPI bindings SHALL verify path, method, and security alignment
The system SHALL automatically verify that every frontend OpenAPI binding maps to an existing `openapi.json` operation with the expected HTTP method and matching public/protected security declaration.

#### Scenario: Frontend binding points at an OpenAPI operation
- **WHEN** a frontend route binding declares a backend path and method
- **THEN** the frontend verification fails if that path or method is absent from the published OpenAPI document

#### Scenario: Frontend binding declares public access
- **WHEN** a frontend route binding is marked public
- **THEN** the matching OpenAPI operation must have an empty operation-level `security` declaration

#### Scenario: Frontend binding declares protected access
- **WHEN** a frontend route binding is marked protected
- **THEN** the matching OpenAPI operation must require the shared `bearerAuth` security scheme

### Requirement: Frontend backend proxy SHALL only forward protected OpenAPI-bound routes
The system SHALL keep the frontend BFF backend proxy constrained to protected routes that are present in the OpenAPI binding table.

#### Scenario: Unknown backend proxy route is requested
- **WHEN** a frontend client requests a backend proxy path that is not registered in the OpenAPI binding table
- **THEN** the proxy returns a structured not-found error instead of forwarding the request upstream

#### Scenario: Public backend operation is requested through the protected proxy
- **WHEN** a frontend client requests a public OpenAPI operation through the protected backend proxy
- **THEN** the proxy rejects the request instead of treating the public operation as an authenticated business endpoint

### Requirement: Frontend OpenAPI bindings SHALL include market prediction
The frontend OpenAPI binding table SHALL include the market-news prediction
endpoint and keep its public/protected security flag aligned with the backend
OpenAPI document.

#### Scenario: Frontend contract tests run
- **WHEN** frontend OpenAPI binding tests compare route bindings with `openapi.json`
- **THEN** the market-news prediction endpoint is covered with the correct path, method, and protected security metadata

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
