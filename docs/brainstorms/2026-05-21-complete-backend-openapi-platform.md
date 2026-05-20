# 完整后端能力与 OpenAPI 平台 Brainstorm

## 背景

当前后端已经形成 Flask app factory、版本化 API、认证、市场数据和回测入口，但距离“完整平台后端”还有明显差距：

- 四类半成品能力没有正式 API 化。
- 还没有统一的 `openapi.json` 作为全局契约。
- 部分模块仍是 legacy adapter，而不是面向契约的 service/API 层。

用户要求是：

1. 后端功能全面完善。
2. 输出全局通用的 `openapi.json`。
3. 基于 OpenSpec + Compound 的工作流完成后端设计开发提案。

## 核心问题

### 1. “全面完善”指什么？

在当前项目里，它应至少包括：

- auth / session / access control
- capabilities inventory
- market / quotes / sectors / news / intelligence
- backtests
- screener
- diagnosis
- factors
- portfolio

不仅要“有路由”，还要做到：

- schema 清晰
- 错误模型统一
- degraded 状态可表达
- OpenAPI 可导出
- 测试可覆盖

### 2. OpenAPI 的角色是什么？

它不只是“文档导出文件”，而应成为：

- frontend 类型生成来源
- 第三方集成边界
- 未来 SDK / 自动化测试 / mock server 的事实来源

### 3. 当前 Flask 栈怎么产出 OpenAPI？

需要决定：

- 继续用现有 Flask + Pydantic，补一层 OpenAPI 生成框架；
- 还是迁移到更原生的 OpenAPI-first 框架 / 插件模式；
- 输出是构建产物、运行时路由，还是二者都有。

## 推荐方向

### 平台化目标

把 backend 从“若干蓝图 + 若干 legacy 适配器”提升成：

- service 层明确
- schema 层系统化
- OpenAPI-first 契约平台
- 支撑前端全页面集成的后端底座

### 最重要的统一面

- 请求/响应 schema 全量显式化
- 错误响应统一标准
- auth header / session 规则统一
- 数据源元数据与 degraded 信息统一

## 成功标准

- 仓库存在可生成、可校验、可分发的 `openapi.json`。
- 所有用户可见后端能力都被纳入 OpenAPI，而不是只覆盖一半路由。
- frontend 后续可直接基于 `openapi.json` 生成类型或 client。
- 新后端提案能够为 4 类半成品和回测替换提供统一契约底座。

## 与其他提案关系

- 为 `complete-skeleton-capabilities` 提供后端契约前提。
- 为 `adopt-akquant-backtesting-engine` 提供回测 API 契约容器。
- 为 `redesign-frontend-with-huashu-openapi` 提供前端全接口接入基础。
