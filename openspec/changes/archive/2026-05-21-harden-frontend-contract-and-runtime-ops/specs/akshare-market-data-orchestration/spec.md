## ADDED Requirements

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
