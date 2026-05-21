# portfolio-optimization-api Specification

## Purpose
Define the formal portfolio-optimization API boundary used by the backend service layer and frontend portfolio workbench.

## Requirements
### Requirement: Portfolio optimization SHALL be exposed as a formal backend API
The system SHALL expose portfolio optimization as a formal backend capability that accepts validated asset lists and optimization constraints, and returns structured allocation results suitable for direct frontend rendering.

#### Scenario: User runs portfolio optimization for a symbol basket
- **WHEN** a client submits a valid set of symbols, date range, and optimization constraints
- **THEN** the system returns normalized allocation weights, portfolio statistics, and optimization metadata

#### Scenario: Portfolio optimization input is invalid
- **WHEN** a client submits an empty symbol basket, malformed dates, or unsupported optimization parameters
- **THEN** the system returns a structured validation error without running the optimization flow
