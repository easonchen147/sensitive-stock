## 1. 依赖与测试基线

- [x] 1.1 升级 backend 的 AkShare 依赖到最新版可安装版本，并整理 market/news 相关配置常量。
- [x] 1.2 为 AkShare 主链路、market API、Jin10 latest-100 与 intelligence 输出补充 backend 单元测试，先完成失败用例。

## 2. AkShare 主数据链路

- [x] 2.1 重构 `backtesting/data.py`，将历史行情优先级明确为 AkShare → Tushare → Sina Direct，并清理旧主优先级说明。
- [x] 2.2 在 backend 新增 AkShare 市场数据 service / schema，提供市场概览、实时行情和热点板块所需的统一返回结构。
- [x] 2.3 接入 `/api/v1/market` 与相关子路由，更新 capability inventory，使 `market` 从 placeholder 升级为 migrated。

## 3. 金十新闻情报链路

- [x] 3.1 新增 Jin10 latest-100 抓取服务，使用官方 flash API 分页拉取并在异常时降级到 `flash_newest.js`。
- [x] 3.2 实现关键词提取与板块提示骨架，输出可供后续“大盘 / 板块预测”复用的 intelligence 结构。
- [x] 3.3 暴露 backend 金十新闻与 intelligence API，并保证响应中包含 source、requestedLimit 与 degraded 元数据。

## 4. 文档与验证

- [x] 4.1 更新根 README、backend README 与相关迁移说明，明确 AkShare-first 策略、fallback 保留范围和 Jin10 news API。
- [x] 4.2 运行 backend 测试与必要语法检查，回填 OpenSpec 任务勾选状态，并按里程碑提交改动。
