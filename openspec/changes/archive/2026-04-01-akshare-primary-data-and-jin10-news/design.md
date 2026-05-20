## Context

当前仓库已经完成第一阶段的 Flask backend / Next.js frontend 架构迁移，但 `market` 能力在 backend 中仍是 placeholder。实际数据侧仍散落在遗留模块中：

- `backtesting/data.py` 的 `SmartDataProvider` 仍保留旧版 AkShare + 手写 Sina/Tencent 回退顺序。
- `market_data.py` 仍以手写 HTTP 聚合财联社、东方财富、同花顺和金十，未沉淀成 backend service。
- `backend/app` 还没有面向市场数据和新闻情报的 schema、service、API 路由。

同时，用户要求后续项目默认优先使用最新版 AkShare 作为核心市场数据源，并把金十实时资讯纳入“大盘 / 板块预测”前置链路。这意味着当前 change 既是依赖升级，也是一次跨 `legacy data layer + backend API + docs + OpenSpec` 的链路重组。

## Goals / Non-Goals

**Goals:**

- 升级 backend 使用的 AkShare 到最新版可安装版本，并以官方 AkShare 接口作为默认核心市场数据源。
- 将回测与 backend 市场服务的数据优先级统一为 AkShare-first，并明确保留的 fallback。
- 在 backend 中新增可调用的市场数据 / 新闻情报服务与 `/api/v1/market/*` 接口。
- 实现金十实时资讯 latest-100 拉取策略，补齐关键词提取与板块预测增强的服务骨架。
- 更新 README / backend README / OpenSpec 说明，使 AkShare-first 策略和 fallback 边界可追溯。

**Non-Goals:**

- 本轮不迁移整个 Streamlit 行情页到前端 React 页面。
- 本轮不实现完整 AI 板块预测模型，只提供可复用的输入数据和分析骨架。
- 本轮不重写所有 legacy 抓取器；对仍保留的 legacy provider 仅做降级说明和必要 fallback。
- 本轮不处理诊股、选股、新闻多源聚合的全部迁移，只优先完成 AkShare 主链路与 Jin10 backend 服务。

## Decisions

### 1. 历史 / 实时 / 板块数据统一改为 AkShare-first

`backtesting/data.py` 继续作为历史行情统一入口，但会调整成：

- 主路径：AkShare 官方接口
  - 历史日线：`stock_zh_a_hist`
  - 实时行情：`stock_zh_a_spot_em`
  - A 股代码表：`stock_info_a_code_name`
  - 概念 / 行业板块：`stock_board_concept_name_em`、`stock_board_industry_name_em`、对应 `*_cons_em`
- fallback：
  - `TushareProvider`：仅在配置了 `TUSHARE_TOKEN` 时作为历史行情的第二优先级
  - `SinaDirectProvider`：仅作为历史行情最后兜底

不再把旧的 AkShare 内部 Sina/Tencent 拉取器放在主优先级路径内，原因是它们会让“AkShare-first”与“旧多源优先级”混在一起，难以向 backend 和文档清晰说明。遗留的手写 EastMoney / Tencent / Sina 聚合逻辑只保留在 legacy 代码中，不再作为 backend 新链路的核心来源。

备选方案：

- 继续维持“AkShare 内多接口 + Tushare + Sina Direct”的混合优先级。
  - 放弃原因：无法清晰表达主数据源，也不利于定位上游字段变更。
- 直接把所有旧 provider 删除，只保留 AkShare。
  - 放弃原因：回测链路仍需要最小可用 fallback，尤其在 AkShare 临时波动时。

### 2. backend 新增独立市场服务，而不是继续堆在 `market_data.py`

在 `backend/app/services/` 新增面向 backend 的服务模块，例如：

- `market_data.py`：AkShare 市场快照、股票列表、热点板块、板块成分股、数据源说明
- `news_intelligence.py`：Jin10 拉取、标准化、关键词提取、板块提示生成

对应增加：

- `backend/app/schemas/market.py`
- `backend/app/api/market.py`

