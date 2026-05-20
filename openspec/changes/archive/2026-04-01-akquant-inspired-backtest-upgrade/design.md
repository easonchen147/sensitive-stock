## Context

当前仓库的回测实现仍然保持 phase one 的“先迁通主链路”形态：

- `backend/app/services/backtests.py` 只是把前端请求转成 legacy `BacktestRequest`，逐个标的串行调用 `BacktestService`。
- `backtesting/engine.py` 采用“信号 × 收益率”的简化收益模型，只在交易点上扣除统一费率，缺少资金、持仓、手数、税费与执行时点的真实账本。
- `backtesting/strategy.py` 虽然允许自定义 Python 策略，但接口仍然只有 `generate_signals(data, ctx)`，前端也没有参数 schema 或策略目录。
- `frontend/components/backtest-console.tsx` 只是基础表单和结果卡片，无法表达策略参数、基准、执行假设和报表解释层。

AKQuant 的公开能力给出了更好的方向：类 / 函数双形态策略、参数模型驱动、`CurrentClose` / `NextOpen` 执行模式、`RiskConfig` 风格的执行约束、以及更丰富的绩效指标与图表输出。当前仓库不适合在这一轮直接引入 AKQuant 的完整运行时或大规模重构，但非常适合迁入这些“高价值的接口和模型设计”。

## Goals / Non-Goals

**Goals:**

- 把回测输入从扁平字段升级为可扩展的结构化契约，覆盖数据范围、策略、执行、成本、仓位与基准设置。
- 用更接近实盘的账本式执行逻辑替换当前简化收益模型，优先覆盖 A 股单标的日线回测。
- 提供策略预设目录与参数 schema，让前端能够像 AKQuant 的参数化工作台一样动态渲染输入。
- 保留自定义 `generate_signals(data, ctx)` 入口，避免破坏现有 AI 生成策略链路。
- 升级后端响应和前端展示，让回测结果具备“结果 + 假设 + 对比 + 解释”的完整工作台体验。

**Non-Goals:**

- 本轮不直接引入 AKQuant 作为运行时依赖，不修改当前仓库的基础依赖管理策略。
- 本轮不实现 AKQuant 完整的事件驱动类策略生命周期，也不迁入多资产组合级撮合。
- 本轮不做回测任务队列、异步流式进度、缓存层或数据库持久化。
- 本轮不重写 Streamlit 老页面，只以 Flask backend + Next.js frontend 为默认升级目标。

## Decisions

### 1. 采用“AKQuant 思路迁移”，而不是直接引入 AKQuant 运行时

本轮借鉴 AKQuant 的设计能力，而不是把仓库直接切换到 AKQuant 依赖。

原因：

- 当前 backend 仍以 Poetry 管理 Python 依赖，直接引入新的核心运行时会把本轮升级扩大成“依赖兼容 + 引擎替换 + API 改写”的复合改造。
- 现有自定义策略执行依赖 `exec()` 和 AI 生成代码，直接切换运行时容易打断现有用户路径。
- 用户明确接受“若完整替换会大爆炸，则优先落一个高价值可合并版本”。

备选方案：

- 直接新增 `akquant` 依赖并改用其原生回测运行时。
  - 放弃原因：依赖风险更高，且当前仓库还没有适配其完整生命周期与前端契约。
- 维持现有引擎，只在前端增加几个输入项。
  - 放弃原因：这会继续输出“看起来更强，实则仍是简化收益乘仓位”的结果，价值有限。

### 2. 回测请求升级为结构化工作台契约，但保留兼容字段映射

`POST /api/v1/backtests/run` 将扩展为可表达以下信息的结构化请求：

- `market`: 标的、日期区间、复权方式、可选基准代码
- `strategy`: 预设策略或自定义代码、参数字典、参数 schema 元数据
- `execution`: 执行时点（`close` / `next_open`）、仓位比例、最小交易手数
- `costs`: 佣金、印花税、滑点
- `risk`: 止损、止盈

为了保持当前代码路径可迁移，backend schema 仍会兼容旧字段命名，并在 service 层归一化到新的内部 dataclass。

备选方案：

- 直接保留原始扁平 schema，不引入分组。
  - 放弃原因：字段会继续膨胀，前后端都难以维护。

### 3. 引擎改为单标的 A 股账本式执行，而不是继续用收益率向量化近似

`backtesting/engine.py` 将重构为“每日状态推进”的执行引擎：

