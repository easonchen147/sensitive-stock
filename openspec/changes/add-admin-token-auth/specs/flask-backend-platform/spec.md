## ADDED Requirements

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
