## MODIFIED Requirements

### Requirement: Backtest API SHALL execute the legacy backtesting pipeline
The system SHALL expose backtest endpoints that accept structured AKQuant-inspired requests, resolve preset or custom strategies through backend service adapters, invoke the upgraded backtesting pipeline, and return settings echoes, analytics, comparison data, and trade logs.

#### Scenario: Valid backtest request returns structured result
- **WHEN** a client submits a valid symbol list, date range, strategy selection, and execution settings to the backtest endpoint
- **THEN** the backend executes the upgraded pipeline and returns a JSON payload whose per-symbol results include structured report sections rather than only flattened metrics and trades

#### Scenario: Backtest presets endpoint is requested
- **WHEN** a client calls the backtest preset catalog endpoint
- **THEN** the backend returns the available strategy presets with parameter schema metadata and default values

#### Scenario: Invalid backtest request is rejected before execution
- **WHEN** a client submits a malformed backtest payload such as an empty symbol list, invalid date range, or unsupported execution mode
- **THEN** the backend returns a validation error response without executing the backtesting pipeline
