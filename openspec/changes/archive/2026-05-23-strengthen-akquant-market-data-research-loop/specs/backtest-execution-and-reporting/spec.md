## MODIFIED Requirements

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

## ADDED Requirements

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
