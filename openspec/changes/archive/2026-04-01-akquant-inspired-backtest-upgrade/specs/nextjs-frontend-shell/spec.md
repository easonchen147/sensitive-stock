## MODIFIED Requirements

### Requirement: Frontend backtest page SHALL call the backend backtest API
The system SHALL provide a backtest workbench page that collects strategy presets or custom code, benchmark and execution settings, and trading-cost controls, submits them to the Flask backend, and renders a structured report with assumptions and analytics.

#### Scenario: User runs a preset-driven backtest from the frontend
- **WHEN** the user selects a built-in strategy preset, adjusts its parameters, and submits the form
- **THEN** the frontend requests the backend preset catalog, builds a structured backtest payload, and renders the returned report without reloading the page

#### Scenario: User switches to custom strategy mode
- **WHEN** the user chooses custom strategy mode
- **THEN** the frontend shows the editable Python strategy area while preserving the upgraded execution, benchmark, and cost configuration inputs

#### Scenario: Backend error is surfaced in the UI
- **WHEN** the backend returns a validation or execution error for a backtest request
- **THEN** the frontend renders a readable error state with the backend message instead of crashing
