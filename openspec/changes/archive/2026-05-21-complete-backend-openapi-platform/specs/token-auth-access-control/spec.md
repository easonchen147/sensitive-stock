## ADDED Requirements

### Requirement: Token authentication SHALL be described as a reusable OpenAPI security scheme
The system SHALL publish the bearer-token authentication model as a reusable OpenAPI security scheme and apply it consistently to protected backend operations.

#### Scenario: Client inspects a protected operation in OpenAPI
- **WHEN** a client reads the published OpenAPI document for a protected backend operation
- **THEN** the operation references the shared bearer-token security scheme rather than restating an ad hoc auth contract

#### Scenario: Client inspects a public allowlist operation in OpenAPI
- **WHEN** a client reads the published OpenAPI document for a public allowlist route such as login or health
- **THEN** the operation is marked as not requiring the shared bearer-token security scheme