这样 backend API 可以直接对前端暴露稳定契约，同时避免把新架构再次耦合回遗留 `Streamlit` 文件。

备选方案：

- 直接从 backend import 现有 `market_data.py`。
  - 放弃原因：该文件过大、耦合多家来源、返回结构不稳定，不适合继续作为 backend service 边界。

### 3. 金十 latest-100 采用“官方 flash API 分页 + 去重补齐”策略

现网验证表明：

- `https://www.jin10.com/flash_newest.js` 可用，但默认不足 100 条。
- 页面 JS 中实际调用 `https://flash-api.jin10.com/get_flash_list`，需要 `x-app-id` 与 `x-version` 请求头。

因此本轮直接实现：

- 主接口：`GET https://flash-api.jin10.com/get_flash_list`
- 参数：
  - `channel=-8200`
  - `max_time=<上一页最旧时间>` 进行翻页
- 策略：
  - 循环抓取，按 `id` 去重，直到拿到 100 条唯一快讯或上游没有更多数据
  - 若官方 API 异常，则降级回 `flash_newest.js`，并在响应中标记 `degraded=true`

这是当前最符合“最新 100 条”要求且可稳定实现的方式。

### 4. 关键词提取与板块预测增强先落“可复用骨架”，不耦合 LLM

`news_intelligence.py` 输出分三层：

- `items`：标准化后的 Jin10 快讯
- `keywords`：综合 `tags + 标题/正文 + 大写金融术语/中文短语` 的词频结果
- `sectorHints`：将关键词与 AkShare 获取的概念/行业板块名称做规则匹配，输出命中板块、命中词和出现频次

这层先作为“大盘 / 板块预测”前置输入，不在本 change 中直接耦合 DeepSeek 或其他 LLM。这样可以先把 backend 契约稳定下来，后续 AI 分析只需消费该结构。

### 5. `/api/v1/market` 从 placeholder 升级为真实 backend 入口

`/api/v1/market` 本轮不再返回纯 placeholder，而是返回市场能力概览，包括：

- 当前 AkShare 主链路与 fallback 顺序
- 可用子接口
- 一次简要的 market intelligence 摘要（可选，取决于实现成本）

并新增子路由：

- `GET /api/v1/market/quotes`
- `GET /api/v1/market/sectors`
- `GET /api/v1/market/news`
- `GET /api/v1/market/news/intelligence`

`capabilities` 中 `market` 状态更新为 `migrated`，但 summary 会说明“已完成 backend 侧数据与新闻接口，前端深度页面仍待迁移”。

## Risks / Trade-offs

- `[AkShare 上游字段变化]` → 通过统一 normalize、异常捕获和测试桩固定输出结构。
- `[金十 API 为非正式公开接口]` → 同时保留 `flash_newest.js` 降级路径，并在响应中显式标记数据源与降级状态。
- `[板块匹配规则偏粗]` → 先输出可解释的 `matchedKeywords` 与 `score`，后续再叠加 AI 或更复杂 NLP。
- `[backend 与 legacy 数据逻辑并存]` → 文档中明确“backend 主链路”和“legacy-only provider”边界，避免再次回退到 Streamlit 直接耦合。

## Migration Plan

1. 升级 backend AkShare 依赖并同步锁文件。
2. 先通过测试定义 backend 市场 API、Jin10 latest-100、AkShare fallback 顺序的目标行为。
3. 实现 backend `market` API、service、schema 和 `backtesting/data.py` 的新主链路。
4. 更新 capability inventory、README、backend README 和 OpenSpec 任务状态。
5. 运行 backend 单测与必要语法检查，按里程碑提交：
   - OpenSpec 制品
   - AkShare 主链路
   - Jin10 新闻 intelligence 骨架与文档

回滚策略：

- 若 AkShare 新版或新 market API 引入问题，可回退到上一提交，旧 backtest / placeholder 能力仍然可恢复。

## Open Questions

- 当前不阻塞实现的开放项只有一项：后续前端市场页是直接消费 `/api/v1/market/*`，还是先保留前端占位页并只开放 API 给后续页面接入。该问题不影响本轮 backend 实现。
