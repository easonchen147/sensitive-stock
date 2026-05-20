## MODIFIED Requirements

### Requirement: Backtest preset metadata SHALL be discoverable
The system SHALL expose a preset catalog so frontend forms can render parameter inputs and usage guidance from backend metadata instead of hardcoding strategy form variants.

#### Scenario: Client requests preset catalog
- **WHEN** a client calls the preset metadata endpoint
- **THEN** the response contains preset `id`, `label`, `description`, `summary`, `useCase`, `riskNotes`, `defaultParams`, `parameterSchema`, and executable strategy `code`

#### Scenario: Client renders parameter help from backend metadata
- **WHEN** a preset parameter includes explanation metadata
- **THEN** the response carries display-ready fields such as grouped parameter placement and help text so the frontend can explain the parameter without duplicating strategy-specific copy

### Requirement: Backtest responses SHALL return structured results and comparison data
The system SHALL return a report organized around execution assumptions, performance metrics, comparison metrics, series data, trade statistics, trade records, warnings, and derived insights so frontend pages can render an interpretable workbench view.

#### Scenario: Benchmark comparison is available
- **WHEN** benchmark history is fetched successfully
- **THEN** the response contains populated `comparison` fields, benchmark series alongside strategy equity, and assumption or insight data that explains how the comparison should be read

#### Scenario: Benchmark data cannot be fetched
- **WHEN** a request includes `benchmarkSymbol` but benchmark history fails to load
- **THEN** the response still succeeds for the main symbol, adds a warning about the skipped benchmark comparison, and omits unavailable comparison values without dropping the rest of the structured report

#### Scenario: Client needs richer execution interpretation
- **WHEN** a backtest run completes successfully
- **THEN** each symbol result includes explicit assumption and insight sections plus richer trade statistics for exposure, costs, or ending equity so the frontend can explain what happened instead of only showing raw returns
