## ADDED Requirements

### Requirement: Market news intelligence SHALL aggregate multiple news channels
The system SHALL preserve the existing Jin10 realtime ingestion path while also
fetching additional market news channels, normalizing items into the shared
market-news shape, deduplicating repeated stories, and returning per-channel
status metadata.

#### Scenario: Multiple channels return overlapping stories
- **WHEN** Jin10 and another configured market news channel return the same or substantially similar story
- **THEN** the intelligence payload contains one normalized story and channel metadata that still records which channels were queried

#### Scenario: One non-primary channel fails
- **WHEN** one additional market news channel fails while at least one other channel succeeds
- **THEN** the news payload still succeeds, marks the response as degraded, and includes warning metadata for the failed channel

### Requirement: Market news predictions SHALL use DeepSeek V4 Flash when configured
The system SHALL use a DeepSeek OpenAI-compatible chat completion adapter with
`deepseek-v4-flash` as the default model when a DeepSeek API key is configured.

#### Scenario: DeepSeek credentials are configured
- **WHEN** a prediction request is made and `BACKEND_DEEPSEEK_API_KEY` is present
- **THEN** the backend submits normalized news context, keywords, sector hints, and requested symbols to the configured DeepSeek model and returns parsed structured predictions

#### Scenario: DeepSeek credentials are not configured
- **WHEN** a prediction request is made without a DeepSeek API key
- **THEN** the backend returns deterministic local heuristic predictions, marks prediction metadata as degraded, and includes a warning explaining that DeepSeek was not called

#### Scenario: DeepSeek returns malformed or unavailable output
- **WHEN** the configured DeepSeek request fails or returns an unparseable prediction payload
- **THEN** the backend falls back to local heuristic predictions with warning metadata instead of failing the whole endpoint

### Requirement: Market prediction API SHALL expose a prediction and backtest handoff payload
The system SHALL expose a protected backend endpoint that returns multi-source
news, keywords, sector hints, structured predictions, risk notes, and a backtest
handoff object suitable for validating the predicted themes.

#### Scenario: Client calls the prediction endpoint
- **WHEN** a client calls `/api/v1/market/news/predictions`
- **THEN** the response contains `items`, `channels`, `keywords`, `sectorHints`, `predictions`, `predictionMetadata`, `riskNotes`, and `backtestHandoff`

#### Scenario: Client supplies symbols for prediction validation
- **WHEN** a client supplies `symbols` in the prediction query
- **THEN** the response includes those symbols in the prediction context and in the backtest handoff payload
