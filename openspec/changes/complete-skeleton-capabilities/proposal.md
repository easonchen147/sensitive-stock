## Why

当前系统已经完成了登录、回测和行情两条主链路，但 `screener`、`diagnosis`、`factors`、`portfolio` 仍停留在 skeleton 或保留模块状态。这样会让能力清单、前端导航、后端平台边界和真实业务完成度长期脱节，也阻断了“选股 -> 回测 -> 诊断 -> 研究决策”的完整闭环。

## What Changes

- 将 `screener` 从 placeholder 升级为真实条件选股工作流，支持条件模板、自然语言筛选、结果排序/导出与回测回灌。
- 将 `diagnosis` 从 placeholder 升级为真实 AI 诊股工作流，支持行情摘要、技术指标计算、结构化诊断报告与失败兜底。
- 将 `factors` 和 `portfolio` 从保留模块升级为正式后端服务、API 与前端工作台。
- 建立这四类能力的共享契约：统一 schema、错误模型、数据源 metadata、导出行为与 capability inventory 状态表达。
- 更新 capability inventory 与前端页面状态，使这四类能力在完成后不再标记为 `skeleton`。

## Capabilities

### New Capabilities
- `screener-workbench`: 定义条件选股、自然语言筛选、结果导出与回测联动能力。
- `diagnosis-reporting`: 定义 AI 诊股输入、指标上下文、结构化诊断报告与失败兜底能力。
- `factor-analysis-api`: 定义因子分析正式 API、结果结构与前端消费契约。
- `portfolio-optimization-api`: 定义组合优化正式 API、约束输入、优化结果与前端消费契约。

### Modified Capabilities
- `flask-backend-platform`: 从“部分能力为 placeholder”升级为“半成品能力正式 API 化并纳入平台边界”。
- `nextjs-frontend-shell`: 从“部分能力仅有 skeleton 页面”升级为“六大研究工作台均有真实页面与交互”。
- `akshare-market-data-orchestration`: 为选股、诊股、因子与组合能力提供统一市场数据与指标输入约束。

## Impact

- Affected code:
  - `backend/app/api/*`
  - `backend/app/services/*`
  - `backend/app/schemas/*`
  - `backend/tests/*`
  - `frontend/app/*`
  - `frontend/components/*`
  - `frontend/lib/*`
  - `frontend/types/*`
- Affected APIs:
  - `GET/POST /api/v1/screener*`
  - `POST /api/v1/diagnosis*`
  - `GET/POST /api/v1/factors*`
  - `GET/POST /api/v1/portfolio*`
  - `GET /api/v1/capabilities`
- Affected systems:
  - capability inventory
  - market data reuse layer
  - backtest linkage flow
  - frontend research workbenches
