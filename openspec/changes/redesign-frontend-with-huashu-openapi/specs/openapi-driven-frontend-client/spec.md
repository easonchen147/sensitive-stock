## ADDED Requirements

### Requirement: Frontend SHALL consume backend APIs through an OpenAPI-governed client layer
The system SHALL consume backend APIs through a client layer whose types and endpoint bindings are generated from or aligned to the published OpenAPI contract.

#### Scenario: Frontend calls a backend API covered by OpenAPI
- **WHEN** a frontend page, server helper, or BFF route consumes a backend API described by the published OpenAPI contract
- **THEN** the frontend uses the OpenAPI-governed type and client binding instead of hand-maintained drifting request or response shapes

#### Scenario: Backend contract changes
- **WHEN** the published OpenAPI contract changes
- **THEN** the frontend client/type layer surfaces the delta during regeneration or verification instead of silently continuing with stale field assumptions
