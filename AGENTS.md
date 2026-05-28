# AGENTS.md

## 项目定位

面向 A 股的一站式研究终端：行情监控、智能选股、AI 诊股、量化回测、因子研究、组合优化、AI 问答、每日复盘。

- `frontend/` — Next.js 16 唯一前端入口
- `backend/` — Flask 唯一 Python 运行工作区
- repo 根目录只保留工作区级文件、文档和 OpenSpec

## 技术栈

| 层 | 技术 |
|---|---|
| 前端框架 | Next.js 16 (App Router) + React 19 + TypeScript 5.9 |
| 样式 | Tailwind CSS v4 + shadcn/ui (new-york) + Recharts |
| 后端框架 | Flask 3.1 + Pydantic v2 |
| 数据源 | akshare (主) / TickFlow / Tushare / Sina (自动故障转移) |
| 回测引擎 | AKQuant + 自研 legacy 引擎 |
| AI | DeepSeek (预测/诊断/问答/日报/策略生成) |
| 认证 | itsdangerous JWT, httpOnly cookie, Next.js SSR 保护 |
| 包管理 | uv + Poetry (后端), npm (前端) |

## 当前能力清单 (8 项)

| 能力 | 后端路由 | 前端页面 | 核心服务 |
|------|---------|---------|---------|
| 行情中心 | `GET /market/*` (14 路由) | `/market` | `market_data.py`, `news_intelligence.py`, `deepseek_prediction.py`, `stock_detail.py` |
| 股票回测 | `POST /backtests/run`, `GET /backtests/presets`, `POST /backtests/generate-strategy` | `/backtests` | `backtests_akquant.py`, `backtesting/presets.py` (8 策略) |
| 条件选股 | `POST /screener/run`, `POST /screener/export` | `/screener` | `screener.py` |
| 智能诊股 | `POST /diagnosis/run` | `/diagnosis` | `diagnosis.py` |
| 因子分析 | `POST /factors/analyze` | `/factors` | `factors.py`, `factor_analysis.py` (15 因子) |
| 组合优化 | `POST /portfolio/optimize` | `/portfolio` | `portfolio.py`, `portfolio_optimizer.py` (4 优化目标) |
| AI 问答 | `POST /qa/ask` | `/qa` | `stock_qa.py` |
| 每日复盘 | `POST /daily/run`, `GET /daily/latest`, `GET /daily/history` | `/daily` | `daily_analysis.py` |

