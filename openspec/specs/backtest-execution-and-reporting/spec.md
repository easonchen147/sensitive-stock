# backtest-execution-and-reporting Specification

## Purpose
Define the AKQuant-inspired backtest workbench contract, preset catalog, single-symbol A-share ledger execution rules, and structured reporting format shared by the backend and frontend.
## Requirements
### Requirement: Backtest workbench requests SHALL use a structured contract with legacy compatibility
The system SHALL accept a structured backtest request grouped by market scope, strategy selection, execution settings, transaction costs, and risk controls, while still normalizing the older flat request shape used before the workbench upgrade.

#### Scenario: Structured workbench payload is submitted
- **WHEN** a client submits `market`, `strategy`, `execution`, `costs`, `risk`, and `initialCapital`
- **THEN** the backend validates those groups and passes a normalized request into the legacy backtesting pipeline

#### Scenario: Legacy flat payload is submitted
- **WHEN** a client submits the older flat backtest fields such as `symbols`, `strategyCode`, and `tradingFee`
- **THEN** the backend maps them into the structured internal request model before execution

### Requirement: Backtest preset metadata SHALL be discoverable
The system SHALL expose a preset catalog so frontend forms can render parameter inputs and usage guidance from backend metadata instead of hardcoding strategy form variants.

#### Scenario: Client requests preset catalog
- **WHEN** a client calls the preset metadata endpoint
- **THEN** the response contains preset `id`, `label`, `description`, `summary`, `useCase`, `riskNotes`, `defaultParams`, `parameterSchema`, and executable strategy `code`

#### Scenario: Client renders parameter help from backend metadata
- **WHEN** a preset parameter includes explanation metadata
- **THEN** the response carries display-ready fields such as grouped parameter placement and help text so the frontend can explain the parameter without duplicating strategy-specific copy

### Requirement: Backtest execution SHALL use a single-symbol A-share ledger model
The system SHALL execute signals with explicit cash, share, fee, tax, slippage, lot-size, and execution-mode handling so reports reflect A-share trading assumptions more faithfully than the old return-times-position approximation.

#### Scenario: next_open execution uses the next session open and round lots
- **WHEN** a strategy signal changes under `next_open` mode
- **THEN** the engine executes on the next bar open, rounds shares by `lotSize`, and applies fees, taxes, and slippage to the trade

#### Scenario: Stop loss or take profit closes the position
- **WHEN** intraday prices hit the configured stop-loss or take-profit threshold
- **THEN** the engine forces a sell, records the closing reason, and reflects the trade in the structured report

### Requirement: Backtest responses SHALL return structured results and comparison data
The system SHALL return a report organized around execution assumptions, performance metrics, comparison metrics, series data, trade statistics, trade records, warnings, and derived insights so frontend pages can render an interpretable workbench view.

#### Scenario: Benchmark comparison is available
- **WHEN** benchmark history is fetched successfully
- **THEN** the response contains populated `comparison` fields, benchmark series alongside strategy equity, and assumption or insight data that explains how the comparison should be read

#### Scenario: Benchmark data cannot be fetched
- **WHEN** a request includes `benchmarkSymbol` but benchmark history fails to load
- **THEN** the response still succeeds for the main symbol, adds a warning about the skipped benchmark comparison, and omits unavailable comparison values without dropping the rest of the structured report

#### Scenario: Client needs richer execution interpretation
- **WHEN** a backtest run completes successfully
- **THEN** each symbol result includes explicit assumption and insight sections plus richer trade statistics for exposure, costs, or ending equity so the frontend can explain what happened instead of only showing raw returns

