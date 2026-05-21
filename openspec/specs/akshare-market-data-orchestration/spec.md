# akshare-market-data-orchestration Specification

## Purpose
Define an AkShare-first market data contract for backend services and AKQuant-backed backtests, with explicit fallback order and callable market APIs.
## Requirements
### Requirement: Backend market data services SHALL use AkShare as the primary A-share data source
The system SHALL use the latest supported AkShare interfaces as the default source for A-share historical行情、实时行情、股票基础信息和板块数据, so backend services and backtesting share a consistent primary market data contract.

#### Scenario: Historical OHLCV request succeeds through AkShare
- **WHEN** a backtest or backend market service requests A-share history for a symbol and date range
- **THEN** the system uses AkShare `stock_zh_a_hist` as the first data source and returns normalized OHLCV rows with `open`, `high`, `low`, `close`, `volume`, `amount`, and `pre_close`

#### Scenario: Realtime quote request succeeds through AkShare
- **WHEN** a backend client requests latest quotes for one or more A-share symbols
- **THEN** the system uses an AkShare realtime quote interface and returns normalized quote payloads keyed by six-digit stock code

### Requirement: Market data fallback policy SHALL be explicit and limited
The system SHALL preserve only the minimum fallback providers required for resiliency, and SHALL make the primary plus fallback order explicit in code and API responses.

#### Scenario: AkShare historical fetch fails but Tushare is configured
- **WHEN** AkShare historical data retrieval fails and `TUSHARE_TOKEN` is available
- **THEN** the system falls back to Tushare before trying any lower-priority source

#### Scenario: All primary and secondary historical providers fail
- **WHEN** both AkShare and Tushare cannot return historical data
- **THEN** the system tries Sina direct as the last-resort fallback and raises a structured error if it also fails

### Requirement: Backend SHALL expose market snapshots and sector data through callable APIs
The system SHALL provide backend endpoints for market overview, quotes, and sector data so frontend and downstream business logic can consume the AkShare-first market services without importing legacy Streamlit modules.

#### Scenario: Client requests market overview
- **WHEN** a client calls the backend market overview endpoint
- **THEN** the response includes the primary data source, fallback order, and available market-related API routes

#### Scenario: Client requests hot sectors
- **WHEN** a client calls the backend hot sectors endpoint
- **THEN** the system returns normalized concept or industry sector rows sourced from AkShare and annotated with the upstream source name

### Requirement: AKQuant-backed backtests SHALL reuse the shared normalized market data contract
The system SHALL ensure that AKQuant-backed backtests consume the same normalized A-share market data contract and fallback policy used by the broader backend platform.

#### Scenario: AKQuant-backed run requests historical market data
- **WHEN** the AKQuant adapter requests historical data for an A-share backtest
- **THEN** the system resolves the request through the shared normalized market-data contract instead of introducing a separate incompatible feed shape

### Requirement: Shared market data contracts SHALL support screener, diagnosis, factor, and portfolio workflows
The system SHALL make AkShare-first market data contracts reusable across screening, diagnosis, factor analysis, and portfolio optimization workflows so all research capabilities consume consistent normalized market inputs.

#### Scenario: Research workflow requests normalized market history
- **WHEN** a screener, diagnosis, factor-analysis, or portfolio workflow requests A-share market data
- **THEN** the system resolves the request through the shared normalized market-data contract instead of introducing a workflow-specific ad hoc data shape

### Requirement: Market quote and sector APIs SHALL return cache-backed degraded responses on upstream failure
The system SHALL cache recent successful market quote and sector responses in memory and return a degraded cached payload when all configured upstream fetch attempts fail and a matching cached payload is still available.

#### Scenario: Primary market quote source fails but fallback succeeds
- **WHEN** AkShare quote retrieval fails and the direct fallback source succeeds
- **THEN** the quote API returns normalized quote rows with explicit fallback source metadata and degraded status

#### Scenario: Market quote refresh fails after a successful prior response
- **WHEN** all quote upstream sources fail for a request that has a still-valid cached prior response
- **THEN** the quote API returns the cached quote rows with `degraded` set to true and warning metadata explaining that cached data was used

#### Scenario: Sector refresh fails after a successful prior response
- **WHEN** all sector upstream sources fail for a request that has a still-valid cached prior response
- **THEN** the sector API returns the cached sector rows with `degraded` set to true and warning metadata explaining that cached data was used
