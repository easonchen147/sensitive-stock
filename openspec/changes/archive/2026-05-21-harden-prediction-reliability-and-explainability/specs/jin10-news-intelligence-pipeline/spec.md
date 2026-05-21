## MODIFIED Requirements

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
