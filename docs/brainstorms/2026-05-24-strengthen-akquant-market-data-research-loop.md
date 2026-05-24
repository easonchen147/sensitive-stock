# Strengthen AKQuant Market Data Research Loop Brainstorm

Created: 2026-05-24
Status: active

## 背景

本轮目标是继续强化股票预测回测系统的真实研究能力，重点来自四个输入：

- 继续挖掘 `akfamily/akquant` 已提供但当前适配层尚未充分暴露的回测能力。
- 将 `akfamily/akshare` 升级到当前可用最新版本，并保持 AkShare 作为 A 股行情主数据源。
- 引入 `tickflow-org/tickflow` 作为优先增强的行情数据补充源，提升历史行情与实时报价的可用性。
- 参考 `ZhuLinsen/daily_stock_analysis` 的多源数据、新闻搜索、社交舆情、回测和预测设计，提炼适合当前系统的增强点。

## 外部调研结论

- AkShare 当前可用版本为 `1.18.63`，本仓库仍固定在 `1.18.49`，需要升级并刷新锁文件。
- AKQuant 当前可用版本仍为 `0.2.37`，本仓库版本已对齐，但适配层还未暴露 `volume_limit_pct`、`min_commission`、`transfer_fee_rate`、策略级风控和流式事件摘要等能力。
- TickFlow 当前可用版本为 `0.1.21`。免费服务支持历史日 K 和标的信息；完整服务在配置 `TICKFLOW_API_KEY` 后支持实时行情和更高频接口。
- `daily_stock_analysis` 的高价值设计不是直接复制代码，而是抽象成当前系统可承载的能力：
  - 数据源接入要有明确优先级、降级状态和错误诊断。
  - TickFlow 适合作为行情稳定性增强源，而不是替换 AkShare 主源。
  - 新闻搜索和社交舆情需要外部 API key、配额和合规边界，当前不应做成无接口支撑的前端入口。
  - 回测报告要展示数据质量、执行质量、风险诊断，而不是只展示收益指标。

## 本轮增强范围

- 行情数据：
  - 升级 AkShare。
  - 增加 TickFlow 历史行情 provider。
  - 增加 TickFlow 实时报价备用路径，仅在配置 API key 时启用。
  - API 返回主源、备用源、最后成功源、错误摘要和数据源能力说明。

- 回测能力：
  - 扩展回测请求契约，暴露成交量限制、最低佣金、过户费和策略级风险参数。
  - 将可安全映射的参数传递给 AKQuant runtime。
  - 收集 AKQuant 流式事件摘要。
  - 输出数据质量、执行质量、风险诊断和更多 AKQuant 指标。

- 前端联动：
  - 回测页面新增高级执行、成本、风险控件。
  - 回测结果展示数据源质量、执行质量、风险诊断和事件摘要。
  - 类型定义与 OpenAPI 契约保持同步。

## 非目标

- 不在本轮实现完整新闻搜索 provider 集群，如 Tavily、Brave、SerpAPI、SearXNG、Bocha 或 MiniMax。
- 不在本轮实现社交舆情 API，因为当前系统主要聚焦 A 股，外部参考库的社交舆情服务主要面向美股且需要单独 API key。
- 不新增没有后端接口和可验证数据源支撑的前端页面或标签。
- 不把 TickFlow 设为默认主源；默认仍保持 AkShare 优先，允许通过环境变量显式偏好 TickFlow。

## 成功标准

- `backend/pyproject.toml` 使用 `akshare==1.18.63`，新增 `tickflow==0.1.21`。
- 后端历史行情 fallback 顺序可配置，默认包含 `akshare -> tickflow -> tushare -> sina_direct`。
- TickFlow 缺包、未配置密钥、免费服务限制或网络错误都只导致明确降级，不导致应用启动失败。
- 回测请求支持新的执行、成本、风险字段，并在 OpenAPI、前端 payload、后端测试中可见。
- 回测结果包含 `dataQuality`、`executionQuality`、`riskDiagnostics`、`engineEvents`。
- 前端回测页面使用中文展示新增能力，不出现中英文混杂的新 UI 文案。
- 后端测试、前端测试、OpenAPI 生成和 OpenSpec 校验通过，或明确记录环境阻塞。

## 后续候选优化

- 独立 OpenSpec 变更：构建可配置新闻搜索 provider 集群，支持 Tavily、Brave、SerpAPI、SearXNG 等。
- 独立 OpenSpec 变更：为美股或港股研究接入社交舆情，并和预测 prompt、回测 handoff 打通。
- 独立 OpenSpec 变更：在行情中心增加 TickFlow 市场宽度、主要指数、涨跌停统计和流动性热力图。
