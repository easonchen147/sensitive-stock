# nextjs-frontend-shell Specification

## Purpose
Define the Next.js application shell, capability inventory view, formal research workbench pages, and AKQuant-backed backtest workbench that consume the Flask backend through OpenAPI-governed client bindings.
## Requirements
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

### Requirement: Frontend backtest page SHALL call the backend backtest API
The system SHALL provide a backtest page that collects the key inputs required by the AKQuant-backed backtest contract, organizes them into guided workbench sections, submits them to the Flask backend, and renders the returned metrics and recent trade records with assumption and risk context.

#### Scenario: User runs a backtest from the frontend
- **WHEN** the user loads the backtest workbench, selects an AKQuant-backed preset or compatible custom strategy, adjusts grouped market/execution/cost/risk inputs, and submits the form
- **THEN** the frontend reads `/api/v1/backtests/presets`, calls `/api/v1/backtests/run`, and renders the returned settings, metrics, benchmark comparison, series summary, trade statistics, warnings, and recent trades without reloading the page

#### Scenario: Backend error is surfaced in the UI
- **WHEN** the backend returns a validation or execution error for an AKQuant-backed backtest request
- **THEN** the frontend renders a readable error state with the backend message, preserves the user's inputs, and avoids crashing the page

### Requirement: Frontend SHALL discover backend migration status
The system SHALL query the backend capability inventory and use it to annotate the frontend dashboard and status views so users can distinguish migrated flows from placeholders.

#### Scenario: Frontend reads capability inventory
- **WHEN** the frontend loads its dashboard or status area
- **THEN** it fetches the backend capability inventory and shows which modules are already migrated in phase one, which modules remain skeletons, and what that means for the current UI

### Requirement: Frontend market page SHALL consume migrated backend market intelligence APIs
The system SHALL provide a market page that reads the migrated backend market and Jin10 intelligence APIs and presents the returned data as a usable market intelligence workspace.

#### Scenario: User opens the market page
- **WHEN** the user loads the frontend market route
- **THEN** the page fetches backend market overview, quotes, sectors, latest news, and intelligence data, and renders real source/status metadata instead of a static placeholder

#### Scenario: Market data request fails or degrades
- **WHEN** one or more market or intelligence requests fail or return degraded metadata
- **THEN** the frontend renders clear loading, empty, degraded, or error states without misreporting the capability as fully unavailable or fully complete

### Requirement: Frontend SHALL manage a token-backed session for backend requests
The system SHALL complete the login flow through frontend-controlled session storage, attach the stored token to protected backend requests, and recover cleanly when the session becomes invalid.

#### Scenario: Frontend login stores a reusable session token
- **WHEN** a user submits valid administrator credentials from the frontend login page
- **THEN** the frontend stores the returned token in a session mechanism that can be used by protected page loads and subsequent API requests

#### Scenario: Frontend protected requests include the access token
- **WHEN** a protected frontend page or client interaction requests backend capability, backtest, market, screener, diagnosis, factor, or portfolio data
- **THEN** the frontend request path includes the stored access token before forwarding the request to the backend

#### Scenario: Invalid frontend session is cleared and redirected
- **WHEN** a protected frontend page or proxied request discovers that the stored token is invalid or expired
- **THEN** the frontend clears the invalid session and returns the user to the login flow instead of leaving the app in a partially authenticated state

### Requirement: Frontend SHALL provide formal workbench pages for screener, diagnosis, factors, and portfolio
The system SHALL replace placeholder capability pages with formal workbench pages that consume the corresponding backend APIs and present actionable results, empty states, degraded states, and error states.

#### Scenario: User opens a newly completed capability page
- **WHEN** a user opens `/screener`, `/diagnosis`, `/factors`, or `/portfolio` after this change
- **THEN** the frontend loads the corresponding backend data contract and renders a real workbench instead of a placeholder brief

#### Scenario: Workbench request fails or degrades
- **WHEN** a backend request for one of the newly completed capability pages fails or returns degraded metadata
- **THEN** the frontend renders a clear recoverable state without misreporting the capability as fully complete or fully unavailable

### Requirement: Frontend SHALL render all major capability pages as formal workbenches
The system SHALL render login, dashboard, backtest, market, screener, diagnosis, factor, and portfolio pages as formal workbenches that follow the shared design system and consume formal backend APIs.

#### Scenario: User opens a formal workbench page
- **WHEN** a user opens any major capability page after this change
- **THEN** the page presents a formal workbench with structured controls, results, and explanation surfaces instead of a placeholder-oriented or page-specific ad hoc layout
