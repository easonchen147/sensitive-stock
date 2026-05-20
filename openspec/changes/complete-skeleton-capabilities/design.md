## Context

当前仓库已经明确采用 `frontend/` + `backend/` 的分离工作区，并通过 capability inventory 区分 `migrated` 与 `skeleton`。问题在于，四类半成品能力虽然已经有名称、路由边界和部分 legacy 模块，但产品和平台都还没有把它们真正“接起来”：

- `screener` 只有 placeholder API 和 brief 页面；
- `diagnosis` 只有 placeholder API 和 brief 页面；
- `factors` / `portfolio` 虽然有底层 Python 模块和测试契约，但没有正式 API 与前端；
- capability inventory 继续把它们当 skeleton，也就意味着首页、导航和文档只能诚实地承认“没做完”。

本设计的目标不是单点补一个页面，而是把四类半成品整体推进为正式研究能力，并与现有登录、行情、回测、OpenAPI 边界衔接。

## Goals / Non-Goals

**Goals:**

- 为四类半成品能力建立正式的 service / schema / API / frontend workbench 闭环。
- 建立“市场数据 + 指标 + 结果导出 + 错误表达”的共享基础层。
- 让 `screener` 结果可以回灌回测，形成研究闭环。
- 让 `diagnosis` 能生成结构化报告，而不是仅做聊天或占位说明。
- 让 `factors` / `portfolio` 从保留代码升级为可调用能力。

**Non-Goals:**

- 本轮不引入多租户、协作、异步任务平台或数据库持久化。
- 本轮不恢复旧 Streamlit 页面。
- 本轮不在该 change 内直接完成 AKQuant 替换或全站视觉重构，这两者由相邻提案承接。

## Decisions

### 1. 四类能力统一走“service first”而不是直接把 legacy 模块暴露为 API

所有能力先收口到 `backend/app/services/*`，由 service 层负责：

- 参数归一化
- 数据源调用
- 结果格式化
- 错误与 degraded metadata 归口

原因：

- 避免 API 层直接持有 legacy 逻辑。
- 为 OpenAPI、前端类型和测试提供稳定边界。
- 便于未来把底层算法或外部依赖替换掉，而不破坏路由。

备选方案：

- 直接在 `api/*.py` 中调用现有模块。
  - 放弃原因：会让平台边界继续脆弱，也不利于后续 OpenAPI 统一。

### 2. `factors` / `portfolio` 先正式 API 化，再推进 `screener` / `diagnosis`

四类能力虽然都属半成品，但成熟度不同：

- `factors` / `portfolio` 已有底层模块与测试契约；
- `screener` / `diagnosis` 还需要更多外部链路、模板与前端闭环。

因此实施顺序应先把“最接近可用 API”的两类能力转正，再推进复杂链路。

### 3. `screener` 采用“模板条件 + 自然语言解释/转换 + 回测联动”的双层模型

`screener` 不应只暴露一个“自然语言请求黑盒”，而应同时支持：

- 可解释的模板条件筛选；
- 自然语言输入转换为结构化筛选条件；
- 结果序列化、导出和一键回测。

这样做的原因：

- 模板条件是稳定、可测试和可复现的主路径；
- 自然语言转换是增强层，而不是唯一执行入口；
- 能避免把选股能力做成只适合演示的 opaque black box。

### 4. `diagnosis` 输出结构化报告，而不是自由文本为主

诊股链路需要结合：

- 最新行情概览
- 技术指标摘要
- 市场背景
- 风险提示
- 最终建议或观察结论

因此 API 返回应以结构化报告为主，文本解释作为字段之一，而不是只有单段大模型输出。

备选方案：

- 仅返回一段 AI 文本。
  - 放弃原因：难以测试、难以前端分块展示，也不利于失败兜底。

### 5. capability inventory 的状态转换必须和真实交付同步

本 change 完成后，对应四类能力应从 `skeleton` 升级为 `migrated` 或等价正式状态。首页、导航和工作台状态语言必须同步更新，不能出现“功能已经做完但 inventory 还说 skeleton”的分叉。

## Risks / Trade-offs

- `[四类能力同时推进范围较大]` -> 通过先 API 化 `factors/portfolio`、再补 `screener/diagnosis` 控制顺序与风险。
- `[自然语言选股与 AI 诊股依赖外部链路]` -> 将结构化模板 / 指标报告作为稳定主路径，外部模型或转换能力作为增强层。
- `[诊股结果主观性较强]` -> 把报告拆成结构化事实层、指标层和解释层，减少纯主观文本漂移。
- `[前端页面一次性增多]` -> 与 Huashu 设计提案协同，以统一页面模板降低重复设计成本。

## Migration Plan

1. 先为 `factors` / `portfolio` 补 service、schema、API 与 contract tests。
2. 再实现 `screener` 的模板筛选、自然语言转换与回测跳转契约。
3. 再实现 `diagnosis` 的指标、上下文和结构化报告链路。
4. 更新 capability inventory 与前端页面，把 skeleton brief 切换为真实工作台。
5. 同步将全部接口纳入 OpenAPI 平台提案的统一契约。

回滚策略：

- 每类能力的 service 与 route 独立落地，可按模块回退。
- `screener` 和 `diagnosis` 若增强层有问题，可保留结构化主路径，临时降级自然语言/AI 部分。

## Open Questions

- 自然语言选股是否直接绑定东方财富链路，还是保留一层中间 DSL，供多数据源或多上游适配。
- 诊股模型调用是仅服务端直接接外部模型，还是为未来 provider 切换预留 provider 抽象。
