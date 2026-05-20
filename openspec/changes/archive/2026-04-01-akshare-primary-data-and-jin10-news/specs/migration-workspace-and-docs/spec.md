## MODIFIED Requirements

### Requirement: Documentation SHALL describe migration status, data-source policy, and startup flow
The system SHALL update the root README, backend README, and related migration documents to describe the current architecture, the available startup commands, the AkShare-first data-source policy, the preserved fallbacks, and the new Jin10-backed market intelligence APIs.

#### Scenario: Developer follows the README
- **WHEN** a developer reads the root README after this change
- **THEN** the documentation explains that backend market and news services now default to AkShare plus Jin10, and points to the relevant API routes and fallback notes

#### Scenario: Developer checks backend setup and market APIs
- **WHEN** a developer opens the backend README
- **THEN** the documentation lists the backend market endpoints, the AkShare version expectation, the fallback providers, and how Jin10 latest-100 ingestion is intended to work
