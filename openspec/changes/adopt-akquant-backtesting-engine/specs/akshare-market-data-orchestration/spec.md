## ADDED Requirements

### Requirement: AKQuant-backed backtests SHALL reuse the shared normalized market data contract
The system SHALL ensure that AKQuant-backed backtests consume the same normalized A-share market data contract and fallback policy used by the broader backend platform.

#### Scenario: AKQuant-backed run requests historical market data
- **WHEN** the AKQuant adapter requests historical data for an A-share backtest
- **THEN** the system resolves the request through the shared normalized market-data contract instead of introducing a separate incompatible feed shape
