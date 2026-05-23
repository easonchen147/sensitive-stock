## Why

当前前端仍存在英文标签、中文乱码和中英混用，页面虽然已经接入后端 API，但整体体验不像一个统一的中文投研系统。同时，市场资讯预测缺少历史、详情和评估闭环，DeepSeek V4 Flash 的思考模式也没有作为显式契约暴露。

本 change 将系统收敛为“中文 A 股研究终端”：统一页面语言与风格，补齐预测复盘闭环，并把新增能力纳入 OpenAPI 与前端绑定。

## What Changes

- 全部正式页面改为中文 UI：登录、总览、行情、回测、选股、诊股、因子、组合页面不得出现用户可见英文标签或乱码。
- 按设计参考图和 HTML 原型统一页面风格：左侧导航、顶部状态、主体数据区、右侧任务/历史、统一卡片/表格/状态面。
- 行情预测页新增预测详情、历史记录、来源质量、模型模式和评估结果展示。
- 后端新增本地预测历史、预测详情和预测评估 API。
- 多源资讯 metadata 增加来源质量评分和解释性质量说明。
- DeepSeek 默认继续使用 `deepseek-v4-flash`，新增 thinking type 与 reasoning effort 配置，并在预测元数据中返回实际模式。
- 更新全局 `openapi.json`、前端类型和 OpenAPI route binding。
- 增加后端、前端和 smoke 测试，覆盖中文页面、接口绑定和预测闭环。

## Capabilities

### New Capabilities
- `prediction-history-and-evaluation`: 定义预测历史、本地持久化、预测详情和基于行情的评估闭环。

### Modified Capabilities
- `frontend-research-design-system`: 增加全中文 UI、统一中文投研终端视觉基准和页面一致性要求。
- `nextjs-frontend-shell`: 要求所有正式页面中文化，并在行情页提供预测详情、历史和评估区域。
- `openapi-driven-frontend-client`: 新增预测历史、详情、评估接口的前端绑定与类型契约。
- `jin10-news-intelligence-pipeline`: 增加来源质量评分、DeepSeek thinking 配置和预测历史写入要求。
- `backend-openapi-publication`: 发布新增预测闭环接口和响应 schema。

## Impact

- 后端：`backend/app/services/deepseek_prediction.py`、`backend/app/services/news_intelligence.py`、新增预测历史服务、market API、market schema、OpenAPI 生成。
- 前端：所有正式页面组件、共享布局、CSS tokens、OpenAPI client/types、smoke 测试。
- 文档：新增计划、HTML 设计原型、OpenSpec delta、最终 solution 文档。
- 数据：新增本地 JSONL 预测历史文件，默认作为开发/单机研究持久化，不引入数据库迁移。
