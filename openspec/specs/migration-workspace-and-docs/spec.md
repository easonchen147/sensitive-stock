# migration-workspace-and-docs Specification

## Purpose
Describe the repository workspace split, Python dependency workflow, and migration-facing documentation so developers can understand the backend/frontend default runtime and the preserved legacy modules.
## Requirements
### Requirement: Repository SHALL expose backend and frontend workspaces
The system SHALL add top-level `backend/` and `frontend/` directories with clear responsibility boundaries, allowing developers to understand where to build API logic and where to build web UI logic.

#### Scenario: Developer inspects repository root
- **WHEN** a developer lists the repository root after phase one migration
- **THEN** the root shows dedicated backend and frontend workspaces plus migration documentation describing their roles

### Requirement: Python dependency workflow SHALL reflect UV plus Poetry
The system SHALL provide Poetry-based Python project metadata for the backend and document a UV-oriented environment and command workflow for local development.

#### Scenario: Developer reads backend setup instructions
- **WHEN** a developer opens the updated documentation
- **THEN** it explains how Poetry defines backend dependencies and how UV is intended to create environments and run backend commands

### Requirement: Documentation SHALL describe migration status, data-source policy, and startup flow
The system SHALL update the root README and related migration documents to describe the current architecture, the available startup commands, the AkShare-first data-source policy, the preserved fallbacks, the Jin10-backed market intelligence APIs, and the truthful completion state of the current frontend pages.

#### Scenario: Developer follows the README
- **WHEN** a developer reads the root README after this change
- **THEN** the documentation explains that the frontend now includes formal backtest, market, screener, diagnosis, factors, and portfolio workbenches backed by real API calls

#### Scenario: Developer checks migration status details
- **WHEN** a developer opens the migration document after this change
- **THEN** it distinguishes current workspace boundaries, formal API coverage, and any explicitly limited runtime behavior without overstating incomplete capabilities

### Requirement: Repository SHALL include an explicit OSS license file
The system SHALL include an MIT `LICENSE` file so the repository license is unambiguous.

#### Scenario: License file exists at the repository root
- **WHEN** a developer or automation tool inspects repository metadata
- **THEN** it finds an MIT license file at the root
