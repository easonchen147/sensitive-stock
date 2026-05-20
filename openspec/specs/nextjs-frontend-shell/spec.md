# nextjs-frontend-shell Specification

## Purpose
Define the Next.js application shell, capability inventory view, placeholder routes, and migrated backtest workbench that consume the Flask backend.
## Requirements
### Requirement: Next.js frontend SHALL provide a new application shell
The system SHALL provide a Next.js frontend workspace with a shared layout, navigation, capability-aware status language, environment-aware API client configuration, a dedicated login route, and protected application pages that require a valid login session before the main shell can be used.

#### Scenario: Unauthenticated user opens the login route
- **WHEN** a user opens `/login` without an active session
- **THEN** the system renders the login page instead of the protected application shell

#### Scenario: Unauthenticated user opens a protected page
- **WHEN** a user opens `/`, `/backtests`, `/market`, `/screener`, or `/diagnosis` without an active session
- **THEN** the system redirects the user to `/login` rather than rendering the protected page content

#### Scenario: Authenticated user opens the application shell
- **WHEN** a user with a valid session opens a protected frontend route
- **THEN** the system renders the branded application shell and the requested page content

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

