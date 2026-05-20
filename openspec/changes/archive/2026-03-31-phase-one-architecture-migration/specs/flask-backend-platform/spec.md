## ADDED Requirements

### Requirement: Flask backend workspace SHALL expose a stable HTTP platform shell
The system SHALL provide a Flask backend workspace with an application factory, shared configuration, JSON error handling, CORS support, and a versioned API root so that frontend and future services can integrate through a consistent HTTP boundary.

#### Scenario: Backend application boots successfully
- **WHEN** the backend application is created in development mode
- **THEN** it returns a Flask app instance with registered blueprints, JSON response behavior, and a configured API prefix

#### Scenario: Health endpoint is reachable
- **WHEN** a client calls the backend health endpoint
- **THEN** the system returns a success payload that includes service name, environment, and API version metadata

### Requirement: Backtest API SHALL execute the legacy backtesting pipeline
The system SHALL expose a backtest execution endpoint that accepts validated request payloads, invokes the existing backtesting pipeline through a backend service adapter, and returns serialized metrics, equity curve, signal data, and trade records.

#### Scenario: Valid backtest request returns structured result
- **WHEN** a client submits a valid symbol, date range, strategy code, and capital settings to the backtest endpoint
- **THEN** the backend executes the legacy pipeline and returns a JSON payload with metrics, performance rows, signal rows, and trades

#### Scenario: Invalid backtest request is rejected before execution
- **WHEN** a client submits a malformed backtest payload such as an empty symbol list or invalid date range
- **THEN** the backend returns a validation error response without executing the backtesting pipeline

### Requirement: Non-migrated capabilities SHALL expose explicit placeholder endpoints
The system SHALL expose discoverable placeholder endpoints for screener, market, diagnosis, factor analysis, and portfolio optimization so that frontend navigation and later migration tasks have stable integration targets.

#### Scenario: Capability inventory is requested
- **WHEN** a client calls the capability inventory endpoint
- **THEN** the backend returns each capability with a status of `migrated`, `skeleton`, or `planned`

#### Scenario: Placeholder capability endpoint is called
- **WHEN** a client calls an endpoint for a first-phase placeholder capability
- **THEN** the backend returns a successful JSON response describing the capability status and next migration step instead of a generic 404

### Requirement: Analytics helper services SHALL use the unified data provider contract
The system SHALL update factor analysis and portfolio optimization helpers to use the `HistoricalDataRequest` plus `get_ohlcv()` contract so they remain callable from the new backend service layer.

#### Scenario: Factor analysis fetches history through the unified contract
- **WHEN** the factor analysis service requests market history for a symbol and date range
- **THEN** it uses `SmartDataProvider.get_ohlcv()` and receives a normalized OHLCV dataframe

#### Scenario: Portfolio optimizer fetches history through the unified contract
- **WHEN** the portfolio optimizer requests market history for one or more symbols
- **THEN** it uses `SmartDataProvider.get_ohlcv()` and calculates returns from the normalized close series
