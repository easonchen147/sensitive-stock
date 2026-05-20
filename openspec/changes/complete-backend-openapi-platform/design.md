## Context

当前后端已经不是“从零开始的迁移骨架”，而是一个真实对外提供能力的平台。但它还没有完成平台化的最后一步：统一 contract 和全局 OpenAPI。

从实际代码看，后端已经具备：

- 版本化 API 前缀
- 认证与 session 保护
- market / backtests 正式路由
- 四类半成品的 placeholder 或底层模块

缺口在于：

- 接口 schema 还没有形成全量对外契约；
- 错误与 degraded metadata 的表达还未平台化；
- 还没有统一的 `openapi.json` 产物；
- frontend 还不能以单一契约源消费所有接口。

## Goals / Non-Goals

**Goals:**

- 让 backend 成为可被 OpenAPI 完整描述的正式平台。
- 把 auth、market、backtests、screener、diagnosis、factors、portfolio 统一纳入契约。
- 提供可构建、可运行时发现、可验证的 `openapi.json`。
- 为 frontend 类型生成、BFF 对齐和自动化测试提供统一事实来源。

**Non-Goals:**

- 本轮不在该 change 内完成全站 UI 重构。
- 本轮不要求切换后端框架；继续基于现有 Flask 架构演进。
- 本轮不引入与当前 repo 目标无关的服务注册中心、网关或微服务拆分。

## Decisions

### 1. 继续保留 Flask 主框架，在其上补 OpenAPI emitter，而不是整栈迁移框架

用户要的是“后端全面完善 + openapi.json”，不是“为了 OpenAPI 把后端整体迁到别的框架”。当前 repo 已经明确收敛到 Flask app factory，因此本轮选择是在现有架构上补：

- 显式 schema 层
- route-to-schema 绑定
- OpenAPI emitter
- validation 流程

这样可以避免把需求扩大为框架迁移。

### 2. OpenAPI 既要有构建产物，也要有运行时发现入口

只生成一个离线文件不够，因为：

- frontend 开发、联调和第三方消费往往希望运行时可发现；
- CI/CD 与归档希望有稳定构建产物；
- 文档系统也需要可引用的固定文件。

因此设计要求：

- 提供运行时 `openapi.json` 路由；
- 同时提供可由命令生成并纳入验证的静态产物。

### 3. 共享组件先统一 auth、错误模型、分页/过滤与 degraded metadata

若只导出一个“路径列表”，价值有限。真正能让 frontend 与自动化稳定消费的，是共享组件先统一：

- bearer auth scheme
- 标准错误响应
- 常用 query/pagination/filter 参数
- degraded/source metadata

### 4. 全量 API 契约以正式能力为准，placeholder 不再长期作为平台事实

这意味着：

- 已正式完成的能力必须进入 OpenAPI；
- 正在被提案补完的能力在落地后进入 OpenAPI；
- placeholder 路由若仅用于阶段说明，应有清晰的迁移或废弃策略，而不是永久停留在对外契约里。

## Risks / Trade-offs

- `[Flask 原生不是最强 OpenAPI-first 框架]` -> 通过显式 schema 和 emitter 层补齐，不扩大为整栈迁移。
- `[现有接口字段可能存在历史漂移]` -> 先做路由盘点与 schema 对齐，再生成 OpenAPI。
- `[placeholder 与正式能力并存时契约容易混乱]` -> 以正式能力优先，placeholder 明确标注迁移/废弃边界。
- `[frontend 过早绑定不稳定字段]` -> 先稳定 OpenAPI 共享组件，再推动全页面接入。

## Migration Plan

1. 盘点现有全部正式与待正式化 API 路由。
2. 为每类路由补齐 request/response schema、错误模型和 auth 声明。
3. 建立 OpenAPI emitter、运行时发现路由与静态生成命令。
4. 将输出纳入验证流程，并用其驱动 frontend 类型/客户端对齐。
5. 文档和 README 同步改为以 `openapi.json` 为后端对外事实来源。

回滚策略：

- OpenAPI emitter 可与现有 route registry 解耦实现，若 emitter 有问题，可临时回退生成流程而不影响业务路由。
- 路由与 schema 对齐分模块推进，可按模块回退，不必整体回退。

## Open Questions

- `openapi.json` 的最终落点是仓库根目录、`backend/` 子目录，还是两者同时存在。
- 是否在本轮同时生成前端 client，还是先稳定 OpenAPI 文件，再由前端提案统一接入。
