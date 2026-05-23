## Overview

本 change 将前端体验和预测后端闭环同时收敛。前端以中文投研终端为目标风格，所有页面共享同一套布局、状态、指标和表格语法。后端在现有多源资讯与 DeepSeek 预测基础上增加质量评分、历史持久化、详情和评估接口，并通过 OpenAPI 暴露给前端。

设计参考：
- `docs/design/2026-05-22-chinese-research-terminal-reference.png`
- `docs/design/2026-05-23-chinese-research-terminal-page-board.png`
- `docs/design/2026-05-23-chinese-research-terminal-prototype.html`

## Frontend Design Direction

目标场景：研究员在白天办公环境中使用的中文 A 股研究终端。界面应高密度、克制、清楚表达状态，不做营销页、英雄区、渐变大标题或装饰性卡片堆叠。

本轮 UI 重构必须以 `huashu-design` 的高保真 HTML 原型工作方式执行：先从现有产品上下文、真实接口和页面信息架构出发，形成可落地的投研终端视觉语法，再映射回 Next.js 页面和组件。交付重点不是保留旧版皮肤，而是重建可上线的页面系统。

页面结构：
- 左侧/顶部导航统一中文模块名。
- 顶部状态区展示数据通路、模型状态和登录态，不展示“已迁移”“已接入”等迁移期标签。
- 主体区域按“控制 -> 结果 -> 解释 -> 风险/历史”组织。
- 行情预测页额外提供预测详情和历史复盘。
- 移动端保留同一信息层级，改为纵向堆叠。

视觉语法：
- 专业中文投研终端：浅底工作区、深色导航轨、低饱和蓝灰与朱砂风险色，少量金融绿只用于收益或命中状态。
- 卡片圆角不超过 8px。
- 状态色只服务成功、降级、错误、待评估，不做装饰色块；不使用大面积渐变、装饰光斑、营销页式 hero 或套卡片。
- 中文正文优先可读性，紧凑但不拥挤。
- 页面组件统一使用“模块头部、工具条、数据表、指标砖、状态条、解释面板、风险提示”这些工作台元素，不保留旧版 placeholder 组件语义。

## UI-To-API Truth Boundary

所有前端功能入口必须能映射到真实后端路由、OpenAPI 绑定或本地认证路由。没有后端接口支撑的页面功能、假状态、迁移口径、占位口径一律从 UI 中移除，而不是以“已迁移”“骨架中”“规划中”“当前可用范围”等文案继续展示。

保留入口：
- 总览页：只展示真实接口清单、研究流程和已可调用模块。
- 行情预测页：`market`、`market/quotes`、`market/sectors`、`market/news`、`market/news/intelligence`、`market/news/predictions`、预测历史、详情和评估接口。
- 回测页：`backtests/presets` 和 `backtests/run`。
- 选股页：`screener`、`screener/run`、`screener/export`。
- 诊股页：`diagnosis` 和 `diagnosis/run`。
- 因子页：`factors` 和 `factors/analyze`。
- 组合页：`portfolio` 和 `portfolio/optimize`。

能力状态契约改为“可用、受限、停用”这类产品运行状态，不再用迁移状态描述能力。OpenAPI、前端类型、后端能力服务和测试需要同步调整。

## Backend Prediction Loop

现有链路：

```text
多源资讯 -> 关键词/板块提示 -> DeepSeek 或本地启发式预测 -> 回测交接
```

新增链路：

```text
多源资讯 -> 来源质量评分
        -> DeepSeek V4 Flash 预测
        -> 写入本地预测历史
        -> 详情查询 / 历史查询 / 行情评估
        -> 前端预测详情页与回测验证
```

## DeepSeek Configuration

默认模型保持 `deepseek-v4-flash`。后端配置项：
- `BACKEND_DEEPSEEK_MODEL`
- `BACKEND_DEEPSEEK_THINKING_TYPE`: `enabled` 或 `disabled`
- `BACKEND_DEEPSEEK_REASONING_EFFORT`: `high` 或 `max`

请求策略：
- 对 DeepSeek Chat Completions 发送 `thinking: {"type": ...}`。
- 当 thinking 启用时发送 `reasoning_effort`。
- cache key 包含 model、schemaVersion、thinkingType、reasoningEffort 和 inputDigest。
- metadata 返回实际模式，前端不得猜测。

## Prediction History Storage

本地持久化采用 JSONL：
- 默认路径由后端配置指定，未配置时落在 Flask instance 目录。
- 每次预测响应生成一个 `runId`。
- 每条 prediction 生成稳定 `predictionId`。
- 单条记录保存预测上下文摘要、metadata、sourceQuality、dedupeMetadata、riskNotes、backtestHandoff 和 predictions。

保留策略：
- 本 change 只实现 bounded read/write，不做定时清理。
- 读取接口支持 limit，默认不返回无限历史。
- 文件损坏行跳过并在 metadata 中体现，不让整个接口失败。

## Evaluation Semantics

评估只对可解释的目标执行：
- 当 prediction target 或 symbols 能映射到股票代码，且行情服务能返回报价和涨跌幅时，生成方向评估。
- bullish 且涨跌幅为正 -> hit。
- bearish 且涨跌幅为负 -> hit。
- neutral 且绝对涨跌幅小于阈值 -> hit。
- 缺少报价、主题/板块无法映射、目标不明确 -> pending。

评估输出：
- `evaluationSummary`: 总数、可评估数、命中数、命中率、待评估数。
- `evaluationItems`: predictionId、target、direction、actualChangePercent、status、note。

## OpenAPI And Frontend Binding

新增 protected routes：
- `GET /api/v1/market/news/prediction-history`
- `GET /api/v1/market/news/predictions/{runId}`
- `GET /api/v1/market/news/predictions/{runId}/evaluate`

现有 `GET /api/v1/market/news/predictions` 扩展 query：
- `thinking`
- `reasoningEffort`

前端 OpenAPI binding 必须覆盖新增路由，并保持 bearerAuth 安全声明一致。

## Compatibility

- 现有 prediction endpoint 继续返回原字段，新增字段为向后兼容扩展。
- 新增接口不会改变已有 market/news/intelligence 行为。
- 本地历史文件不存在时返回空历史，不视为错误。
- DeepSeek 配置缺失时继续使用本地启发式预测。

## Cutover

1. 发布后端字段和新增接口。
2. 重新生成 OpenAPI。
3. 更新前端类型与 binding。
4. 前端先兼容空历史和降级预测，再展示详情与评估。

## Rollback

- 前端可隐藏预测历史/评估区域，主 prediction endpoint 仍可工作。
- 删除或忽略本地 JSONL 历史文件不会影响实时预测。
- DeepSeek thinking 配置可通过环境变量切回默认启用或非思考模式。
