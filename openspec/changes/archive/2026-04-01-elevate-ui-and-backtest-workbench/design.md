## Context

当前仓库已经完成 phase-one 的默认运行形态切换：`frontend/` 负责 Next.js UI，`backend/` 负责 Flask API，legacy 业务模块继续作为适配层复用。问题不在“有没有壳”，而在“壳是否像一个真的产品”。

目前主要存在四类落差：

- `frontend/app/page.tsx`、`frontend/components/app-shell.tsx` 和 `frontend/app/globals.css` 已形成统一样式，但视觉结构仍偏演示页，不足以承载高密度金融工具的工作台信息。
- `frontend/components/backtest-console.tsx` 已能完成主链路调用，但输入是长表单堆叠，默认值与执行假设缺少解释，结果区也偏“指标平铺”，不利于理解风险、成本和执行差异。
- `frontend/app/market/page.tsx` 仍然只是 placeholder，和 backend 已经提供的 `/api/v1/market/*`、Jin10 intelligence 链路脱节。
- `frontend/app/screener/page.tsx` 与 `frontend/app/diagnosis/page.tsx` 仍需要保持诚实的骨架表达，但当前 placeholder 过于粗糙，容易给人“只是暂时没做样式”的感觉，而不是“有明确边界和后续路线”。

这一轮既涉及前端整体交互与视觉升级，也会牵动回测 preset metadata、report contract 和部分 backend service 输出，因此属于典型的跨模块 change。

## Goals / Non-Goals

**Goals:**

- 为 Next.js 前端建立更完整、更专业的研究工作台体验，而不是继续停留在 phase-one 演示壳层。
- 用统一的布局、视觉语义和状态组件，改善首页、回测页、市场页与占位页之间的一致性。
- 把市场页升级为真实消费 backend 市场与新闻 intelligence API 的工作台，但只展示仓库当前已经真实提供的数据与规则引擎结果。
- 继续增强回测工作台的输入体验、默认值解释、结果可解释性和风险/成本/执行假设清晰度。
- 保持前后端契约和文档诚实一致，不把 `screener` / `diagnosis` 伪装成已迁移完成。

**Non-Goals:**

- 本轮不迁移东方财富条件选股的真实后端链路，也不把 screener 页面升级成可执行工作台。
- 本轮不迁移 AI 诊股的实时行情与提示词拼装逻辑。
- 本轮不把回测升级成组合级撮合、异步任务执行器或策略代码 IDE。
- 本轮不为市场页新增与现有 API 完全重复的新 endpoint，除非现有响应无法支撑必要交互。

## Decisions

### 1. 采用“研究台 + 交易台”混合视觉方向，而不是继续沿用 landing page 叙事

前端整体视觉方向将收敛为“研究台 + 交易台”混合风格：保留现有温暖纸张底色与带网格的背景气质，但提高面板密度、数据层级、状态对比和信息边界，让页面更像专业 A 股研究工具。

实现方式：

- 继续复用 `Fraunces + IBM Plex Sans` 作为 display/body 字体，避免无必要的字体依赖变更。
- 在 `globals.css` 中引入更完整的 design tokens：面板层级、状态色、边框透明度、风险/成功/告警色、图表底层色。
- 统一 panel、metric、status pill、section title、empty/loading/error card 的视觉规范。
- 让导航、首页、市场页、回测页共用相同的“顶层摘要 + 主内容工作区 + 辅助解释区”结构。

备选方案：

- 直接只微调现有卡片圆角、颜色和字距。
  - 放弃原因：只能算“换皮”，不能解决工作台信息密度和状态表达不足的问题。
- 完全切成暗色金融终端风格。
  - 放弃原因：当前仓库已有浅色品牌基调，完全推翻会扩大改动范围，也未必适合所有页面。

### 2. 首页、市场页、回测页按“真实能力分层”组织，而不是按文案块堆叠

页面结构会统一采用三层信息架构：

- 顶层：当前能力概况与路线定位
- 中层：用户可操作或可验证的工作区
- 底层：边界、假设、风险和下一步说明

具体落地：

- 首页：展示 capability inventory、真实完成度、推荐入口和 backend/runtime 事实，而不是只讲迁移故事。
- 回测页：将输入拆成 `市场范围 / 策略 / 执行 / 成本 / 风险` 五组，旁侧提供实时摘要与最佳实践提示，结果区拆成收益、风险、假设、交易记录几个层次。
- 市场页：真正调用 API，呈现数据源概览、监控标的报价、热门板块、最新快讯、关键词和板块提示。
- screener / diagnosis：继续保留 placeholder，但升级为统一“诚实骨架页”，展示当前状态、依赖条件和下一阶段边界。

备选方案：

- 仅升级 backtests 页面，其它页面保持原样。
  - 放弃原因：用户明确要求 UI / UX / 交互全面升级，且首页、市场页仍是当前主要割裂点。

### 3. 市场页前端直接聚合现有 backend market/news API，不新增冗余 dashboard endpoint

市场页将新增一个专用 client component，在前端并行请求：

- `GET /api/v1/market`
- `GET /api/v1/market/quotes`
- `GET /api/v1/market/sectors`
- `GET /api/v1/market/news`
- `GET /api/v1/market/news/intelligence`

