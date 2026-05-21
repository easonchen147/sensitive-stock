## Why

The backend and frontend have reached a working OpenAPI-governed workbench baseline, but several operational gaps still make the system fragile: the frontend still uses the deprecated Next.js middleware entrypoint, OpenAPI route binding checks do not yet fully prove security alignment, critical browser flows are not covered by formal smoke tests, and external market/news failures are not consistently bounded by cache-backed degraded responses.

## What Changes

- Move the protected frontend route gate to the Next.js 16 `proxy.ts` convention and configure Turbopack with an explicit application root.
- Strengthen the frontend OpenAPI binding verification so path, method, public/protected security, and BFF proxy eligibility stay aligned with `openapi.json`.
- Add executable browser smoke coverage for login, unauthenticated redirects, authenticated dashboard/workbench pages, and mobile entry.
- Harden market quotes/sectors and Jin10 news ingestion with bounded retry/cache behavior and explicit degraded metadata when upstream services fail.
- Preserve the existing backend/Next.js architecture; no framework migration, database migration, staging, or commit is included.

## Capabilities

### New Capabilities

### Modified Capabilities
- `nextjs-frontend-shell`: add Next.js 16 proxy runtime hygiene, Turbopack root configuration, and browser smoke expectations for critical frontend flows.
- `openapi-driven-frontend-client`: add route-binding verification requirements for OpenAPI path/method/security alignment and protected BFF proxy eligibility.
- `akshare-market-data-orchestration`: add cache-backed degraded responses for market quote and sector upstream failures.
- `jin10-news-intelligence-pipeline`: add cache-backed degraded responses when both primary and fallback Jin10 sources are unavailable.

## Impact

- Affected frontend code:
  - `frontend/proxy.ts`
  - `frontend/middleware.ts`
  - `frontend/next.config.ts`
  - `frontend/lib/openapi-client.ts`
  - `frontend/lib/openapi-client.test.ts`
  - `frontend/playwright.config.ts`
  - `frontend/scripts/*`
  - `frontend/tests/smoke/*`
- Affected backend code:
  - `backend/app/services/market_data.py`
  - `backend/app/services/news_intelligence.py`
  - `backend/tests/test_market_api.py`
  - `backend/tests/test_news_intelligence_service.py`
- Affected contracts:
  - frontend route binding expectations against `openapi.json`
  - optional degraded/source/warnings metadata in market/news responses
- No destructive git operation, staging, or commit is part of this change.
