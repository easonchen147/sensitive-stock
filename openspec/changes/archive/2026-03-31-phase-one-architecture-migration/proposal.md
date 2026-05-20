## Why

当前项目以 Streamlit 单体应用为核心，页面状态、流程编排、业务服务和外部数据访问高度耦合，已经不适合作为可持续演进的产品骨架。第一阶段需要先完成架构迁移，把现有能力拆分为可维护的 Flask 后端与 Next.js 前端，并建立新的工程与文档基线，为后续分批迁移功能和补测试创造条件。

## What Changes

- **BREAKING**: 将默认运行形态从 `streamlit run app.py` 切换为前后端分离模式，新增 `backend/` 与 `frontend/` 两个主工作区。
- 新增 Flask 后端应用骨架，按 `api / services / domain / schemas / config` 组织现有能力，并为条件选股、回测执行、市场数据、AI 诊股、因子分析、组合优化预留或实现 API 入口。
- 新增 Next.js + React 前端应用骨架，建立基础布局、页面路由、API client 和功能入口，替代现有 Streamlit 页面导航。
- 将现有回测主链路优先迁移为可调用 API，并在前端打通一条从页面到后端的关键链路。
- 采用 `uv + Poetry` 作为新的 Python 依赖与环境工作流，统一后端工程配置、脚本入口与运行方式。
- 新增架构迁移说明、目录结构说明、运行文档与迁移状态文档，并重写根目录 README 以反映新架构。
- 补充 MIT LICENSE，确保仓库许可信息明确。

## Capabilities

### New Capabilities
- `flask-backend-platform`: 基于 Flask 的后端平台能力，定义应用工厂、REST API、服务边界、错误模型与现有业务模块的承接方式。
- `nextjs-frontend-shell`: 基于 Next.js + React 的前端壳层能力，定义页面结构、共享布局、API 调用层以及与后端的交互契约。
- `migration-workspace-and-docs`: 定义 `uv + Poetry` Python 工作流、新目录结构、迁移状态跟踪与开发运行文档。

### Modified Capabilities
- None.

## Impact

- 受影响代码：`app.py`、`pages/*`、`utils.py`、`market_data.py`、`screener.py`、`ai_diagnosis.py`、`backtesting/*`、`factor_analysis.py`、`portfolio_optimizer.py`、`report_exporter.py`。
- 新增系统：Flask HTTP API、Next.js 前端应用、前后端联调配置、项目级 Python 工程配置。
- 依赖变化：Python 侧引入 Flask、Pydantic、Flask-CORS 等后端依赖，并采用 Poetry 管理依赖、UV 负责环境与安装执行；前端侧引入 Next.js、React、TypeScript 与基础 UI/数据请求依赖。
- 运行方式变化：开发与部署入口将由单一 Streamlit 进程改为 `backend` 与 `frontend` 双进程模式。
