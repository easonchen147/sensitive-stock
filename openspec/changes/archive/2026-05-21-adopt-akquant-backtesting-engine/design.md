## Context

当前仓库的 `backtest-execution-and-reporting` 规格已经是 AKQuant-inspired，但实现仍停留在“内部引擎 + AKQuant 思路迁移”的阶段。用户现在要求明确改变：不再停留在 inspired 路线，而是直接使用 `akfamily/akquant` 作为第三方回测内核。

这意味着本 change 的关键不只是 Python 依赖调整，而是三件事一起落地：

1. 回测 runtime 的真实替换；
2. 前后端 contract 的重新对齐；
3. 旧自定义策略/旧字段的迁移兼容与下线路径。

## Goals / Non-Goals

**Goals:**

- 让 AKQuant 成为仓库唯一主回测执行内核。
- 保留现有 `/api/v1/backtests/*` 路由边界，但内部 contract 与执行由 AKQuant 驱动。
- 为内置策略和必要的自定义策略保留 adapter 层，避免一次性切断现有路径。
- 用 AKQuant 输出重建前端回测工作台和 OpenAPI 契约。

**Non-Goals:**

- 本轮不在该 change 内完成所有选股、诊股、因子、组合工作流。
- 本轮不引入数据库持久化、任务队列或多用户回测管理。
- 本轮不保留 legacy 引擎为长期并行主路径；最多只保留短期迁移兼容层。

## Decisions

### 1. AKQuant 作为唯一执行内核，旧 `backend/backtesting/*` 只保留迁移兼容职责

直接替换的目标不能做成“又加一个可选引擎”。否则：

- 契约会双轨；
- 测试会双轨；
- 前端工作台会双轨；
- 回测解释与结果字段也会双轨。

因此本设计要求 AKQuant 成为唯一主执行内核，legacy backtesting 只在迁移期间保留兼容辅助职责。

### 2. 保留外部 API 路径稳定，但内部 contract 升级为 AKQuant-first

不改变现有主要路由：

- `GET /api/v1/backtests/presets`
- `POST /api/v1/backtests/run`

但请求/响应 contract 升级为 AKQuant-first，必要时在 adapter 层接收旧字段并归一化。

原因：

- 外部路径稳定，便于前后端联调和渐进迁移；
- 内部模型不再继续向 legacy 字段妥协。

### 3. 自定义策略通过 adapter 进入 AKQuant，而不是继续直接执行旧策略 runtime

当前仓库存在自定义策略路径。如果完全舍弃，将打断原有使用方式；如果原样保留，又会继续维持旧引擎。折中方式是：

- 内置策略直接对齐 AKQuant 的策略表达；
- 自定义策略通过 adapter 转换为 AKQuant 可接受的策略形式；
- 不能适配的旧路径明确标记为迁移限制，而不是默默继续走旧引擎。

### 4. 回测数据、执行参数、结果结构全部以 AKQuant product contract 归一化

本轮不是单纯“把内部执行换成 AKQuant，但对外仍像以前”。前端和 OpenAPI 都应看到更真实的 AKQuant 集成模型：

- 策略 preset 目录
- 执行模式 / fill policy
- 成本与风险参数
- 结果统计、净值、回撤、trade log

## Risks / Trade-offs

- `[AKQuant 官方 API 后续可能演进]` -> 显式 pin 依赖版本，并通过 adapter 隔离上游变化。
- `[旧策略接口可能无法 1:1 适配]` -> 将 adapter 支持范围写清楚，超出范围的旧策略明确 fail fast。
- `[前后端字段改动面较大]` -> 保持路由稳定、旧字段短期归一化，配合 OpenAPI 统一升级。
- `[legacy backtesting 删除过早会影响排障]` -> 先保留迁移兼容层，再在验证稳定后删除。

## Migration Plan

1. 核实 AKQuant 当前官方安装方式、依赖与支持能力，并锁定版本。
2. 在 backend 中引入 AKQuant 依赖，建立独立 adapter/service。
3. 用 AKQuant 打通最小 `run` + `presets` 路径，跑通后端测试。
4. 对齐请求/响应 contract 与前端类型，升级回测工作台；全局 `openapi.json` 发布由后续 `complete-backend-openapi-platform` change 统一完成。
5. 将旧 `backend/backtesting/*` 主路径降级为兼容层，再逐步下线。

回滚策略：

- 若 AKQuant 集成在短期内阻断主链路，可临时回退到上一个回测 commit。
- 迁移期间保留 legacy 兼容层，但不再把它定义为长期主路径。

## Open Questions

- AKQuant 对当前仓库自定义策略模型的最小可接受 adapter 形式是什么。
- 当前仓库是否需要为多标的批量回测增加 AKQuant 层的批量编排，而不是简单逐标的包装。
