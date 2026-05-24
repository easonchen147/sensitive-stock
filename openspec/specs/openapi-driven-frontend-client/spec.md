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

### Requirement: Frontend backtest client SHALL use the expanded OpenAPI-backed contract
The frontend SHALL send advanced backtest execution, fee, and risk fields through the existing OpenAPI-backed backend route and SHALL render returned diagnostic sections in Chinese.

#### Scenario: User submits advanced backtest controls
- **WHEN** the user configures advanced execution, fee, or risk values on the回测页面
- **THEN** the frontend payload includes those values in the structured backend request

#### Scenario: Backtest response includes diagnostics
- **WHEN** the backend returns `dataQuality`, `executionQuality`, `riskDiagnostics`, or `engineEvents`
- **THEN** the回测页面 renders the diagnostic information with Chinese labels and without unsupported fake controls

### Requirement: Frontend fallback preset metadata SHALL remain compatible
The frontend fallback preset metadata SHALL remain compatible with the backend execution metadata shape after AKQuant diagnostics are expanded.

#### Scenario: Preset catalog request falls back locally
- **WHEN** the preset catalog request fails and the frontend uses local fallback metadata
- **THEN** the fallback metadata still exposes AKQuant execution modes and risk-control support consistently with the expanded contract
