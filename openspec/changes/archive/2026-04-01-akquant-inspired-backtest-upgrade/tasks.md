## 1. 契约与测试基线

- [x] 1.1 为升级后的 backtest schema、策略预设目录、结果序列化和执行行为补充 backend 定向测试。
- [x] 1.2 为前端 payload 组装、预设参数渲染和结果展示补充直接相关的 helper / component 测试。

## 2. 回测核心升级

- [x] 2.1 在 `backtesting/` 中新增结构化请求/结果模型与策略预设注册表，保留自定义 `generate_signals(data, ctx)` 入口。
- [x] 2.2 重构 `backtesting/engine.py` 为单标的 A 股账本式执行引擎，支持执行时点、仓位比例、手数、佣金、印花税、滑点、止损止盈。
- [x] 2.3 升级 `backtesting/pipeline.py` 与相关数据获取逻辑，支持可选基准、设置回显、对比指标与 richer report 输出。

## 3. Flask Backtest API

- [x] 3.1 扩展 `backend` backtest schema / service / serializer，接入新的结构化契约与结果格式。
- [x] 3.2 新增 `GET /api/v1/backtests/presets`，向前端暴露策略预设、参数 schema 和默认值。
- [x] 3.3 保持现有 `POST /api/v1/backtests/run` 路由稳定，并兼容旧的自定义策略字段映射。

## 4. Next.js 回测工作台

- [x] 4.1 升级前端类型、API client 与 payload builder，支持策略预设、基准、执行与成本配置。
- [x] 4.2 重做回测页交互：策略预设选择、动态参数表单、自定义代码编辑区和配置分组。
- [x] 4.3 升级结果展示，渲染设置摘要、指标、基准对比、序列摘要、交易统计、告警与最近成交记录。

## 5. 文档与验证

- [x] 5.1 更新 README、backend README 与迁移文档，说明 AKQuant-inspired 回测升级范围、接口变化和限制。
- [x] 5.2 运行定向 backend / frontend 测试、必要类型检查与语法检查，回填 OpenSpec 任务状态并提交改动。
