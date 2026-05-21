---
title: Migrate placeholder capabilities through service-first workbenches
date: 2026-05-21
category: docs/solutions/architecture-patterns
module: backend/app/services
problem_type: architecture_pattern
component: service_object
severity: medium
applies_when:
  - replacing placeholder capability routes with formal product workflows
  - keeping backend APIs, OpenAPI, capability inventory, and frontend pages aligned
tags: [capability-migration, service-layer, openapi, workbench, openspec]
---

# Migrate placeholder capabilities through service-first workbenches

## Context
The project had four capability areas that were visible in navigation but still
behaved like skeletons: screener, diagnosis, factor analysis, and portfolio
optimization. Completing them required more than swapping placeholder pages for
UI forms. Each area needed a validated backend contract, a service boundary,
OpenAPI coverage, capability inventory truth, frontend workbench rendering, and
tests proving the new behavior.

## Guidance
Promote a placeholder capability by moving from the service layer outward, then
use OpenAPI and the capability inventory as drift checks.

In this repo the pattern is:

- define request/response schemas in `backend/app/schemas/` before adding route
  behavior;
- put business logic in `backend/app/services/`, not in Flask route handlers;
- expose versioned routes in `backend/app/api/` with shared validation and error
  conventions;
- update `backend/app/services/capabilities.py` only when the capability has a
  real route and tests, so `status: migrated` reflects delivered behavior;
- include every formal route and schema in `backend/app/openapi.py`;
- replace frontend placeholder pages with workbench pages that call
  `frontend/lib/api.ts` helpers and handle loading, empty, degraded, and error
  states;
- sync OpenSpec main specs before archiving the migration change.

## Why This Matters
Placeholder-to-feature migrations fail when product status, route behavior, and
frontend copy move independently. A page can look finished while the backend is
still a skeleton, or OpenAPI can claim support for a route that tests never
exercise.

The service-first sequence gives each capability one backend ownership point
and makes the visible surfaces prove the same truth:

- service tests and route tests prove the backend workflow;
- OpenAPI tests prove contract publication includes the workflow;
- frontend API helper tests prove pages use the intended backend paths;
- capability inventory tests prove navigation status matches actual
  availability;
- OpenSpec specs document the post-migration behavior after archive.

## When to Apply
- A capability already exists in navigation or docs but only returns a
  placeholder payload.
- Multiple frontend pages need to call newly formalized backend APIs.
- A route's readiness needs to be visible to users and future developers.
- OpenSpec is the formal source of truth for the migration.

## Examples
The four completed capabilities follow the same shape:

```text
backend/app/schemas/research.py
backend/app/services/screener.py
backend/app/services/diagnosis.py
backend/app/services/factors.py
backend/app/services/portfolio.py
backend/app/api/screener.py
backend/app/api/diagnosis.py
backend/app/api/factors.py
backend/app/api/portfolio.py
frontend/components/research-workbenches.tsx
```

Use targeted verification before marking the capability migrated:

```bash
cd backend
uv run pytest tests/test_research_capabilities_api.py tests/test_openapi_publication.py -q
uv run ruff check app tests scripts

cd frontend
npm test
npm run build
```

## Related
- `openspec/specs/screener-workbench/spec.md`
- `openspec/specs/diagnosis-reporting/spec.md`
- `openspec/specs/factor-analysis-api/spec.md`
- `openspec/specs/portfolio-optimization-api/spec.md`
- `openspec/changes/archive/2026-05-21-complete-skeleton-capabilities/`
