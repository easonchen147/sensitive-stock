## ADDED Requirements

### Requirement: Factor analysis SHALL be exposed as a formal backend API
The system SHALL expose factor analysis as a formal backend capability that accepts validated analysis inputs and returns structured factor results suitable for direct frontend rendering.

#### Scenario: User runs factor analysis for a symbol and period
- **WHEN** a client submits a valid factor analysis request with symbol and date range inputs
- **THEN** the system returns normalized factor outputs, summary statistics, and the effective analysis window

#### Scenario: Invalid factor analysis input is rejected
- **WHEN** a client submits an invalid symbol, malformed date range, or unsupported factor configuration
- **THEN** the system returns a structured validation error without executing the analysis flow
