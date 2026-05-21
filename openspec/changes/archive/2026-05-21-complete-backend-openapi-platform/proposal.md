## Why

当前 backend 已经具备 Flask app factory、认证、市场数据、回测和若干保留中的研究模块，但系统仍缺少一个可以覆盖全量接口的统一后端契约。没有全局 `openapi.json`，前端类型、第三方集成、自动化契约校验和文档边界就都只能依赖手写约定，随着能力增多会越来越难以维护。

## What Changes

- 将 backend 提升为 OpenAPI-first 的完整能力平台，覆盖 auth、market、backtests、screener、diagnosis、factors、portfolio 全部正式接口。
- 为所有正式接口补齐显式 request/response schema、错误响应模型、鉴权描述与 degraded metadata 表达。
- 增加全局 `openapi.json` 生成、校验和发布路径，使其成为后端与前端之间的统一事实来源。
- 统一后端命名、分页/过滤、错误模型、源数据元信息与状态字段，减少各模块接口漂移。
- 为后续 frontend OpenAPI 集成和外部消费保留稳定的契约输出。

## Capabilities

### New Capabilities
- `backend-openapi-publication`: 定义全局 OpenAPI 生成、验证、发布与共享组件契约。

### Modified Capabilities
- `flask-backend-platform`: 从“稳定 HTTP 壳层”升级为“完整正式 API 平台 + OpenAPI 发现与契约化约束”。
- `token-auth-access-control`: 从“鉴权能力已存在”升级为“鉴权方案同时成为可被 OpenAPI 声明与复用的正式平台契约”。

## Impact

- Affected code:
  - `backend/app/api/*`
  - `backend/app/schemas/*`
  - `backend/app/services/*`
  - `backend/tests/*`
  - `backend/pyproject.toml`
  - `openapi.json` 或 `backend/openapi.json`
- Affected APIs:
  - `GET /api/v1/openapi.json` 或等价发现路径
  - 现有所有 `/api/v1/*` 正式业务接口
- Affected systems:
  - backend route registry
  - request/response schema layer
  - auth scheme publication
  - frontend generated types / clients
