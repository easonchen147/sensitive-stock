# jin10-news-intelligence-pipeline Specification

## Purpose

Define market-news intelligence updates for source-quality scoring, DeepSeek V4 Flash mode configuration, and prediction-history handoff.

## ADDED Requirements

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
