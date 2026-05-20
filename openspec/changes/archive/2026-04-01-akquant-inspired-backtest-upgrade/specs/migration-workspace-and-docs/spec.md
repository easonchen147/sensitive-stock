## MODIFIED Requirements

### Requirement: Documentation SHALL describe migration status, data-source policy, and startup flow
The system SHALL update the root README, backend README, and related migration documents to describe the AKQuant-inspired backtest workbench contract, the new preset catalog endpoint, the upgraded execution assumptions, and the current scope limits of the migration.

#### Scenario: Developer follows the README
- **WHEN** a developer reads the root README after this change
- **THEN** the documentation explains how the upgraded backtest request and result model differ from the earlier legacy passthrough flow

#### Scenario: Developer checks backend setup and market APIs
- **WHEN** a developer opens the backend README
- **THEN** the documentation lists the upgraded backtest endpoints, strategy preset contract, and the execution / cost assumptions used by the new engine
