# flask-backend-platform Specification

## Purpose
Define the stable Flask HTTP shell that exposes migrated capabilities, forwards backtest workbench requests into legacy services, and keeps remaining modules discoverable through explicit placeholder endpoints.
## Requirements
### Requirement: Flask backend workspace SHALL expose a stable HTTP platform shell
The system SHALL provide a Flask backend workspace with an application factory, shared configuration, JSON error handling, CORS support, and a versioned API root so that frontend and future services can integrate through a consistent HTTP boundary.

#### Scenario: Backend application boots successfully
- **WHEN** the backend application is created in development mode
- **THEN** it returns a Flask app instance with registered blueprints, JSON response behavior, and a configured API prefix

#### Scenario: Health endpoint is reachable
- **WHEN** a client calls the backend health endpoint
- **THEN** the system returns a success payload that includes service name, environment, and API version metadata

### Requirement: Backtest API SHALL execute the legacy backtesting pipeline
The system SHALL expose backtest endpoints that accept validated request payloads, invoke the existing backtesting pipeline through a backend service adapter, expose preset metadata for guided frontend forms, and return a richer structured report for the Next.js workbench.

#### Scenario: Valid backtest request returns structured result
- **WHEN** a client submits a valid legacy or structured workbench payload to the backtest endpoint
- **THEN** the backend executes the legacy pipeline and returns a JSON payload with `settings`, `metrics`, `comparison`, `series`, `tradeStats`, `trades`, `warnings`, `assumptions`, and `insights`

#### Scenario: Client requests preset metadata for the workbench
- **WHEN** a client calls the preset catalog endpoint
- **THEN** the backend returns the configured preset list with strategy descriptions and parameter explanation metadata suitable for direct frontend rendering

#### Scenario: Invalid backtest request is rejected before execution
- **WHEN** a client submits a malformed backtest payload such as an empty symbol list or invalid date range
- **THEN** the backend returns a validation error response without executing the backtesting pipeline

### Requirement: Backend capabilities SHALL expose explicit migrated or placeholder endpoints
The system SHALL expose discoverable backend endpoints for migrated capabilities and explicit placeholder endpoints only for the capabilities that remain unmigrated, so frontend navigation and future services can distinguish live modules from placeholders.

#### Scenario: Capability inventory is requested
- **WHEN** a client calls the capability inventory endpoint
- **THEN** the system returns each capability with a status of `migrated`, `skeleton`, or `planned`, and the `market` capability is reported as migrated once the backend market services are available

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
The system SHALL expose backend authentication endpoints for login and current-session validation, and SHALL require a valid bearer token for all functional API routes except the explicit auth and health allowlist.

#### Scenario: Public allowlist remains reachable without login
- **WHEN** a client calls `POST /api/v1/auth/login` or `GET /api/v1/health` without a bearer token
- **THEN** the backend accepts the request according to each endpoint contract instead of rejecting it as unauthorized

#### Scenario: Protected API rejects missing bearer token
- **WHEN** a client calls a protected functional endpoint such as `/api/v1/capabilities` or `/api/v1/backtests/presets` without a bearer token
- **THEN** the backend returns a structured `401` authentication error

#### Scenario: Authenticated session endpoint resolves the current principal
- **WHEN** a client calls the backend session endpoint with a valid bearer token
- **THEN** the backend returns the authenticated administrator identity and session metadata suitable for frontend session checks

