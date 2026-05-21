## ADDED Requirements

### Requirement: Frontend SHALL use the Next.js 16 proxy convention for protected route gating
The system SHALL expose the protected application route gate through `proxy.ts` with an exported `proxy` function so the frontend follows the Next.js 16 routing boundary convention.

#### Scenario: Unauthenticated user opens a protected route through the proxy
- **WHEN** an unauthenticated user opens `/`, `/backtests`, `/market`, `/screener`, `/diagnosis`, `/factors`, or `/portfolio`
- **THEN** the proxy redirects the request to `/login` with the original route encoded in the `next` query parameter

#### Scenario: User opens an unprotected route through the proxy
- **WHEN** a user opens `/login`, a frontend auth API route, a backend proxy API route, or a Next.js asset route
- **THEN** the proxy lets the request continue without forcing the application login redirect

### Requirement: Frontend SHALL configure Turbopack with an explicit application root
The system SHALL configure the Next.js Turbopack root as an absolute path to the frontend application directory so local builds do not rely on ambiguous workspace-root inference.

#### Scenario: Frontend build reads Next.js configuration
- **WHEN** the frontend build or dev server loads `next.config.ts`
- **THEN** the Turbopack configuration contains an absolute `root` value for the frontend workspace

### Requirement: Frontend SHALL provide executable browser smoke coverage for critical workbench flows
The system SHALL provide a repeatable browser smoke test lane that validates login, unauthenticated redirect, authenticated workbench entry, and mobile dashboard entry.

#### Scenario: Browser smoke tests run against local services
- **WHEN** the smoke test command starts the local backend and frontend services
- **THEN** the browser tests can verify the login page, protected redirect behavior, authenticated dashboard rendering, representative workbench pages, and a mobile viewport without relying on manual inspection
