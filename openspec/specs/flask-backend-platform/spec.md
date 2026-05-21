# flask-backend-platform Specification

## Purpose
Define the stable Flask HTTP shell that exposes migrated capabilities, forwards backtest workbench requests into AKQuant-backed services, publishes OpenAPI discovery, and keeps remaining modules discoverable through explicit placeholder endpoints.
## Requirements
### Requirement: Flask backend workspace SHALL expose a stable HTTP platform shell
The system SHALL provide a Flask backend workspace with an application factory, shared configuration, JSON error handling, CORS support, a versioned API root, and an OpenAPI discovery surface so that frontend and future services can integrate through a consistent HTTP boundary.

#### Scenario: Backend application boots successfully
- **WHEN** the backend application is created in development mode
- **THEN** it returns a Flask app instance with registered blueprints, JSON response behavior, a configured API prefix, and the route infrastructure needed to expose the published OpenAPI contract

#### Scenario: Health endpoint is reachable
- **WHEN** a client calls the backend health endpoint
- **THEN** the system returns a success payload that includes service name, environment, and API version metadata

### Requirement: Backtest API SHALL execute the AKQuant-backed pipeline
The system SHALL expose backtest endpoints that accept validated request payloads, invoke the AKQuant runtime through a backend adapter service, expose preset metadata for guided frontend forms, and return a richer structured report for the Next.js workbench.

#### Scenario: Valid backtest request returns structured result
- **WHEN** a client submits a valid legacy-compatible or AKQuant-first workbench payload to the backtest endpoint
- **THEN** the backend executes the request through the AKQuant adapter and returns a JSON payload with `settings`, `metrics`, `comparison`, `series`, `tradeStats`, `trades`, `warnings`, `assumptions`, and `insights`

#### Scenario: Client requests preset metadata for the workbench
- **WHEN** a client calls the preset catalog endpoint
- **THEN** the backend returns the configured AKQuant-backed preset list with strategy descriptions and parameter explanation metadata suitable for direct frontend rendering

#### Scenario: Invalid backtest request is rejected before execution
- **WHEN** a client submits a malformed backtest payload such as an empty symbol list or invalid date range
- **THEN** the backend returns a validation error response without executing the AKQuant runtime

### Requirement: Backend capabilities SHALL expose explicit migrated or placeholder endpoints
The system SHALL expose discoverable backend endpoints for migrated capabilities and explicit placeholder endpoints only for the capabilities that remain unmigrated, so frontend navigation and future services can distinguish live modules from placeholders.

#### Scenario: Capability inventory is requested
- **WHEN** a client calls the capability inventory endpoint
- **THEN** the system returns each capability with a status of `migrated`, `skeleton`, or `planned`, and the `market`, `screener`, `diagnosis`, `factors`, and `portfolio` capabilities are reported according to their real backend availability

#### Scenario: Migrated market endpoint is called
- **WHEN** a client calls the backend market endpoint after this change
- **THEN** the system returns a real market service payload that describes the AkShare primary source, fallback order, and available market subroutes instead of a generic placeholder response

#### Scenario: Placeholder capability endpoint is called
- **WHEN** a client calls an endpoint for a first-phase placeholder capability
- **THEN** the system returns a successful JSON response describing that capability status and next migration step instead of a generic 404

### Requirement: Analytics helper services SHALL use the unified data provider contract
The system SHALL update factor analysis and portfolio optimization helpers to use the `HistoricalDataRequest` plus `get_ohlcv()` contract so they remain callable from the new backend service layer.

#### Scenario: Factor analysis fetches history through the unified contract
- **WHEN** the factor analysis service requests market history for a symbol and date range
- **THEN** it uses `SmartDataProvider.get_ohlcv()` and receives a normalized OHLCV dataframe

#### Scenario: Portfolio optimizer fetches history through the unified contract
- **WHEN** the portfolio optimizer requests market history for one or more symbols
- **THEN** it uses `SmartDataProvider.get_ohlcv()` and calculates returns from the normalized close series

### Requirement: Flask backend SHALL expose token authentication endpoints and enforce protected APIs
The system SHALL expose backend authentication endpoints for login and current-session validation, and SHALL require a valid bearer token for all functional API routes except the explicit auth, health, and OpenAPI discovery allowlist.

#### Scenario: Public allowlist remains reachable without login
- **WHEN** a client calls `POST /api/v1/auth/login`, `GET /api/v1/health`, or `GET /api/v1/openapi.json` without a bearer token
- **THEN** the backend accepts the request according to each endpoint contract instead of rejecting it as unauthorized

#### Scenario: Protected API rejects missing bearer token
- **WHEN** a client calls a protected functional endpoint such as `/api/v1/capabilities` or `/api/v1/backtests/presets` without a bearer token
- **THEN** the backend returns a structured `401` authentication error

#### Scenario: Authenticated session endpoint resolves the current principal
- **WHEN** a client calls the backend session endpoint with a valid bearer token
- **THEN** the backend returns the authenticated administrator identity and session metadata suitable for frontend session checks

### Requirement: Flask backend SHALL expose formal APIs through shared platform conventions
The system SHALL expose formal business APIs through shared platform conventions for auth, schema binding, error shape, and degraded/source metadata so all backend capabilities can be described consistently in OpenAPI.

#### Scenario: Client calls a formal backend business endpoint
- **WHEN** a client calls a formal backend endpoint covered by the platform contract
- **THEN** the endpoint uses the shared platform conventions for authentication requirements, response structure, and error formatting instead of introducing a one-off route contract

### Requirement: Backend SHALL expose formal screener, diagnosis, factor, and portfolio APIs
The system SHALL expose formal backend APIs for screening, diagnosis, factor analysis, and portfolio optimization so those capabilities can be consumed as first-class platform services instead of placeholder routes.

#### Scenario: Client calls a formal half-finished capability API
- **WHEN** a client calls a formal API route for `screener`, `diagnosis`, `factors`, or `portfolio`
- **THEN** the backend returns structured business results or structured validation/degraded errors rather than a placeholder summary payload
