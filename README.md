# Sensitive Stock

Sensitive Stock 是一个面向 A 股研究、资讯预测、策略回测和组合分析的前后端分离项目。当前主运行形态已经收敛为：

- `frontend/`：Next.js 16 + React 19 前端研究工作台。
- `backend/`：Flask API、认证、市场数据、资讯预测、AKQuant 回测和研究分析服务。
- `openapi.json`：后端导出的全局 OpenAPI 3.1 静态契约。
- `openspec/`：高风险变更的规格与归档记录。

根目录不再承载运行时代码。旧的 Streamlit 入口、根目录 Python 服务模块、旧式 `pages/` 运行路径和根目录 `config.json` 配置链都不是当前默认架构的一部分。

## 当前完善度

| 功能域 | 完善度 | 当前已有能力 | 主要边界 |
| --- | --- | --- | --- |
| 项目架构 | 已完成 | 前端、后端、文档、OpenSpec 已分层；后端代码收敛到 `backend/`；前端入口收敛到 `frontend/`。 | 根目录只放工作区文件、文档和规格，不再新增运行时代码。 |
| 认证与访问保护 | 已可用 | 管理员登录、Bearer Token、后端鉴权、前端受保护页面、前端后端代理链路。 | 开发默认账号密码应只用于本地，部署前必须通过环境变量覆盖。 |
| OpenAPI 契约 | 已可用 | 运行时 `GET /api/v1/openapi.json`，静态 `openapi.json`，生成脚本，前端接口绑定测试。 | 修改后端正式接口后需要重新生成并验证 `openapi.json`。 |
| 前端工作台 | 已可用 | 登录页、研究总览、回测验证、行情预测、选股研究、诊股报告、因子研究、组合研究。 | 页面只展示已有后端接口支撑的能力，不保留无接口支撑的占位入口。 |
| 行情数据 | 已可用，依赖外部数据源 | AkShare 优先，东方财富直连备用，行情总览、股票报价、概念和行业板块。 | 外部数据源失败时会进入降级或缓存路径。 |
| 多源资讯 | 已可用，依赖外部渠道 | 金十快讯、东方财富资讯、新浪财经直播聚合，去重、质量评分、渠道状态和关键词提取。 | 第三方接口不可用时会展示降级元数据。 |
| 资讯预测 | 已可用，远程模型可选 | DeepSeek `deepseek-v4-flash`、思考模式、推理强度、预测历史、预测详情、行情评估。 | 未配置 `BACKEND_DEEPSEEK_API_KEY` 时会明确降级到本地启发式预测。 |
| 回测验证 | 已可用 | AKQuant 回测执行链路、策略预设、自定义策略代码、成交模式、交易成本、止损止盈、基准对比、结构化报告。 | 历史行情仍依赖外部数据源；当前适配层负责信号回放和结果整理。 |
| 条件选股 | 已可用，第一版规则化能力 | 模板、结构化筛选条件、自然语言提示解释、候选排序、导出数据、回测交接载荷。 | 自然语言理解是轻量规则解释，不是完整大模型选股代理。 |
| 智能诊股 | 已可用，第一版规则化能力 | 股票报价上下文、日内动量、风险等级、诊断段落、风险提示。 | 当前以行情和规则摘要为主，不构成投资建议。 |
| 因子分析 | 已可用 | 因子计算、最新因子快照、IC 排名、窗口统计。 | 结果质量取决于可获取的历史行情和因子计算窗口。 |
| 组合优化 | 已可用 | 等权、最小方差、最大夏普、风险平价、目标权重、统计指标。 | 组合统计依赖历史行情，数据不足时会返回降级提示。 |
| 测试与规格 | 已建立 | 后端 pytest、ruff；前端 Vitest、构建、冒烟测试；OpenSpec 校验命令。 | 当前仓库没有活动中的 OpenSpec change。 |

## 已有页面

| 路径 | 页面 | 说明 |
| --- | --- | --- |
| `/login` | 登录 | 管理员登录入口，写入前端登录态。 |
| `/` | 研究总览 | 展示能力清单、真实接口入口和研究工作台概览。 |
| `/backtests` | 回测验证 | 运行策略预设或自定义策略，查看 AKQuant 回测报告。 |
| `/market` | 行情预测 | 查看行情、板块、资讯、DeepSeek 预测、历史和评估。 |
| `/screener` | 选股研究 | 执行条件筛选、查看候选、导出结果并交接回测。 |
| `/diagnosis` | 诊股报告 | 生成结构化诊断段落和风险提示。 |
| `/factors` | 因子研究 | 分析因子快照和 IC 排名。 |
| `/portfolio` | 组合研究 | 执行组合优化并查看权重和统计指标。 |

