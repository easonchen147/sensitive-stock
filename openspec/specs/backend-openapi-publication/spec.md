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
