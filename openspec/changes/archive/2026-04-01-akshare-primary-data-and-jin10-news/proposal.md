## Why

当前后端和遗留模块仍混用旧版 AkShare、Sina/Tencent 直连以及手写新闻抓取逻辑，数据优先级和回退策略分散，导致回测、行情、板块和新闻分析链路缺少统一的数据契约。与此同时，Flask backend 的 `market` 能力仍停留在 placeholder，无法为前端和后续业务提供可复用的 AkShare 市场数据与金十实时资讯接口。

## What Changes

- 升级项目使用的 AkShare 到最新版可安装版本，并以官方 AkShare 接口作为默认核心市场数据源。
- 重构 A 股市场数据优先级：历史行情、实时行情、股票基础信息和板块数据优先走 AkShare；仅保留必要的旧数据源作为明确 fallback。
- 在 backend 中新增市场数据服务与新闻情报服务，提供可被前端/业务调用的 `/api/v1/market/*` 接口。
- 新增金十实时资讯抓取链路，统一按“最新 100 条”拉取，并补充关键词提取与板块预测增强流程骨架。
- 更新 capability inventory、README、backend README 和相关迁移说明，明确 AkShare-first 策略及 fallback 边界。

## Capabilities

### New Capabilities
- `akshare-market-data-orchestration`: 统一定义 AkShare 优先的 A 股历史行情、实时行情、股票列表与板块数据服务，以及明确的 fallback 顺序。
- `jin10-news-intelligence-pipeline`: 定义金十最新 100 条资讯抓取、关键词提取、板块预测增强输入输出和后端 API 骨架。

### Modified Capabilities
- `flask-backend-platform`: 将 `market` 从纯 placeholder 推进为可调用的 backend 数据/新闻接口，并更新 capability inventory 的状态与路由行为。
- `migration-workspace-and-docs`: 文档需要明确最新版 AkShare 接入、fallback 保留策略、金十新闻能力和新的 backend API。

## Impact

- Affected code:
  - `backtesting/data.py`
  - `backend/app/api/*`
  - `backend/app/services/*`
  - `backend/app/schemas/*`
  - `backend/tests/*`
  - `README.md`
  - `backend/README.md`
  - 相关迁移文档 / OpenSpec 制品
- Affected dependencies:
  - `backend/pyproject.toml`
  - `backend/poetry.lock`（若存在或需生成）
- Affected systems:
  - Backtest data acquisition chain
  - Backend market/news APIs
  - Sector prediction / keyword extraction preparation flow
