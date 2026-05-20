# Sensitive Stock Backend

`backend/` 现在是一个可独立工作的 Flask 后端工作区，不再依赖 repo 根目录注入路径来导入核心模块。

## 目录说明

```text
backend/
├── app/
│   ├── api/         # HTTP 路由
│   ├── schemas/     # Pydantic 请求模型
│   └── services/    # 业务服务与 legacy 适配层
├── backtesting/     # 当前仍被 API 复用的回测核心
├── tests/
├── factor_analysis.py
├── portfolio_optimizer.py
├── pyproject.toml
├── poetry.lock
├── uv.lock
└── wsgi.py
```

## 包管理

当前后端采用 `uv + Poetry` 对齐管理：

- `pyproject.toml` 使用标准 `[project]` 依赖声明，便于 `uv` 读取
- `tool.poetry.package-mode = false`，说明这里只做依赖管理，不打包发布
- `poetry.lock` 和 `uv.lock` 都已生成，方便团队按偏好使用
- `poetry.toml` 将虚拟环境固定到 `backend/.venv`

## 初始化

```bash
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv\Scripts\python.exe
poetry sync --with dev
```

如果你走 uv 链路：

```bash
cd backend
uv sync --locked
```

## 常用命令

```bash
cd backend

# 查看 Poetry 当前绑定的解释器
poetry env info

# 刷新锁文件
poetry lock
uv lock

# 同步依赖
poetry sync --with dev
uv sync --locked

# 启动服务
poetry run flask --app wsgi:application run --debug --port 5000

# 测试与静态检查
poetry run pytest tests -q
poetry run ruff check .
```

## 环境变量

模板见 [`backend/.env.example`](/c:/Users/Administrator/Desktop/sensitive-stock/backend/.env.example)。

重点变量：

- `BACKEND_CORS_ORIGINS`
- `BACKEND_AUTH_ADMIN_USERNAME`
- `BACKEND_AUTH_ADMIN_PASSWORD`
- `BACKEND_AUTH_TOKEN_SECRET`
- `BACKEND_AUTH_TOKEN_TTL_SECONDS`
- `TUSHARE_TOKEN`

## API 边界

已落地：

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/session`
- `GET /api/v1/capabilities`
- `GET /api/v1/backtests/presets`
- `POST /api/v1/backtests/run`
- `GET /api/v1/market`
- `GET /api/v1/market/quotes`
- `GET /api/v1/market/sectors`
- `GET /api/v1/market/news`
- `GET /api/v1/market/news/intelligence`

保留 placeholder：

- `GET /api/v1/screener`
- `GET /api/v1/diagnosis`
- `GET /api/v1/factors`
- `GET /api/v1/portfolio`

除 `GET /api/v1/health` 与 `POST /api/v1/auth/login` 外，其余功能 API 默认要求 `Authorization: Bearer <token>`。
