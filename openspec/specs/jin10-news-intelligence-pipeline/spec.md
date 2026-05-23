# jin10-news-intelligence-pipeline Specification

## Purpose
Define a Jin10 latest-news ingestion and rule-based intelligence contract that backend consumers can reuse for market analysis and later sector prediction workflows.
## Requirements
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

### Requirement: Market news intelligence SHALL aggregate multiple news channels
The system SHALL preserve the existing Jin10 realtime ingestion path while also
fetching additional market news channels, normalizing items into the shared
market-news shape, deduplicating repeated stories, and returning per-channel
status, source-quality, and dedupe metadata.

#### Scenario: Multiple channels return overlapping stories
- **WHEN** Jin10 and another configured market news channel return the same or substantially similar story
- **THEN** the intelligence payload contains one normalized story, channel metadata that records which channels were queried, `sourceQuality.duplicateItems`, and `dedupeMetadata.duplicateCount`

#### Scenario: One non-primary channel fails
- **WHEN** one additional market news channel fails while at least one other channel succeeds
- **THEN** the news payload still succeeds, marks the response as degraded, includes warning metadata for the failed channel, and increments `sourceQuality.failedChannels`

### Requirement: Market news predictions SHALL use DeepSeek V4 Flash when configured
The system SHALL use a DeepSeek OpenAI-compatible chat completion adapter with
`deepseek-v4-flash` as the default model when a DeepSeek API key is configured,
request JSON object output, provide a prompt-level JSON schema example, expose a
prompt/schema version, and cache successful equivalent remote predictions for a
bounded TTL.

#### Scenario: DeepSeek credentials are configured
- **WHEN** a prediction request is made and `BACKEND_DEEPSEEK_API_KEY` is present
- **THEN** the backend submits normalized news context, keywords, sector hints, and requested symbols to the configured DeepSeek model with JSON object output and returns parsed structured predictions with `predictionMetadata.schemaVersion`, `inputDigest`, and input count metadata

#### Scenario: Equivalent DeepSeek request repeats
- **WHEN** a prediction request repeats with the same normalized context, symbols, model, and schema version after a successful remote prediction
- **THEN** the backend returns the cached prediction payload without another remote model call and marks `predictionMetadata.cached` as true

#### Scenario: DeepSeek credentials are not configured
- **WHEN** a prediction request is made without a DeepSeek API key
- **THEN** the backend returns deterministic local heuristic predictions, marks prediction metadata as degraded, includes a warning explaining that DeepSeek was not called, and still includes schema version and input summary metadata

#### Scenario: DeepSeek returns malformed or unavailable output
- **WHEN** the configured DeepSeek request fails or returns an unparseable prediction payload
- **THEN** the backend falls back to local heuristic predictions with warning metadata instead of failing the whole endpoint

### Requirement: Market prediction API SHALL expose a prediction and backtest handoff payload
The system SHALL expose a protected backend endpoint that returns multi-source
news, keywords, sector hints, structured predictions, risk notes, source-quality
metadata, dedupe metadata, prediction operational metadata, and a backtest
handoff object suitable for validating the predicted themes.

#### Scenario: Client calls the prediction endpoint
- **WHEN** a client calls `/api/v1/market/news/predictions`
- **THEN** the response contains `items`, `channels`, `sourceQuality`, `dedupeMetadata`, `keywords`, `sectorHints`, `predictions`, `predictionMetadata`, `riskNotes`, and `backtestHandoff`

#### Scenario: Client supplies symbols for prediction validation
- **WHEN** a client supplies `symbols` in the prediction query
- **THEN** the response includes those symbols in the prediction context, in the prediction cache key input, and in the backtest handoff payload

### Requirement: Market news aggregation SHALL provide source quality scoring
The market news aggregation payload SHALL include a normalized source-quality score and component scores for coverage, freshness, reliability, and duplicate pressure.

#### Scenario: Multiple channels succeed with low duplication
- **WHEN** multiple configured news channels return usable unique items
- **THEN** `sourceQuality.qualityScore`, `coverageScore`, `freshnessScore`, and `reliabilityScore` reflect a high-quality source set with Chinese-readable quality notes available to clients

#### Scenario: One or more channels fail
- **WHEN** at least one configured news channel fails
- **THEN** source-quality scoring lowers reliability, preserves failed channel counts, and includes quality notes explaining the degradation

### Requirement: Market news predictions SHALL expose DeepSeek V4 Flash thinking mode
The prediction adapter SHALL use `deepseek-v4-flash` as the default DeepSeek model and SHALL explicitly configure and report thinking mode and reasoning effort.

#### Scenario: Default prediction request uses configured thinking mode
- **WHEN** a prediction request is made with DeepSeek credentials configured
- **THEN** the backend sends the configured `thinking.type` and `reasoning_effort` values to DeepSeek and returns them in `predictionMetadata`

#### Scenario: Prediction request overrides thinking mode
- **WHEN** a client supplies a supported thinking-mode query override
- **THEN** the backend uses that mode for the request, includes it in the cache key, and reports it in `predictionMetadata`

### Requirement: Market news predictions SHALL write successful responses to prediction history
The prediction endpoint SHALL hand successful prediction payloads to the local prediction-history store before returning the response.

#### Scenario: Prediction response contains rows
- **WHEN** the prediction endpoint produces one or more prediction rows
- **THEN** the response includes `runId` and prediction ids, and the same run can be retrieved from prediction history
