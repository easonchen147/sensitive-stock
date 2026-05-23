## MODIFIED Requirements

### Requirement: Prediction runs SHALL be persisted locally
The system SHALL persist each market-news prediction response to a local bounded history store with a stable run identifier, prediction identifiers, prediction metadata, source-quality metadata, risk notes, and backtest handoff data suitable for direct frontend rendering.

#### Scenario: Prediction endpoint returns successfully
- **WHEN** a client calls the market-news prediction endpoint and the backend returns predictions
- **THEN** the backend stores a prediction-history run containing `runId`, `createdAt`, `predictionMetadata`, `sourceQuality`, `dedupeMetadata`, `predictions`, `riskNotes`, and `backtestHandoff`

#### Scenario: History store is empty
- **WHEN** a client requests prediction history before any run has been stored
- **THEN** the backend returns an empty history list rather than failing

#### Scenario: History store contains a corrupt line
- **WHEN** the local history file contains an unreadable record
- **THEN** the backend skips the corrupt line, returns readable history records, and includes warning metadata

#### Scenario: Prediction response includes backtest handoff guidance
- **WHEN** market-news prediction returns candidate symbols or themes together with a backtest handoff object
- **THEN** the persisted run preserves the handoff notes as user-facing research guidance
- **AND** the handoff does not present prediction output as trading instructions
