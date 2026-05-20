## MODIFIED Requirements

### Requirement: Backtest API SHALL execute the legacy backtesting pipeline
The system SHALL expose backtest endpoints that accept validated request payloads, invoke the AKQuant runtime through a backend adapter service, expose preset metadata for guided frontend forms, and return a richer structured report for the Next.js workbench.

#### Scenario: Valid backtest request returns structured result
- **WHEN** a client submits a valid legacy-compatible or AKQuant-first workbench payload to the backtest endpoint
- **THEN** the backend executes the request through the AKQuant adapter and returns a JSON payload with `settings`, `metrics`, `comparison`, `series`, `tradeStats`, `trades`, `warnings`, `assumptions`, and `insights`

#### Scenario: Client requests preset metadata for the workbench
- **WHEN** a client calls the preset catalog endpoint
- **THEN** the backend returns the configured AKQuant-backed preset list with strategy descriptions and parameter explanation metadata suitable for direct frontend rendering

#### Scenario: Invalid backtest request is rejected before execution
- **WHEN** a client submits a malformed backtest payload such as an empty symbol list or invalid date range
- **THEN** the backend returns a validation error response without executing the AKQuant runtime
