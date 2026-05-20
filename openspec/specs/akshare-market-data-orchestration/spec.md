# akshare-market-data-orchestration Specification

## Purpose
Define an AkShare-first market data contract for backend services and the legacy backtesting pipeline, with explicit fallback order and callable market APIs.

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
