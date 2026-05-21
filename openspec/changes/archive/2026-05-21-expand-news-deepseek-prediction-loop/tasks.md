## 1. Planning And OpenSpec Source

- [x] 1.1 Write the Compound plan document for multi-source news, DeepSeek prediction, and prediction-backtest loop.
- [x] 1.2 Create OpenSpec proposal, design, spec deltas, and tasks for `expand-news-deepseek-prediction-loop`.

## 2. Multi-Source News Aggregation

- [x] 2.1 Add multi-source news fetchers and aggregation metadata while preserving Jin10 latest-news behavior.
- [x] 2.2 Add tests for multi-channel merge, dedupe, partial degradation, and cache-backed aggregate fallback.

## 3. DeepSeek V4 Flash Prediction

- [x] 3.1 Add DeepSeek prediction service with `deepseek-v4-flash` default, configurable base URL, API key, and timeout.
- [x] 3.2 Add deterministic heuristic fallback and tests for no-key, remote success, and malformed/failing remote output.

## 4. Prediction API And OpenAPI

- [x] 4.1 Add `GET /api/v1/market/news/predictions` with optional symbol query support.
- [x] 4.2 Update OpenAPI schemas, static `openapi.json`, and backend API contract tests.

## 5. Frontend Prediction Binding

- [x] 5.1 Add frontend route binding, API helper, and TypeScript response types.
- [x] 5.2 Render prediction provider, degraded status, prediction rows, drivers, confidence, and backtest handoff in the market workbench.

## 6. Backtest Prediction Validation

- [x] 6.1 Add `event_theme_momentum` AKQuant-backed preset metadata and signal code.
- [x] 6.2 Add preset catalog tests for prediction-validation metadata.

## 7. Verification, Archive, And Compound Learning

- [x] 7.1 Run backend tests, ruff, frontend tests, OpenSpec strict validation, and whitespace checks.
- [x] 7.2 Archive the OpenSpec change after verification passes.
- [x] 7.3 Write a Compound solution note for the multi-source news plus DeepSeek prediction pattern.
