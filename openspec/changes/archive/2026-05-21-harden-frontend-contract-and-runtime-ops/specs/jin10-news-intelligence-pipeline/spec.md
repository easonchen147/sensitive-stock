## ADDED Requirements

### Requirement: Jin10 news ingestion SHALL return cache-backed degraded responses when all upstream sources fail
The system SHALL cache recent successful Jin10 latest-news payloads in memory and return a degraded cached payload when both the primary flash API and public fallback feed are unavailable.

#### Scenario: Primary Jin10 API fails but public fallback succeeds
- **WHEN** the primary Jin10 flash API fails and the public newest feed succeeds
- **THEN** the news response returns normalized fallback items with `degraded` set to true

#### Scenario: All Jin10 upstream sources fail after a successful prior response
- **WHEN** both the primary Jin10 flash API and public fallback feed fail for a request that has a still-valid cached prior response
- **THEN** the news response returns cached items with `degraded` set to true and warning metadata explaining that cached data was used

#### Scenario: Intelligence is built from cached degraded news
- **WHEN** news intelligence is requested while the latest-news payload is served from degraded cache
- **THEN** the intelligence response preserves the degraded news metadata while still deriving keywords and sector hints from the available cached items
