---
title: Adopt AKQuant behind a stable backtest adapter
date: 2026-05-21
category: docs/solutions/tooling-decisions
module: backend/backtesting
problem_type: tooling_decision
component: service_object
severity: medium
applies_when:
  - replacing an in-house financial runtime with a third-party engine
  - keeping existing API and frontend contracts stable during a runtime migration
tags: [akquant, backtesting, adapter, openspec, financial-runtime]
---

# Adopt AKQuant behind a stable backtest adapter

## Context
The project needed to replace the in-house backtesting execution path with
`akfamily/akquant` while preserving the backend API and frontend workbench
contract. The old `backend/backtesting/*` modules still contained useful
preset metadata and legacy signal generation behavior, so deleting them outright
would have made the migration larger and riskier than needed.

## Guidance
Keep the third-party runtime behind a dedicated backend adapter and make the
application contract the stable boundary.

In this repo that means:

- `backend/app/services/backtests_akquant.py` owns AKQuant integration,
  request normalization, execution policy, error translation, and response
  serialization.
- `backend/app/services/backtests.py` remains a compatibility export so existing
  imports can move without breaking at the same time as the runtime migration.
- `backend/backtesting/*` is no longer the main execution engine; it is a
  bounded compatibility layer for preset metadata, market data support, and
  legacy custom signal replay.
- OpenSpec main specs name AKQuant as the execution runtime while preserving
  legacy-field compatibility as an explicit migration concern.

## Why This Matters
Financial backtesting has many hidden assumptions: fill timing, lot size, T+1
sellability, fees, taxes, slippage, and protective exits. Moving those semantics
directly into route handlers or frontend code would couple the app to one
library shape and make future verification hard.

The adapter keeps that complexity in one place and lets tests assert the real
business contract:

- backend routes execute through `AKQuantBacktestService`;
- responses expose `settings.engine = "akquant"`, effective fill policy,
  assumptions, insights, metrics, comparison data, trade statistics, and trades;
- legacy flat payloads still map into the AKQuant-first internal request model;
- frontend pages can render richer execution metadata without duplicating
  strategy-specific behavior.

## When to Apply
- A third-party engine replaces an existing in-house implementation.
- Existing API consumers need a stable contract during migration.
- The third-party library has domain semantics that must be made visible in
  product reports.
- Legacy modules still provide useful data or metadata but should no longer own
  execution.

## Examples
Use tests to pin the adapter contract rather than the third-party internals:

```text
backend/tests/test_backtest_engine_upgrade.py
backend/tests/test_backtest_reporting_contract.py
backend/tests/test_backtests_api.py
```

The critical checks are:

- the service invokes AKQuant through `runtime_runner = akquant.run_backtest`;
- `next_open` execution is represented through the effective fill policy;
- A-share trading assumptions such as round lots, T+1, fees, and stamp tax are
  reflected in the normalized result;
- protective stop/take-profit exits survive serialization even when AKQuant
  trade tags are normalized by the runtime.

## Related
- `openspec/specs/akquant-runtime-adapter/spec.md`
- `openspec/specs/backtest-execution-and-reporting/spec.md`
- `openspec/changes/archive/2026-05-21-adopt-akquant-backtesting-engine/`
