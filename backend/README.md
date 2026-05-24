# Sensitive Stock Backend

`backend/` 是当前项目唯一的 Python 运行工作区，承载 Flask API、认证、行情数据、多源资讯聚合、结构化事件提示、DeepSeek 预测、AKQuant 回测、诊股、因子和组合服务。

根目录不再承载 Python 运行时代码。新的后端模块应进入 `backend/app/`、`backend/backtesting/` 或明确的后端服务目录。

## 运行环境

- Python `3.12`
- `uv`
- `Poetry`
- Windows PowerShell 或等价 shell

## 初始化

```powershell
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv\Scripts\python.exe
poetry sync --with dev
```

如果只用 `uv` 同步：

```powershell
cd backend
uv sync --locked
```

## 启动

```powershell
cd backend
poetry run flask --app wsgi:application run --debug --port 5000
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/v1/health
```

运行时 OpenAPI：

```text
http://127.0.0.1:5000/api/v1/openapi.json
```

## 依赖

核心数据和回测依赖：

- `akshare==1.18.63`
- `akquant==0.2.37`
- `tickflow==0.1.21`
- `pandas==2.2.3`
- `numpy==2.2.6`

依赖调整后同步刷新锁文件：

```powershell
cd backend
poetry lock
uv lock
```

## 关键配置

认证：

- `BACKEND_AUTH_ADMIN_USERNAME`
- `BACKEND_AUTH_ADMIN_PASSWORD`
- `BACKEND_AUTH_TOKEN_SECRET`
- `BACKEND_AUTH_TOKEN_TTL_SECONDS`

行情：

- `BACKEND_MARKET_DATA_ENABLE_TICKFLOW`：是否启用 TickFlow 历史行情 provider，默认 `true`。
- `BACKEND_MARKET_DATA_PREFER_TICKFLOW`：是否把 TickFlow 提到 AkShare 前面，默认 `false`。
- `BACKEND_TICKFLOW_TIMEOUT`：TickFlow 请求超时。
- `TICKFLOW_API_KEY`：TickFlow 完整服务密钥；配置后可启用 TickFlow 实时报价备用路径。
- `TICKFLOW_BASE_URL`：TickFlow 完整服务地址。
- `TICKFLOW_FREE_BASE_URL`：TickFlow 免费服务地址。
- `TUSHARE_TOKEN`：Tushare 历史行情备用 token。

资讯和预测：

- `BACKEND_JIN10_FLASH_API_URL`
- `BACKEND_JIN10_FALLBACK_URL`
- `BACKEND_EASTMONEY_NEWS_URL`
- `BACKEND_SINA_FINANCE_NEWS_URL`
- `BACKEND_CLS_TELEGRAPH_URL`
- `BACKEND_STCN_NEWS_URL`
- `BACKEND_21JINGJI_CAPITAL_NEWS_URL`
- `BACKEND_CNINFO_DISCLOSURE_URL`
- `BACKEND_CNINFO_DISCLOSURE_REFERER_URL`
- `BACKEND_CNINFO_STATIC_BASE_URL`
- `BACKEND_DEEPSEEK_API_KEY`
- `BACKEND_DEEPSEEK_MODEL`
- `BACKEND_DEEPSEEK_THINKING_TYPE`
- `BACKEND_DEEPSEEK_REASONING_EFFORT`

当前默认新闻聚合会接入：

```text
金十快讯 -> 东方财富 -> 新浪财经直播 -> 财联社电报 -> 证券时报 -> 21世纪经济报道资本市场 -> 巨潮公告-深市 -> 巨潮公告-沪市 -> 巨潮公告-北交所
```

其中财联社使用页面内嵌 `__NEXT_DATA__`，证券时报和 21 财经当前使用标题级页面聚合，不抓详情页正文；巨潮公告使用官方结构化接口，不解析 PDF 正文。完整模板见 `.env.example`。

新闻情报会在聚合资讯和巨潮公告上生成 `eventHints`，与 `keywords`、`sectorHints` 并列返回。当前事件规则覆盖股份回购、股东增持、股权激励、中标与订单、业绩预增、分红派息、股东减持、监管问询、立案处罚、退市风险、股东大会、董事会和停复牌等公告/资讯信号。

预测接口会把 `eventHints` 传入 DeepSeek 上下文；未配置 DeepSeek 密钥时，本地启发式预测会优先使用高分事件信号，再结合板块提示和关键词补足预测。调用 `/api/v1/market/news/predictions` 时如果没有传 `symbols`，后端会从高优先级事件的 `relatedSymbols` 自动补全 `backtestHandoff.symbols`，方便把事件驱动预测直接交给回测接口验证。

## 行情数据顺序

默认历史行情 provider 顺序：

```text
akshare -> tickflow -> tushare -> sina_direct
```

显式设置 TickFlow 优先后：

```powershell
$env:BACKEND_MARKET_DATA_PREFER_TICKFLOW="true"
```

历史行情 provider 顺序变为：

```text
tickflow -> akshare -> tushare -> sina_direct
```

注意：

- TickFlow 免费服务支持历史日 K 和标的信息，不提供实时报价。
- TickFlow 实时报价 fallback 需要 `TICKFLOW_API_KEY`。
- API 响应会返回 `primarySource`、`fallbackSources`、`sourceOrder`、`lastSuccessSource`、`providerErrors` 和 `skippedProviders` 等诊断字段。

## 回测能力

回测执行由 AKQuant runtime 完成，当前后端适配层负责：

- 结构化请求校验。
- 兼容旧 flat payload。
- 策略预设和自定义策略信号回放。
- A 股整手、T+1、成交模式、费用和滑点参数传递。
- 成交量限制、最低佣金、过户费和策略级风险控制参数传递。
- 结构化输出 `metrics`、`comparison`、`series`、`tradeStats`、`trades`、`assumptions`、`insights`。
- 诊断输出 `dataQuality`、`executionQuality`、`riskDiagnostics`、`engineEvents`。

高级请求字段：

- `execution.volumeLimitPct`
- `costs.minCommission`
- `costs.transferFeeRate`
- `risk.maxDrawdown`
- `risk.maxDailyLoss`
- `risk.maxPositionSize`
- `risk.reduceOnlyAfterRisk`
- `risk.riskCooldownBars`

## OpenAPI

重新生成根目录静态契约：

```powershell
cd backend
uv run python scripts/generate_openapi.py
```

修改正式 API 后，需要同步：

- `backend/app/openapi.py`
- `openapi.json`
- `frontend/types/api.ts`
- 前端 OpenAPI client 或业务 payload builder
- 相关测试

## 验证

```powershell
cd backend
poetry run pytest tests -q
poetry run ruff check .
poetry check
```

如果只验证本轮行情和回测增强：

```powershell
cd backend
poetry run pytest tests/test_data_provider_priority.py tests/test_market_data_resilience.py tests/test_market_api.py -q
poetry run pytest tests/test_backtests_api.py tests/test_backtest_engine_upgrade.py tests/test_backtest_reporting_contract.py tests/test_openapi_publication.py -q
```

## 目录

```text
backend/
├── app/
│   ├── api/          # Flask routes
│   ├── schemas/      # Pydantic request schemas
│   └── services/     # auth, market data, news, prediction, backtests, research services
├── backtesting/      # market-data providers, presets, strategy execution helpers
├── scripts/          # OpenAPI generation
├── tests/            # backend test suite
├── factor_analysis.py
├── portfolio_optimizer.py
├── pyproject.toml
├── poetry.lock
├── uv.lock
└── wsgi.py
```
