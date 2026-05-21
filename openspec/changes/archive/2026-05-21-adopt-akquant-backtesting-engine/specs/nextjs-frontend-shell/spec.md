## MODIFIED Requirements

### Requirement: Frontend backtest page SHALL call the backend backtest API
The system SHALL provide a backtest page that collects the key inputs required by the AKQuant-backed backtest contract, organizes them into guided workbench sections, submits them to the Flask backend, and renders the returned metrics and recent trade records with assumption and risk context.

#### Scenario: User runs a backtest from the frontend
- **WHEN** the user loads the backtest workbench, selects an AKQuant-backed preset or compatible custom strategy, adjusts grouped market/execution/cost/risk inputs, and submits the form
- **THEN** the frontend reads `/api/v1/backtests/presets`, calls `/api/v1/backtests/run`, and renders the returned settings, metrics, benchmark comparison, series summary, trade statistics, warnings, and recent trades without reloading the page

#### Scenario: Backend error is surfaced in the UI
- **WHEN** the backend returns a validation or execution error for an AKQuant-backed backtest request
- **THEN** the frontend renders a readable error state with the backend message, preserves the user's inputs, and avoids crashing the page
