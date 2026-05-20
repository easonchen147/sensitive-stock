from __future__ import annotations

CAPABILITIES = [
    {
        "name": "backtest",
        "label": "股票回测",
        "status": "migrated",
        "path": "/api/v1/backtests/run",
        "summary": "第一阶段已迁通回测主链路，可从前端调用 Flask API 执行旧回测引擎。",
    },
    {
        "name": "screener",
        "label": "条件选股",
        "status": "skeleton",
        "path": "/api/v1/screener",
        "summary": "保留后端入口和前端占位页，后续阶段迁移东方财富选股链路。",
    },
    {
        "name": "market",
        "label": "行情中心",
        "status": "migrated",
        "path": "/api/v1/market",
        "summary": (
            "已提供 backend 侧 AkShare 市场数据与 Jin10 新闻 intelligence API，"
            "前端深度页面仍待继续迁移。"
        ),
    },
    {
        "name": "diagnosis",
        "label": "AI 诊股",
        "status": "skeleton",
        "path": "/api/v1/diagnosis",
        "summary": "保留 AI 诊股入口，后续阶段迁移提示词拼装和行情抓取逻辑。",
    },
    {
        "name": "factors",
        "label": "因子分析",
        "status": "skeleton",
        "path": "/api/v1/factors",
        "summary": "已预留后端入口，并同步修正底层数据契约，后续阶段补齐完整 API。",
    },
    {
        "name": "portfolio",
        "label": "组合优化",
        "status": "skeleton",
        "path": "/api/v1/portfolio",
        "summary": "已预留后端入口，并同步修正底层数据契约，后续阶段补齐完整 API。",
    },
]


def list_capabilities() -> list[dict[str, str]]:
    return CAPABILITIES


def get_capability(name: str) -> dict[str, str] | None:
    for capability in CAPABILITIES:
        if capability["name"] == name:
            return capability
    return None
