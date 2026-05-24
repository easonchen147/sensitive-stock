## MODIFIED Requirements

### Requirement: News intelligence SHALL extract keywords for market analysis
The system SHALL extract structured keywords from the normalized market-news
items using tags, titles, content, and rule-based token heuristics so the
output can be reused by sector prediction workflows, and SHALL also emit
structured `eventHints` for high-value announcement or news events.

#### Scenario: Intelligence request includes event-driven items
- **WHEN** the aggregated market-news items contain recognizable events such as buybacks, reductions, incentives, shareholder meetings, earnings guidance, or regulatory risk signals
- **THEN** the intelligence response returns ranked `eventHints` with direction, score, source linkage, and related security context

### Requirement: Market prediction API SHALL expose a prediction and backtest handoff payload
The system SHALL expose a protected backend endpoint that returns multi-source
news, keywords, sector hints, event hints, structured predictions, risk notes,
source-quality metadata, dedupe metadata, prediction operational metadata, and
a backtest handoff object suitable for validating the predicted themes.

#### Scenario: Client calls the prediction endpoint
- **WHEN** a client calls `/api/v1/market/news/predictions`
- **THEN** the response contains `items`, `channels`, `sourceQuality`, `dedupeMetadata`, `keywords`, `sectorHints`, `eventHints`, `predictions`, `predictionMetadata`, `riskNotes`, and `backtestHandoff`

#### Scenario: Prediction context contains event hints
- **WHEN** one or more `eventHints` are available
- **THEN** both the remote-model path and the local heuristic path use those event hints as part of the prediction context instead of ignoring them

#### Scenario: Client does not supply symbols but event hints include specific securities
- **WHEN** the prediction request omits `symbols` and high-priority `eventHints` contain related stock codes
- **THEN** the backtest handoff payload uses those related stock codes as suggested symbols for follow-up validation
