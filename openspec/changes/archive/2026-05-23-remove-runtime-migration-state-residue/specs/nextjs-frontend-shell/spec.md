## MODIFIED Requirements

### Requirement: Frontend SHALL discover backend migration status
The system SHALL query the backend capability inventory and use it to annotate the frontend dashboard and status views with current product runtime states, so users can understand which modules are ready, limited, or disabled without seeing migration-era language.

#### Scenario: Frontend reads capability inventory
- **WHEN** the frontend loads its dashboard or status area
- **THEN** it fetches the backend capability inventory
- **AND** it explains the current module status in runtime product language rather than `migrated`, `skeleton`, or placeholder labels

### Requirement: Frontend market page SHALL consume migrated backend market intelligence APIs
The system SHALL provide a market page that reads the formal backend market and Jin10 intelligence APIs and presents the returned data as a usable market intelligence workspace.

#### Scenario: User opens the market page
- **WHEN** the user loads the frontend market route
- **THEN** the page fetches backend market overview, quotes, sectors, latest news, and intelligence data
- **AND** it renders real source/status metadata instead of static or migration-era placeholder copy

### Requirement: Frontend SHALL provide formal workbench pages for screener, diagnosis, factors, and portfolio
The system SHALL render screener, diagnosis, factors, and portfolio pages as formal workbenches that consume the corresponding backend APIs and present actionable results, empty states, degraded states, and error states.

#### Scenario: User opens a completed capability page
- **WHEN** a user opens `/screener`, `/diagnosis`, `/factors`, or `/portfolio`
- **THEN** the frontend loads the corresponding backend data contract and renders a real workbench rather than a placeholder brief

#### Scenario: Workbench request fails or degrades
- **WHEN** a backend request for one of those capability pages fails or returns degraded metadata
- **THEN** the frontend renders a clear recoverable state without misreporting the capability as fully complete or fully unavailable
