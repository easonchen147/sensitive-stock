## ADDED Requirements

### Requirement: OpenAPI SHALL publish expanded backtest execution contracts
The global OpenAPI document SHALL publish the expanded backtest request schema and diagnostic response fields used by backend and frontend clients.

#### Scenario: OpenAPI document is generated after backtest contract expansion
- **WHEN** the OpenAPI generation command runs
- **THEN** `BacktestRunRequest` includes the advanced execution, fee, and risk properties using their public JSON aliases

#### Scenario: Backtest result diagnostics are documented
- **WHEN** clients inspect the `BacktestSymbolResult` schema
- **THEN** the schema includes `dataQuality`, `executionQuality`, `riskDiagnostics`, and `engineEvents`
