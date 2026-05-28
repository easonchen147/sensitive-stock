# Sensitive Stock

一站式 A 股研究终端 — 行情监控、AI 诊股、量化回测、因子研究、组合优化，全部集成在一个工作台中。

[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19-blue)](https://react.dev)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com)
[![Python](https://img.shields.io/badge/Python-3.12-yellow)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 项目定位

Sensitive Stock 是一个面向 A 股投资者的研究终端，目标是**用一个工具替代多个分散的数据源和分析软件**。它整合了实时行情、新闻情报、AI 分析、量化回测和投资组合优化，通过统一的界面提供连贯的研究体验。

核心理念：**数据 → 洞察 → 验证 → 决策**，从信息获取到策略验证形成闭环。

---

## 功能模块

### 行情中心 `/market`

实时行情、板块热度、多源新闻聚合、AI 预测。

- **实时报价**：A 股全市场行情，支持点击展开个股详情面板
- **板块分析**：热门板块轮动，领涨股追踪
- **新闻聚合**：聚合 7 大财经信息源（金十、东方财富、新浪财经、财联社、证券时报、21 世纪经济报道、巨潮资讯）
- **AI 预测**：基于新闻情绪和事件驱动的市场方向预测，支持置信度评估和历史回测验证
- **个股详情**：基本面数据（PE/PB/市值/换手率）、K 线图（蜡烛图 + MA 均线叠加）

### 智能诊股 `/diagnosis`

输入股票代码，获取 AI 驱动的全面诊断报告。

- **技术评分**：MA5/10/20/60、RSI14、MACD、布林带、量比等指标打分
- **结构化报告**：市场背景、技术分析、基本面摘要、AI 洞察、风险提示
- **诊股→问答**：诊断完成后可一键跳转 AI 问答深入追问

### 量化回测 `/backtests`

完整的策略回测引擎，支持 8 种预设策略和自然语言策略生成。

- **8 种预设策略**：双均线交叉、RSI 均值回归、通道突破、事件驱动、MACD 趋势、布林带回归、KDJ 信号、量价背离
- **自定义策略**：Python 代码编辑器，支持完整的策略逻辑编写
- **自然语言生成**：用中文描述策略思路，AI 自动生成可执行的策略代码
- **精细参数**：滑点、佣金、印花税、过户费、止损止盈、最大回撤限制
- **策略对比**：多策略并排回测，指标对比表 + 权益曲线叠加图

### 选股研究 `/screener`

多因子条件筛选，支持结构化条件和自然语言描述。

- **筛选条件**：价格区间、涨跌幅、行业、PE、市值、量比、换手率
- **自然语言**：用中文描述选股逻辑，自动解释为筛选条件
- **结果联动**：筛选结果可直接跳转诊股或运行回测

### 因子研究 `/factors`

15 个因子的快照分析和 IC 排名。

- **因子库**：动量（5/10/20 日）、反转（5/10 日）、波动率（10/20 日）、量比、价格位置、均线交叉、振幅、资金流向
- **IC 分析**：Spearman 秩相关系数排名，滚动窗口统计

### 组合优化 `/portfolio`

4 种优化目标的投资组合权重分配。

- **优化方法**：等权重、最小方差、最大夏普比率、风险平价
- **统计指标**：总收益、年化收益、波动率、夏普比率、最大回撤
- **风险提示**：集中度风险、行业暴露、优化假设说明

### AI 问答 `/qa`

对话式股票分析，支持多轮追问。

- **数据增强**：自动获取股票基本面和 K 线数据作为分析上下文
- **多维分析**：基本面分析、技术面分析、股票对比、板块分析
- **来源标注**：回答附带数据来源标签

### 每日复盘 `/daily`

AI 驱动的每日市场分析报告。

- **市场总结**：当日大盘走势、热点板块、关键事件回顾
- **精选推荐**：多指标复合筛选 + AI 评分，含买入理由
- **板块分析**：板块趋势判断和配置建议
- **历史回溯**：过往日报存档和对比

### 股票对比 `/compare`

2-5 只股票的横向对比分析。

- **基本面对比**：价格、PE、PB、市值、换手率、涨跌幅
- **技术面对比**：MA5/10/20/60、RSI14、MACD（DIF/DEA/柱状图）
- **智能高亮**：最优/最差指标自动标色

### 自选股 `/watchlist`

个人关注列表和持仓追踪。

- **管理自选**：添加、编辑、删除关注的股票
- **成本追踪**：记录买入成本价和持股数量
- **盈亏计算**：实时价格刷新，自动计算浮动盈亏和收益率
- **持仓概览**：总成本、总市值、总盈亏一目了然

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 前端框架 | Next.js 16 (App Router) | SSR、路由、API 代理 |
| UI 库 | React 19 + shadcn/ui + Recharts | 组件库和图表 |
| 样式 | Tailwind CSS v4 | 原子化 CSS |
| 后端框架 | Flask 3.1 + Pydantic v2 | API 服务 + 数据校验 |
| 数据源 | AKShare（主）/ TickFlow / Tushare / Sina | A 股行情数据（自动故障转移） |
| 回测引擎 | AKQuant + 自研引擎 | 策略回测 |
| AI | DeepSeek `deepseek-v4-flash` | 预测、诊断、问答、日报、策略生成 |
| 新闻源 | 金十/东方财富/新浪/财联社/证券时报/21 世纪/巨潮 | 7 路财经资讯聚合 |
| 包管理 | uv + Poetry（后端）/ npm（前端） | 依赖管理 |

---

## 快速开始

### 环境要求

- Python 3.12
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) + [Poetry](https://python-poetry.org)

### 后端启动

```bash
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv/bin/python   # Windows: .venv\Scripts\python.exe
poetry sync --with dev

cp .env.example .env              # 配置 API 密钥和认证凭据
poetry run flask --app wsgi:application run --debug --port 5000
```

健康检查：`curl http://127.0.0.1:5000/api/v1/health`

### 前端启动

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

打开 http://localhost:3000，注册账号或使用默认凭据登录。

---

## 架构

```
sensitive-stock/
├── backend/
│   ├── app/
│   │   ├── api/              # 12 个 Flask Blueprint，30+ 路由
│   │   │   ├── auth.py       # 登录 / 注册 / 会话管理
│   │   │   ├── market.py     # 行情 / 板块 / 新闻 / 预测 / 个股 / K线
│   │   │   ├── backtests.py  # 回测运行 / 策略预设 / 策略生成
│   │   │   ├── screener.py   # 条件选股
│   │   │   ├── diagnosis.py  # 智能诊股
│   │   │   ├── factors.py    # 因子分析
│   │   │   ├── portfolio.py  # 组合优化
│   │   │   ├── qa.py         # AI 问答
│   │   │   ├── daily.py      # 每日复盘
│   │   │   └── watchlist.py  # 自选股管理
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   ├── services/         # 业务逻辑（17 个服务）
│   │   └── auth.py           # 认证守卫
│   ├── backtesting/          # 8 策略预设 / 技术指标 / 策略执行
│   │   ├── presets.py        # 8 种预设策略
│   │   ├── indicators.py     # SMA/EMA/RSI/MACD/Bollinger/KDJ
│   │   └── engine.py         # 回测引擎
│   ├── factor_analysis.py    # 15 因子 + IC 分析
│   ├── portfolio_optimizer.py # 4 种优化方法
│   └── wsgi.py
├── frontend/
│   ├── app/                  # 10 个页面 + API 代理
│   │   ├── page.tsx          # 首页仪表盘
│   │   ├── market/           # 行情中心
│   │   ├── backtests/        # 回测验证（含策略对比）
│   │   ├── diagnosis/        # 诊股报告
│   │   ├── screener/         # 选股研究
│   │   ├── factors/          # 因子研究
│   │   ├── portfolio/        # 组合研究
│   │   ├── qa/               # AI 问答
│   │   ├── daily/            # 每日复盘
│   │   ├── compare/          # 股票对比
│   │   └── watchlist/        # 自选股
│   ├── components/           # UI 组件
│   ├── lib/                  # API 客户端 / 认证 / OpenAPI 绑定
│   └── types/                # TypeScript 类型定义（840+ 行）
└── README.md
```

### 数据流

```
浏览器 → Next.js (SSR) → /api/backend/[...slug] → Flask → AKShare / DeepSeek
                                     ↓
                              Bearer Token 认证
```

所有业务端点需要 `Authorization: Bearer <token>`。前端代理自动附加会话 Token。

---

## API 端点

<details>
<summary><b>认证 (3)</b></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/register` | 用户注册 |
| GET | `/api/v1/auth/session` | 会话验证 |
</details>

<details>
<summary><b>行情 (14)</b></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/market` | 行情总览 |
| GET | `/api/v1/market/quotes` | 实时报价 |
| GET | `/api/v1/market/sectors` | 板块数据 |
| GET | `/api/v1/market/stock/{symbol}/detail` | 个股详情 |
| GET | `/api/v1/market/stock/{symbol}/kline` | K 线数据 |
| GET | `/api/v1/market/stock/{symbol}/financials` | 财务摘要 |
| GET | `/api/v1/market/stock/{symbol}/news` | 个股新闻 |
| GET | `/api/v1/market/compare` | 股票对比 |
| GET | `/api/v1/market/news` | 新闻聚合 |
| GET | `/api/v1/market/news/intelligence` | 新闻情报 |
| GET | `/api/v1/market/news/categories` | 新闻分类 |
| GET | `/api/v1/market/news/predictions` | AI 预测 |
| GET | `/api/v1/market/news/prediction-history` | 预测历史 |
| GET | `/api/v1/market/news/predictions/{runId}/evaluate` | 预测评估 |
</details>

<details>
<summary><b>回测 (3)</b></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/backtests/presets` | 策略预设列表 |
| POST | `/api/v1/backtests/run` | 运行回测 |
| POST | `/api/v1/backtests/generate-strategy` | 自然语言策略生成 |
</details>

<details>
<summary><b>研究 (5)</b></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/screener/run` | 条件选股 |
| POST | `/api/v1/diagnosis/run` | 智能诊股 |
| POST | `/api/v1/factors/analyze` | 因子分析 |
| POST | `/api/v1/portfolio/optimize` | 组合优化 |
| POST | `/api/v1/qa/ask` | AI 问答 |
</details>

<details>
<summary><b>日报 (3)</b></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/daily/run` | 生成日报 |
| GET | `/api/v1/daily/latest` | 最新报告 |
| GET | `/api/v1/daily/history` | 历史报告 |
</details>

<details>
<summary><b>自选股 (4)</b></summary>

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/watchlist` | 获取自选列表 |
| POST | `/api/v1/watchlist` | 添加自选股 |
| PUT | `/api/v1/watchlist/{symbol}` | 更新自选股 |
| DELETE | `/api/v1/watchlist/{symbol}` | 删除自选股 |
</details>

运行时 OpenAPI 合约：`GET /api/v1/openapi.json`

---

## 配置

后端 `.env` 关键配置：

| 变量 | 说明 |
|------|------|
| `BACKEND_DEEPSEEK_API_KEY` | DeepSeek API 密钥（AI 功能必需） |
| `BACKEND_AUTH_ADMIN_USERNAME` | 管理员用户名 |
| `BACKEND_AUTH_ADMIN_PASSWORD` | 管理员密码 |
| `BACKEND_MARKET_DATA_PREFER_TICKFLOW` | 优先使用 TickFlow 数据源 |
| `TICKFLOW_API_KEY` | TickFlow API 密钥（可选） |

完整配置见 `backend/.env.example`。

---

## 开发

```bash
# 后端测试 + 代码检查
cd backend && poetry run pytest tests -q && poetry run ruff check .

# 前端类型检查 + 构建
cd frontend && npx tsc --noEmit && npm run build

# 重新生成 OpenAPI 合约
cd backend && uv run python scripts/generate_openapi.py
```

---

## License

[MIT](LICENSE)
