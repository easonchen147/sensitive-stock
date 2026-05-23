## MODIFIED Requirements

### Requirement: Documentation SHALL describe migration status, data-source policy, and startup flow
The system SHALL update the root README and related migration documents to describe the current architecture, the available startup commands, the AkShare-first data-source policy, the preserved fallbacks, the Jin10-backed market intelligence APIs, and the truthful completion state of the current frontend pages.

#### Scenario: Developer follows the README
- **WHEN** a developer reads the root README after this change
- **THEN** the documentation explains that the frontend now includes formal backtest, market, screener, diagnosis, factors, and portfolio workbenches backed by real API calls

#### Scenario: Developer checks migration status details
- **WHEN** a developer opens the migration document after this change
- **THEN** it distinguishes current workspace boundaries, formal API coverage, and any explicitly limited runtime behavior without overstating placeholder or skeleton capabilities
