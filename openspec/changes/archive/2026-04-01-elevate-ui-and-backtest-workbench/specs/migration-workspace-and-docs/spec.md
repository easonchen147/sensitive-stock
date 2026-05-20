## MODIFIED Requirements

### Requirement: Documentation SHALL describe migration status, data-source policy, and startup flow
The system SHALL update the root README and related migration documents to describe the current architecture, the available startup commands, the AkShare-first data-source policy, the preserved fallbacks, the Jin10-backed market intelligence APIs, and the truthful completion state of the current frontend pages.

#### Scenario: Developer follows the README
- **WHEN** a developer reads the root README after this change
- **THEN** the documentation explains that the frontend now includes an upgraded backtest workbench and a market intelligence page backed by real API calls, while screener and diagnosis remain explicit skeleton capabilities

#### Scenario: Developer checks migration status details
- **WHEN** a developer opens the migration document after this change
- **THEN** it distinguishes migrated pages, migrated backend-only capabilities, and still-unmigrated user flows without overstating what the frontend actually supports
