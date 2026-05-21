## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Backend SHALL expose formal screener, diagnosis, factor, and portfolio APIs
The system SHALL expose formal backend APIs for screening, diagnosis, factor analysis, and portfolio optimization so those capabilities can be consumed as first-class platform services instead of placeholder routes.

#### Scenario: Client calls a formal half-finished capability API
- **WHEN** a client calls a formal API route for `screener`, `diagnosis`, `factors`, or `portfolio`
- **THEN** the backend returns structured business results or structured validation/degraded errors rather than a placeholder summary payload
