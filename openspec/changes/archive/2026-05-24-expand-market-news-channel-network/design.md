## Context

现有资讯聚合已经具备清晰的分层：

- `Jin10NewsService` 管主快讯与 fallback。
- `MultiSourceNewsService` 管渠道聚合、去重、质量评分和缓存降级。
- `MarketNewsIntelligenceService` 管关键词、板块提示、预测和回测 handoff。

因此，本轮不需要重写架构，只需要为 `MultiSourceNewsService` 增加新的可稳定解析渠道，并把渠道配置上提到 `config.py` 和 API factory。

## Goals / Non-Goals

**Goals:**

- 增加第一批稳定可接入的公开资讯渠道。
- 复用现有 market news response contract。
- 保持单渠道失败不影响整体返回。
- 用测试固定页面嵌入 JSON 和 HTML 标题列表解析行为。

**Non-Goals:**

- 不引入全文详情抓取。
- 不新增签名 API、登录态依赖或新的抓取基础设施。
- 不修改前端展示结构。

## Decisions

### Decision: CLS 使用页面内嵌 JSON 解析

`https://www.cls.cn/telegraph` 页面内嵌 `__NEXT_DATA__`，其中 `telegraphList` 已经给出标题、正文、作者、时间和详情链接。优先解析该 JSON，而不是从 DOM 可见文本回刮。

Rationale:

- 结构化程度高。
- 不依赖页面样式类名。
- 比搜索未公开接口或签名请求更稳。

Alternative considered:

- 抓取 CLS 未公开接口。Rejected，因为签名和风控不稳定。

### Decision: STCN 与 21 财经采用标题级 HTML 文章列表聚合

这两个站点当前最稳定的是首页或频道页上的文章链接集合，因此本轮只聚合标题、链接和基础时间线索，不抓详情页正文。

Rationale:

- 请求量低。
- 实现简单，适合作为第一批公开源。
- 仍能显著提升题材覆盖。

Alternative considered:

- 二跳抓详情页并抽正文。Rejected，因为复杂度明显上升，且当前 prediction 流程并不要求每条新闻都必须有长正文。

### Decision: 不接入当前异常 RSS 作为正式源

调研发现部分公开 RSS 当前存在编码异常、历史内容或空白结果，因此不纳入默认正式源。

Rationale:

- 资讯数量增加不能以内容失真为代价。
- 渠道质量直接影响 `sourceQuality` 和 prediction 上下文。

Alternative considered:

- 先接入 RSS 再容忍噪声。Rejected，因为会污染聚合质量分和下游预测输入。

## Risks / Trade-offs

- 页面结构变化 -> 通过解析测试和宽松提取策略缓解。
- 标题级 source 缺少长正文 -> 用标题作为内容占位，不阻断关键词提取。
- 新渠道增加重复率 -> 继续依赖现有去重键和 source-quality 评分反映 duplicate pressure。

## Migration Plan

1. 新增配置项和 source class。
2. 将 source 接入 `NEWS_INTELLIGENCE_SERVICE_FACTORY`。
3. 添加解析与聚合测试。
4. 更新 README 与 backend README。
5. 跑后端测试与 OpenSpec 校验。

Rollback:

- 删除新增 source 注入即可回到旧的三源聚合。
- 或将对应 URL 配置清空并在 factory 层跳过注入。

## Open Questions

- 本轮无阻塞问题。后续若要引入搜索 provider 或社交舆情，应单独做新 change。

## Next Candidates

本轮实现完成后，下一批高价值候选方向如下：

1. 交易所与公告披露源
   - 巨潮资讯、上交所、深交所公告与监管问询。
   - 价值：结构化程度高，适合直接转成事件信号。
   - 原因：需要单独评估站点稳定性、频控和公告去重策略。

2. 稳定的快讯补充源
   - 同花顺快讯、凤凰财经等公开页面或 feed。
   - 价值：可继续补足盘中热点覆盖。
   - 原因：当前环境连通性和内容质量不稳定，不宜直接纳入默认正式源。

3. 社交舆情源
   - 雪球热帖、东方财富股吧热榜、微博财经话题。
   - 价值：可补足市场情绪与散户讨论热度。
   - 原因：需要单独设计情绪打分、反噪声和频控策略，不应与新闻源混在同一 change 内。
