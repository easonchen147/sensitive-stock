## MODIFIED Requirements

### Requirement: Next.js frontend SHALL provide a new application shell
The system SHALL provide a Next.js frontend workspace with a shared layout, navigation, capability-aware status language, environment-aware API client configuration, and route structure for the migrated and planned capabilities.

#### Scenario: Frontend home page loads application shell
- **WHEN** a user opens the frontend root route
- **THEN** the system shows a branded application shell with navigation entries for dashboard, backtest, screener, market, and diagnosis, plus capability-oriented summary content that reflects the real migration state

#### Scenario: Placeholder pages remain navigable
- **WHEN** a user opens a capability page that is not fully migrated in phase one
- **THEN** the system renders a clear, honest capability brief describing current status, missing backend dependencies, and the next migration step instead of implying that the feature is already complete

### Requirement: Frontend backtest page SHALL call the backend backtest API
The system SHALL provide a backtest page that collects the key inputs required by the existing backtesting pipeline, organizes them into guided workbench sections, submits them to the Flask backend, and renders the returned metrics and recent trade records with assumption and risk context.

#### Scenario: User runs a backtest from the frontend
- **WHEN** the user loads the backtest workbench, selects a preset or custom strategy, adjusts grouped market/execution/cost/risk inputs, and submits the form
- **THEN** the frontend reads `/api/v1/backtests/presets`, calls `/api/v1/backtests/run`, and renders the returned settings, metrics, benchmark comparison, series summary, trade statistics, warnings, and recent trades without reloading the page

#### Scenario: Backend error is surfaced in the UI
- **WHEN** the backend returns a validation or execution error for a backtest request
- **THEN** the frontend renders a readable error state with the backend message, preserves the user's inputs, and avoids crashing the page

### Requirement: Frontend SHALL discover backend migration status
The system SHALL query the backend capability inventory and use it to annotate the frontend dashboard and status views so users can distinguish migrated flows from placeholders.

#### Scenario: Frontend reads capability inventory
- **WHEN** the frontend loads its dashboard or status area
- **THEN** it fetches the backend capability inventory and shows which modules are already migrated in phase one, which modules remain skeletons, and what that means for the current UI

## ADDED Requirements

### Requirement: Frontend market page SHALL consume migrated backend market intelligence APIs
The system SHALL provide a market page that reads the migrated backend market and Jin10 intelligence APIs and presents the returned data as a usable market intelligence workspace.

#### Scenario: User opens the market page
- **WHEN** the user loads the frontend market route
- **THEN** the page fetches backend market overview, quotes, sectors, latest news, and intelligence data, and renders real source/status metadata instead of a static placeholder

#### Scenario: Market data request fails or degrades
- **WHEN** one or more market or intelligence requests fail or return degraded metadata
- **THEN** the frontend renders clear loading, empty, degraded, or error states without misreporting the capability as fully unavailable or fully complete
