---
title: Build Chinese runtime terminals from API truth boundaries
date: 2026-05-23
category: docs/solutions/design-patterns
module: frontend/app
problem_type: design_pattern
component: frontend_stimulus
severity: medium
applies_when:
  - redesigning data-heavy Chinese financial workbenches
  - removing migration labels or unsupported feature cards from production UI
  - binding frontend pages to a generated OpenAPI backend contract
tags: [frontend-design, huashu-design, openapi, chinese-ui, capability-status]
---

# Build Chinese runtime terminals from API truth boundaries

## Context
The product needed to move from a migration-era interface to a production-facing
Chinese A-share research terminal. The old UI could show labels such as
"migrated", "skeleton", or "planned", and some components described future or
partial capabilities instead of only showing callable workflows.

This created two problems: visual inconsistency across workbench pages, and a
risk that the UI implied capabilities not backed by backend routes.

## Guidance
Use the OpenAPI contract as the visible feature boundary. A page feature should
exist only when it maps to one of these sources:

- a real backend route published through `backend/app/openapi.py`
- a route binding in `frontend/lib/openapi-client.ts`
- a local authentication route such as login, logout, or session

For the UI language, use product runtime states instead of delivery states:

- `ready` -> 可用
- `limited` -> 受限
- `disabled` -> 停用

Do not expose migration process labels in navigation, cards, empty states,
status chips, or workbench result panels. If a workflow is not implemented,
remove the visible feature instead of explaining that it is a future capability.

For the visual system, keep a restrained Chinese terminal grammar:

- dark left navigation rail, light work area, compact metric tiles
- shared module headers, toolbars, data tables, state surfaces, risk panels,
  and explanation panels
- Chinese labels for buttons, tables, states, errors, and empty results
- technical identifiers only where they carry business meaning, such as stock
  codes, dates, model configuration values, or API contract files

## Why This Matters
Financial research tools lose trust when the UI advertises roadmap state instead
of runtime truth. A user should know what can be called now, what is degraded,
and what is unavailable without seeing implementation history.

The API truth boundary also gives the frontend a verification target. When
`openapi.json`, `frontend/lib/openapi-client.ts`, and page features stay aligned,
contract drift becomes searchable and testable instead of a visual review guess.

## When to Apply
- A workbench has multiple pages that all depend on backend contracts.
- The product is leaving an incremental migration phase.
- Users need a Chinese production interface rather than developer-facing status
  copy.
- The backend can degrade gracefully with empty results rather than 500s for
  unavailable data providers.

## Examples
Core files from this implementation:

```text
backend/app/openapi.py
backend/app/services/capabilities.py
backend/app/services/market_data.py
frontend/app/globals.css
frontend/components/app-shell.tsx
frontend/components/workbench-layout.tsx
frontend/lib/openapi-client.ts
frontend/lib/display.ts
frontend/tests/smoke/workbench-smoke.spec.ts
openapi.json
```

Verification loop:

```bash
cd backend
uv run pytest -q
uv run ruff check app tests scripts

cd ../frontend
npx tsc --noEmit --pretty false
npm test
npm run test:smoke

cd ..
openspec validate --all --strict
git diff --check
```

Browser verification should include both desktop and mobile viewports. Check the
login page, dashboard, market prediction page, and backtest page for visible
Chinese labels, non-overlapping controls, and absence of migration labels.

## Related
- `docs/solutions/design-patterns/quiet-capital-terminal-openapi-workbenches-2026-05-21.md`
- `docs/solutions/architecture-patterns/harden-nextjs-openapi-smoke-and-degraded-cache-2026-05-21.md`
- `openspec/changes/unify-chinese-ui-prediction-loop/`
