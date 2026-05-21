## 1. Runtime And Contract Setup

- [x] 1.1 Add the canonical Next.js 16 `proxy.ts` route guard and configure absolute `turbopack.root`.
- [x] 1.2 Strengthen frontend OpenAPI binding tests for path, method, public/protected security alignment, and protected proxy eligibility.

## 2. Browser Smoke Verification

- [x] 2.1 Add Playwright smoke test dependencies, config, local service starter, and `test:smoke` script.
- [x] 2.2 Add browser smoke tests for login, unauthenticated redirect, authenticated workbench entry, and mobile dashboard entry.

## 3. External Data Degradation Hardening

- [x] 3.1 Add bounded cache-backed degraded behavior for market quote and sector responses.
- [x] 3.2 Add bounded cache-backed degraded behavior for Jin10 latest-news and intelligence responses.

## 4. Verification And Closeout

- [x] 4.1 Run targeted frontend/backend tests and update implementation until they pass or produce an environment blocker.
- [x] 4.2 Run strict OpenSpec validation, sync/archive the completed change, and record reusable learning if this change creates a durable pattern.
