## MODIFIED Requirements

### Requirement: Next.js frontend SHALL provide a new application shell
The system SHALL provide a Next.js frontend workspace with a shared layout, navigation, capability-aware status language, environment-aware API client configuration, a dedicated login route, and protected application pages that require a valid login session before the main shell can be used.

#### Scenario: Unauthenticated user opens the login route
- **WHEN** a user opens `/login` without an active session
- **THEN** the system renders the login page instead of the protected application shell

#### Scenario: Unauthenticated user opens a protected page
- **WHEN** a user opens `/`, `/backtests`, `/market`, `/screener`, `/diagnosis`, `/factors`, or `/portfolio` without an active session
- **THEN** the system redirects the user to `/login` rather than rendering the protected page content

#### Scenario: Authenticated user opens the application shell
- **WHEN** a user with a valid session opens a protected frontend route
- **THEN** the system renders the branded application shell and the requested page content

### Requirement: Frontend SHALL discover backend migration status
The system SHALL query the backend capability inventory and use it to annotate the frontend dashboard and status views so users can distinguish migrated flows from placeholders.

#### Scenario: Frontend reads capability inventory
- **WHEN** the frontend loads its dashboard or status area
- **THEN** it fetches the backend capability inventory and shows which modules are already migrated in phase one, which modules remain skeletons, and what that means for the current UI

## ADDED Requirements

### Requirement: Frontend SHALL provide formal workbench pages for screener, diagnosis, factors, and portfolio
The system SHALL replace placeholder capability pages with formal workbench pages that consume the corresponding backend APIs and present actionable results, empty states, degraded states, and error states.

#### Scenario: User opens a newly completed capability page
- **WHEN** a user opens `/screener`, `/diagnosis`, `/factors`, or `/portfolio` after this change
- **THEN** the frontend loads the corresponding backend data contract and renders a real workbench instead of a placeholder brief

#### Scenario: Workbench request fails or degrades
- **WHEN** a backend request for one of the newly completed capability pages fails or returns degraded metadata
- **THEN** the frontend renders a clear recoverable state without misreporting the capability as fully complete or fully unavailable
