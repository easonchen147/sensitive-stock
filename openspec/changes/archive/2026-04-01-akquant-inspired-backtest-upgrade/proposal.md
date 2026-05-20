## Why

当前回测主链路仍然只是对 legacy `BacktestService` 的薄封装：策略接口只有“返回信号序列”，交易执行仍是收益率乘仓位的简化模型，前后端也缺少参数模型、基准比较和可解释报表。这让回测结果很难达到“可配置、可复盘、可解释、可扩展”的工作台体验。

AKQuant 已经验证了一组更成熟的能力方向：策略参数模型化、`CurrentClose/NextOpen` 这类执行模式、风险与成本配置、详细绩效统计、前后端统一的结构化契约。本 change 需要在不引入爆炸式重构的前提下，把这些高价值能力迁入当前 Flask + Next.js 架构。

## What Changes

- 引入一套 AKQuant-inspired 的结构化回测契约：区分市场范围、执行配置、交易成本、风险控制、策略选择与参数。
- 用 A 股更真实的账本式执行逻辑升级 legacy 回测引擎，支持 `close/next_open` 执行时点、仓位比例、手数约束、佣金、印花税、滑点、止损止盈和基准对比。
- 新增策略预设目录与参数 schema，前端可直接渲染参数表单；同时保留自定义 `generate_signals(data, ctx)` 策略入口。
- 升级 Flask backtest API：返回设置回显、核心指标、基准比较、净值/回撤/仓位序列、月度收益、交易统计与告警信息，并补充策略预设元数据接口。
- 升级 Next.js 回测页：支持策略预设切换、动态参数输入、基准/执行/成本配置和更完整的结果展示。
- 更新 README、backend README、迁移文档与测试，明确本轮为“AKQuant 思路迁移版”，而不是整库直接替换。

## Capabilities

### New Capabilities
- `backtest-execution-and-reporting`: 定义 AKQuant-inspired 的回测输入契约、账本式执行模型、策略预设与可解释报表输出。

### Modified Capabilities
- `flask-backend-platform`: 回测 API 从“legacy 结果透传”升级为“结构化工作台接口”，并新增策略预设元数据路由。
- `nextjs-frontend-shell`: 回测页面从基础表单升级为参数化工作台，支持策略预设、基准/执行设置和更丰富的结果视图。
- `migration-workspace-and-docs`: 文档需要明确新的回测契约、策略预设、执行假设和验证方式。

## Impact

- Affected code:
  - `backtesting/engine.py`
  - `backtesting/pipeline.py`
  - `backtesting/strategy.py`
  - `backtesting/data.py`
  - `backend/app/api/backtests.py`
  - `backend/app/schemas/backtests.py`
  - `backend/app/services/backtests.py`
  - `backend/tests/test_backtests_api.py`
  - `frontend/components/backtest-console.tsx`
  - `frontend/lib/api.ts`
  - `frontend/lib/backtests.ts`
  - `frontend/types/api.ts`
  - `README.md`
  - `backend/README.md`
  - `docs/migration/phase-one-architecture-migration.md`
- Affected APIs:
  - `POST /api/v1/backtests/run`
  - `GET /api/v1/backtests/presets`
- Affected systems:
  - Legacy backtesting pipeline
  - Flask backtest service adapter
  - Next.js backtest workbench
