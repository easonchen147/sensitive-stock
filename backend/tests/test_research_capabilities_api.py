from __future__ import annotations

from app import create_app
from tests.auth_helpers import auth_test_config, issue_auth_headers


class StubScreenerService:
    def list_templates(self) -> dict:
        return {
            "status": "migrated",
            "templates": [{"id": "momentum"}],
            "metadata": {"source": "stub", "degraded": False},
        }

    def run(self, request):  # noqa: ANN001
        return {
            "items": [
                {
                    "symbol": request.universe[0],
                    "name": "Ping An",
                    "price": 12.3,
                    "changePercent": 2.1,
                    "score": 4.2,
                    "matchedRules": ["changePercent >= 0"],
                    "factorSummary": {"momentum": 2.1},
                }
            ],
            "summary": {"matchCount": 1},
            "appliedFilters": {"minChangePercent": 0},
            "interpretedPrompt": request.prompt or "",
            "exportRows": [{"symbol": request.universe[0], "score": 4.2}],
            "backtestHandoff": {
                "endpoint": "/api/v1/backtests/run",
                "payload": {"market": {"symbols": [request.universe[0]]}},
            },
            "metadata": {"source": "stub", "degraded": False, "warnings": []},
        }

    def export(self, request):  # noqa: ANN001
        return {
            "format": request.format,
            "columns": ["symbol", "score"],
            "rows": [{"symbol": request.universe[0], "score": 4.2}],
            "metadata": {"source": "stub", "degraded": False},
        }


class StubDiagnosisService:
    def describe(self) -> dict:
        return {
            "status": "migrated",
            "sections": ["market_context"],
            "metadata": {"source": "stub", "degraded": False},
        }

    def run(self, request):  # noqa: ANN001
        return {
            "symbol": request.symbol,
            "name": "Ping An",
            "marketContext": {"price": 12.3, "changePercent": 2.1, "source": "stub"},
            "indicators": [{"name": "intraday_momentum", "value": 2.1, "tone": "positive"}],
            "sections": [{"title": "Market context", "tone": "positive", "summary": "ok"}],
            "riskNotes": ["Research only."],
            "metadata": {"source": "stub", "degraded": False, "warnings": []},
        }


class StubFactorService:
    def describe(self) -> dict:
        return {
            "status": "migrated",
            "supportedFactors": ["momentum_5"],
            "metadata": {"source": "stub", "degraded": False},
        }

    def analyze(self, request):  # noqa: ANN001
        return {
            "symbol": request.symbol,
            "window": {
                "startDate": str(request.start_date),
                "endDate": str(request.end_date),
                "observations": 30,
                "forwardDays": request.forward_days,
            },
            "latestFactors": {"momentum_5": 0.12},
            "rankedFactors": [{"name": "momentum_5", "ic": 0.3, "absIc": 0.3}],
            "summary": {"factorCount": 1, "topFactor": "momentum_5"},
            "metadata": {"source": "stub", "degraded": False, "warnings": []},
        }


class StubPortfolioService:
    def describe(self) -> dict:
        return {
            "status": "migrated",
            "objectives": ["equal_weight"],
            "metadata": {"source": "stub", "degraded": False},
        }

    def optimize(self, request):  # noqa: ANN001
        weight = 1 / len(request.symbols)
        return {
            "objective": request.objective,
            "window": {
                "startDate": str(request.start_date),
                "endDate": str(request.end_date),
                "riskFreeRate": request.risk_free_rate,
            },
            "allocations": [{"symbol": symbol, "weight": weight} for symbol in request.symbols],
            "statistics": {"sharpeRatio": 1.2},
            "metadata": {"source": "stub", "degraded": False, "warnings": []},
        }


def _app_with_stubs():
    return create_app(
        {
            "TESTING": True,
            **auth_test_config(),
            "SCREENER_SERVICE_FACTORY": StubScreenerService,
            "DIAGNOSIS_SERVICE_FACTORY": StubDiagnosisService,
            "FACTOR_ANALYSIS_SERVICE_FACTORY": StubFactorService,
            "PORTFOLIO_OPTIMIZATION_SERVICE_FACTORY": StubPortfolioService,
        }
    )


def test_research_capabilities_are_marked_migrated() -> None:
    app = _app_with_stubs()
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.get("/api/v1/capabilities", headers=headers)

    assert response.status_code == 200
    items = {item["name"]: item for item in response.get_json()["items"]}
    for name in ("screener", "diagnosis", "factors", "portfolio"):
        assert items[name]["status"] == "migrated"


def test_screener_api_runs_and_exports_backtest_handoff() -> None:
    app = _app_with_stubs()
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/screener/run",
        json={
            "universe": ["000001"],
            "prompt": "strong momentum",
            "filters": {"minChangePercent": 0},
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["items"][0]["symbol"] == "000001"
    assert payload["backtestHandoff"]["endpoint"] == "/api/v1/backtests/run"

    export_response = client.post(
        "/api/v1/screener/export",
        json={"universe": ["000001"], "format": "json"},
        headers=headers,
    )
    assert export_response.status_code == 200
    assert export_response.get_json()["rows"][0]["symbol"] == "000001"


def test_diagnosis_api_returns_structured_report() -> None:
    app = _app_with_stubs()
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/diagnosis/run",
        json={
            "symbol": "000001",
            "startDate": "2025-01-01",
            "endDate": "2025-01-31",
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["symbol"] == "000001"
    assert payload["sections"][0]["title"] == "Market context"
    assert payload["metadata"]["degraded"] is False


def test_factor_api_returns_ranked_factor_results() -> None:
    app = _app_with_stubs()
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/factors/analyze",
        json={
            "symbol": "000001",
            "startDate": "2025-01-01",
            "endDate": "2025-01-31",
            "forwardDays": 5,
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["rankedFactors"][0]["name"] == "momentum_5"
    assert payload["summary"]["topFactor"] == "momentum_5"


def test_portfolio_api_returns_allocations() -> None:
    app = _app_with_stubs()
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/portfolio/optimize",
        json={
            "symbols": ["000001", "600000"],
            "startDate": "2025-01-01",
            "endDate": "2025-01-31",
            "objective": "equal_weight",
        },
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["objective"] == "equal_weight"
    assert payload["allocations"][0]["weight"] == 0.5


def test_research_capability_validation_errors_are_structured() -> None:
    app = _app_with_stubs()
    client = app.test_client()
    headers = issue_auth_headers(client)

    response = client.post(
        "/api/v1/portfolio/optimize",
        json={
            "symbols": ["000001"],
            "startDate": "2025-02-01",
            "endDate": "2025-01-01",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "validation_error"