- 按配置在 `close` 或 `next_open` 计算成交价
- 按现金、仓位比例和 `lot_size` 计算可买股数
- 显式维护 `cash`、`shares`、`market_value`、`total_equity`
- 在买卖时分别计入佣金、印花税和滑点
- 支持止损 / 止盈触发后的强制平仓
- 输出逐日资金、仓位、回撤和交易明细

这样能把 AKQuant 的执行模式、风险配置和交易成本思想落到现有 Python-only 引擎里。

备选方案：

- 继续保留原来的向量化收益模型，只追加几个指标字段。
  - 放弃原因：无法真实表达 lot size、税费、现金占用和执行时点。

### 4. 策略接口采用“预设目录 + 自定义代码”双通道

AKQuant 的一个核心优势是参数模型化和策略组织能力。本轮不直接迁入完整类策略生命周期，而采用更适合当前仓库的折中实现：

- 新增内置策略预设目录，例如：
  - `ma_cross`
  - `rsi_reversion`
  - `breakout_channel`
- 每个预设都提供：
  - `id`
  - `label`
  - `description`
  - `parameterSchema`
  - `defaultParams`
  - 生成或绑定的策略代码
- 同时继续支持 `custom` 模式下的 `generate_signals(data, ctx)` 自定义代码

这样前端可以渲染 AKQuant 风格的参数化工作台，而 backend 仍能复用现有安全执行器。

### 5. 回测输出改为“结果 + 假设 + 解释”三层结构

每个标的结果将至少输出：

- `settings`: 请求回显、执行时点、成本参数、数据源顺序、是否有降级
- `metrics`: 核心收益 / 风险 / 交易指标
- `comparison`: 基准收益、超额收益、最大回撤差、信息比率等
- `series`: 净值、基准净值、回撤、仓位、现金占用、月度收益
- `tradeStats`: 交易次数、胜率、平均持仓天数、平均盈亏、总成本
- `trades`: 详细成交记录与触发原因
- `warnings`: 例如“无交易”“基准数据缺失已跳过对比”“next_open 因最后一根 K 线无下一日开盘价而回退”

这层契约直接面向 frontend 页面，不再让前端自己猜测结果含义。

### 6. 新增策略预设元数据 API，由前端动态渲染参数表单

新增 `GET /api/v1/backtests/presets`：

- 返回可选策略预设列表
- 每个预设包含参数 schema 和默认值
- 前端以此动态渲染参数输入区

这样可以把“新增策略”和“新增前端表单”解耦，贴近 AKQuant 的参数驱动工作流。

## Risks / Trade-offs

- `[不是完整 AKQuant 引擎]` → 在文档、spec 和响应 metadata 中明确本轮是 AKQuant-inspired 工作台升级，后续仍可继续演进到更完整的事件驱动模型。
- `[账本式执行比现有引擎复杂]` → 先用定向单测锁定执行时点、税费、止损止盈、手数四类关键行为，再做重构。
- `[next_open 依赖下一根 K 线的 open]` → 对最后一个交易日提供明确回退或告警，而不是静默使用错误价格。
- `[前后端契约一次性变更较大]` → 保持 `/api/v1/backtests/run` 路由不变，schema 兼容旧字段，前端先吃新字段，旧调用路径不立即删除。
- `[多标的仍然是逐标的执行，不是组合撮合]` → 在结果中明确这是“单标的批量回测”，不虚构组合层指标。

## Migration Plan

1. 先补 backend / frontend 的定向失败测试，锁定新 contract、策略预设、执行时点和结果结构。
2. 实现 legacy 层的新 dataclass、策略预设注册表和账本式执行引擎。
3. 扩展 Flask schema / service / API，新增预设元数据路由并序列化 richer report。
4. 升级 Next.js 回测页与类型定义，消费预设元数据和新结果结构。
5. 更新 README / backend README / 迁移文档，说明 AKQuant-inspired 升级范围。
6. 运行定向后端测试、前端测试 / 类型检查，并在验证通过后提交。

回滚策略：

- 保留旧字段兼容映射和原有自定义策略入口。
- 若 richer report 或 preset UI 引发问题，可回退到本变更前的 backtest API 行为与旧前端页面。

## Open Questions

- 本轮不阻塞实现的开放项只有一项：后续是否继续向 AKQuant 的“类策略生命周期 + 组合级撮合”演进。当前 change 明确不把该能力作为本轮完成条件。
