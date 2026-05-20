# Directory Map

## 当前主工作区

```text
frontend/
├── app/             # Next.js 路由与页面
├── components/      # UI 组件
├── lib/             # API client、auth helper、server helper
└── types/           # 前端接口类型

backend/
├── app/
│   ├── api/         # Flask 蓝图
│   ├── schemas/     # 请求/响应模型
│   └── services/    # 服务层与 legacy 适配
├── backtesting/     # 被后端复用的回测核心
├── tests/
├── factor_analysis.py
├── portfolio_optimizer.py
└── wsgi.py
```

## 根目录职责

根目录现在只保留工作区级内容：

- `README.md`
- `AGENTS.md`
- `docs/`
- `openspec/`
- `frontend/`
- `backend/`
- `LICENSE`

旧的 Streamlit 入口、页面目录和联调脚本已经清理，不再是运行时的一部分。

## 依赖方向

```text
frontend
  -> frontend/app/api/backend/*
  -> backend/app/api/*
  -> backend/app/services/*
  -> backend/backtesting/*
```

## 备注

- `backend/backtesting/` 仍属于迁移过渡层，但已经被收口到后端工作区内部。
- `backend/factor_analysis.py` 和 `backend/portfolio_optimizer.py` 仍有测试覆盖，但当前仅作为保留模块存在，尚未开放 API。
- 新功能不要再向 repo 根目录添加 Python 运行文件。
