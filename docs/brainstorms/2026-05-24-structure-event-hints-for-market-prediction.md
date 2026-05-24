# Structure Event Hints For Market Prediction Brainstorm

Created: 2026-05-24
Status: active

## 背景

当前市场资讯链路已经具备：

- 多源资讯聚合，包括媒体快讯、标题流和官方公告披露。
- `MarketNewsIntelligenceService` 输出关键词和板块提示。
- `DeepSeekMarketPredictionService` 与本地启发式预测都能基于新闻上下文生成预测。

但现阶段系统仍把“公告/监管事件”主要当成普通新闻文本处理，没有单独抽出结构化事件层。这样会削弱公告流的研究价值，也让本地启发式预测无法直接利用回购、减持、股权激励、问询函等强信号。

## 当前判断

在现有架构下，最值得继续增强的不是再堆渠道，而是把当前已经接入的资讯变成更强的结构化上下文：

- 将新闻与公告按事件规则抽成 `eventHints`。
- 将 `eventHints` 进入 intelligence、prediction 和历史记录链路。
- 让本地启发式预测能优先利用事件信号，而不只是关键词和板块词命中。
- 当事件里包含明确股票代码时，把这些标的直接交接给回测 handoff。

## 本轮范围

- 在后端新增结构化 `eventHints` 提取能力。
- 为 intelligence / predictions API 增加 `eventHints` 字段。
- 更新 DeepSeek 预测上下文，纳入事件提示。
- 升级本地启发式预测，使其可根据强事件直接产生个股或事件主题预测。
- 若用户未显式传入 symbols，则用高置信事件中的相关标的回填 `backtestHandoff.symbols`。
- 在前端市场页展示事件提示。

## 非目标

- 不新增新的外部新闻源。
- 不做 PDF 正文解析。
- 不做真正的情绪模型或 NLP 分类器训练。
- 不改动认证、回测接口或前端整体布局系统。

## 成功标准

- `/api/v1/market/news/intelligence` 和 `/api/v1/market/news/predictions` 返回结构化 `eventHints`。
- 本地启发式预测在存在强事件时可给出更有针对性的预测，而不是只给板块泛化结果。
- `backtestHandoff.symbols` 在没有手工 symbols 时，可自动带出高优先级事件相关标的。
- 前端市场页能展示事件提示，不出现英文混用。
- 后端测试、OpenAPI 生成、前端类型和 OpenSpec 校验通过。

## 后续候选

- 基于事件类型做可调权重表和运营配置。
- 为监管问询、处罚、减持等高风险事件增加专门的风险面板。
- 在回测层增加“事件驱动候选股批量验证”工作流。
