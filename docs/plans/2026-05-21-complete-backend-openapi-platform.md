# 完整后端能力与 OpenAPI 平台 Plan

## 目标

把后端提升为 OpenAPI-first 的完整能力平台，并输出全局 `openapi.json`。

## 技术方案

### 平台契约化

1. 清点全部 API 面：
   - auth
   - capabilities
   - market
   - backtests
   - screener
   - diagnosis
   - factors
   - portfolio
2. 为全部接口补齐显式 request/response schema。
3. 统一错误响应与鉴权要求描述。

### OpenAPI 生成

1. 选定 Flask 侧 OpenAPI 生成路径。
2. 使 `openapi.json` 可通过命令构建，也可通过运行时路由暴露。
3. 把生成物纳入验证流程。

### 平台一致性

1. 统一 endpoint 命名和状态字段。
2. 统一数据源元信息与 degraded 表达。
3. 为前端类型生成与接口接入保留稳定字段。

## 影响文件

- `backend/app/api/*`
- `backend/app/schemas/*`
- `backend/app/services/*`
- `backend/tests/*`
- `backend/pyproject.toml`
- `openapi.json` 或 `backend/openapi.json`

## 测试策略

- OpenAPI schema validation
- API contract tests
- auth-protected route coverage
- generated client smoke tests（若引入）

## 里程碑

1. 完成全接口盘点与 schema 补全。
2. 跑通 OpenAPI 生成。
3. 把四类半成品与回测接口纳入同一契约。
4. 对前端暴露稳定 `openapi.json`。
