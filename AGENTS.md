# AGENTS.md

## 项目定位

这是一个面向 A 股研究、回测和市场情报的前后端分离项目。

当前默认架构已经明确：

- `frontend/` 是唯一前端入口
- `backend/` 是唯一 Python 运行工作区
- repo 根目录只保留工作区级文件、文档和 OpenSpec

不要再把它当成旧的 Streamlit 单体应用来维护。

## 当前事实速览

- 前端入口：`frontend/app`
- 后端入口：`backend/wsgi.py`
- Flask app factory：`backend/app/__init__.py`
- 回测核心：`backend/backtesting/*`
- 市场数据服务：`backend/app/services/market_data.py`
- Jin10 资讯与 intelligence：`backend/app/services/news_intelligence.py`
- 保留中的分析模块：
  - `backend/factor_analysis.py`
  - `backend/portfolio_optimizer.py`

## 目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── schemas/
│   │   └── services/
│   ├── backtesting/
│   ├── tests/
│   ├── factor_analysis.py
│   ├── portfolio_optimizer.py
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── uv.lock
│   └── wsgi.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── types/
├── docs/
├── openspec/
├── README.md
└── LICENSE
```

## 开发约定

### 1. 根目录不再承载运行时代码

不要新增：

- `app.py`
- `pages/`
- 根目录 Python 服务模块
- 旧式 `config.json` 配置链

新的 Python 代码应进入 `backend/`，新的前端代码应进入 `frontend/`。

### 2. 后端工作区要能独立运行

`backend/` 现在应满足：

- 在 `backend/` 目录下可直接运行测试
- 不依赖 repo 根目录 `sys.path` hack 导入业务模块
- 依赖与虚拟环境由 `uv + Poetry` 共同管理

如果新增模块导致必须重新把 repo 根目录塞进 `sys.path`，通常说明结构设计退化了。

### 3. 仍保留的 legacy 模块也只能留在 backend 内

当前仍保留的过渡代码：

- `backend/backtesting/`
- `backend/factor_analysis.py`
- `backend/portfolio_optimizer.py`

这代表“后端尚未完全内聚”，不代表可以把新的 legacy 继续放回根目录。

### 4. 前端默认通过受保护链路访问后端

认证相关主链路：

- 页面保护：`frontend/middleware.ts`
- 登录态 helper：`frontend/lib/auth.ts`
- 后端代理：`frontend/app/api/backend/[...slug]/route.ts`
- 登录接口：`frontend/app/api/auth/*`
- 后端认证：`backend/app/auth.py`、`backend/app/services/auth.py`

除健康检查和登录外，功能 API 默认要求 bearer token。

### 5. 包管理以 `backend/pyproject.toml` 为准

后端当前使用：

- `poetry.lock`
- `uv.lock`

依赖调整后，建议同步刷新：

```bash
cd backend
poetry lock
uv lock
```

初始化建议：

```bash
cd backend
uv python install 3.12
uv venv .venv --python 3.12
poetry env use .venv\Scripts\python.exe
poetry sync --with dev
```

### 6. 文档要跟代码对齐

如果修改了：

- 目录结构
- 启动方式
- API 路径
- 认证边界
- 占位能力与已迁移能力的状态

就要同步更新：

- `README.md`
- `backend/README.md`
- `docs/architecture/directory-map.md`
- `docs/migration/phase-one-architecture-migration.md`

### 7. OpenSpec 以实际状态为准

当前仓库使用 `openspec/` 管理变更。处理需求时先确认：

```bash
openspec list --json
openspec status --change <name> --json
```

如果只是做实现清理或结构收口，不要在文档里虚报为“新增功能已完成”。
