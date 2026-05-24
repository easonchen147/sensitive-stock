## MODIFIED Requirements

### Requirement: Market news intelligence SHALL aggregate multiple news channels
The system SHALL preserve the existing Jin10 realtime ingestion path while also
fetching additional market news channels, normalizing items into the shared
market-news shape, deduplicating repeated stories, and returning per-channel
status, source-quality, and dedupe metadata. The default configured extra
channels SHALL include Eastmoney stock news, Sina finance live feed, CLS
telegraph page items, STCN article headlines, 21st Century Business Herald
capital-market headlines, and CNInfo official disclosure feeds for SZSE, SSE,
and BSE when those sources are reachable.

#### Scenario: CNInfo official disclosure source is reachable
- **WHEN** a configured CNInfo market-disclosure source responds successfully
- **THEN** the aggregation layer includes normalized official disclosure items with announcement title, publish time, security context, and source link in the merged news payload

#### Scenario: CNInfo disclosure source returns structured market-specific rows
- **WHEN** the CNInfo disclosure endpoint returns flat announcement rows for a configured market column
- **THEN** the source normalizes the announcement type, security name, and security code into the shared item structure without changing the existing API contract

#### Scenario: One official disclosure source fails
- **WHEN** one CNInfo market-disclosure channel fails while at least one other source succeeds
- **THEN** the aggregated news payload still succeeds, marks the response as degraded, records the failed disclosure channel in `channels`, and appends a warning explaining the failure
