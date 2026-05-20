## ADDED Requirements

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

### Requirement: Documentation SHALL describe migration status and startup flow
The system SHALL update the root README and migration documents to describe the new architecture, the available startup commands, the migrated capabilities, and the capabilities that remain as skeletons.

#### Scenario: Developer follows the README
- **WHEN** a developer reads the root README after phase one migration
- **THEN** the default startup guidance points to the Flask backend plus Next.js frontend workflow instead of Streamlit

#### Scenario: Developer checks migration progress
- **WHEN** a developer opens the migration status document
- **THEN** it lists the phase-one delivered items, the preserved legacy modules, and the areas explicitly deferred to later phases

### Requirement: Repository SHALL include an explicit OSS license file
The system SHALL include an MIT `LICENSE` file so the repository license is unambiguous.

#### Scenario: License file exists at the repository root
- **WHEN** a developer or automation tool inspects repository metadata
- **THEN** it finds an MIT license file at the root
