# Expand Market News Channel Network Brainstorm

Created: 2026-05-24
Status: active

## 背景

当前市场资讯链路已经具备：

- `Jin10NewsService` 作为主快讯源，带官方接口和公开 fallback。
- `MultiSourceNewsService` 作为聚合器，当前额外接入东方财富资讯和新浪财经直播。
- `MarketNewsIntelligenceService` 负责关键词、板块提示、DeepSeek 预测和回测 handoff。

用户本轮要求继续增强新闻源内容，增加更多资讯渠道，但不能为了“渠道数量”接入质量差、当前不可用或返回失真的公开 feed。

## 当前调研结论

本轮优先接入的第一批稳定源：

- `财联社电报页`：`https://www.cls.cn/telegraph`
  - 页面可访问。
  - HTML 中内嵌 `__NEXT_DATA__` JSON，包含实时电报列表、标题、正文、作者、时间和详情链接。
  - 适合做结构化抓取，不需要额外签名接口。

- `证券时报首页`：`https://www.stcn.com/`
  - 页面可访问。
  - 页面中包含大量 `/article/detail/<id>.html` 链接，可提取当前财经/证券新闻标题和链接。
  - 适合做标题级聚合，必要时用标题作为内容占位。

- `21世纪经济报道证券频道`：`https://www.21jingji.com/channel/capital`
  - 页面可访问。
  - 页面包含大量 `/article/...html` 链接，且聚焦证券与资本市场。
  - 适合做资本市场方向的补充源。

本轮不作为第一批正式源的候选：

- `Sina RSS`
  - 当前公开 feed 在实际返回中出现明显编码异常和历史内容，不适合直接生产接入。

- `Ifeng RSS`
  - 当前公开 feed 可访问，但返回几乎空白，无法稳定提供有效资讯内容。

- `10jqka 快讯`
  - 当前环境访问握手不稳定，不适合直接作为第一批默认源。

## 本轮范围

- 为市场资讯链路新增 3 个额外渠道：
  - 财联社电报页
  - 证券时报首页文章列表
  - 21世纪经济报道证券频道文章列表
- 将这些渠道接入 `MultiSourceNewsService`，并保持现有 Jin10 / 东方财富 / 新浪路径。
- 保持现有聚合返回结构：
  - `channels`
  - `sourceQuality`
  - `dedupeMetadata`
  - `warnings`
- 扩展配置项和 README，明确每个渠道的 URL 与行为。
- 补测试，验证：
  - 页面嵌入 JSON 解析
  - HTML 标题列表解析
  - 多渠道失败/成功/去重行为

## 非目标

- 不新增前端页面或新的 API 路径。
- 不做全文抓取、正文详情页二跳抓取或复杂反爬逻辑。
- 不引入需要登录态、签名算法或付费 API key 的资讯源。
- 不把新闻源扩展变成社交舆情系统，本轮仍是资讯聚合增强，不是情绪因子平台。

## 成功标准

- `/api/v1/market/news`、`/api/v1/market/news/intelligence`、`/api/v1/market/news/predictions` 在无需新前端改造的前提下返回更多来源的资讯结果。
- `channels` 中能看到新增的渠道名称与状态。
- 单一新增渠道失败不会导致整个资讯接口失败；所有渠道失败时仍遵守缓存降级语义。
- 新增 source 经过去重后不会显著放大同一条重复资讯。
- 后端测试、OpenSpec 校验和文档更新通过。

## 后续候选

- 引入渠道启停开关和优先级配置，而不是固定写死 extra source 列表。
- 将新闻源按“快讯 / 深度 / 券商 / 海外”分组，进一步优化 prediction prompt 的上下文构成。
- 单独做一轮“社交舆情与新闻搜索 provider” OpenSpec 变更，接入需要 API key 的搜索或舆情源。
