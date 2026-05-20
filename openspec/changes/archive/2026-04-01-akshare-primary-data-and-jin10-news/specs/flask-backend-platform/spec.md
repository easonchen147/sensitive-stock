## MODIFIED Requirements

### Requirement: Backend capabilities SHALL expose explicit migrated or placeholder endpoints
The system SHALL expose discoverable backend endpoints for migrated capabilities and explicit placeholder endpoints only for the capabilities that remain unmigrated, so frontend navigation and future services can distinguish live modules from placeholders.

#### Scenario: Capability inventory is requested
- **WHEN** a client calls the backend capability inventory endpoint
- **THEN** the system returns each capability with a status of `migrated`, `skeleton`, or `planned`, and the `market` capability is reported as migrated once the backend market services are available

#### Scenario: Migrated market endpoint is called
- **WHEN** a client calls the backend market endpoint after this change
- **THEN** the system returns a real market service payload that describes the AkShare primary source, fallback order, and available market subroutes instead of a generic placeholder response

#### Scenario: Placeholder capability endpoint is called
- **WHEN** a client calls an endpoint for a capability that is still not migrated in the backend
- **THEN** the system returns a successful JSON response describing that capability status and next migration step instead of a generic 404
