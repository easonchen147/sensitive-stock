---
title: Keep runtime contract language aligned across OpenSpec, OpenAPI, and UI copy
date: 2026-05-23
category: docs/solutions/architecture-patterns
module: openspec/specs
problem_type: documentation_gap
component: documentation
severity: medium
applies_when:
  - retiring transitional capability language after a formal runtime is live
  - making generated OpenAPI the source of truth for frontend integration
  - returning backend text that is rendered directly in a Chinese UI
tags: [openspec, openapi, runtime-contract, chinese-copy, verification]
---

# Keep runtime contract language aligned across OpenSpec, OpenAPI, and UI copy

## Context
The system had already moved to formal backend APIs, OpenAPI-governed frontend
bindings, and Chinese research workbenches. A few authoritative surfaces still
used transitional wording: main OpenSpec specs described delivery states, README
sections talked about former capability phases, and some backend response text
still exposed raw engine or English copy.

That drift matters because future implementation work tends to follow the
specs and generated contracts. If those sources still describe transitional
states, new code can reintroduce old product semantics even after the runtime is
already formal.

## Guidance
Treat runtime language as a contract layer, not as cosmetic copy. When a
capability becomes formal, update these surfaces together:

- `openspec/specs/*/spec.md`: requirements should describe current product
  states and callable behavior.
- `backend/app/openapi.py` and `openapi.json`: summaries and tag descriptions
  should describe stable API contracts, not implementation rollout history.
- Backend direct-render text: fields such as preset descriptions, risk notes,
  assumption details, and handoff notes should use product language suitable for
  the frontend.
- Runtime docs: README and architecture docs should explain what works now and
  what is explicitly limited, without leaking delivery-phase labels.
- Tests: update contract and rendering assertions so the new language is
  checked, not just manually reviewed.

Keep machine identifiers stable. Values such as `akquant`, `next_open`,
`event_theme_momentum`, route paths, stock codes, and model names are part of
the technical contract and can remain literal. Change the user-facing
explanation around them.

## Why This Matters
Spec drift is a product risk in OpenSpec-driven projects. If the active specs
say one thing and the runtime says another, future changes can follow the wrong
source of truth.

Generated OpenAPI also feeds frontend route bindings and external integration.
Stable, neutral summaries make the API read like a platform boundary instead of
an implementation diary.

## When to Apply
- A migration or staged build has finished and the runtime is now formal.
- The UI must remove transitional labels before being treated as production
  facing.
- Backend responses include display-ready text rendered by frontend pages.
- OpenSpec changes are archived but the merged main specs still carry old
  wording.

## Examples
Files that usually need to move together:

```text
openspec/specs/flask-backend-platform/spec.md
openspec/specs/nextjs-frontend-shell/spec.md
openspec/specs/backend-openapi-publication/spec.md
backend/app/openapi.py
backend/backtesting/presets.py
backend/app/services/backtests_akquant.py
backend/app/services/news_intelligence.py
openapi.json
README.md
backend/README.md
docs/architecture/directory-map.md
docs/migration/phase-one-architecture-migration.md
```

Useful verification loop:

```bash
cd backend
uv run pytest -q
uv run ruff check app tests scripts
uv run python scripts/generate_openapi.py --output ..\openapi.json

cd ..\frontend
npx tsc --noEmit --pretty false
npm test
npm run test:smoke

cd ..
openspec validate --all --strict
git diff --check
```

Search for stale terms after the edit. Literal HTML attributes such as
`placeholder="请输入管理员用户名"` are not evidence of unsupported feature
semantics; delivery-state labels in specs, README, response text, or visible UI
are.

## Related
- `docs/solutions/design-patterns/chinese-runtime-terminal-api-truth-boundary.md`
- `docs/solutions/tooling-decisions/global-openapi-contract-for-flask-backend-2026-05-21.md`
- `openspec/changes/remove-runtime-migration-state-residue/`
