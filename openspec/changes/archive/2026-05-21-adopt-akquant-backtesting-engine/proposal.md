## Why

当前回测虽然已经做过一轮 AKQuant-inspired 升级，但仍然是仓库自维护的 legacy stack。用户这次的要求已经变化为“直接使用 `akfamily/akquant` 全面替代现有回测实现”，因此继续在自研引擎上做局部打补丁，会让技术债和产品契约同时继续分叉。

## What Changes

- 将现有回测主执行路径替换为 `akfamily/akquant`，并以其官方 runtime 作为新的唯一回测内核。
- 建立 AKQuant adapter/service 层，把现有 Flask API、前端工作台和必要兼容字段映射到 AKQuant 运行模型。
- 用 AKQuant 的策略目录、执行配置、结果统计与回测运行输出重构现有回测 contract。
- 逐步下线 `backend/backtesting/*` 的主执行职责，将其保留为迁移兼容层直至完全移除。
- 更新前后端类型、文档和测试，并把回测 contract 稳定到可供后续 `complete-backend-openapi-platform` change 统一发布 `openapi.json` 的状态，使“AKQuant 直连集成”成为仓库的正式事实。

## Capabilities

### New Capabilities
- `akquant-runtime-adapter`: 定义 AKQuant 运行时接入、请求映射、结果归一化与自定义策略适配边界。

### Modified Capabilities
- `backtest-execution-and-reporting`: 从“AKQuant-inspired contract + legacy execution”升级为“AKQuant-native execution + productized response contract”。
- `flask-backend-platform`: 回测 API 从调用 legacy pipeline 改为调用 AKQuant runtime 及其 adapter。
- `nextjs-frontend-shell`: 回测工作台从消费 legacy-compat contract 升级为消费 AKQuant-backed contract。
- `akshare-market-data-orchestration`: 回测数据获取应与 AKQuant 集成路径保持统一的市场数据契约。

## Impact

- Affected code:
  - `backend/pyproject.toml`
  - `backend/app/api/backtests.py`
  - `backend/app/schemas/backtests.py`
  - `backend/app/services/backtests.py`
  - `backend/backtesting/*`
  - `backend/tests/test_backtests_api.py`
  - `backend/tests/test_backtest_*`
  - `frontend/components/backtest-console.tsx`
  - `frontend/lib/backtests.ts`
  - `frontend/types/api.ts`
- Affected APIs:
  - `GET /api/v1/backtests/presets`
  - `POST /api/v1/backtests/run`
- Affected systems:
  - backtest engine runtime
  - strategy preset registry
  - OpenAPI contract
  - frontend backtest workbench
