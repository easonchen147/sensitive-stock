## ADDED Requirements

### Requirement: Backtest requests SHALL carry explicit market, strategy, execution, and cost settings
The system SHALL accept a structured backtest contract that separates market scope, strategy selection, execution assumptions, trading costs, and risk controls, so backend services and the frontend workbench can share one extensible model.

#### Scenario: Request includes benchmark and execution settings
- **WHEN** a client submits a backtest request with a primary symbol, optional benchmark symbol, execution mode, and trading-cost settings
- **THEN** the backend normalizes those fields into one internal request model and echoes the effective settings in the result

#### Scenario: Request targets a preset strategy
- **WHEN** a client selects a built-in strategy preset and passes parameter values
- **THEN** the backend validates the provided parameters against the preset schema before running the backtest

### Requirement: Backtest engine SHALL execute A-share trades with ledger-based accounting
The system SHALL convert target signals into daily cash, holdings, equity, and trades using explicit execution timing, lot-size rounding, commission, stamp-tax, slippage, and stop-loss / take-profit rules.

#### Scenario: Execution mode is next open
- **WHEN** a strategy generates an entry or exit signal under `next_open` mode
- **THEN** the engine uses the next available bar open price for execution and records the trade in the ledger

#### Scenario: Trade size must respect A-share lot size
- **WHEN** the configured position size would produce a non-round-lot share count
- **THEN** the engine rounds down to the nearest valid lot size and reflects the actual filled shares in cash and trade records

### Requirement: Backtest workbench SHALL support parameterized presets and preserved custom code
The system SHALL expose built-in strategy presets with parameter schemas for UI rendering while preserving custom `generate_signals(data, ctx)` strategy execution for advanced users.

#### Scenario: Client loads strategy presets
- **WHEN** the frontend requests the preset catalog
- **THEN** the backend returns preset identifiers, labels, descriptions, default parameters, and parameter schema metadata

#### Scenario: Client submits custom strategy code
- **WHEN** the client runs a backtest in custom mode with Python strategy code
- **THEN** the backend still executes `generate_signals(data, ctx)` and applies the upgraded execution engine to the returned target signal

### Requirement: Backtest results SHALL expose explainable report sections
The system SHALL return report data that includes settings echoes, core metrics, benchmark comparison, equity and drawdown series, trade statistics, trade records, and warnings so users can understand both outcomes and assumptions.

#### Scenario: Successful run returns structured report
- **WHEN** a backtest finishes successfully
- **THEN** the response contains `settings`, `metrics`, `comparison`, `series`, `tradeStats`, `trades`, and `warnings` for each symbol result

#### Scenario: Run produces no trades or partial comparison data
- **WHEN** the backtest has no fills or the benchmark data cannot be aligned
- **THEN** the response still returns a valid report and includes human-readable warnings that explain the limitation
