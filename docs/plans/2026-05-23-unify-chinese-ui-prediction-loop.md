---
status: active
created: 2026-05-23
origin: user request
workflow: openspec + compound-engineering
change: unify-chinese-ui-prediction-loop
---

# 统一中文投研终端与预测闭环计划

## 问题框架

当前系统已经完成了后端 OpenAPI、AKQuant 回测、多源资讯和 DeepSeek 预测的主链路，但产品体验仍然像几个阶段性成果拼在一起：前端页面存在英文标签、中文乱码和中英混用；预测结果只展示当次输出，缺少可回看、可解释、可评估的闭环；DeepSeek V4 Flash 虽然已接入，但思考/非思考模式没有显式配置和返回说明。

本计划把系统收敛为一个中文 A 股研究终端：所有正式页面统一中文语言、统一视觉系统、统一 OpenAPI 契约，并补齐预测评估、来源质量评分、预测历史、DeepSeek 模式配置和预测详情页。

## 范围

本次覆盖登录页、研究总览、行情预测、回测控制台、选股、诊股、因子研究、组合研究等正式页面；覆盖市场资讯预测后端、OpenAPI、前端类型与页面绑定；覆盖本地预测历史和基础评估闭环。

本次不做真实交易、自动下单、用户多账户体系、生产级数据库迁移、实时推送告警或商业权限后台。预测结果继续定位为研究辅助信息，不作为投资建议。

## 需求追踪

- 全中文界面：正式页面、状态、按钮、表格、指标、空态、错误态均使用中文，不保留英文 UI 标签。
- 统一视觉：以 `docs/design/2026-05-22-chinese-research-terminal-reference.png`、`docs/design/2026-05-23-chinese-research-terminal-page-board.png` 和 HTML 原型为视觉基准，形成“中文投研终端”的一致页面密度、色彩、组件和状态语言。
- 接口对齐：所有页面继续通过 OpenAPI 绑定访问后端，新增预测历史、详情和评估接口也进入全局 `openapi.json`。
- 预测评估闭环：预测响应记录本地历史，暴露详情和历史列表，并提供基于最新行情的方向命中评估摘要。
- 来源质量评分：多源资讯除成功/失败计数外，提供可解释的质量评分、覆盖度和降级原因。
- DeepSeek V4 Flash：默认使用 `deepseek-v4-flash`，并显式支持思考/非思考模式与 reasoning effort 配置。
- 预测详情页：前端提供每条预测的证据、驱动因子、风险、来源质量、评估状态和回测交接信息。

## 关键决策

1. 继续使用现有 `/api/v1/market/news/predictions` 作为预测主入口，同时新增历史与详情接口。
   这样前端行情页的刷新链路不变，历史和详情作为研究复盘能力独立扩展，避免把列表接口变成过大的万能接口。

2. 预测历史使用本地 JSONL 文件持久化。
   这满足当前“本地持久化”和研究复盘目标，不引入数据库迁移。后续如果需要多用户、多实例或长期归档，再单独做数据库化 change。

3. 评估先做“行情可得时的方向评估”，不承诺完整收益归因。
   当前预测对象可能是板块、主题或个股。只有明确个股符号且能取到当前行情时，才生成命中/未命中/待观察状态；其他预测保留待评估，避免伪造精度。

4. DeepSeek 模式作为请求体外的后端配置和查询覆盖项处理。
   默认配置来自环境变量；接口允许查询参数临时覆盖 `thinking` 与 `reasoningEffort`，返回元数据必须说明实际使用的模式。

5. 前端不新增重量级组件库。
   现有页面已经有稳定 CSS 组件语法，新增依赖会增加构建风险。采用原生 React + CSS tokens 实现统一风格；如后续需要复杂表格/图表，再单独评估。

## 实现单元

### U1: OpenSpec 与设计源文件

文件：
- `docs/plans/2026-05-23-unify-chinese-ui-prediction-loop.md`
- `docs/design/2026-05-22-chinese-research-terminal-reference.png`
- `docs/design/2026-05-23-chinese-research-terminal-page-board.png`
- `docs/design/2026-05-23-chinese-research-terminal-prototype.html`
- `openspec/changes/unify-chinese-ui-prediction-loop/proposal.md`
- `openspec/changes/unify-chinese-ui-prediction-loop/design.md`
- `openspec/changes/unify-chinese-ui-prediction-loop/specs/**/spec.md`
- `openspec/changes/unify-chinese-ui-prediction-loop/tasks.md`

做法：
- 先把中文化、设计系统、预测闭环、OpenAPI 和前后端绑定写成正式规格。
- HTML 原型作为实现参考，不替代 OpenSpec 的行为契约。

测试场景：
- OpenSpec strict 校验通过。
- 计划、设计和 spec delta 覆盖用户列出的全部优化点。

验证：
- `openspec validate unify-chinese-ui-prediction-loop --strict`

### U2: DeepSeek V4 Flash 模式配置与预测元数据

文件：
- `backend/app/config.py`
- `backend/.env.example`
- `backend/app/services/deepseek_prediction.py`
- `backend/tests/test_deepseek_prediction_service.py`

做法：
- 保留 `deepseek-v4-flash` 默认模型。
- 增加 `BACKEND_DEEPSEEK_THINKING_TYPE` 和 `BACKEND_DEEPSEEK_REASONING_EFFORT`。
- 请求 DeepSeek 时发送 `thinking: {"type": "enabled"|"disabled"}`，需要时发送 `reasoning_effort`。
- `predictionMetadata` 返回 `thinkingType`、`reasoningEffort`、`requestMode`。

