## 1. Route And Contract Inventory

- [x] 1.1 盘点 auth、market、backtests、screener、diagnosis、factors、portfolio 的正式与待正式化路由。
- [x] 1.2 为全部正式接口定义统一 request/response schema、错误模型与 degraded/source metadata 约定。

## 2. Platform OpenAPI Publication

- [x] 2.1 建立 OpenAPI emitter、运行时发现路由与静态生成命令。
- [x] 2.2 将 bearer auth、共享错误模型和常用参数抽为 OpenAPI 共享组件。

## 3. Backend Consistency Hardening

- [x] 3.1 对齐后端 endpoint 命名、状态字段、错误格式和鉴权声明。
- [x] 3.2 将四类半成品能力与 AKQuant 回测接口纳入同一 OpenAPI 契约。

## 4. Verification And Documentation

- [x] 4.1 为 `openapi.json` 增加生成校验、schema validation 和 API contract tests。
- [x] 4.2 更新 README、backend README 与开发流程文档，使 OpenAPI 成为正式对外事实来源。
