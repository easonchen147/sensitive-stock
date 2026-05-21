## ADDED Requirements

### Requirement: Screener workbench SHALL execute structured stock screening queries
The system SHALL provide a screening workbench that accepts structured conditions and returns ranked A-share candidates with normalized summary fields so users can review and reuse screening results.

#### Scenario: User submits structured screening conditions
- **WHEN** a client submits a screener request with one or more structured filters such as universe, turnover, price range, momentum, or sector constraints
- **THEN** the system returns a successful response containing matched symbols, ranking metadata, applied filters, and result summary fields

#### Scenario: Screener request yields no matches
- **WHEN** a client submits valid screening conditions but no symbols satisfy the filters
- **THEN** the system returns an empty result set with the applied filter summary instead of failing the request

### Requirement: Screener workbench SHALL support natural-language-to-filter translation
The system SHALL support a natural-language screening entry path that converts a user query into structured screening conditions before execution.

#### Scenario: User submits a natural-language screener prompt
- **WHEN** a client submits a screening request using natural language instead of explicit filter fields
- **THEN** the system returns the interpreted structured filters together with the screened results so the conversion remains inspectable

### Requirement: Screener results SHALL support export and backtest handoff
The system SHALL make screening results reusable by exposing export-ready fields and a handoff contract that can be used to initiate or prefill a backtest workflow.

#### Scenario: User exports screening results
- **WHEN** a client requests to export or serialize a screener result set
- **THEN** the system returns exportable rows with normalized symbol, name, score, and factor summary fields

#### Scenario: User sends screened symbols into backtesting
- **WHEN** a client chooses to backtest a screened result set
- **THEN** the system returns or forwards a contract that can be consumed by the backtest workflow without requiring the user to re-enter the selected symbols