测试场景：
- 默认请求使用 `deepseek-v4-flash` 和配置的 thinking 参数。
- 非思考模式配置会发送 `thinking.type=disabled`。
- 缓存 key 包含模型、schema 和 thinking 配置，避免模式切换后复用旧输出。
- 本地启发式降级也返回同样的模式元数据。

验证：
- `cd backend; uv run pytest tests/test_deepseek_prediction_service.py -q`

### U3: 来源质量评分、预测历史和评估服务

文件：
- `backend/app/services/news_intelligence.py`
- `backend/app/services/prediction_history.py`
- `backend/app/api/market.py`
- `backend/app/schemas/market.py`
- `backend/tests/test_multisource_news_service.py`
- `backend/tests/test_market_predictions_api.py`
- `backend/tests/test_prediction_history_service.py`

做法：
- 在多源资讯 metadata 中增加 `qualityScore`、`freshnessScore`、`coverageScore`、`reliabilityScore` 和解释性 `qualityNotes`。
- 预测响应写入本地历史记录，生成稳定 `runId` 和预测 `predictionId`。
- 新增历史列表、详情和评估接口：列表用于复盘，详情用于单条解释，评估用于行情可得时判断方向表现。

测试场景：
- 多源资讯成功、部分失败、重复新闻都会产出可解释质量评分。
- 预测成功后写入历史，历史列表可按 limit 返回。
- 详情接口能根据 runId/predictionId 返回预测、证据和 metadata。
- 评估接口在有报价时给出命中/未命中/中性/待评估状态；无报价时不失败。

验证：
- `cd backend; uv run pytest tests/test_multisource_news_service.py tests/test_market_predictions_api.py tests/test_prediction_history_service.py -q`

### U4: OpenAPI 与前端类型绑定

文件：
- `backend/app/openapi.py`
- `backend/scripts/generate_openapi.py`
- `backend/tests/test_openapi_publication.py`
- `openapi.json`
- `frontend/types/api.ts`
- `frontend/lib/openapi-client.ts`
- `frontend/lib/api.ts`

做法：
- 将新增预测历史、详情、评估、质量评分、DeepSeek 模式字段加入 OpenAPI。
- 更新前端类型和 binding 表，保持 protected/public 安全声明对齐。
- 重新生成根目录 `openapi.json`。

测试场景：
- OpenAPI 包含新增 market prediction history/detail/evaluation 操作。
- 前端 binding 表中的路径、方法和安全声明与 OpenAPI 匹配。
- 类型覆盖新增字段，页面不依赖隐式 `any`。

验证：
- `cd backend; uv run pytest tests/test_openapi_publication.py -q`
- `cd backend; uv run python scripts/generate_openapi.py --output ..\openapi.json`
- `cd frontend; npm test`

### U5: 全中文页面与统一视觉实现

文件：
- `frontend/app/page.tsx`
- `frontend/components/app-shell.tsx`
- `frontend/components/auth-status.tsx`
- `frontend/components/login-screen.tsx`
- `frontend/components/workbench-layout.tsx`
- `frontend/components/market-workbench.tsx`
- `frontend/components/backtest-console.tsx`
- `frontend/components/research-workbenches.tsx`
- `frontend/app/globals.css`
- `frontend/tests/smoke/workbench-smoke.spec.ts`

做法：
- 替换所有用户可见英文文案、英文状态和乱码。
- 统一页面骨架：左侧导航、顶部状态、右侧任务/历史、主体数据区和详情区。
- 让所有页面的控件、指标卡、表格、空态、降级态和错误态使用同一套中文组件语法。
- 行情页增加预测历史、详情和评估区域。

测试场景：
- 登录、总览、回测、行情、选股、诊股、因子、组合页面均能渲染中文主标题。
- 页面不出现已知英文 UI 标签和 mojibake。
- 行情页能展示预测详情、来源质量、历史记录和评估状态。
- 移动视口下导航、按钮和长中文文本不重叠。

验证：
- `cd frontend; npm run build`
- `cd frontend; npm run test:smoke`
- Playwright 截图检查桌面和移动页面。

### U6: 终验、归档和知识沉淀

文件：
- `openspec/specs/**/spec.md`
- `openspec/changes/archive/**`
- `docs/solutions/**`

做法：
- 跑后端、前端、OpenSpec、diff 校验。
- 完成后归档 OpenSpec change。
- 写一篇 Compound solution，沉淀中文投研终端、OpenAPI 绑定和预测闭环的实现模式。

验证：
- `cd backend; uv run pytest -q`
- `cd backend; uv run ruff check app tests scripts`
- `cd frontend; npm test`
- `cd frontend; npm run build`
- `openspec validate --all --strict`
- `git diff --check`

## 风险与处理

- DeepSeek API 仍可能变化。已用官方文档确认 V4 Flash、thinking 配置和 JSON output 能力；实现保留环境变量覆盖。
- 本地 JSONL 历史不适合多实例生产。当前只作为本地研究复盘能力，后续数据库化需单独设计迁移。
- 全中文检查不能简单禁止所有 ASCII，因为股票代码、日期、接口路径、模型名和指标缩写有业务价值。验证脚本应关注用户可见标签和已知英文 UI 文案，而不是机械删除所有英文字母。
- 设计还原度的“99%”不能用像素级 Figma diff 衡量，因为参考图是生成稿。验收以同一页面结构、色彩、密度、状态语言和中文信息层级为准。

## 验证策略

先完成 OpenSpec strict，再实现后端预测闭环和 OpenAPI，随后接入前端页面并统一中文视觉。验证顺序为后端单测、OpenAPI 生成、前端测试/build、浏览器 smoke 和截图检查，最后做 OpenSpec verify、archive 和 Compound 文档沉淀。
