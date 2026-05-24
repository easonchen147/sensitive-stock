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
| 认证与访问保护 | 已可用 | 管理员登录、Bearer Token、后端鉴权、前端受保护页面、前端后端代理链路。 | 开发默认账号密码应只用于本地，部署前应修改各自工作区的 `.env` 配置。 |
| OpenAPI 契约 | 已可用 | 运行时 `GET /api/v1/openapi.json`，静态 `openapi.json`，生成脚本，前端接口绑定测试。 | 修改后端正式接口后需要重新生成并验证 `openapi.json`。 |
| 前端工作台 | 已可用 | 登录页、研究总览、回测验证、行情预测、选股研究、诊股报告、因子研究、组合研究。 | 页面只展示已有后端接口支撑的能力，不保留无接口支撑的占位入口。 |
| 行情数据 | 已增强，依赖外部数据源 | AkShare `1.18.63` 优先，TickFlow 历史行情备用，Tushare 可选，Sina 兜底；报价支持 AkShare、TickFlow API Key 备用和东方财富直连备用；行情总览会返回数据源顺序和诊断元数据。 | TickFlow 免费服务只支持历史日 K；实时报价备用需要 `TICKFLOW_API_KEY`。外部数据源失败时会进入降级或缓存路径。 |
| 多源资讯 | 已增强，依赖外部渠道 | 金十快讯、东方财富资讯、新浪财经直播、财联社电报、证券时报标题流、21世纪经济报道资本市场标题流，以及巨潮官方公告的深市/沪市/北交所披露流聚合，支持去重、质量评分、渠道状态、关键词提取和结构化事件提示。 | 第三方接口不可用时会展示降级元数据；标题级渠道当前不抓详情正文，官方公告当前不解析 PDF 正文。 |
| 资讯预测 | 已可用，远程模型可选 | DeepSeek `deepseek-v4-flash`、思考模式、推理强度、结构化事件上下文、预测历史、预测详情、行情评估；未传观察标的时可根据高优先级事件自动回填回测候选股票代码。 | 未配置 `BACKEND_DEEPSEEK_API_KEY` 时会明确降级到本地启发式预测。 |
| 回测验证 | 已增强 | AKQuant 回测执行链路、策略预设、自定义策略代码、成交模式、成交量限制、最低佣金、过户费、滑点、止损止盈、策略级风险控制、基准对比、数据质量、执行质量、风险诊断和引擎事件摘要。 | 历史行情仍依赖外部数据源；当前适配层负责信号回放和结果整理。 |
| 条件选股 | 已可用，第一版规则化能力 | 模板、结构化筛选条件、自然语言提示解释、候选排序、导出数据、回测交接载荷。 | 自然语言理解是轻量规则解释，不是完整大模型选股代理。 |
| 智能诊股 | 已可用，第一版规则化能力 | 股票报价上下文、日内动量、风险等级、诊断段落、风险提示。 | 当前以行情和规则摘要为主，不构成投资建议。 |
| 因子分析 | 已可用 | 因子计算、最新因子快照、IC 排名、窗口统计。 | 结果质量取决于可获取的历史行情和因子计算窗口。 |
| 组合优化 | 已可用 | 等权、最小方差、最大夏普、风险平价、目标权重、统计指标。 | 组合统计依赖历史行情，数据不足时会返回降级提示。 |
| 测试与规格 | 已建立 | 后端 pytest、ruff；前端 Vitest、构建、冒烟测试；OpenSpec 校验命令。 | 活动中的 OpenSpec change 以 `openspec list --json` 实时结果为准，不在文档中写死。 |

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

### 结构化事件提示

`GET /api/v1/market/news/intelligence` 和 `GET /api/v1/market/news/predictions` 会返回 `eventHints`。该字段由后端在已聚合的新闻和巨潮公告上做规则抽取，当前覆盖：

- 正向事件：股份回购、股东增持、股权激励、中标与订单、业绩预增与扭亏、分红派息。
- 负向事件：股东减持、监管问询、立案与处罚、退市与风险提示。
- 中性事件：股东大会与董事会、停复牌。

每条事件提示包含 `eventType`、`label`、`signal`、`score`、`count`、`relatedSymbols`、`relatedNames`、`sourceIds` 和 `matchedTitles`。预测接口会把 `eventHints` 纳入 DeepSeek 上下文；本地启发式预测会优先使用强事件信号。调用预测接口时如果不传 `symbols`，`backtestHandoff.symbols` 会尝试从高优先级事件涉及的股票代码自动补全。

## 仓库结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/          # Flask HTTP 路由
│   │   ├── schemas/      # Pydantic 请求和响应模型
│   │   └── services/     # 认证、行情、资讯、预测、回测和研究服务
│   ├── backtesting/      # 回测策略、AKQuant 信号适配和多源行情 provider
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

后端默认读取 `backend/.env`，不把进程环境变量作为业务配置的默认来源。首次准备本地配置：

```powershell
cd backend
copy .env.example .env
```

然后直接编辑 `backend/.env` 中的账号、密钥和数据源参数。环境模板见 `backend/.env.example`。

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
copy .env.example .env
```

`frontend/.env` 默认指向本地后端：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

启动前端：

```powershell
npm run dev
```

当前 `npm run dev` 固定使用 Next.js Webpack dev server。Next.js `16.2.1`
在 Windows 路径下的 Turbopack dev server 会偶发生成非法 RSC manifest，
表现为 `/login` 报 `global-error.js#default` 找不到；生产构建仍使用
`next build`。

