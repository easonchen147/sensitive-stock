# prediction-history-and-evaluation Specification

## Purpose
Define the local prediction history, detail lookup, evaluation loop, and backtest handoff contract used by the market research workbench.
## Requirements
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

### Requirement: Prediction history API SHALL expose recent runs
The system SHALL expose a protected API that returns recent prediction runs in reverse chronological order with compact metadata suitable for a history panel.

#### Scenario: Client requests recent prediction history
- **WHEN** a client calls `GET /api/v1/market/news/prediction-history`
- **THEN** the response contains recent runs with `runId`, `createdAt`, model/provider metadata, prediction count, source-quality score, evaluation summary if available, and degraded state

### Requirement: Prediction detail API SHALL expose one full run
The system SHALL expose a protected API that returns one stored prediction run by `runId`, including prediction rows and evidence source items needed by the frontend detail view.

#### Scenario: Client requests an existing prediction run
- **WHEN** a client calls `GET /api/v1/market/news/predictions/{runId}` for an existing run
- **THEN** the response contains the full stored run

#### Scenario: Client requests a missing prediction run
- **WHEN** a client calls the detail endpoint for an unknown `runId`
- **THEN** the backend returns a structured not-found error

### Requirement: Prediction evaluation SHALL compare assessable predictions with market movement
The system SHALL evaluate stored predictions when quote data is available and return a transparent hit, miss, neutral, or pending status without inventing performance for unassessable targets.

#### Scenario: Bullish symbol prediction has positive movement
- **WHEN** a stored prediction targets a symbol and the latest quote change is positive
- **THEN** evaluation marks the bullish prediction as `hit`

#### Scenario: Prediction target cannot be mapped to a symbol
- **WHEN** a stored prediction targets a theme or sector that cannot be mapped to quote data
- **THEN** evaluation marks the row as `pending` with an explanatory note

#### Scenario: Quote service fails during evaluation
- **WHEN** quote retrieval fails while evaluating a prediction run
- **THEN** the evaluation endpoint returns pending items with warning metadata instead of failing the entire request

#### Scenario: Prediction response includes backtest handoff guidance
- **WHEN** market-news prediction returns candidate symbols or themes together with a backtest handoff object
- **THEN** the persisted run preserves the handoff notes as user-facing research guidance
- **AND** the handoff does not present prediction output as direct buy or sell guidance
