## ADDED Requirements

### Requirement: Jin10 news ingestion SHALL collect the latest 100 unique items
The system SHALL fetch Jin10 realtime news through the latest available official web API pattern, paginate as needed, and return up to the latest 100 unique items in reverse chronological order.

#### Scenario: Primary Jin10 API returns fewer than 100 items per page
- **WHEN** the primary Jin10 endpoint returns only a partial page
- **THEN** the system continues fetching older pages using pagination parameters until it reaches 100 unique items or there is no more upstream data

#### Scenario: Primary Jin10 API is unavailable
- **WHEN** the primary Jin10 flash API cannot be used
- **THEN** the system falls back to the public newest feed, returns the available normalized items, and marks the response as degraded

### Requirement: News intelligence SHALL extract keywords for market analysis
The system SHALL extract structured keywords from the normalized Jin10 items using tags, titles, content, and rule-based token heuristics so the output can be reused by sector prediction workflows.

#### Scenario: Intelligence request includes repeated market topics
- **WHEN** multiple Jin10 items mention the same market theme, company, or macro topic
- **THEN** the system returns ranked keywords with occurrence counts and source coverage metadata

### Requirement: News intelligence SHALL generate sector prediction hints
The system SHALL compare extracted keywords against concept and industry sector names and produce ranked sector hints that can be consumed by later“大盘 / 板块预测” logic.

#### Scenario: Keywords match AkShare sector names
- **WHEN** extracted keywords overlap with available concept or industry board names
- **THEN** the system returns sector hint rows that include matched keywords, score, and source board type

#### Scenario: No sector names match the extracted keywords
- **WHEN** the keyword set does not map to any concept or industry board
- **THEN** the system returns an empty sector hint list without failing the request

### Requirement: Backend SHALL expose Jin10 news intelligence through an API
The system SHALL provide a backend endpoint that returns normalized Jin10 items, keyword ranking, sector hints, and source metadata in one response.

#### Scenario: Client calls news intelligence endpoint
- **WHEN** a client calls the backend market news intelligence endpoint
- **THEN** the response contains `items`, `keywords`, `sectorHints`, `source`, `requestedLimit`, and `degraded` fields
