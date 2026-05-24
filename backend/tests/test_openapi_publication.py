from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from app import create_app
from app.openapi import build_openapi_document
from tests.auth_helpers import auth_test_config

EXPECTED_FORMAL_PATHS = {
    "/api/v1/openapi.json",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/session",
    "/api/v1/capabilities",
    "/api/v1/market",
    "/api/v1/market/quotes",
    "/api/v1/market/sectors",
    "/api/v1/market/news",
    "/api/v1/market/news/intelligence",
    "/api/v1/market/news/predictions",
    "/api/v1/market/news/prediction-history",
    "/api/v1/market/news/predictions/{runId}",
    "/api/v1/market/news/predictions/{runId}/evaluate",
    "/api/v1/backtests/presets",
    "/api/v1/backtests/run",
    "/api/v1/screener",
    "/api/v1/screener/run",
    "/api/v1/screener/export",
    "/api/v1/diagnosis",
    "/api/v1/diagnosis/run",
    "/api/v1/factors",
    "/api/v1/factors/analyze",
    "/api/v1/portfolio",
    "/api/v1/portfolio/optimize",
}


def test_openapi_document_endpoint_is_public_and_covers_formal_routes() -> None:
    app = create_app({"TESTING": True, **auth_test_config()})
    client = app.test_client()

    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    document = response.get_json()
    assert document["openapi"] == "3.1.0"
    assert set(document["paths"]) == EXPECTED_FORMAL_PATHS
    assert (
        document["components"]["securitySchemes"]["bearerAuth"]["scheme"]
        == "bearer"
    )


def test_openapi_security_scheme_distinguishes_public_and_protected_operations() -> None:
    document = build_openapi_document()

    login_operation = document["paths"]["/api/v1/auth/login"]["post"]
    health_operation = document["paths"]["/api/v1/health"]["get"]
    openapi_operation = document["paths"]["/api/v1/openapi.json"]["get"]
    backtest_operation = document["paths"]["/api/v1/backtests/run"]["post"]
    screener_overview_operation = document["paths"]["/api/v1/screener"]["get"]

    assert login_operation["security"] == []
    assert health_operation["security"] == []
    assert openapi_operation["security"] == []
    assert backtest_operation["security"] == [{"bearerAuth": []}]
    assert screener_overview_operation["security"] == [{"bearerAuth": []}]


def test_openapi_components_publish_shared_error_and_backend_schemas() -> None:
    document = build_openapi_document()
    schemas = document["components"]["schemas"]

    assert schemas["ErrorEnvelope"]["properties"]["error"]["$ref"] == (
        "#/components/schemas/APIError"
    )
    assert "BacktestRunRequest" in schemas
    assert "BacktestMarketRequest" in schemas
    assert "ScreenerRunRequest" in schemas
    assert "DiagnosisRequest" in schemas
    assert "FactorAnalysisRequest" in schemas
    assert "PortfolioOptimizationRequest" in schemas
    assert "MarketQuotesResponse" in schemas
    assert "MarketNewsPredictionsResponse" in schemas
    assert "MarketPrediction" in schemas
    assert "MarketPredictionMetadata" in schemas
    assert "MarketNewsSourceQuality" in schemas
    assert "MarketNewsDedupeMetadata" in schemas
    assert "PredictionHistoryResponse" in schemas
    assert "PredictionDetailResponse" in schemas
    assert "PredictionEvaluationResponse" in schemas
    assert "BacktestHandoff" in schemas
    assert "ScreenerRunResponse" in schemas
    assert "DiagnosisRunResponse" in schemas
    assert schemas["Capability"]["properties"]["status"]["enum"] == [
        "ready",
        "limited",
        "disabled",
    ]

    backtest_request = schemas["BacktestRunRequest"]
    assert set(backtest_request["required"]) == {"market", "strategy"}
    backtest_execution = schemas["BacktestExecutionRequest"]
    assert "volumeLimitPct" in backtest_execution["properties"]
    backtest_costs = schemas["BacktestCostRequest"]
    assert "minCommission" in backtest_costs["properties"]
    assert "transferFeeRate" in backtest_costs["properties"]
    backtest_risk = schemas["BacktestRiskRequest"]
    assert "maxDrawdown" in backtest_risk["properties"]
    assert "reduceOnlyAfterRisk" in backtest_risk["properties"]
    backtest_result = schemas["BacktestSymbolResult"]
    assert "dataQuality" in backtest_result["required"]
    assert "executionQuality" in backtest_result["required"]
    assert "riskDiagnostics" in backtest_result["required"]
    assert "engineEvents" in backtest_result["required"]
    assert (
        document["paths"]["/api/v1/backtests/run"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/BacktestRunRequest"
    )

    prediction_metadata = schemas["MarketPredictionMetadata"]
    assert "schemaVersion" in prediction_metadata["required"]
    assert "cached" in prediction_metadata["required"]
    assert "inputDigest" in prediction_metadata["required"]
    assert "thinkingType" in prediction_metadata["required"]
    assert "reasoningEffort" in prediction_metadata["required"]
    assert "requestMode" in prediction_metadata["required"]
    assert "qualityScore" in schemas["MarketNewsSourceQuality"]["required"]
    assert "predictionId" in schemas["MarketPrediction"]["properties"]
    assert (
        schemas["MarketNewsPredictionsResponse"]["allOf"][1]["properties"]["sourceQuality"][
            "$ref"
        ]
        == "#/components/schemas/MarketNewsSourceQuality"
    )


def test_static_openapi_generation_command_writes_valid_json(tmp_path: Path) -> None:
    backend_root = Path(__file__).resolve().parents[1]
    output_path = tmp_path / "openapi.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_openapi.py",
            "--output",
            str(output_path),
        ],
        cwd=backend_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert str(output_path) in result.stdout
    document = json.loads(output_path.read_text(encoding="utf-8"))
    assert document["openapi"] == "3.1.0"
    assert set(document["paths"]) == EXPECTED_FORMAL_PATHS
