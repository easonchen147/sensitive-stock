---
title: Publish a global OpenAPI contract from the Flask backend
date: 2026-05-21
category: docs/solutions/tooling-decisions
module: backend/openapi
problem_type: tooling_decision
component: service_object
severity: medium
applies_when:
  - a Flask backend needs to become the stable contract source for frontend work
  - route, schema, auth, and placeholder capability drift must be caught by tests
tags: [openapi, flask, contract-tests, backend-platform, frontend-integration]
---

# Publish a global OpenAPI contract from the Flask backend

## Context
The backend had real Flask routes for auth, capabilities, market data, and
AKQuant-backed backtests, plus skeleton endpoints for screener, diagnosis,
factors, and portfolio. The missing piece was a single contract artifact that
frontend work and future external consumers could trust.

## Guidance
Keep OpenAPI publication close to the Flask backend, but do not change the
framework just to get OpenAPI support.

In this repo:

- `backend/app/openapi.py` owns the OpenAPI document assembly.
- `backend/app/api/openapi.py` exposes `GET /api/v1/openapi.json` at runtime.
- `backend/scripts/generate_openapi.py` writes the static root `openapi.json`.
- `backend/tests/test_openapi_publication.py` pins path coverage, security
  declarations, shared schemas, and static generation.

The published document should cover both migrated capabilities and temporary
skeleton endpoints. Skeletons are still part of the platform surface while the
frontend depends on them, but their response schema must make their migration
status explicit.

## Why This Matters
A route list is not enough for a frontend/backend split. The useful contract is
the combination of:

- concrete paths and methods;
- request and response schemas;
- shared error envelope;
- reusable bearer-token security scheme;
- source and degraded metadata conventions;
- a generated artifact that tests can compare against.

Making OpenAPI generation a tested backend behavior catches contract drift
before frontend integration work consumes stale assumptions.

## When to Apply
- A Flask backend already exists and replacing the framework would be avoidable
  scope expansion.
- Frontend pages need a single source of truth for API paths and types.
- Some capabilities are complete while others are still skeletons.
- Auth rules must be visible to tooling, not just enforced at runtime.

## Examples
The critical verification loop is:

```bash
cd backend
uv run python scripts/generate_openapi.py
uv run pytest tests/test_openapi_publication.py -q
uv run ruff check app tests backtesting scripts
```

The generated contract should be accessible through both:

- `GET /api/v1/openapi.json`
- `openapi.json`

Public routes should have `security: []`; protected business routes should
declare `security: [{"bearerAuth": []}]`.

## Related
- `backend/app/openapi.py`
- `backend/app/api/openapi.py`
- `backend/scripts/generate_openapi.py`
- `backend/tests/test_openapi_publication.py`
- `openspec/specs/backend-openapi-publication/spec.md`
