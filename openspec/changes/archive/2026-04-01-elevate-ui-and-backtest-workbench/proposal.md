## Why

当前 Next.js 前端虽然已经接管默认入口，但整体仍停留在 phase-one 的“壳层可用”状态：首页、回测页与占位页的信息架构、视觉层级、交互反馈和状态表达都偏原型化，难以体现这是一个专业股票分析与回测工具。与此同时，AKQuant-inspired 回测链路已经打通，但输入引导、默认值说明、执行假设解释和结果可读性仍有明显提升空间。

现在推进这一轮 change 的价值在于：在不做无关大重构的前提下，把已经真实落地的前后端能力包装成更可信、更易用、更可解释的工作台体验，并让文档与能力状态表达保持诚实一致。

## What Changes

- 系统性升级 Next.js 应用壳层与主要页面的 UI/UX，包括导航、首页 capability inventory、回测页、市场页以及 screener / diagnosis 的占位状态表达。
- 将市场页从 placeholder 升级为真实消费 `/api/v1/market`、`/api/v1/market/quotes`、`/api/v1/market/sectors`、`/api/v1/market/news`、`/api/v1/market/news/intelligence` 的前端工作台，但只展示当前后端已真实提供的数据与 intelligence 骨架。
- 继续增强回测工作台：优化输入分组、默认值与参数说明、策略预设交互、执行/成本/风险假设摘要、结果分层展示、空状态/加载态/错误态与多标的结果对比。
- 扩展回测前后端契约，在不破坏现有路由的前提下增加更适合前端解释型工作台消费的 schema / metadata / report 字段。
- 更新 README、迁移文档与 OpenSpec delta，使“哪些页面已真实接入 API、哪些仍是骨架、回测增强做到哪一步”与代码状态保持一致。

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `nextjs-frontend-shell`: 前端壳层、首页、市场页与回测页的要求会升级为更完整的工作台 UI，并要求市场页真实消费已迁移的 backend market/news API。
- `backtest-execution-and-reporting`: 回测契约会补充更强的参数 metadata、执行假设摘要、解释型结果字段和更清晰的报告结构。
- `flask-backend-platform`: Flask backtest/market API 需要稳定支撑新的前端消费方式和 richer backtest report，而不是只返回最薄结果。
- `migration-workspace-and-docs`: 文档需要同步描述新的前端完成度、市场页真实状态和回测工作台增强边界。

## Impact

- Affected code:
  - `frontend/app/layout.tsx`
  - `frontend/app/globals.css`
  - `frontend/app/page.tsx`
  - `frontend/app/backtests/page.tsx`
  - `frontend/app/market/page.tsx`
  - `frontend/app/screener/page.tsx`
  - `frontend/app/diagnosis/page.tsx`
  - `frontend/components/app-shell.tsx`
  - `frontend/components/backtest-console.tsx`
  - `frontend/components/capability-placeholder.tsx`
  - `frontend/lib/api.ts`
  - `frontend/lib/backtests.ts`
  - `frontend/lib/backtests.test.ts`
  - `frontend/types/api.ts`
  - `backend/app/api/backtests.py`
  - `backend/app/api/market.py`
  - `backend/app/schemas/backtests.py`
  - `backend/app/services/backtests.py`
  - `backend/app/services/market_data.py`
  - `backend/tests/test_backtests_api.py`
  - `backend/tests/test_market_api.py`
  - `README.md`
  - `docs/migration/phase-one-architecture-migration.md`
- Affected APIs:
  - `GET /api/v1/backtests/presets`
  - `POST /api/v1/backtests/run`
  - `GET /api/v1/market`
  - `GET /api/v1/market/quotes`
  - `GET /api/v1/market/sectors`
  - `GET /api/v1/market/news`
  - `GET /api/v1/market/news/intelligence`
- Affected systems:
  - Next.js frontend shell and page routing
  - Flask backtest service adapter
  - Flask market/news API consumption path
  - OpenSpec capability specs and migration-facing documentation
