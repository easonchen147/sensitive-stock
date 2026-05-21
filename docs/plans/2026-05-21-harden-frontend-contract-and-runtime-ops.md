# Harden Frontend Contract And Runtime Ops Plan

## Problem Frame

The platform now has a completed Flask/OpenAPI backend and a Huashu-style Next.js workbench frontend, but the optimization pass surfaced four operational gaps that should be closed before the system is treated as stable: Next.js 16 runtime hygiene, stronger OpenAPI route binding verification, executable browser smoke coverage, and bounded external-market degradation behavior.

## Scope

This plan targets the existing runtime, contract, and resilience surfaces. It does not redesign the Huashu visual system, replace AKQuant work already completed, or introduce a new backend framework.

## Requirements Traceability

- Runtime hygiene: migrate the protected-route guard toward the Next.js 16 `proxy.ts` convention and configure Turbopack with an explicit root.
- Contract hygiene: make frontend route bindings prove both path/method existence and public/protected security alignment against `openapi.json`.
- Browser verification: add repeatable smoke coverage for login, protected redirects, authenticated dashboard/workbench pages, and mobile layout entry.
- Degradation behavior: make market/news external fetch failures bounded, observable, and cache-backed where a previously successful payload exists.
- Workflow constraint: do not stage or commit during this work.

## Key Decisions

1. Keep the route guard logic shared and move the canonical entry to `frontend/proxy.ts`.
   Next.js 16 documents `proxy.ts` as the replacement for `middleware.ts`. Because deleting files is a guarded operation in this workspace, this implementation can keep any old file only as transitional compatibility; the canonical implementation must live in `proxy.ts`.

2. Treat `openapi.json` as a verification input, not only documentation.
   The binding table in `frontend/lib/openapi-client.ts` remains hand-curated for now, but tests must fail when it drifts from the backend contract or declares a protected route as public.

3. Use Playwright smoke tests as a separate explicit verification lane.
   Unit tests still cover helpers and contracts. Smoke tests start local frontend/backend services and verify the user-visible protected flows through a browser.

4. Add small in-memory TTL caches for external market/news responses.
   This is enough to bound repeated upstream failures without introducing persistence, background workers, or distributed cache concerns.

## Implementation Units

### U1: OpenSpec Change Source

Files:
- `openspec/changes/harden-frontend-contract-and-runtime-ops/proposal.md`
- `openspec/changes/harden-frontend-contract-and-runtime-ops/design.md`
- `openspec/changes/harden-frontend-contract-and-runtime-ops/specs/**/spec.md`
- `openspec/changes/harden-frontend-contract-and-runtime-ops/tasks.md`

Approach:
- Define modified requirements for `nextjs-frontend-shell`, `openapi-driven-frontend-client`, `akshare-market-data-orchestration`, and `jin10-news-intelligence-pipeline`.
- Keep implementation tasks small and directly verifiable.

Verification:
- `openspec validate harden-frontend-contract-and-runtime-ops --strict`

### U2: Next.js Runtime Hygiene

Files:
- `frontend/proxy.ts`
- `frontend/middleware.ts`
- `frontend/next.config.ts`
- `frontend/lib/auth.test.ts`

Approach:
- Add `frontend/proxy.ts` as the canonical protected-route gate with `export function proxy`.
- Configure `turbopack.root` with an absolute path derived from `__dirname`.
- Keep helper-level tests focused on protected route coverage and redirect behavior.

Test Scenarios:
- Unauthenticated protected routes redirect to `/login?next=...`.
- Login and API routes remain unprotected.
- Turbopack root is an absolute frontend path.

Verification:
- `cd frontend; npm test`
- `cd frontend; npm run build`

### U3: OpenAPI Route Binding Hardening

Files:
- `frontend/lib/openapi-client.ts`
- `frontend/lib/openapi-client.test.ts`
- `frontend/app/api/backend/[...slug]/route.ts`

Approach:
- Strengthen tests so every binding matches OpenAPI path/method and security.
- Verify every non-public OpenAPI operation has a frontend route binding or a documented reason for exclusion.
- Keep the BFF proxy constrained to protected OpenAPI bindings.

Test Scenarios:
- Public bindings correspond to OpenAPI operations with `security: []`.
- Protected bindings correspond to operations with `bearerAuth`.
- Every protected BFF route maps to a known OpenAPI binding.

Verification:
- `cd frontend; npm test`

### U4: Browser Smoke Verification

Files:
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/playwright.config.ts`
- `frontend/scripts/smoke-server.mjs`
- `frontend/tests/smoke/workbench-smoke.spec.ts`

Approach:
- Add a `test:smoke` script using Playwright.
- Start backend and frontend local services for smoke runs without requiring global tooling.
- Verify login, unauthenticated redirect, authenticated dashboard/workbench pages, and mobile viewport entry.

Test Scenarios:
- `/login` renders the login workflow.
- `/market` redirects to `/login` when unauthenticated.
- A successful login lands on the dashboard.
- Dashboard, backtests, screener, and market pages render under authenticated session.
- The dashboard remains navigable at a mobile viewport.

Verification:
- `cd frontend; npm run test:smoke`

### U5: Market And News Degradation Resilience

Files:
- `backend/app/services/market_data.py`
- `backend/app/services/news_intelligence.py`
- `backend/tests/test_market_api.py`
- `backend/tests/test_news_intelligence_service.py`

Approach:
- Add bounded retry and TTL cache helpers for external fetches.
- Return degraded metadata and warnings when falling back to cached data.
- Preserve current response shapes while adding optional `degraded` and `warnings` fields to market quote/sector payloads.

Test Scenarios:
- AkShare success returns non-degraded source metadata.
- Eastmoney fallback success returns degraded metadata with fallback source.
- A repeated upstream failure returns the cached prior payload with warning metadata.
- Jin10 primary/fallback failure can return cached news with `degraded: true` and warnings.

Verification:
- `cd backend; uv run pytest tests/test_market_api.py tests/test_news_intelligence_service.py -q`

### U6: Final Verification, Archive, And Learning

Files:
- `openapi.json`
- `openspec/specs/**/spec.md`
- `openspec/changes/archive/**`
- `docs/solutions/**`

Approach:
- Run affected backend/frontend tests and OpenSpec validation.
- Sync modified specs by archiving the completed change.
- Capture a reusable solution note if the change produces a durable pattern.

Verification:
- `openspec validate --all --strict`
- `git diff --check`

## Risks And Mitigations

- Playwright browsers may be unavailable in the local environment -> keep smoke tests isolated under `test:smoke` and report any environment blocker distinctly from unit/build results.
- Deleting `frontend/middleware.ts` would remove the Next 16 deprecation warning but is guarded by workspace dangerous-operation rules -> make `frontend/proxy.ts` canonical first and avoid deletion unless explicit confirmation is available.
- Cache helpers can hide upstream failures -> attach degraded metadata and warnings whenever cached data is returned after a failed refresh.

## Verification Strategy

Run targeted tests after each implementation unit, then finish with frontend test/build, backend focused tests/full tests where feasible, OpenSpec strict validation, and whitespace diff checks. No staging or commit operations are part of this plan.
