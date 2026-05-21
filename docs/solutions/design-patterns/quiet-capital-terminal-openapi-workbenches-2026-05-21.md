---
title: Use a Quiet Capital Terminal system for OpenAPI workbenches
date: 2026-05-21
category: docs/solutions/design-patterns
module: frontend/app
problem_type: design_pattern
component: frontend_stimulus
severity: medium
applies_when:
  - redesigning data-heavy financial research pages
  - connecting multiple frontend workbenches to a shared OpenAPI backend contract
tags: [frontend-design, huashu, openapi-client, workbench, state-surfaces]
---

# Use a Quiet Capital Terminal system for OpenAPI workbenches

## Context
The frontend had usable pages for login, dashboard, backtests, and market data,
plus newly migrated screener, diagnosis, factor, and portfolio workflows. The
problem was consistency: page structure, status language, and API path ownership
could drift as each workbench grew independently.

## Guidance
For data-heavy financial research tools, use a restrained terminal-like product
language rather than a marketing-page composition.

In this repo that means:

- `frontend/app/globals.css` owns the Quiet Capital Terminal tokens and layout
  rules: low-noise surfaces, strong information hierarchy, 8px-or-less radius,
  compact controls, and visible status treatments.
- `frontend/components/workbench-layout.tsx` owns shared workbench headers,
  metric tiles, and loading/empty/degraded/error/ready state surfaces.
- Every major page starts from the same workbench grammar: summary, controls,
  results, and explanation/status context.
- `frontend/lib/openapi-client.ts` is the route binding table from frontend
  route keys to backend OpenAPI paths.
- `frontend/lib/openapi-client.test.ts` verifies the route binding table against
  the generated root `openapi.json`, so contract drift becomes a test failure.

## Why This Matters
Financial research interfaces need scanability, not decoration. A user moving
from backtesting to screening to portfolio optimization should not have to learn
new page structure every time. The visual system should make the state of the
workflow obvious: no result yet, request running, backend degraded, failed, or
ready.

The OpenAPI route binding table also keeps frontend integration honest. Page
helpers can still use ergonomic functions, but the actual backend path must be
registered once and validated against the published contract.

## When to Apply
- Multiple workbench pages consume related backend APIs.
- Backend OpenAPI is already generated and tested.
- Product value comes from interpreting data and workflow state, not visual
  novelty.
- Pages need to expose degraded or partial backend results without pretending
  they are either fully healthy or fully unavailable.

## Examples
Core files:

```text
frontend/app/globals.css
frontend/components/workbench-layout.tsx
frontend/lib/openapi-client.ts
frontend/lib/openapi-client.test.ts
```

Verification loop:

```bash
cd frontend
npm test
npm run build
```

Browser verification should include at least one authenticated dashboard page,
one form-heavy workbench, and one mobile viewport. In this migration those were
covered with the login/dashboard/screener flows through local Next.js and Flask
servers.

## Related
- `openspec/specs/frontend-research-design-system/spec.md`
- `openspec/specs/openapi-driven-frontend-client/spec.md`
- `openspec/specs/nextjs-frontend-shell/spec.md`
- `openspec/changes/archive/2026-05-21-redesign-frontend-with-huashu-openapi/`
