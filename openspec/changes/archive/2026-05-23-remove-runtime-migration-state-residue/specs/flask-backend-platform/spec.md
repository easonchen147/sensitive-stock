## MODIFIED Requirements

### Requirement: Backend capabilities SHALL expose explicit migrated or placeholder endpoints
The system SHALL expose a discoverable backend capability inventory and formal capability routes that reflect the current product runtime, so frontend navigation and future services can distinguish ready, limited, and disabled modules without relying on placeholder endpoints.

#### Scenario: Capability inventory is requested
- **WHEN** a client calls the capability inventory endpoint
- **THEN** the system returns each capability with a status of `ready`, `limited`, or `disabled`
- **AND** the `market`, `screener`, `diagnosis`, `factors`, and `portfolio` capabilities are reported according to their real backend availability

#### Scenario: Formal capability overview endpoint is called
- **WHEN** a client calls a formal capability overview endpoint such as `GET /api/v1/market` or `GET /api/v1/screener`
- **THEN** the system returns a structured overview or business payload that reflects the real route contract
- **AND** it does not return a generic placeholder summary response