## 目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                  # 12 个 Flask Blueprint, 30+ 路由
│   │   │   ├── __init__.py       # 注册所有 blueprint
│   │   │   ├── auth.py           # POST /auth/login, GET /auth/session
│   │   │   ├── backtests.py      # 回测 + 策略生成
│   │   │   ├── capabilities.py   # GET /capabilities
│   │   │   ├── daily.py          # 每日复盘
│   │   │   ├── diagnosis.py      # 智能诊股
│   │   │   ├── factors.py        # 因子分析
│   │   │   ├── health.py         # GET /health
│   │   │   ├── market.py         # 行情/板块/资讯/预测/个股详情/K线/财务/新闻 (最大)
│   │   │   ├── openapi.py        # GET /openapi.json
│   │   │   ├── portfolio.py      # 组合优化
│   │   │   ├── qa.py             # AI 问答
│   │   │   └── screener.py       # 条件选股
│   │   ├── schemas/              # 9 个 Pydantic 模型文件
│   │   │   ├── auth.py, backtests.py, daily.py, market.py
│   │   │   ├── research.py, stock_detail.py, stock_qa.py, strategy.py
│   │   │   └── __init__.py
│   │   ├── services/             # 17 个服务 (全部真实实现, 无 stub)
│   │   │   ├── auth.py           # HMAC 凭证 + JWT 签发/验证
│   │   │   ├── backtests_akquant.py  # AKQuant 引擎适配器 (1096 行, 最大服务)
│   │   │   ├── backtests.py      # 兼容 shim, 重导出 AKQuant
│   │   │   ├── capabilities.py   # 静态能力注册表 (8 项)
│   │   │   ├── daily_analysis.py # 多指标复合筛选 + DeepSeek 日报
│   │   │   ├── deepseek_prediction.py  # DeepSeek 预测 + 启发式回退
│   │   │   ├── diagnosis.py      # 技术指标计算 + AI 诊断 (601 行)
│   │   │   ├── factors.py        # 包装 factor_analysis.py
│   │   │   ├── market_data.py    # 多源行情 (akshare/TickFlow/东方财富/Sina)
│   │   │   ├── news_intelligence.py  # 7 个新闻源 + 情报分析 (1424 行, 最大)
│   │   │   ├── portfolio.py      # 包装 portfolio_optimizer.py
│   │   │   ├── prediction_history.py # JSONL 预测历史存储/评估
│   │   │   ├── runtime_cache.py  # 通用 TTL 缓存
│   │   │   ├── screener.py       # 结构化筛选 + NL 解释
│   │   │   ├── stock_detail.py   # 个股详情/K线/财务/新闻
│   │   │   ├── stock_qa.py       # DeepSeek 股票问答
│   │   │   └── strategy_generator.py # NL → akquant 策略代码
│   │   ├── auth.py               # before_request 认证守卫
│   │   ├── config.py             # ~35 个配置项, 从 .env 读取
│   │   ├── errors.py             # 统一错误处理
│   │   ├── openapi.py            # OpenAPI 3.1 文档动态生成
│   │   └── __init__.py           # Flask app factory
│   ├── backtesting/              # 回测基础设施
│   │   ├── data.py               # 4 个数据提供者 + SmartDataProvider 故障转移链
│   │   ├── engine.py             # 纯 Python 回测引擎 (legacy)
│   │   ├── indicators.py         # 8 个技术指标 (SMA/EMA/RSI/MACD/Bollinger/KDJ/cross)
│   │   ├── presets.py            # 8 个策略预设 (532 行)
│   │   ├── strategy.py           # 沙箱策略执行器
│   │   └── pipeline.py           # Legacy 回测流水线
│   ├── factor_analysis.py        # FactorAnalyzer (15 因子, IC 分析)
│   ├── portfolio_optimizer.py    # PortfolioOptimizer (4 优化方法)
│   ├── tests/                    # 19 个测试文件
│   ├── scripts/generate_openapi.py
│   ├── wsgi.py
│   └── pyproject.toml / poetry.lock / uv.lock
├── frontend/
│   ├── app/
│   │   ├── login/page.tsx        # 登录页
│   │   ├── page.tsx              # 首页仪表盘
│   │   ├── market/page.tsx       # 行情中心
│   │   ├── backtests/page.tsx    # 回测验证
│   │   ├── screener/page.tsx     # 选股研究
│   │   ├── diagnosis/page.tsx    # 诊股报告
│   │   ├── factors/page.tsx      # 因子研究
│   │   ├── portfolio/page.tsx    # 组合研究
│   │   ├── qa/page.tsx           # AI 问答
│   │   ├── daily/page.tsx        # 每日复盘
│   │   └── api/                  # Next.js API 路由 (auth + catch-all proxy)
│   ├── components/
│   │   ├── app-shell.tsx         # 主布局 (侧边栏 9 个导航项)
│   │   ├── market-workbench.tsx  # 行情中心 (最大, ~930 行)
│   │   ├── backtest-console.tsx  # 回测控制台 (~925 行)
│   │   ├── research-workbenches.tsx  # 选股/诊股/因子/组合 (4 个 workbench)
│   │   ├── daily-report.tsx      # 每日复盘报告
│   │   ├── stock-qa.tsx          # AI 聊天界面
│   │   ├── dashboard-widgets.tsx # 首页组件
│   │   ├── stock-detail-panel.tsx # 个股详情面板
│   │   ├── kline-chart.tsx       # K 线图 (Recharts)
│   │   ├── nl-strategy-editor.tsx # NL 策略生成器
│   │   ├── workbench-layout.tsx  # 共享布局原语
│   │   ├── login-screen.tsx      # 登录表单
│   │   ├── auth-status.tsx       # 认证状态
│   │   └── ui/                   # 27 个 shadcn/ui 原语
│   ├── lib/
│   │   ├── api.ts                # 30 个类型化 API 函数
│   │   ├── openapi-client.ts     # 35 条路由绑定 + 通用 fetch 客户端
│   │   ├── server-auth.ts        # SSR 认证 (requireAuthenticatedPage)
│   │   ├── server-api.ts         # SSR API 调用
│   │   ├── auth.ts               # cookie/路径工具
│   │   ├── api-base.ts           # 后端 URL 解析
│   │   ├── display.ts            # 18 个中文显示格式化函数
│   │   ├── backtests.ts          # 回测表单 helper
│   │   └── utils.ts              # cn() Tailwind 合并
│   └── types/
│       └── api.ts                # 840 行完整 TypeScript 类型定义
├── docs/
├── openspec/
├── README.md
└── LICENSE
```

## 开发约定

### 1. 根目录不再承载运行时代码

不要新增 `app.py`、`pages/`、根目录 Python 服务模块或旧式 `config.json`。新代码分别进入 `backend/` 和 `frontend/`。

### 2. 后端工作区独立运行

- `backend/` 下可直接运行测试，不依赖 repo 根目录 `sys.path`
- 依赖由 `uv + Poetry` 共管
- 新增模块不应导致需要把 repo 根目录塞进 `sys.path`

### 3. Legacy 模块留在 backend 内

仍保留的过渡代码：`backend/backtesting/`、`backend/factor_analysis.py`、`backend/portfolio_optimizer.py`。新的 legacy 不应放回根目录。

### 4. 前端通过受保护链路访问后端

- SSR 页面保护：`frontend/lib/server-auth.ts` (无 middleware.ts)
- 后端代理：`frontend/app/api/backend/[...slug]/route.ts` (校验路由注册后转发)
- 后端认证：`backend/app/auth.py` + `backend/app/services/auth.py`
- 除 health/login/openapi 外，所有 API 要求 bearer token

### 5. 包管理

后端依赖调整后刷新：
```bash
cd backend && poetry lock && uv lock
```

### 6. 文档对齐

修改目录结构、启动方式、API 路径、认证边界时，同步更新：
- `README.md`
- `backend/README.md`

### 7. OpenSpec 以实际状态为准

处理需求前确认 `openspec status`，不虚报完成状态。

### 8. Capabilities 注册

新增后端能力时，同步更新：
- `backend/app/services/capabilities.py` — 添加能力条目
- `backend/app/api/__init__.py` — 注册新 blueprint
- `frontend/lib/openapi-client.ts` — 添加路由绑定
- `frontend/lib/api.ts` — 添加类型化 API 函数
- `frontend/types/api.ts` — 添加类型定义
- `frontend/components/app-shell.tsx` — 添加导航项（如有新页面）