交互范围控制在高价值、低耦合的几项：

- 自定义 watchlist 股票代码输入
- 热门板块类型切换（concept / industry）
- 新闻列表与 intelligence 摘要同步刷新
- 明确展示 `source`、`degraded`、`requestedLimit` 等真实元信息

这样可以最大化复用已落地的 backend API，同时避免为了 UI 拼装再新增一个只服务单页的新聚合接口。

备选方案：

- 在 backend 新增 `/api/v1/market/dashboard` 聚合接口。
  - 放弃原因：当前 API 已足够支撑页面，新增聚合层会增加维护成本且收益有限。

### 4. 回测工作台强化“引导式输入”和“解释型结果”，重点增强 metadata 与 derived report，而非继续堆更多执行开关

这轮回测增强不会继续扩展大量新参数，而是优先做三件高价值事情：

- 用 richer preset metadata 驱动更好的参数解释
- 用 quick profiles 和实时摘要降低配置门槛
- 用 derived report 提高结果解释性

具体契约变化：

- `GET /api/v1/backtests/presets`
  - 为 preset 增加更强的展示字段，例如 `summary`、`useCase`、`riskNotes`
  - 为 `parameterSchema` 增加 `helpText`、`group`
- `POST /api/v1/backtests/run`
  - 保持现有路由与主分组结构不变
  - 增强结果中的交易统计与解释字段，至少覆盖更清晰的风险/成本/暴露信息，供前端渲染摘要与说明

前端交互变化：

- 引入研究默认 / 保守成交 / 趋势放大等 quick profile，快速设置 execution/cost/risk 组合
- 新增前端校验和解释文案，例如 symbol 数量、日期范围、`next_open` 最后一根 K 线限制、成本参数含义
- 结果按“总览 / 绩效风险 / 交易执行 / 月度与告警”分组，而不是只平铺指标

备选方案：

- 新增更多 engine 参数，例如最小持有天数、分批成交、停牌约束。
  - 放弃原因：这会显著扩大 scope，且未必比先提升默认值解释与结果可读性更高价值。

### 5. Backend 只补足前端真正需要的 report 字段，不重构整个回测执行链

后端增强的重点放在“前端可直接消费的解释型数据”，而不是大规模改写引擎。计划包括：

- 在 `backtesting/presets.py` 为预设和参数 schema 增加 metadata
- 在 `backtesting/engine.py` / `backend/app/services/backtests.py` 中补充高价值统计，例如暴露率、收益因子、期末权益、净利润或等价解释字段
- 保持 `BacktestRunRequest` 的主结构稳定，避免破坏现有 API 兼容性

这样既能为 UI 提供更好的解释数据，又能控制风险。

备选方案：

- 直接在 frontend 从现有字段临时拼接所有解释，不做任何 backend contract 增强。
  - 放弃原因：部分高价值指标和 preset metadata 更适合由 backend/engine 输出，避免前端重复推导和魔法常量。

### 6. Placeholder 页面继续保留，但升级为“诚实的 capability brief”

`screener` 和 `diagnosis` 页面不会继续使用泛化 placeholder 文案，而会升级为统一的 capability brief 组件，明确说明：

- 当前 capability status
- 已经具备的前置边界
- 尚未迁入的真实依赖
- 下一阶段计划

这样既能提升整体 UI 完整度，也能满足“完成度必须诚实”的要求。

## Risks / Trade-offs

- `[前端改动面较广]` → 通过复用共享样式 token 和组件语义，避免每个页面各自长出一套样式。
- `[回测解释字段扩展可能牵动多层类型]` → 先以定向测试锁定新增 metadata / report 字段，再修改 backend serializer 和 frontend types。
- `[市场页真实接 API 后更依赖网络与上游源]` → 前端必须实现清晰的 loading / error / degraded 状态，而不是假设接口总成功。
- `[placeholder 升级容易被误解为“功能快做完了”]` → 文案与 capability pill 必须始终明确 `skeleton` 状态，不使用模糊表述。
- `[CSS 重构影响全站]` → 避免无边界地重写所有 class，优先保留现有命名并逐步扩展 token 和布局层。

## Migration Plan

1. 先为回测 helper / backend API contract 补失败测试，锁定新增 metadata 和解释型字段。
2. 扩展 preset metadata、trade stats / report serializer，并在 backend 测试通过后再改前端 types。
3. 重构前端 app shell、首页、回测页、市场页与 capability brief 组件，统一样式和状态表达。
4. 同步更新 README、迁移文档和 OpenSpec delta，确保“真实完成度”与页面状态一致。
5. 完成自查 review、运行 OpenSpec 校验、前后端测试/类型检查/构建与必要 smoke。

回滚策略：

- 后端 API 路由不变，必要时可先保留新增字段为可选，避免影响现有调用。
- 前端市场页若出现问题，可降回 capability brief，但本轮默认目标是接通真实 API。

## Open Questions

- 当前没有阻塞性开放问题。本轮默认不新增市场聚合 endpoint，也不扩展 screener / diagnosis 的真实业务执行链路；若实现中发现现有 API 无法支撑必要页面交互，再局部补充最小后端字段。
