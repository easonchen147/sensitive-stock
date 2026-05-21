## ADDED Requirements

### Requirement: Backtest preset catalog SHALL include event prediction validation
The AKQuant-backed backtest preset catalog SHALL include a prediction-validation
preset that helps users test event or theme momentum after market-news
predictions identify candidate sectors or symbols.

#### Scenario: Client requests preset catalog after prediction integration
- **WHEN** a client requests backtest presets
- **THEN** the catalog includes an `event_theme_momentum` preset with summary, use case, risk notes, default params, and grouped parameter schema

#### Scenario: Prediction response includes backtest handoff
- **WHEN** market-news prediction returns candidate symbols or themes
- **THEN** the response includes a handoff object pointing to the backtest run endpoint and the prediction-validation preset
