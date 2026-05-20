## MODIFIED Requirements

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

## ADDED Requirements

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
