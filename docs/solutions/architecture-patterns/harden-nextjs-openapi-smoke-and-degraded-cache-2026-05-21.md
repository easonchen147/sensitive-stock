---
title: Harden Next.js OpenAPI workbenches with smoke tests and degraded caches
date: 2026-05-21
category: docs/solutions/architecture-patterns
module: frontend/backend runtime hardening
problem_type: architecture_pattern
component: tooling
severity: medium
applies_when:
  - a Next.js frontend is governed by a backend OpenAPI contract
  - protected page routing, BFF proxy forwarding, and backend auth must stay aligned
  - external market or news sources can fail but stale recent data is still useful
tags: [nextjs, openapi, playwright, degraded-cache, smoke-tests]
---

# Harden Next.js OpenAPI workbenches with smoke tests and degraded caches

## Context

The system already had a Flask OpenAPI backend and a Huashu-style Next.js
workbench frontend. The remaining risk was operational: Next.js 16 deprecated
`middleware.ts`, frontend bindings could still drift from `openapi.json`,
browser flows lacked formal smoke coverage, and external market/news failures
could leave users with either raw errors or no useful stale context.

## Guidance

Treat runtime hygiene, contract verification, browser smoke, and degraded data
as one hardening pass when they protect the same user flows.

For this repo, the pattern is:

- Use `frontend/proxy.ts` as the canonical protected-route gate for Next.js 16.
- Configure `frontend/next.config.ts` with an absolute `turbopack.root`.
- Keep `frontend/lib/openapi-client.test.ts` strict about OpenAPI path,
  method, and public/protected security alignment.
- Add `frontend/tests/smoke/` with Playwright checks for login, protected
  redirects, authenticated dashboard/workbench entry, and mobile entry.
- Use a small shared `TTLCache` in backend services so successful external
  market/news payloads can be reused as explicit degraded responses after
  transient upstream failures.

## Why This Matters

OpenAPI-driven pages can still fail in ways that unit tests miss. A binding
table can drift from security declarations; a protected page can pass helper
tests but fail in a browser; an upstream source can fail after a user has
already seen useful recent data. The stable operating pattern is to make each
failure mode visible and testable:

- contract drift fails at Vitest level;
- route/login regressions fail at Playwright level;
- upstream outages return `degraded: true` plus warnings when cached data is
  used;
- production build remains the smoke target instead of relying on a dev-server
  state that can differ from deployable output.

## When to Apply

- The frontend is a Next.js App Router application with protected routes.
- Backend APIs are published through a static or runtime OpenAPI document.
- Browser-level confidence is needed but a full E2E suite would be excessive.
- Market-data or news providers are external and intermittently unreliable.

## Examples

The verification lane is intentionally layered:

```bash
cd frontend
npm test
npm run build
npm run test:smoke

cd ../backend
uv run pytest -q
uv run ruff check app tests scripts
```

The degraded-cache service behavior should stay explicit:

```python
cached = self._cache.get(cache_key)
if cached is None:
    raise
return {
    **cached,
    "degraded": True,
    "warnings": [*cached.get("warnings", []), "using cached market data"],
}
```

## Related

- `frontend/proxy.ts`
- `frontend/lib/openapi-client.test.ts`
- `frontend/tests/smoke/workbench-smoke.spec.ts`
- `backend/app/services/runtime_cache.py`
- `backend/app/services/market_data.py`
- `backend/app/services/news_intelligence.py`
- `openspec/specs/nextjs-frontend-shell/spec.md`
- `openspec/specs/openapi-driven-frontend-client/spec.md`
- `openspec/specs/akshare-market-data-orchestration/spec.md`
- `openspec/specs/jin10-news-intelligence-pipeline/spec.md`
