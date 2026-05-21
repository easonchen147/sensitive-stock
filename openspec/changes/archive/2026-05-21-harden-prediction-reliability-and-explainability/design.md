# Design

## Architecture

The change keeps the existing route and orchestration shape:

```text
MarketNewsIntelligenceService
  -> MultiSourceNewsService
  -> DeepSeekMarketPredictionService
  -> GET /api/v1/market/news/predictions
```

The implementation only enriches the data contract and runtime behavior:

- `MultiSourceNewsService` computes source-quality and dedupe metadata whenever
  it aggregates channel results.
- `DeepSeekMarketPredictionService` computes a normalized context digest,
  requests strict JSON output from DeepSeek, caches successful remote prediction
  payloads, and returns richer prediction metadata.
- The market workbench renders the new diagnostics compactly beside the
  prediction rows.

## DeepSeek JSON Contract

The adapter continues to call:

```text
POST {BACKEND_DEEPSEEK_BASE_URL}/chat/completions
```

with:

```json
{"response_format": {"type": "json_object"}}
```

The system message must also contain a concrete JSON object example with these
top-level fields:

- `summary`
- `riskNotes`
- `predictions`

Each prediction row must include:

- `targetType`
- `target`
- `direction`
- `confidence`
- `score`
- `horizon`
- `drivers`
- `sourceIds`

The prompt/schema version is exposed as `predictionMetadata.schemaVersion` and
included in the cache key.

## Prediction Cache

The adapter uses an in-memory TTL cache. The key includes:

- model;
- prompt/schema version;
- normalized news items, keywords, sector hints, and symbols;
- context digest.

Only successful remote DeepSeek payloads are cached. Heuristic fallbacks are not
cached because they are already cheap and should keep warning metadata fresh.

Cache hits return:

- `provider: "deepseek"`;
- `degraded: false`;
- `cached: true`;
- the same predictions, summary, and risk notes from the successful remote call.

## Source Quality

`MultiSourceNewsService` returns:

- `sourceQuality.queriedChannels`
- `sourceQuality.succeededChannels`
- `sourceQuality.degradedChannels`
- `sourceQuality.failedChannels`
- `sourceQuality.totalItems`
- `sourceQuality.uniqueItems`
- `sourceQuality.duplicateItems`
- `sourceQuality.sourceCoverage`

It also returns:

- `dedupeMetadata.strategy`
- `dedupeMetadata.originalCount`
- `dedupeMetadata.uniqueCount`
- `dedupeMetadata.duplicateCount`

These fields are included in latest-news, intelligence, and prediction payloads
when the multi-source service is in use.

## OpenAPI And Frontend

OpenAPI gains explicit schemas for the new metadata instead of relying only on
`additionalProperties`. Frontend types mirror these fields, and the market
workbench displays:

- model/provider/cache state;
- schema version and input digest;
- source-quality counts;
- duplicate count;
- source IDs for prediction evidence.

## Compatibility

Existing clients that ignore unknown fields remain compatible. The prediction
endpoint path, query parameters, and existing core fields remain unchanged.

## Rollback

Rollback is local:

- remove metadata rendering from the market workbench;
- remove new OpenAPI schema fields;
- disable prediction cache and schema metadata in the adapter.

No persistent data or schema migration is involved.
