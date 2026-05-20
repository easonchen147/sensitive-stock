## MODIFIED Requirements

### Requirement: Next.js frontend SHALL provide a new application shell
The system SHALL provide a Next.js frontend workspace with a shared layout, navigation, capability-aware status language, environment-aware API client configuration, a dedicated login route, protected application pages, and a unified research-workbench presentation language across all formal pages.

#### Scenario: Unauthenticated user opens the login route
- **WHEN** a user opens `/login` without an active session
- **THEN** the system renders the login page instead of the protected application shell

#### Scenario: Unauthenticated user opens a protected page
- **WHEN** a user opens `/`, `/backtests`, `/market`, `/screener`, `/diagnosis`, `/factors`, or `/portfolio` without an active session
- **THEN** the system redirects the user to `/login` rather than rendering the protected page content

#### Scenario: Authenticated user opens the application shell
- **WHEN** a user with a valid session opens a protected frontend route
- **THEN** the system renders the branded application shell and the requested page content using the shared research-workbench presentation language

### Requirement: Frontend SHALL discover backend migration status
The system SHALL query the backend capability inventory and use it to annotate the frontend dashboard and status views so users can distinguish migrated flows from placeholders.

#### Scenario: Frontend reads capability inventory
- **WHEN** the frontend loads its dashboard or status area
- **THEN** it fetches the backend capability inventory and shows which modules are already migrated in phase one, which modules remain skeletons, and what that means for the current UI

## ADDED Requirements

### Requirement: Frontend SHALL render all major capability pages as formal workbenches
The system SHALL render login, dashboard, backtest, market, screener, diagnosis, factor, and portfolio pages as formal workbenches that follow the shared design system and consume formal backend APIs.

#### Scenario: User opens a formal workbench page
- **WHEN** a user opens any major capability page after this change
- **THEN** the page presents a formal workbench with structured controls, results, and explanation surfaces instead of a placeholder-oriented or page-specific ad hoc layout
