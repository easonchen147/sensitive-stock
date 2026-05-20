## ADDED Requirements

### Requirement: Next.js frontend SHALL provide a new application shell
The system SHALL provide a Next.js frontend workspace with a shared layout, navigation, environment-aware API client configuration, and route structure for the migrated and planned capabilities.

#### Scenario: Frontend home page loads application shell
- **WHEN** a user opens the frontend root route
- **THEN** the system shows a branded application shell with navigation entries for dashboard, backtest, screener, market, and diagnosis

#### Scenario: Placeholder pages remain navigable
- **WHEN** a user opens a capability page that is not fully migrated in phase one
- **THEN** the system renders a clear placeholder view describing current migration status and planned next steps

### Requirement: Frontend backtest page SHALL call the backend backtest API
The system SHALL provide a backtest page that collects the key inputs required by the existing backtesting pipeline, submits them to the Flask backend, and renders the returned metrics and recent trade records.

#### Scenario: User runs a backtest from the frontend
- **WHEN** the user enters a symbol, date range, and strategy code then submits the form
- **THEN** the frontend calls the backend backtest API and renders the returned result summary without reloading the page

#### Scenario: Backend error is surfaced in the UI
- **WHEN** the backend returns a validation or execution error for a backtest request
- **THEN** the frontend renders a readable error state with the backend message instead of crashing

### Requirement: Frontend SHALL discover backend migration status
The system SHALL query the backend capability inventory and use it to annotate the frontend navigation or status views so users can distinguish migrated flows from placeholders.

#### Scenario: Frontend reads capability inventory
- **WHEN** the frontend loads its dashboard or status area
- **THEN** it fetches the backend capability inventory and shows which modules are already migrated in phase one
