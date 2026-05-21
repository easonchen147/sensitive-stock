# Design

## Architecture

The change adds two backend service layers around the existing market
intelligence code:

1. `MultiSourceNewsService`
   - wraps the existing `Jin10NewsService`;
   - fetches additional market news channels;
   - normalizes item shape;
   - deduplicates by title/content/source URL;
   - returns per-channel status, warnings, and cache-backed degraded metadata.

2. `DeepSeekMarketPredictionService`
   - receives normalized news items, keywords, sector hints, and optional
     symbols;
   - calls DeepSeek through an OpenAI-compatible chat completion request when
     `BACKEND_DEEPSEEK_API_KEY` is configured;
   - defaults to model `deepseek-v4-flash`;
   - parses JSON output defensively;
   - returns local heuristic predictions when credentials are unavailable or
     the remote call fails.

`MarketNewsIntelligenceService` becomes the orchestration layer. It still
returns latest news and intelligence, but also exposes `build_predictions()`.

## API Shape

New endpoint:

```text
GET /api/v1/market/news/predictions?limit=60&symbols=000001,600000
```

Response includes:

- latest normalized items;
- `channels`;
- `keywords`;
- `sectorHints`;
- `predictions`;
- `predictionMetadata`;
- `riskNotes`;
- `backtestHandoff`.

## DeepSeek Integration

Configuration:

- `BACKEND_DEEPSEEK_API_KEY`
- `BACKEND_DEEPSEEK_BASE_URL`, default `https://api.deepseek.com`
- `BACKEND_DEEPSEEK_MODEL`, default `deepseek-v4-flash`
- `BACKEND_DEEPSEEK_TIMEOUT`, default backend HTTP timeout

The adapter uses `POST /chat/completions` with JSON output requested. The
service must not fail the market endpoint only because the model is unavailable.

## Prediction Semantics

Predictions are research hints, not investment instructions. Each prediction
contains:

- target type and label;
- direction;
- confidence;
- score;
- drivers;
- source IDs;
- horizon.

The heuristic fallback ranks sector hints and frequent keywords to produce
transparent, deterministic predictions.

## Backtest Loop

Prediction output includes a `backtestHandoff` object with:

- endpoint: `/api/v1/backtests/run`;
- suggested preset: `event_theme_momentum`;
- symbols from the request when available;
- default validation params.

The preset itself remains a normal AKQuant-backed signal replay preset.

## Compatibility

Existing endpoints continue to work. `MarketNewsQuery` accepts optional
`symbols`, but existing callers that only pass `limit` are unchanged.

## Rollback

Rollback is local:

- remove the new route binding and endpoint;
- revert OpenAPI path/schema additions;
- keep existing Jin10 latest-news/intelligence behavior.

No data migration or persistent state is introduced.
