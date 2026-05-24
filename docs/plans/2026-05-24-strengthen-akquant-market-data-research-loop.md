---
title: Strengthen AKQuant Market Data Research Loop
date: 2026-05-24
status: active
origin: docs/brainstorms/2026-05-24-strengthen-akquant-market-data-research-loop.md
---

# Strengthen AKQuant Market Data Research Loop Plan

## Problem Frame

当前系统已经把回测执行迁移到 AKQuant，并建立了 AkShare-first 行情契约。但行情源仍主要依赖 AkShare 与少量直连接口，回测适配层还没有充分暴露 AKQuant 的成交量限制、费用、风险控制、事件流和诊断信息。用户要求优先增强行情数据接入 TickFlow，同时继续参考 `daily_stock_analysis` 的多源数据与研究闭环设计。

## Scope Boundaries

本轮交付：

- 升级 AkShare，加入 TickFlow 依赖和配置。
- 为历史行情和报价增加 TickFlow provider 与降级诊断。
- 扩展回测请求、AKQuant runtime 参数和结果报告。
- 同步 OpenAPI、前端类型、前端回测控件和结果展示。
- 更新 README 与后端环境变量说明。

本轮不交付：

- 不新增新闻搜索 provider 集群和社交舆情页面。
- 不新增没有后端接口支撑的功能入口。
- 不把 TickFlow 设为默认唯一行情源。
- 不引入新的根目录 Python runtime 或旧 Streamlit 路径。

## Key Decisions

- **AkShare 仍是默认主源。** 这样保留当前 A 股研究默认路径，降低切换数据口径造成的回测结果漂移。
- **TickFlow 默认作为第二历史源。** 可通过 `BACKEND_MARKET_DATA_PREFER_TICKFLOW=true` 显式提到首位，适合用户主动验证 TickFlow 质量时使用。
- **TickFlow 报价仅在 `TICKFLOW_API_KEY` 存在时启用。** 免费服务不提供实时行情，前端和 API 不应暗示无 key 也有实时 TickFlow 报价。
- **回测高级风险字段以单策略 `signal_replay` ID 传给 AKQuant。** 当前适配层每次运行一个主信号回放策略，因此策略级风控 map 使用稳定 ID，而不是股票代码。
- **结果报告新增诊断对象而不破坏既有字段。** 前端和历史调用者仍可读取原有 `metrics`、`tradeStats`、`series`、`trades`。

## Implementation Units

### U1: OpenSpec Artifacts

Files:

- `openspec/changes/strengthen-akquant-market-data-research-loop/proposal.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/design.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/tasks.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/specs/akshare-market-data-orchestration/spec.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/specs/akquant-runtime-adapter/spec.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/specs/backtest-execution-and-reporting/spec.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/specs/backend-openapi-publication/spec.md`
- `openspec/changes/strengthen-akquant-market-data-research-loop/specs/openapi-driven-frontend-client/spec.md`

Verification:

- `openspec status --change strengthen-akquant-market-data-research-loop --json`
- `openspec validate --all --strict`

### U2: Dependencies and Configuration

Files:

- `backend/pyproject.toml`
- `backend/poetry.lock`
- `backend/uv.lock`
- `backend/app/config.py`
- `backend/.env.example`
- `README.md`
- `backend/README.md`

Approach:

- Upgrade AkShare pin to `1.18.63`.
- Add TickFlow pin `0.1.21`.
- Add env vars for TickFlow API key, base URL, free base URL, enable flag, preference flag, and timeout.

Verification:

- `cd backend && poetry lock`
- `cd backend && uv lock`
- `cd backend && poetry check`

### U3: TickFlow Market Data Provider

Files:

- `backend/backtesting/data.py`
- `backend/tests/test_data_provider_priority.py`

Approach:

- Add symbol conversion helpers for A 股 TickFlow suffixes.
- Add `TickflowProvider` with lazy import and lazy client creation.
- Normalize TickFlow DataFrame rows into the shared OHLCV contract.
- Track `lastSuccessSource` and `lastErrors` in `SmartDataProvider`.
- Support `BACKEND_MARKET_DATA_PREFER_TICKFLOW`.

Verification:

- `cd backend && poetry run pytest tests/test_data_provider_priority.py -q`

### U4: TickFlow Quote Fallback

Files:

- `backend/app/services/market_data.py`
- `backend/tests/test_market_data_resilience.py`
- `backend/tests/test_market_api.py`

Approach:

- Add optional TickFlow quote client injection for tests.
- Use TickFlow quote fallback after AkShare and before EastMoney direct when API key is configured.
- Normalize TickFlow quote fields and return source metadata.

Verification:

- `cd backend && poetry run pytest tests/test_market_data_resilience.py tests/test_market_api.py -q`

### U5: AKQuant Request and Runtime Enhancement

Files:

- `backend/app/schemas/backtests.py`
- `backend/app/services/backtests_akquant.py`
- `backend/tests/test_backtests_api.py`
- `backend/tests/test_backtest_engine_upgrade.py`
- `backend/tests/test_backtest_reporting_contract.py`

Approach:

- Add `volumeLimitPct`, `minCommission`, `transferFeeRate`, `maxDrawdown`, `maxDailyLoss`, `maxPositionSize`, `reduceOnlyAfterRisk`, `riskCooldownBars`.
- Pass safe runtime args to AKQuant.
- Use `strategy_id="signal_replay"` for strategy-level risk maps.
- Collect `on_event` event counts and warnings.
- Add `dataQuality`, `executionQuality`, `riskDiagnostics`, `engineEvents` to each symbol result.

Verification:

- `cd backend && poetry run pytest tests/test_backtests_api.py tests/test_backtest_engine_upgrade.py tests/test_backtest_reporting_contract.py -q`

### U6: OpenAPI and Frontend Contract

Files:

- `backend/app/openapi.py`
- `backend/tests/test_openapi_publication.py`
- `openapi.json`
- `frontend/types/api.ts`
- `frontend/lib/backtests.ts`
- `frontend/lib/backtests.test.ts`
- `frontend/components/backtest-console.tsx`

Approach:

- Ensure OpenAPI exposes the expanded request schema and response diagnostic fields.
- Update TypeScript types and payload builder.
- Add Chinese-only UI controls and report panels for the new fields.

Verification:

- `cd backend && uv run python scripts/generate_openapi.py`
- `cd backend && poetry run pytest tests/test_openapi_publication.py -q`
- `cd frontend && npm test`
- `cd frontend && npm run build`

### U7: Documentation, Verification, Archive, and Compound

Files:

- `README.md`
- `backend/README.md`
- `docs/solutions/tooling-decisions/*.md`
- `openspec/changes/archive/**`

Approach:

- Update startup/config docs and current capability table.
- Run OpenSpec verify fallback and archive only after tasks and tests are complete.
- Add durable Compound Engineering solution note for future TickFlow/AKQuant work.

Verification:

- `openspec validate --all --strict`
- Manual verification report against proposal, specs, tasks, implementation, and tests.