## 后端接口

当前正式后端接口以 `openapi.json` 为准，共覆盖以下路径：

- 公开接口：`GET /api/v1/health`、`GET /api/v1/openapi.json`、`POST /api/v1/auth/login`。
- 登录态：`GET /api/v1/auth/session`。
- 能力清单：`GET /api/v1/capabilities`。
- 回测：`GET /api/v1/backtests/presets`、`POST /api/v1/backtests/run`。
- 行情：`GET /api/v1/market`、`GET /api/v1/market/quotes`、`GET /api/v1/market/sectors`。
- 资讯：`GET /api/v1/market/news`、`GET /api/v1/market/news/intelligence`。
- 预测：`GET /api/v1/market/news/predictions`、`GET /api/v1/market/news/prediction-history`、`GET /api/v1/market/news/predictions/{runId}`、`GET /api/v1/market/news/predictions/{runId}/evaluate`。
- 选股：`GET /api/v1/screener`、`POST /api/v1/screener/run`、`POST /api/v1/screener/export`。
- 诊股：`GET /api/v1/diagnosis`、`POST /api/v1/diagnosis/run`。
- 因子：`GET /api/v1/factors`、`POST /api/v1/factors/analyze`。
- 组合：`GET /api/v1/portfolio`、`POST /api/v1/portfolio/optimize`。

除健康检查、OpenAPI 文档和登录接口外，正式业务接口默认要求：

```http
Authorization: Bearer <token>
```

前端通过 `frontend/app/api/backend/[...slug]/route.ts` 代理后端请求，并由 `frontend/lib/openapi-client.ts` 维护页面到 OpenAPI 路径的绑定关系。

## 仓库结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/          # Flask HTTP 路由
│   │   ├── schemas/      # Pydantic 请求和响应模型
│   │   └── services/     # 认证、行情、资讯、预测、回测和研究服务
│   ├── backtesting/      # 当前仍复用的回测策略和数据适配代码
│   ├── scripts/          # OpenAPI 生成脚本
│   ├── tests/            # 后端测试
│   ├── factor_analysis.py
│   ├── portfolio_optimizer.py
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── uv.lock
│   └── wsgi.py
├── frontend/
│   ├── app/              # Next.js App Router 页面和代理接口
│   ├── components/       # 页面组件和工作台组件
│   ├── lib/              # 鉴权、OpenAPI 客户端、业务请求封装
│   ├── tests/            # 前端冒烟测试
│   └── types/            # 前端接口类型
├── docs/
├── openspec/
├── openapi.json
├── README.md
└── LICENSE
```

## 环境要求

- Windows PowerShell，或等价的 shell 环境。
- Python `3.12`。
- `uv`。
- `Poetry`。
- Node.js `20` 或更高版本。
- npm。
- 可选：OpenSpec CLI，用于规格检查。

## 后端启动

进入后端目录：

```powershell
cd backend
```

首次初始化推荐使用 `uv + Poetry`：

```powershell
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv\Scripts\python.exe
poetry sync --with dev
```

如果只使用 uv 同步依赖：

```powershell
uv sync --locked
```

启动后端：

```powershell
poetry run flask --app wsgi:application run --debug --port 5000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

默认开发登录信息来自 `backend/app/config.py`：

```text
用户名：admin
密码：SensitiveStock-Internal-MVP
```

本地或部署时应通过进程环境变量覆盖默认值。PowerShell 示例：

```powershell
$env:BACKEND_AUTH_ADMIN_USERNAME="admin"
$env:BACKEND_AUTH_ADMIN_PASSWORD="change-me"
$env:BACKEND_AUTH_TOKEN_SECRET="local-dev-secret"
$env:BACKEND_DEEPSEEK_API_KEY=""
poetry run flask --app wsgi:application run --debug --port 5000
```

环境变量模板见 `backend/.env.example`。当前后端配置直接读取进程环境变量；如果使用 `.env` 文件，需要由你的启动器或进程管理工具负责加载。

## 前端启动

另开一个 PowerShell 窗口，进入前端目录：

```powershell
cd frontend
```

首次安装依赖：

```powershell
npm install
```

准备前端环境文件：

```powershell
copy .env.example .env.local
```

`.env.local` 默认指向本地后端：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

启动前端：

```powershell
npm run dev
```

浏览器访问：

```text
http://localhost:3000
```

如果使用默认后端配置，登录账号为 `admin`，密码为 `SensitiveStock-Internal-MVP`。如果你按上面的环境变量示例覆盖了密码，则使用覆盖后的密码。

