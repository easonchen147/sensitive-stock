## MODIFIED Requirements

### Requirement: Backtest workbench requests SHALL use a structured contract with legacy compatibility
The system SHALL accept an AKQuant-first structured backtest request grouped by market scope, strategy selection, execution settings, transaction costs, and risk controls, while still mapping the supported legacy flat request fields for compatibility.

#### Scenario: Structured AKQuant-backed payload is submitted
- **WHEN** a client submits `market`, `strategy`, `execution`, `costs`, `risk`, and `initialCapital`
- **THEN** the backend validates those groups and passes a normalized request into the AKQuant runtime adapter

#### Scenario: Legacy flat payload is submitted
- **WHEN** a client submits the older flat backtest fields such as `symbols`, `strategyCode`, and `tradingFee`
- **THEN** the backend maps the supported legacy fields into the AKQuant-backed internal request model before execution

### Requirement: Backtest preset metadata SHALL be discoverable
The system SHALL expose a preset catalog sourced from the AKQuant-backed strategy registry so frontend forms can render parameter inputs and usage guidance from backend metadata instead of hardcoding strategy form variants.

#### Scenario: Client requests preset catalog
- **WHEN** a client calls the preset metadata endpoint
- **THEN** the response contains preset `id`, `label`, `description`, `summary`, `useCase`, `riskNotes`, `defaultParams`, `parameterSchema`, and AKQuant-backed execution metadata suitable for direct frontend rendering
- **AND** the preset explanation fields use product-facing research language rather than raw engine-internal English phrasing

#### Scenario: Client renders parameter help from backend metadata
- **WHEN** a preset parameter includes explanation metadata
- **THEN** the response carries display-ready fields such as grouped parameter placement and help text so the frontend can explain the parameter without duplicating strategy-specific copy

### Requirement: Backtest responses SHALL return structured results and comparison data
The system SHALL return a normalized response organized around execution assumptions, performance metrics, comparison metrics, series data, trade statistics, trade records, warnings, and derived insights, even though the underlying execution is performed by AKQuant.

#### Scenario: Benchmark comparison is available
- **WHEN** benchmark history is fetched successfully during an AKQuant-backed run
- **THEN** the response contains populated `comparison` fields, benchmark series alongside strategy equity, and assumption or insight data that explains how the comparison should be read

#### Scenario: Benchmark data cannot be fetched
- **WHEN** a request includes `benchmarkSymbol` but benchmark history fails to load
- **THEN** the response still succeeds for the main symbol, adds a warning about the skipped benchmark comparison, and omits unavailable comparison values without dropping the rest of the structured report

#### Scenario: Client needs richer execution interpretation
- **WHEN** a backtest run completes successfully through AKQuant
- **THEN** each symbol result includes explicit assumption and insight sections plus richer trade statistics
- **AND** those explanatory fields use direct-render research language instead of raw runtime jargon