浏览器访问：

```text
http://localhost:3000
```

如果使用默认后端配置，登录账号为 `admin`，密码为 `SensitiveStock-Internal-MVP`。如果你修改了 `backend/.env` 中的账号或密码，则以前端登录页填写修改后的值为准。

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

当前活动中的 OpenSpec change 请直接以命令输出为准，不要依赖文档里的静态示例。

## 关键配置

后端主要 `.env` 配置项：

- `BACKEND_ENV`：运行环境，默认 `development`。
- `BACKEND_API_PREFIX`：接口前缀，默认 `/api/v1`。
- `BACKEND_CORS_ORIGINS`：允许访问后端的前端来源，默认 `http://localhost:3000`。
- `BACKEND_AUTH_ADMIN_USERNAME`：管理员用户名。
- `BACKEND_AUTH_ADMIN_PASSWORD`：管理员密码。
- `BACKEND_AUTH_TOKEN_SECRET`：Token 签名密钥。
- `BACKEND_AUTH_TOKEN_TTL_SECONDS`：Token 有效期。
- `BACKEND_MARKET_DATA_ENABLE_TICKFLOW`：是否启用 TickFlow 历史行情 provider，默认 `true`。
- `BACKEND_MARKET_DATA_PREFER_TICKFLOW`：是否把 TickFlow 放到 AkShare 前面，默认 `false`。
- `BACKEND_TICKFLOW_TIMEOUT`：TickFlow 请求超时，默认跟随 `BACKEND_HTTP_TIMEOUT`。
- `TICKFLOW_API_KEY`：TickFlow 完整服务密钥；配置后可作为实时报价备用源。
- `TICKFLOW_BASE_URL`：TickFlow 完整服务地址，默认 `https://api.tickflow.org`。
- `TICKFLOW_FREE_BASE_URL`：TickFlow 免费服务地址，默认 `https://free-api.tickflow.org`。
- `BACKEND_JIN10_FLASH_API_URL`：金十快讯接口。
- `BACKEND_JIN10_FALLBACK_URL`：金十公开快讯回退地址。
- `BACKEND_EASTMONEY_NEWS_URL`：东方财富资讯接口。
- `BACKEND_SINA_FINANCE_NEWS_URL`：新浪财经直播接口。
- `BACKEND_CLS_TELEGRAPH_URL`：财联社电报页地址。
- `BACKEND_STCN_NEWS_URL`：证券时报首页地址。
- `BACKEND_21JINGJI_CAPITAL_NEWS_URL`：21世纪经济报道资本市场频道地址。
- `BACKEND_CNINFO_DISCLOSURE_URL`：巨潮官方公告接口地址。
- `BACKEND_CNINFO_DISCLOSURE_REFERER_URL`：巨潮公告页 Referer。
- `BACKEND_CNINFO_STATIC_BASE_URL`：巨潮 PDF 静态资源基地址。
- `BACKEND_DEEPSEEK_API_KEY`：DeepSeek 访问密钥。
- `BACKEND_DEEPSEEK_BASE_URL`：DeepSeek 接口地址，默认 `https://api.deepseek.com`。
- `BACKEND_DEEPSEEK_MODEL`：预测模型，默认 `deepseek-v4-flash`。
- `BACKEND_DEEPSEEK_THINKING_TYPE`：思考模式，默认 `enabled`。
- `BACKEND_DEEPSEEK_REASONING_EFFORT`：推理强度，默认 `high`。
- `BACKEND_PREDICTION_HISTORY_PATH`：预测历史 JSONL 文件路径；留空时使用后端 instance 目录。
- `BACKEND_PREDICTION_HISTORY_LIMIT`：预测历史保留数量。
- `TUSHARE_TOKEN`：可选历史行情备用配置。

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
- 行情历史数据默认顺序是 `akshare -> tickflow -> tushare -> sina_direct`；如果显式设置 `BACKEND_MARKET_DATA_PREFER_TICKFLOW=true`，顺序变为 `tickflow -> akshare -> tushare -> sina_direct`。
- TickFlow 免费服务可用于历史日 K，实时报价 fallback 只有配置 `TICKFLOW_API_KEY` 后才启用。
- 所有预测、诊断、因子和组合结果都只作为研究辅助，不构成投资建议。

## 排障提示

- 后端 401：确认是否已登录，或请求是否带有 `Authorization: Bearer <token>`。
- 前端无法访问后端：确认后端运行在 `http://localhost:5000`，并检查 `frontend/.env` 的 `NEXT_PUBLIC_API_BASE_URL`。
- 行情、资讯为空或降级：先看接口返回里的 `degraded`、`warnings`、`sourceQuality` 和 `channels` 字段，通常是外部数据源不可用或网络超时。
- DeepSeek 预测降级：确认 `BACKEND_DEEPSEEK_API_KEY` 是否已设置；未设置时系统会返回本地启发式预测，并在元数据中标记 `degraded: true`。
- 前端依赖安装失败：优先检查 npm registry、lockfile 中的 resolved 地址和本机 DNS。