## OpenAPI 使用

运行时文档：

```text
http://localhost:5000/api/v1/openapi.json
```

重新生成根目录静态契约：

```powershell
cd backend
uv run python scripts/generate_openapi.py
```

生成后应检查根目录 `openapi.json` 是否与代码预期一致。前端的 OpenAPI 路径绑定由 `frontend/lib/openapi-client.ts` 维护，相关测试在 `frontend/lib/openapi-client.test.ts`。

## 常用验证命令

后端测试和静态检查：

```powershell
cd backend
poetry run pytest tests -q
poetry run ruff check .
```

前端测试和构建：

```powershell
cd frontend
npm test
npm run build
```

前端冒烟测试：

```powershell
cd frontend
npm run test:smoke
```

OpenSpec 检查：

```powershell
openspec list --json
openspec validate --all --strict
```

当前本地检查结果显示：

```json
{"changes":[]}
```

也就是说，当前没有活动中的 OpenSpec change。

## 关键配置

后端主要环境变量：

- `BACKEND_ENV`：运行环境，默认 `development`。
- `BACKEND_API_PREFIX`：接口前缀，默认 `/api/v1`。
- `BACKEND_CORS_ORIGINS`：允许访问后端的前端来源，默认 `http://localhost:3000`。
- `BACKEND_AUTH_ADMIN_USERNAME`：管理员用户名。
- `BACKEND_AUTH_ADMIN_PASSWORD`：管理员密码。
- `BACKEND_AUTH_TOKEN_SECRET`：Token 签名密钥。
- `BACKEND_AUTH_TOKEN_TTL_SECONDS`：Token 有效期。
- `BACKEND_JIN10_FLASH_API_URL`：金十快讯接口。
- `BACKEND_EASTMONEY_NEWS_URL`：东方财富资讯接口。
- `BACKEND_SINA_FINANCE_NEWS_URL`：新浪财经直播接口。
- `BACKEND_DEEPSEEK_API_KEY`：DeepSeek 访问密钥。
- `BACKEND_DEEPSEEK_BASE_URL`：DeepSeek 接口地址，默认 `https://api.deepseek.com`。
- `BACKEND_DEEPSEEK_MODEL`：预测模型，默认 `deepseek-v4-flash`。
- `BACKEND_DEEPSEEK_THINKING_TYPE`：思考模式，默认 `enabled`。
- `BACKEND_DEEPSEEK_REASONING_EFFORT`：推理强度，默认 `high`。
- `BACKEND_PREDICTION_HISTORY_PATH`：预测历史 JSONL 文件路径；留空时使用后端 instance 目录。
- `BACKEND_PREDICTION_HISTORY_LIMIT`：预测历史保留数量。
- `TUSHARE_TOKEN`：可选市场数据备用配置。

前端主要环境变量：

- `NEXT_PUBLIC_API_BASE_URL`：浏览器侧可见的后端地址，默认 `http://localhost:5000`。

## 开发约束

- 新的 Python 运行代码只进入 `backend/`。
- 新的前端代码只进入 `frontend/`。
- 不要重新引入根目录 `app.py`、根目录 `pages/` 或旧 Streamlit 默认入口。
- 不要恢复根目录 `config.json` 作为运行时配置来源。
- 修改正式 API 后，需要同步更新后端 OpenAPI 生成逻辑、根目录 `openapi.json`、前端 OpenAPI 绑定和相关测试。
- 修改目录结构、启动方式、认证边界或能力状态后，需要同步更新 README、`backend/README.md`、`docs/architecture/directory-map.md` 和迁移文档。
- 回测相关功能当前以 AKQuant 为执行内核，旧兼容代码只负责请求适配、信号回放和结果整理，不应重新扩展为独立回测引擎。
- 所有预测、诊断、因子和组合结果都只作为研究辅助，不构成投资建议。

## 排障提示

- 后端 401：确认是否已登录，或请求是否带有 `Authorization: Bearer <token>`。
- 前端无法访问后端：确认后端运行在 `http://localhost:5000`，并检查 `frontend/.env.local` 的 `NEXT_PUBLIC_API_BASE_URL`。
- 行情、资讯为空或降级：先看接口返回里的 `degraded`、`warnings`、`sourceQuality` 和 `channels` 字段，通常是外部数据源不可用或网络超时。
- DeepSeek 预测降级：确认 `BACKEND_DEEPSEEK_API_KEY` 是否已设置；未设置时系统会返回本地启发式预测，并在元数据中标记 `degraded: true`。
- 前端依赖安装失败：优先检查 npm registry、lockfile 中的 resolved 地址和本机 DNS。
