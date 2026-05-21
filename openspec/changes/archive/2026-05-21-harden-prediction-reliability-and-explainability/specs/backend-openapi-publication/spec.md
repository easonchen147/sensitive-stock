## MODIFIED Requirements

### Requirement: OpenAPI SHALL publish market prediction contracts
The generated OpenAPI document SHALL include the market-news prediction endpoint,
query parameters, response schemas, bearer-auth security declaration, source
quality metadata, dedupe metadata, and enriched prediction operational metadata.

#### Scenario: OpenAPI document is generated
- **WHEN** `openapi.json` is generated or served by the backend
- **THEN** it includes `GET /api/v1/market/news/predictions` with protected bearer authentication

#### Scenario: Prediction response schema is inspected
- **WHEN** a client reads the prediction response schema
- **THEN** it can discover prediction metadata, prediction rows, channel metadata, source-quality metadata, dedupe metadata, risk notes, and backtest handoff fields
