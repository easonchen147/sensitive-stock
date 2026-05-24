## MODIFIED Requirements

### Requirement: Market data fallback policy SHALL be explicit and limited
The system SHALL preserve only the minimum fallback providers required for resiliency, and SHALL make the primary plus fallback order explicit in code and API responses. The default historical source order SHALL be AkShare, TickFlow, Tushare when configured, and Sina direct as last resort; the system SHALL allow an explicit TickFlow-preferred mode without changing the default AkShare-first behavior.

#### Scenario: AkShare historical fetch fails and TickFlow is enabled
- **WHEN** AkShare historical data retrieval fails and TickFlow is available
- **THEN** the system falls back to TickFlow before trying Tushare or Sina direct

#### Scenario: TickFlow-preferred mode is enabled
- **WHEN** `BACKEND_MARKET_DATA_PREFER_TICKFLOW` is enabled
- **THEN** the historical source order uses TickFlow before AkShare and still reports the resulting primary and fallback order

#### Scenario: All primary and secondary historical providers fail
- **WHEN** AkShare, TickFlow, and any configured secondary provider cannot return historical data
- **THEN** the system tries Sina direct as the last-resort fallback and raises a structured error if it also fails

## ADDED Requirements

### Requirement: Market data diagnostics SHALL expose provider success and failure metadata
The system SHALL expose the configured source order, last successful source, skipped provider notes, and provider error summaries for shared market-data requests.

#### Scenario: Historical provider succeeds after fallback
- **WHEN** a historical data request succeeds through a non-primary provider
- **THEN** the source metadata includes the selected source and errors from earlier failed providers

#### Scenario: Provider cannot initialize
- **WHEN** an optional provider cannot initialize because of missing dependency, disabled configuration, or missing credentials
- **THEN** the provider is skipped with an explicit diagnostic note instead of failing backend startup

### Requirement: TickFlow SHALL be available as an optional market data provider
The system SHALL integrate TickFlow as an optional A-share market-data provider for historical day K data and API-key-backed realtime quote fallback.

#### Scenario: TickFlow historical data is requested
- **WHEN** the shared market-data contract invokes TickFlow for an A-share symbol
- **THEN** the system converts six-digit A-share symbols into TickFlow market suffix format and normalizes returned rows into the shared OHLCV contract

#### Scenario: TickFlow realtime quote fallback is available
- **WHEN** AkShare quote retrieval fails and `TICKFLOW_API_KEY` is configured
- **THEN** the quote API tries TickFlow before the direct EastMoney fallback and returns normalized quote rows with `source` set to `tickflow`
