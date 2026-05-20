from __future__ import annotations

from app import create_app
from tests.auth_helpers import auth_test_config, issue_auth_headers


class StubBacktestService:
    def __init__(self) -> None:
        self.seen_request = None

    def run_batch(self, request):  # noqa: ANN001
        self.seen_request = request
        return {
            "results": [
                {
                    "symbol": "000001",
                    "settings": {
                        "benchmarkSymbol": "159919",
                        "executionMode": "next_open",
                        "positionSize": 0.9,
                    },
                    "metrics": {
                        "strategy_total_return": 0.12,
                        "annualized_return": 0.08,
                    },
                    "comparison": {
                        "benchmark_total_return": 0.04,
                        "excess_return": 0.08,
                    },
                    "series": {
                        "equity": [
                            {"date": "2025-01-02", "value": 101000.0},
                        ],
                        "drawdown": [
                            {"date": "2025-01-02", "value": -0.01},
                        ],
                    },
                    "tradeStats": {
                        "tradeCount": 1,
                        "winRate": 1.0,
                        "endingEquity": 112000.0,
                        "netProfit": 12000.0,
                        "exposureRate": 0.5,
                    },
                    "trades": [
                        {
                            "date": "2025-01-02",
                            "action": "Buy",
                            "reason": "signal_entry",
                            "price": 10.2,
                            "shares": 900,
                            "notional": 9180.0,
                            "fee": 4.59,
                            "tax": 0.0,
                        }
                    ],
                    "warnings": [],
                    "assumptions": [
                        {
                            "label": "执行模式",
                            "value": "next_open",
                            "detail": "信号变化后的下一交易日开盘成交。",
                        }
                    ],
                    "insights": [
                        {
                            "title": "相对基准",
                            "tone": "positive",
                            "detail": "策略跑赢基准 8.00%。",
                        }
                    ],
                }
            ],
            "failures": [],
        }

    def list_presets(self):
        return {
            "items": [
                {
                    "id": "ma_cross",
                    "label": "双均线策略",
                    "description": "AKQuant-inspired moving average crossover preset.",
                    "defaultParams": {"fast_window": 5, "slow_window": 20},
                    "parameterSchema": [
                        {
                            "name": "fast_window",
                            "label": "快线窗口",
                            "type": "number",
                            "default": 5,
                            "min": 2,
                            "max": 60,
                            "step": 1,
                        }
                    ],
                }
            ]
        }


CUSTOM_STRATEGY_CODE = (
    "def generate_signals(data, ctx):\n"
    "    return ctx.new_signal().fillna(0)\n"
)


def test_backtest_endpoint_validates_and_serializes_results() -> None:
    service = StubBacktestService()
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "BACKTEST_SERVICE_FACTORY": lambda: service,
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/backtests/run",
        json={
            "symbols": ["000001"],
            "startDate": "2025-01-01",
            "endDate": "2025-03-31",
            "strategyCode": CUSTOM_STRATEGY_CODE,
            "initialCapital": 100000,
            "tradingFee": 0.0005,
            "slippage": 0.0,
            "adjust": "qfq",
            "stopLoss": 0.0,
            "takeProfit": 0.0,
            "params": {"fast_window": 5},
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["results"][0]["symbol"] == "000001"
    assert payload["results"][0]["series"]["equity"][0]["value"] == 101000.0
    assert service.seen_request.symbols == ["000001"]
    assert service.seen_request.params == {"fast_window": 5}
    assert payload["results"][0]["assumptions"][0]["label"] == "执行模式"
    assert payload["results"][0]["insights"][0]["title"] == "相对基准"


def test_backtest_endpoint_accepts_structured_workbench_payload() -> None:
    service = StubBacktestService()
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "BACKTEST_SERVICE_FACTORY": lambda: service,
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/backtests/run",
        json={
            "market": {
                "symbols": ["000001"],
                "startDate": "2025-01-01",
                "endDate": "2025-03-31",
                "adjust": "qfq",
                "benchmarkSymbol": "159919",
            },
            "strategy": {
                "mode": "preset",
                "presetId": "ma_cross",
                "params": {
                    "fast_window": 5,
                    "slow_window": 20,
                },
            },
            "execution": {
                "mode": "next_open",
                "positionSize": 0.9,
                "lotSize": 100,
            },
            "costs": {
                "tradingFee": 0.0005,
                "stampTax": 0.001,
                "slippage": 0.0005,
            },
            "risk": {
                "stopLoss": 0.05,
                "takeProfit": 0.12,
            },
            "initialCapital": 100000,
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert service.seen_request.market.symbols == ["000001"]
    assert service.seen_request.market.benchmark_symbol == "159919"
    assert service.seen_request.strategy.mode == "preset"
    assert service.seen_request.strategy.preset_id == "ma_cross"
    assert service.seen_request.execution.mode == "next_open"
    assert service.seen_request.execution.position_size == 0.9
    assert service.seen_request.costs.stamp_tax == 0.001
    assert payload["results"][0]["comparison"]["excess_return"] == 0.08
    assert payload["results"][0]["trades"][0]["shares"] == 900


def test_backtest_presets_endpoint_returns_catalog() -> None:
    service = StubBacktestService()
    app = create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "BACKTEST_SERVICE_FACTORY": lambda: service,
        }
    )
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get("/api/v1/backtests/presets", headers=headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["items"][0]["id"] == "ma_cross"
    assert payload["items"][0]["parameterSchema"][0]["name"] == "fast_window"


def test_backtest_endpoint_rejects_invalid_payload() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/backtests/run",
        json={
            "symbols": [],
            "startDate": "2025-03-31",
            "endDate": "2025-01-01",
            "strategyCode": "",
        },
        headers=headers,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert "symbols" in payload["error"]["message"] or "startDate" in payload["error"]["message"]
