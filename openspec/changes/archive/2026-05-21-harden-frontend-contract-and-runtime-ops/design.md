## Context

The current system already has a completed Flask backend contract, a root `openapi.json`, and a Huashu-style Next.js workbench frontend. The remaining gaps are not new product capabilities; they are operational hardening around framework compatibility, contract drift detection, browser-level confidence, and external upstream resilience.

Next.js 16 deprecates `middleware.ts` in favor of `proxy.ts`, with `proxy` running on the Node.js runtime. The current protected route guard only checks a local access-token cookie and does not require Edge-only behavior, so it can move to `proxy.ts`.

## Goals / Non-Goals

**Goals:**

- Make `frontend/proxy.ts` the canonical protected route gate for Next.js 16.
- Configure Turbopack with an explicit absolute frontend root.
- Ensure frontend OpenAPI route bindings fail tests when path, method, or security declarations drift.
- Add a browser smoke lane that exercises login, redirects, authenticated workbench navigation, and mobile entry.
- Return degraded/cache metadata for market/news upstream failures instead of unbounded exceptions where cached data exists.

**Non-Goals:**

- Do not redesign the frontend visual language again.
- Do not replace the completed AKQuant backtest adapter.
- Do not introduce Redis, databases, background workers, or distributed caching.
- Do not stage or commit changes.
- Do not delete files unless explicit dangerous-operation confirmation is available.

## Decisions

### 1. Canonical proxy entry with guarded middleware deletion

`frontend/proxy.ts` becomes the canonical implementation and exports `proxy`. The workspace rules treat file deletion as a dangerous operation, so this change avoids deleting `frontend/middleware.ts` unless explicit confirmation is available. If the old file remains, it must only delegate to the canonical proxy implementation and must not keep a separate copy of the route logic.

Alternative considered: run the official codemod and remove `middleware.ts` immediately. That would be technically cleaner for eliminating the warning, but it violates the workspace confirmation rule for file deletion.

### 2. Verification-first OpenAPI binding improvement

The current binding table remains a small curated table because the project has no OpenAPI generator dependency yet. This change strengthens verification around it instead of adding a new generated-client dependency in the same pass. Tests compare every binding to `openapi.json`, assert public/protected security alignment, and ensure protected BFF routes cannot drift outside the contract.

Alternative considered: add a full TypeScript OpenAPI generator. That is a larger dependency and code-shape change better suited to a later dedicated change once the current contract is stable.

### 3. Playwright smoke tests stay in a separate lane

Browser smoke tests use a separate `test:smoke` script so unit/build validation remains fast and deterministic. The smoke server script starts backend and frontend services together and shuts them down on process exit.

Alternative considered: fold browser behavior into Vitest. That would not prove the actual routed browser experience, especially redirects and authenticated page rendering.

### 4. In-memory TTL cache for external market/news data

Market/news services gain small per-process TTL caches for successful upstream payloads. A failed refresh may return cached data with `degraded: true` and warnings. This avoids over-building infrastructure while still giving users inspectable stale data during transient upstream failures.

Alternative considered: persistent cache. That adds lifecycle and invalidation concerns out of proportion to the current local research workbench.

## Risks / Trade-offs

- `[middleware.ts remains present]` -> `proxy.ts` becomes canonical now; the final warning removal requires explicit deletion confirmation later.
- `[Smoke tests depend on local browser availability]` -> keep them isolated under `npm run test:smoke` and report browser-install failures as environment blockers.
- `[Cached market data can be stale]` -> add degraded metadata and warning text whenever stale cache is returned after a refresh failure.
- `[Retry can amplify upstream load]` -> keep retry bounded and only retry direct HTTP fallback paths.

## Migration Plan

1. Create the OpenSpec source of truth for the hardening work.
2. Add the canonical proxy entry and Turbopack root config.
3. Strengthen OpenAPI route-binding tests and BFF protection behavior.
4. Add Playwright smoke infrastructure and route tests.
5. Add bounded cache-backed degraded behavior for market/news services.
6. Run targeted tests, strict OpenSpec validation, and archive the completed change.

Rollback strategy:

- Proxy migration can be rolled back by pointing route-guard logic back to the previous middleware implementation.
- OpenAPI binding tests are additive and can be narrowed if they reveal a deliberate contract exception.
- Browser smoke infrastructure is isolated under its own script.
- Cache-backed degraded behavior is contained inside service classes and can be disabled by setting TTL to zero in tests or future configuration.
