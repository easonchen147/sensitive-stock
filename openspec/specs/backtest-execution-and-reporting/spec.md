# backtest-execution-and-reporting Specification

## Purpose
Define the AKQuant-backed backtest workbench contract, preset catalog, single-symbol A-share ledger execution rules, and structured reporting format shared by the backend and frontend.
## Requirements
### Requirement: Backtest workbench requests SHALL use a structured contract with legacy compatibility
The system SHALL accept an AKQuant-first structured backtest request grouped by market scope, strategy selection, execution settings, transaction costs, and risk controls, while still mapping the supported legacy flat request fields for compatibility. The structured contract SHALL include optional advanced execution, fee, and risk fields that map to AKQuant runtime behavior when provided.

#### Scenario: Structured AKQuant-backed payload is submitted
- **WHEN** a client submits `market`, `strategy`, `execution`, `costs`, `risk`, and `initialCapital`
- **THEN** the backend validates those groups and passes a normalized request into the AKQuant runtime adapter

#### Scenario: Structured payload includes advanced AKQuant controls
- **WHEN** a client submits advanced controls such as `volumeLimitPct`, `minCommission`, `transferFeeRate`, `maxDrawdown`, `maxDailyLoss`, or `maxPositionSize`
- **THEN** the backend validates those values and includes them in the normalized request consumed by the AKQuant adapter

#### Scenario: Legacy flat payload is submitted
- **WHEN** a client submits the older flat backtest fields such as `symbols`, `strategyCode`, and `tradingFee`
- **THEN** the backend maps the supported legacy fields into the AKQuant-backed internal request model before execution

### Requirement: Backtest preset metadata SHALL be discoverable
The system SHALL expose a preset catalog sourced from the AKQuant-backed strategy registry so frontend forms can render parameter inputs and usage guidance from backend metadata instead of hardcoding strategy form variants.

#### Scenario: Client requests preset catalog
- **WHEN** a client calls the preset metadata endpoint
- **THEN** the response contains preset `id`, `label`, `description`, `summary`, `useCase`, `riskNotes`, `defaultParams`, `parameterSchema`, and AKQuant-backed execution metadata suitable for direct frontend rendering
- **AND** the preset explanation fields use product-facing research language rather than raw engine-internal English phrasing

#### Scenario: Client renders parameter help from backend metadata
- **WHEN** a preset parameter includes explanation metadata
- **THEN** the response carries display-ready fields such as grouped parameter placement and help text so the frontend can explain the parameter without duplicating strategy-specific copy

### Requirement: Backtest execution SHALL use a single-symbol A-share ledger model
The system SHALL execute backtests through the AKQuant runtime and expose its effective execution model, including fill behavior, fees, taxes, slippage, and risk settings, so reports reflect the real third-party engine assumptions used by the application.

#### Scenario: Supported execution mode is used
- **WHEN** a backtest request specifies a supported execution mode or fill policy
- **THEN** the backend executes the request through AKQuant and returns the effective execution assumptions in the normalized response

#### Scenario: Stop loss or take profit closes the position
- **WHEN** a request includes supported stop-loss or take-profit controls that trigger during execution
- **THEN** the resulting trade and closing reason are reflected in the normalized trade output returned by the backend

### Requirement: Backtest responses SHALL return structured results and comparison data
The system SHALL return a normalized response organized around execution assumptions, performance metrics, comparison metrics, series data, trade statistics, trade records, warnings, and derived insights, even though the underlying execution is performed by AKQuant.

#### Scenario: Benchmark comparison is available
- **WHEN** benchmark history is fetched successfully during an AKQuant-backed run
- **THEN** the response contains populated `comparison` fields, benchmark series alongside strategy equity, and assumption or insight data that explains how the comparison should be read

#### Scenario: Benchmark data cannot be fetched
- **WHEN** a request includes `benchmarkSymbol` but benchmark history fails to load
- **THEN** the response still succeeds for the main symbol, adds a warning about the skipped benchmark comparison, and omits unavailable comparison values without dropping the rest of the structured report

#### Scenario: Client needs richer execution interpretation
- **WHEN** a backtest run completes successfully through AKQuant
- **THEN** each symbol result includes explicit assumption and insight sections plus richer trade statistics so the frontend can explain what happened instead of only showing raw returns
- **AND** those explanatory fields use direct-render research language instead of raw runtime jargon

### Requirement: Backtest preset catalog SHALL include event prediction validation
The AKQuant-backed backtest preset catalog SHALL include a prediction-validation
preset that helps users test event or theme momentum after market-news
predictions identify candidate sectors or symbols.

#### Scenario: Client requests preset catalog after prediction integration
- **WHEN** a client requests backtest presets
- **THEN** the catalog includes an `event_theme_momentum` preset with summary, use case, risk notes, default params, and grouped parameter schema

#### Scenario: Prediction response includes backtest handoff
- **WHEN** market-news prediction returns candidate symbols or themes
- **THEN** the response includes a handoff object pointing to the backtest run endpoint and the prediction-validation preset

### Requirement: Backtest responses SHALL include data, execution, risk, and engine diagnostics
The system SHALL return diagnostic sections that explain market-data provenance, execution realism, applied risk controls, and AKQuant engine events for each symbol result.

#### Scenario: Backtest run completes with provider metadata
- **WHEN** a backtest run completes successfully
- **THEN** each symbol result includes `dataQuality` with source order, selected source, trading-day count, window, and provider warnings

#### Scenario: Backtest run completes with advanced execution settings
- **WHEN** a backtest run completes successfully
- **THEN** each symbol result includes `executionQuality` with volume limit, fee floor, transfer fee, turnover, filled/rejected order counts, and capacity warnings

#### Scenario: Backtest run completes with risk controls
- **WHEN** a backtest run completes successfully
- **THEN** each symbol result includes `riskDiagnostics` with configured risk controls and realized risk metrics

#### Scenario: Backtest run completes through AKQuant
- **WHEN** a backtest run completes through AKQuant
- **THEN** each symbol result includes `engineEvents` summarizing runtime events without exposing raw third-party event objects

### Requirement: Backtest metrics SHALL expose additional AKQuant risk statistics when available
The system SHALL map additional AKQuant metrics into the normalized `metrics` object when they are present in AKQuant output.

#### Scenario: AKQuant provides richer metrics
- **WHEN** AKQuant returns metrics such as Sortino, Calmar, VaR, CVaR, ulcer index, SQN, or Kelly criterion
- **THEN** the normalized response includes those values in `metrics`
