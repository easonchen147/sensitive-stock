# Sensitive Stock

这是一个面向 A 股研究与策略回测的前后端分离项目，当前默认运行形态已经收敛为：

- `frontend/`: Next.js 16 + React 19 的前端壳层与登录态代理
- `backend/`: Flask API、认证、市场数据服务，以及仍在复用的 Python 回测核心
- `openspec/`: 变更管理与规格文档

旧的 Streamlit 入口、页面目录和配套脚本已经从主代码路径中清理出去，不再是当前项目的一部分。

## 当前功能状态

- 已迁移并可运行：
  - 管理员 token 登录
  - 能力清单 API
  - 回测预设目录与回测执行 API
  - AkShare-first 市场概览、行情、板块、Jin10 资讯与 intelligence API
- 已保留但尚未对外开放完整能力：
  - 条件选股
  - AI 诊股
  - 因子分析
  - 组合优化

其中，回测核心与分析模块已收拢进 `backend/` 工作区，根目录不再承载 Python 运行代码。

## 仓库结构

```text
.
├── backend/
│   ├── app/                    # Flask app factory、API、schema、service
│   ├── backtesting/            # 当前仍被后端复用的回测核心
│   ├── tests/                  # 后端测试
│   ├── factor_analysis.py      # 保留中的分析模块，尚未暴露 API
│   ├── portfolio_optimizer.py  # 保留中的分析模块，尚未暴露 API
│   ├── pyproject.toml          # uv + Poetry 对齐后的项目配置
│   ├── poetry.lock             # Poetry 锁文件
│   ├── uv.lock                 # uv 锁文件
│   └── wsgi.py                 # Flask 启动入口
├── frontend/
│   ├── app/                    # Next.js App Router
│   ├── components/
│   ├── lib/
│   └── types/
├── docs/
├── openspec/
├── AGENTS.md
└── LICENSE
```

## OpenSpec 状态

当前 `openspec list --json` 显示只有一个活动变更：

- `add-admin-token-auth`
  - 状态：`in-progress`
  - 进度：`11/12`
  - 剩余任务：`4.4 仅在 review 与验证通过后 archive 该 change，并完成 git add / git commit`

也就是说，功能实现和验证基本完成，剩下的是归档与提交收尾，而不是新的功能缺口。

## 后端初始化

推荐在 `backend/` 目录使用 `uv + Poetry`：

```bash
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv\Scripts\python.exe
poetry sync --with dev
```

如果你偏好 uv 的同步链路，也可以：

```bash
cd backend
uv sync --locked
```

依赖声明统一来自 [`backend/pyproject.toml`](/c:/Users/Administrator/Desktop/sensitive-stock/backend/pyproject.toml)，当前同时维护：

- `poetry.lock`
- `uv.lock`

依赖变更后，建议同时刷新：

```bash
cd backend
poetry lock
uv lock
```

环境变量模板见 [`backend/.env.example`](/c:/Users/Administrator/Desktop/sensitive-stock/backend/.env.example)。

## 启动方式

后端：

```bash
cd backend
poetry run flask --app wsgi:application run --debug --port 5000
```

前端：

```bash
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

前端默认读取：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

## 验证命令

后端：

```bash
cd backend
poetry run pytest tests -q
poetry run ruff check .
```

前端：

```bash
cd frontend
npm test
npm run build
```

OpenSpec：

```bash
openspec list --json
openspec status --change add-admin-token-auth --json
```

## 开发约束

- 不要把新的业务逻辑重新堆回根目录。
- 不要重新引入 `Streamlit app.py + pages/` 作为默认入口。
- 新的后端能力优先进入 `backend/app/api` 和 `backend/app/services`。
- 仍在保留的 `backend/backtesting/`、`backend/factor_analysis.py`、`backend/portfolio_optimizer.py` 代表“尚未完全迁出的旧域逻辑”，不是继续往根目录扩散的理由。
- 本地敏感配置应使用环境变量或 `backend/.env`，不要再依赖旧的根目录 `config.json` 方案。
