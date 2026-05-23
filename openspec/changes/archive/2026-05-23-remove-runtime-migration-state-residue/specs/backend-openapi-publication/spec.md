## MODIFIED Requirements

### Requirement: Backend SHALL publish a global OpenAPI contract for all formal APIs
The system SHALL generate and publish a global OpenAPI document that describes every formal backend API exposed under the versioned platform boundary, including auth, market, backtests, screener, diagnosis, factor, portfolio, and prediction-loop operations.

#### Scenario: Client requests the published OpenAPI document
- **WHEN** a client requests the backend OpenAPI discovery route or generated artifact
- **THEN** the system returns a valid OpenAPI document that covers the formal auth, market, backtest, screener, diagnosis, factor, portfolio, and prediction-loop APIs
- **AND** the document includes the formal `/screener/run`, `/diagnosis/run`, `/factors/analyze`, and `/portfolio/optimize` operations
