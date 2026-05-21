## ADDED Requirements

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
