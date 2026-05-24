## Context

现有资讯聚合已经形成稳定分层：

- `Jin10NewsService` 管主快讯与 fallback。
- `MultiSourceNewsService` 管渠道聚合、去重、质量评分和缓存降级。
- `MarketNewsIntelligenceService` 管关键词、板块提示、预测和回测 handoff。

本轮不需要重构聚合架构，只需要把 `CNInfo` 官方公告流作为新的结构化 source 接入。

## Goals / Non-Goals

**Goals:**

- 增加第一批官方公告披露渠道。
- 让公告源进入现有多源资讯、关键词和预测链路。
- 保持现有 market news response contract 不变。
- 用测试固定 CNInfo 接口请求参数和字段标准化行为。

**Non-Goals:**

- 不抓取 PDF 正文。
- 不新增公告专属 API 路径或前端页面。
- 不直接接入交易所监管问询页。
- 不改变现有 prediction/backtest 流程。

## Decisions

### Decision: 使用 CNInfo 结构化接口而不是页面硬刮

`https://www.cninfo.com.cn/new/disclosure` 已提供公告结构化列表，字段和市场列值均在官方页面脚本中直接可见。

Rationale:

- 字段完整，包含公告标题、时间、证券简称/代码、公告类型和 PDF 链接。
- 解析成本明显低于 HTML 页面。
- 比单独维护多个交易所 HTML 抓取更稳定。

Alternative considered:

- 分别抓取上交所/深交所官网列表页。Rejected，因为当前页面多为前端二次拉数或模板渲染，接入复杂度更高。

### Decision: 按市场拆分成独立 channel

第一批将 `szse_latest`、`sse_latest`、`bj_latest` 分别视为独立 source。

Rationale:

- 便于质量监测和失败隔离。
- 便于后续做启停开关和优先级控制。

Alternative considered:

- 将全部公告混成一个 CNInfo 总源。Rejected，因为会弱化每个市场的可观测性。

### Decision: 继续使用标题级正文占位，不解析 PDF 内容

本轮将公告行标准化为“证券简称 + 公告标题 + 公告类型”的简要内容占位，不下载 PDF 正文。

Rationale:

- 请求成本低。
- 足够支撑关键词和主题抽取。
- 避免引入 PDF 解析、摘要抽取和额外失败面。

Alternative considered:

- 解析 PDF 正文或自动摘要。Rejected，因为超出本轮范围。

## Risks / Trade-offs

- 公告天然数量多、重复率高 -> 继续依赖现有去重与 quality scoring。
- 结构化接口返回字段可能调整 -> 用单元测试固定字段读取行为。
- 公告标题比媒体快讯更“文书化” -> 用证券简称、证券代码和公告类型增强 tags，提升下游可用性。

## Migration Plan

1. 新增 CNInfo 配置项和 source class。
2. 将深市、沪市、北交所三个 source 接入默认工厂。
3. 添加解析与聚合测试。
4. 更新 README 与 backend README。
5. 跑后端测试与 OpenSpec 校验。

Rollback:

- 删除新增 source 注入即可回到现有媒体/快讯聚合。
- 或将 CNInfo URL 配置清空并在 factory 层跳过注入。

## Open Questions

- 本轮无阻塞问题。后续若要接入监管问询、纪律处分、审核动态，应单独做新 change。

## Next Candidates

1. 上交所监管问询与审核动态
   - 价值：更适合做“风险事件/监管事件”线索。
   - 原因：需要单独确认页面拉数接口和字段稳定性。

2. 深交所问询函、监管函与关注函
   - 价值：对高风险个股和主题退潮判断很有帮助。
   - 原因：不应和公告流混在同一 source 中处理。

3. 公告事件类型结构化
   - 价值：可把回购、减持、激励、业绩预告等直接转成预测 prompt 的高权重因子。
   - 原因：需要单独设计事件分类与噪声过滤策略。
