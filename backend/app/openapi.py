from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from .schemas.auth import LoginRequest
from .schemas.backtests import BacktestRunRequest
from .schemas.market import (
    MarketNewsQuery,
    MarketQuotesQuery,
    MarketSectorsQuery,
    PredictionHistoryQuery,
)
from .schemas.research import (
    DiagnosisRequest,
    FactorAnalysisRequest,
    PortfolioOptimizationRequest,
    ScreenerExportRequest,
    ScreenerRunRequest,
)

DEFAULT_API_PREFIX = "/api/v1"
OPENAPI_VERSION = "3.1.0"


def _schema(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema(by_alias=True, ref_template="#/components/schemas/{model}")


def _json_response(schema_ref: str, description: str = "Successful response") -> dict[str, Any]:
    return {
        "description": description,
        "content": {
            "application/json": {
                "schema": {"$ref": schema_ref},
            },
        },
    }


def _error_response(description: str) -> dict[str, Any]:
    return _json_response("#/components/schemas/ErrorEnvelope", description)


def _query_parameters(model: type[BaseModel]) -> list[dict[str, Any]]:
    schema = _schema(model)
    required = set(schema.get("required", []))
    parameters: list[dict[str, Any]] = []
    for name, property_schema in schema.get("properties", {}).items():
        parameter = {
            "name": name,
            "in": "query",
            "required": name in required,
            "schema": property_schema,
        }
        if property_schema.get("type") == "array":
            parameter["style"] = "form"
            parameter["explode"] = False
        parameters.append(parameter)
    return parameters


def _operation(
    *,
    method: str,
    path: str,
    tag: str,
    operation_id: str,
    summary: str,
    response_schema: str,
    request_schema: str | None = None,
    parameters: list[dict[str, Any]] | None = None,
    public: bool = False,
) -> dict[str, Any]:
    responses: dict[str, Any] = {
        "200": _json_response(response_schema),
        "400": _error_response("Validation or request error"),
        "401": _error_response("Authentication error"),
        "500": _error_response("Unexpected backend error"),
    }

    operation: dict[str, Any] = {
        "tags": [tag],
        "operationId": operation_id,
        "summary": summary,
        "security": [] if public else [{"bearerAuth": []}],
        "responses": responses,
    }
    if parameters:
        operation["parameters"] = parameters
    if request_schema:
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": request_schema},
                },
            },
        }
    if method == "post" and response_schema.endswith("BacktestRunResponse"):
        operation["responses"] = {
            **responses,
            "200": _json_response(response_schema, "Backtest execution result"),
        }
    return operation


def build_openapi_document(
    *,
    api_prefix: str = DEFAULT_API_PREFIX,
    title: str = "Sensitive Stock Backend API",
    version: str = "0.1.0",
) -> dict[str, Any]:
    paths = _build_paths(api_prefix)
    return {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": title,
            "version": version,
            "description": (
                "Global OpenAPI contract for the Sensitive Stock Flask backend. "
                "All protected business operations use the shared bearerAuth scheme."
            ),
        },
        "servers": [{"url": api_prefix}],
        "security": [{"bearerAuth": []}],
        "paths": paths,
        "components": _build_components(),
        "tags": [
            {"name": "platform", "description": "Health, discovery, and capability inventory."},
            {"name": "auth", "description": "Token login and session APIs."},
            {"name": "market", "description": "AkShare market data and Jin10 intelligence APIs."},
            {"name": "backtests", "description": "AKQuant-backed backtest APIs."},
            {"name": "capabilities", "description": "Current research capability runtime status."},
        ],
    }


def _build_paths(api_prefix: str) -> dict[str, Any]:
    def full(path: str) -> str:
        return f"{api_prefix}{path}"

    run_id_parameter = {
        "name": "runId",
        "in": "path",
        "required": True,
        "schema": {"type": "string"},
    }

    return {
        full("/openapi.json"): {
            "get": _operation(
                method="get",
                path=full("/openapi.json"),
                tag="platform",
                operation_id="getOpenApiDocument",
                summary="Return the published OpenAPI document.",
                response_schema="#/components/schemas/OpenApiDocument",
                public=True,
            )
        },
        full("/health"): {
            "get": _operation(
                method="get",
                path=full("/health"),
                tag="platform",
                operation_id="getHealth",
                summary="Return backend service health metadata.",
                response_schema="#/components/schemas/HealthResponse",
                public=True,
            )
        },
        full("/auth/login"): {
            "post": _operation(
                method="post",
                path=full("/auth/login"),
                tag="auth",
                operation_id="login",
                summary="Issue a bearer token for valid administrator credentials.",
                request_schema="#/components/schemas/LoginRequest",
                response_schema="#/components/schemas/LoginResponse",
                public=True,
            )
        },
        full("/auth/session"): {
            "get": _operation(
                method="get",
                path=full("/auth/session"),
                tag="auth",
                operation_id="getSession",
                summary="Return the authenticated administrator session.",
                response_schema="#/components/schemas/SessionResponse",
            )
        },
        full("/capabilities"): {
            "get": _operation(
                method="get",
                path=full("/capabilities"),
                tag="capabilities",
                operation_id="listCapabilities",
                summary="List backend research capabilities and runtime status.",
                response_schema="#/components/schemas/CapabilityInventoryResponse",
            )
        },
        full("/market"): {
            "get": _operation(
                method="get",
                path=full("/market"),
                tag="market",
                operation_id="getMarketOverview",
                summary="Return market source metadata and available market routes.",
                response_schema="#/components/schemas/MarketOverviewResponse",
            )
        },
        full("/market/quotes"): {
            "get": _operation(
                method="get",
                path=full("/market/quotes"),
                tag="market",
                operation_id="getMarketQuotes",
                summary="Return latest quotes for one or more A-share symbols.",
                response_schema="#/components/schemas/MarketQuotesResponse",
                parameters=_query_parameters(MarketQuotesQuery),
            )
        },
        full("/market/sectors"): {
            "get": _operation(
                method="get",
                path=full("/market/sectors"),
                tag="market",
                operation_id="getMarketSectors",
                summary="Return hot concept or industry sectors.",
                response_schema="#/components/schemas/MarketSectorsResponse",
                parameters=_query_parameters(MarketSectorsQuery),
            )
        },
        full("/market/news"): {
            "get": _operation(
                method="get",
                path=full("/market/news"),
                tag="market",
                operation_id="getMarketNews",
                summary="Return latest Jin10 market news items.",
                response_schema="#/components/schemas/MarketNewsResponse",
                parameters=_query_parameters(MarketNewsQuery),
            )
        },
        full("/market/news/intelligence"): {
            "get": _operation(
                method="get",
                path=full("/market/news/intelligence"),
                tag="market",
                operation_id="getMarketNewsIntelligence",
                summary="Return derived market intelligence from Jin10 news and market data.",
                response_schema="#/components/schemas/MarketNewsIntelligenceResponse",
                parameters=_query_parameters(MarketNewsQuery),
            )
        },
        full("/market/news/predictions"): {
            "get": _operation(
                method="get",
                path=full("/market/news/predictions"),
                tag="market",
                operation_id="getMarketNewsPredictions",
                summary="Return multi-source market news predictions and backtest handoff.",
                response_schema="#/components/schemas/MarketNewsPredictionsResponse",
                parameters=_query_parameters(MarketNewsQuery),
            )
        },
        full("/market/news/prediction-history"): {
            "get": _operation(
                method="get",
                path=full("/market/news/prediction-history"),
                tag="market",
                operation_id="getMarketPredictionHistory",
                summary="Return recent stored market prediction runs.",
                response_schema="#/components/schemas/PredictionHistoryResponse",
                parameters=_query_parameters(PredictionHistoryQuery),
            )
        },
        full("/market/news/predictions/{runId}"): {
            "get": _operation(
                method="get",
                path=full("/market/news/predictions/{runId}"),
                tag="market",
                operation_id="getMarketPredictionDetail",
                summary="Return one stored market prediction run.",
                response_schema="#/components/schemas/PredictionDetailResponse",
                parameters=[run_id_parameter],
            )
        },
        full("/market/news/predictions/{runId}/evaluate"): {
            "get": _operation(
                method="get",
                path=full("/market/news/predictions/{runId}/evaluate"),
                tag="market",
                operation_id="evaluateMarketPredictionRun",
                summary="Evaluate one stored market prediction run against latest quotes.",
                response_schema="#/components/schemas/PredictionEvaluationResponse",
                parameters=[run_id_parameter],
            )
        },
        full("/backtests/presets"): {
            "get": _operation(
                method="get",
                path=full("/backtests/presets"),
                tag="backtests",
                operation_id="listBacktestPresets",
                summary="Return AKQuant-backed preset strategy metadata.",
                response_schema="#/components/schemas/BacktestPresetCatalogResponse",
            )
        },
        full("/backtests/run"): {
            "post": _operation(
                method="post",
                path=full("/backtests/run"),
                tag="backtests",
                operation_id="runBacktests",
                summary="Run an AKQuant-backed backtest.",
                request_schema="#/components/schemas/BacktestRunRequest",
                response_schema="#/components/schemas/BacktestRunResponse",
            )
        },
        full("/screener"): {
            "get": _operation(
                method="get",
                path=full("/screener"),
                tag="capabilities",
                operation_id="getScreenerOverview",
                summary="Return screener templates and capability metadata.",
                response_schema="#/components/schemas/ScreenerOverviewResponse",
            )
        },
        full("/screener/run"): {
            "post": _operation(
                method="post",
                path=full("/screener/run"),
                tag="capabilities",
                operation_id="runScreener",
                summary="Execute a structured or natural-language screening request.",
                request_schema="#/components/schemas/ScreenerRunRequest",
                response_schema="#/components/schemas/ScreenerRunResponse",
            )
        },
        full("/screener/export"): {
            "post": _operation(
                method="post",
                path=full("/screener/export"),
                tag="capabilities",
                operation_id="exportScreenerResults",
                summary="Return export-ready screener rows.",
                request_schema="#/components/schemas/ScreenerExportRequest",
                response_schema="#/components/schemas/ScreenerExportResponse",
            )
        },
        full("/diagnosis"): {
            "get": _operation(
                method="get",
                path=full("/diagnosis"),
                tag="capabilities",
                operation_id="getDiagnosisOverview",
                summary="Return diagnosis report metadata.",
                response_schema="#/components/schemas/DiagnosisOverviewResponse",
            )
        },
        full("/diagnosis/run"): {
            "post": _operation(
                method="post",
                path=full("/diagnosis/run"),
                tag="capabilities",
                operation_id="runDiagnosis",
                summary="Generate a structured stock diagnosis report.",
                request_schema="#/components/schemas/DiagnosisRequest",
                response_schema="#/components/schemas/DiagnosisRunResponse",
            )
        },
        full("/factors"): {
            "get": _operation(
                method="get",
                path=full("/factors"),
                tag="capabilities",
                operation_id="getFactorsOverview",
                summary="Return factor analysis metadata.",
                response_schema="#/components/schemas/FactorsOverviewResponse",
            )
        },
        full("/factors/analyze"): {
            "post": _operation(
                method="post",
                path=full("/factors/analyze"),
                tag="capabilities",
                operation_id="analyzeFactors",
                summary="Run factor analysis for a symbol and date range.",
                request_schema="#/components/schemas/FactorAnalysisRequest",
                response_schema="#/components/schemas/FactorAnalysisResponse",
            )
        },
        full("/portfolio"): {
            "get": _operation(
                method="get",
                path=full("/portfolio"),
                tag="capabilities",
                operation_id="getPortfolioOverview",
                summary="Return portfolio optimization metadata.",
                response_schema="#/components/schemas/PortfolioOverviewResponse",
            )
        },
        full("/portfolio/optimize"): {
            "post": _operation(
                method="post",
                path=full("/portfolio/optimize"),
                tag="capabilities",
                operation_id="optimizePortfolio",
                summary="Optimize a portfolio for the requested objective.",
                request_schema="#/components/schemas/PortfolioOptimizationRequest",
                response_schema="#/components/schemas/PortfolioOptimizationResponse",
            )
        },
    }


def _build_components() -> dict[str, Any]:
    schemas = {
        "LoginRequest": _schema(LoginRequest),
        "BacktestRunRequest": _schema(BacktestRunRequest),
        "ScreenerRunRequest": _schema(ScreenerRunRequest),
        "ScreenerExportRequest": _schema(ScreenerExportRequest),
        "DiagnosisRequest": _schema(DiagnosisRequest),
        "FactorAnalysisRequest": _schema(FactorAnalysisRequest),
        "PortfolioOptimizationRequest": _schema(PortfolioOptimizationRequest),
        "HealthResponse": {
            "type": "object",
            "required": ["service", "environment", "apiVersion", "status"],
            "properties": {
                "service": {"type": "string"},
                "environment": {"type": "string"},
                "apiVersion": {"type": "string"},
                "status": {"type": "string", "enum": ["ok"]},
            },
        },
        "LoginResponse": {
            "type": "object",
            "required": ["accessToken", "tokenType", "expiresIn", "user"],
            "properties": {
                "accessToken": {"type": "string"},
                "tokenType": {"type": "string", "enum": ["Bearer"]},
                "expiresIn": {"type": "integer"},
                "user": {"$ref": "#/components/schemas/UserPrincipal"},
            },
        },
        "SessionResponse": {
            "type": "object",
            "required": ["authenticated", "expiresIn", "user"],
            "properties": {
                "authenticated": {"type": "boolean"},
                "expiresIn": {"type": "integer"},
                "user": {"$ref": "#/components/schemas/UserPrincipal"},
            },
        },
        "UserPrincipal": {
            "type": "object",
            "required": ["username", "roles"],
            "properties": {
                "username": {"type": "string"},
                "roles": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "APIError": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"},
                "details": {},
            },
            "additionalProperties": False,
        },
        "ErrorEnvelope": {
            "type": "object",
            "required": ["error"],
            "properties": {
                "error": {"$ref": "#/components/schemas/APIError"},
            },
            "additionalProperties": False,
        },
        "Capability": {
            "type": "object",
            "required": ["name", "label", "status", "path", "summary"],
            "properties": {
                "name": {"type": "string"},
                "label": {"type": "string"},
                "status": {"type": "string", "enum": ["ready", "limited", "disabled"]},
                "path": {"type": "string"},
                "summary": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "CapabilityInventoryResponse": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/Capability"},
                }
            },
            "additionalProperties": False,
        },
        "CapabilityMetadata": {
            "type": "object",
            "required": ["source", "degraded"],
            "properties": {
                "source": {"type": "string"},
                "degraded": {"type": "boolean"},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "unavailableInputs": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "SourceMetadata": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "primarySource": {"type": "string"},
                "fallbackSources": {"type": "array", "items": {"type": "string"}},
                "degraded": {"type": "boolean"},
                "requestedLimit": {"type": "integer"},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "MarketOverviewResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/SourceMetadata"},
                {
                    "type": "object",
                    "required": ["primarySource", "fallbackSources", "routes"],
                    "properties": {
                        "routes": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        }
                    },
                },
            ]
        },
        "MarketQuotesResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/SourceMetadata"},
                {
                    "type": "object",
                    "required": ["source", "items"],
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MarketQuote"},
                        }
                    },
                },
            ]
        },
        "MarketQuote": {
            "type": "object",
            "required": ["symbol"],
            "properties": {
                "symbol": {"type": "string"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "changePercent": {"type": "number"},
            },
            "additionalProperties": True,
        },
        "MarketSectorsResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/SourceMetadata"},
                {
                    "type": "object",
                    "required": ["source", "sectorType", "items"],
                    "properties": {
                        "sectorType": {"type": "string", "enum": ["concept", "industry"]},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MarketSector"},
                        },
                    },
                },
            ]
        },
        "MarketSector": {
            "type": "object",
            "required": ["name", "type", "source"],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "changePercent": {"type": "number"},
                "source": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "MarketNewsResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/SourceMetadata"},
                {
                    "type": "object",
                    "required": ["source", "requestedLimit", "degraded", "items"],
                    "properties": {
                        "sourceQuality": {
                            "$ref": "#/components/schemas/MarketNewsSourceQuality"
                        },
                        "dedupeMetadata": {
                            "$ref": "#/components/schemas/MarketNewsDedupeMetadata"
                        },
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MarketNewsItem"},
                        }
                    },
                },
            ]
        },
        "MarketNewsSourceQuality": {
            "type": "object",
            "required": [
                "queriedChannels",
                "succeededChannels",
                "degradedChannels",
                "failedChannels",
                "totalItems",
                "uniqueItems",
                "duplicateItems",
                "sourceCoverage",
                "qualityScore",
                "coverageScore",
                "freshnessScore",
                "reliabilityScore",
                "duplicatePressure",
                "qualityNotes",
            ],
            "properties": {
                "queriedChannels": {"type": "integer"},
                "succeededChannels": {"type": "integer"},
                "degradedChannels": {"type": "integer"},
                "failedChannels": {"type": "integer"},
                "totalItems": {"type": "integer"},
                "uniqueItems": {"type": "integer"},
                "duplicateItems": {"type": "integer"},
                "sourceCoverage": {"type": "array", "items": {"type": "string"}},
                "qualityScore": {"type": "number"},
                "coverageScore": {"type": "number"},
                "freshnessScore": {"type": "number"},
                "reliabilityScore": {"type": "number"},
                "duplicatePressure": {"type": "number"},
                "qualityNotes": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
        "MarketNewsDedupeMetadata": {
            "type": "object",
            "required": ["strategy", "originalCount", "uniqueCount", "duplicateCount"],
            "properties": {
                "strategy": {"type": "string"},
                "originalCount": {"type": "integer"},
                "uniqueCount": {"type": "integer"},
                "duplicateCount": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "MarketNewsItem": {
            "type": "object",
            "required": ["id", "publishedAt", "title", "content"],
            "properties": {
                "id": {"type": "string"},
                "publishedAt": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "important": {"type": "boolean"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "MarketNewsChannel": {
            "type": "object",
            "required": ["name", "source", "status", "itemCount"],
            "properties": {
                "name": {"type": "string"},
                "source": {"type": "string"},
                "status": {"type": "string", "enum": ["ok", "degraded", "failed"]},
                "itemCount": {"type": "integer"},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "MarketNewsIntelligenceResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/MarketNewsResponse"},
                {
                    "type": "object",
                    "required": ["keywords", "sectorHints"],
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": True,
                            },
                        },
                        "sectorHints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": True,
                            },
                        },
                    },
                },
            ]
        },
        "MarketPredictionMetadata": {
            "type": "object",
            "required": [
                "provider",
                "model",
                "requestMode",
                "degraded",
                "cached",
                "schemaVersion",
                "cacheKey",
                "inputDigest",
                "thinkingType",
                "reasoningEffort",
                "newsItemCount",
                "keywordCount",
                "sectorHintCount",
                "symbolCount",
            ],
            "properties": {
                "provider": {"type": "string"},
                "model": {"type": "string"},
                "requestMode": {"type": "string", "enum": ["remote", "heuristic"]},
                "degraded": {"type": "boolean"},
                "cached": {"type": "boolean"},
                "schemaVersion": {"type": "string"},
                "cacheKey": {"type": "string"},
                "inputDigest": {"type": "string"},
                "thinkingType": {"type": "string", "enum": ["enabled", "disabled"]},
                "reasoningEffort": {"type": "string", "enum": ["high", "max"]},
                "newsItemCount": {"type": "integer"},
                "keywordCount": {"type": "integer"},
                "sectorHintCount": {"type": "integer"},
                "symbolCount": {"type": "integer"},
                "latencyMs": {"type": "integer"},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "MarketPrediction": {
            "type": "object",
            "required": [
                "targetType",
                "target",
                "direction",
                "confidence",
                "score",
                "horizon",
                "drivers",
                "sourceIds",
            ],
            "properties": {
                "predictionId": {"type": "string"},
                "targetType": {"type": "string"},
                "target": {"type": "string"},
                "direction": {"type": "string", "enum": ["bullish", "neutral", "bearish"]},
                "confidence": {"type": "number"},
                "score": {"type": "number"},
                "horizon": {"type": "string"},
                "drivers": {"type": "array", "items": {"type": "string"}},
                "sourceIds": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "BacktestHandoff": {
            "type": "object",
            "required": ["endpoint", "suggestedPreset", "symbols", "defaultParams"],
            "properties": {
                "endpoint": {"type": "string"},
                "suggestedPreset": {"type": "string"},
                "symbols": {"type": "array", "items": {"type": "string"}},
                "defaultParams": {"type": "object", "additionalProperties": True},
                "notes": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
        "MarketNewsPredictionsResponse": {
            "allOf": [
                {"$ref": "#/components/schemas/MarketNewsIntelligenceResponse"},
                {
                    "type": "object",
                    "required": [
                        "runId",
                        "createdAt",
                        "channels",
                        "predictionMetadata",
                        "predictions",
                        "riskNotes",
                        "backtestHandoff",
                    ],
                    "properties": {
                        "runId": {"type": "string"},
                        "createdAt": {"type": "string"},
                        "channels": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MarketNewsChannel"},
                        },
                        "sourceQuality": {
                            "$ref": "#/components/schemas/MarketNewsSourceQuality"
                        },
                        "dedupeMetadata": {
                            "$ref": "#/components/schemas/MarketNewsDedupeMetadata"
                        },
                        "predictionMetadata": {
                            "$ref": "#/components/schemas/MarketPredictionMetadata"
                        },
                        "predictions": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/MarketPrediction"},
                        },
                        "predictionSummary": {"type": "string"},
                        "riskNotes": {"type": "array", "items": {"type": "string"}},
                        "backtestHandoff": {"$ref": "#/components/schemas/BacktestHandoff"},
                    },
                },
            ]
        },
        "PredictionHistoryResponse": {
            "type": "object",
            "required": ["items", "metadata"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/PredictionHistoryRun"},
                },
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "PredictionHistoryRun": {
            "type": "object",
            "required": ["runId", "createdAt", "predictionCount", "degraded"],
            "properties": {
                "runId": {"type": "string"},
                "createdAt": {"type": "string"},
                "provider": {"type": "string"},
                "model": {"type": "string"},
                "thinkingType": {"type": "string"},
                "reasoningEffort": {"type": "string"},
                "degraded": {"type": "boolean"},
                "predictionCount": {"type": "integer"},
                "qualityScore": {"type": "number"},
                "summary": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "PredictionDetailResponse": {
            "type": "object",
            "required": ["runId", "createdAt", "predictions", "predictionMetadata"],
            "properties": {
                "runId": {"type": "string"},
                "createdAt": {"type": "string"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/MarketNewsItem"},
                },
                "sourceQuality": {"$ref": "#/components/schemas/MarketNewsSourceQuality"},
                "dedupeMetadata": {"$ref": "#/components/schemas/MarketNewsDedupeMetadata"},
                "predictionMetadata": {"$ref": "#/components/schemas/MarketPredictionMetadata"},
                "predictions": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/MarketPrediction"},
                },
                "riskNotes": {"type": "array", "items": {"type": "string"}},
                "backtestHandoff": {"$ref": "#/components/schemas/BacktestHandoff"},
            },
            "additionalProperties": True,
        },
        "PredictionEvaluationResponse": {
            "type": "object",
            "required": [
                "runId",
                "evaluatedAt",
                "evaluationSummary",
                "evaluationItems",
                "metadata",
            ],
            "properties": {
                "runId": {"type": "string"},
                "evaluatedAt": {"type": "string"},
                "evaluationSummary": {"$ref": "#/components/schemas/PredictionEvaluationSummary"},
                "evaluationItems": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/PredictionEvaluationItem"},
                },
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "PredictionEvaluationSummary": {
            "type": "object",
            "required": ["total", "assessable", "hit", "miss", "neutral", "pending"],
            "properties": {
                "total": {"type": "integer"},
                "assessable": {"type": "integer"},
                "hit": {"type": "integer"},
                "miss": {"type": "integer"},
                "neutral": {"type": "integer"},
                "pending": {"type": "integer"},
                "hitRate": {"type": ["number", "null"]},
            },
            "additionalProperties": True,
        },
        "PredictionEvaluationItem": {
            "type": "object",
            "required": ["predictionId", "target", "direction", "status", "note"],
            "properties": {
                "predictionId": {"type": "string"},
                "target": {"type": "string"},
                "direction": {"type": "string", "enum": ["bullish", "neutral", "bearish"]},
                "status": {"type": "string", "enum": ["hit", "miss", "neutral", "pending"]},
                "actualChangePercent": {"type": ["number", "null"]},
                "note": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "BacktestPresetCatalogResponse": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/BacktestPreset"},
                }
            },
            "additionalProperties": False,
        },
        "BacktestPreset": {
            "type": "object",
            "required": ["id", "label", "description", "defaultParams", "parameterSchema"],
            "properties": {
                "id": {"type": "string"},
                "label": {"type": "string"},
                "description": {"type": "string"},
                "summary": {"type": "string"},
                "useCase": {"type": "string"},
                "riskNotes": {"type": "string"},
                "defaultParams": {"type": "object", "additionalProperties": True},
                "parameterSchema": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "executionMetadata": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": True,
        },
        "BacktestRunResponse": {
            "type": "object",
            "required": ["results", "failures"],
            "properties": {
                "results": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/BacktestSymbolResult"},
                },
                "failures": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
            },
            "additionalProperties": False,
        },
        "BacktestSymbolResult": {
            "type": "object",
            "required": ["symbol", "settings", "metrics", "series", "tradeStats", "trades"],
            "properties": {
                "symbol": {"type": "string"},
                "settings": {"type": "object", "additionalProperties": True},
                "metrics": {"type": "object", "additionalProperties": True},
                "comparison": {"type": "object", "additionalProperties": True},
                "series": {"type": "object", "additionalProperties": True},
                "tradeStats": {"type": "object", "additionalProperties": True},
                "trades": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "warnings": {"type": "array", "items": {"type": "string"}},
                "assumptions": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "insights": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
            },
            "additionalProperties": True,
        },
        "ScreenerOverviewResponse": {
            "type": "object",
            "required": ["status", "templates", "metadata"],
            "properties": {
                "status": {"type": "string", "enum": ["ready", "limited", "disabled"]},
                "templates": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "ScreenerRunResponse": {
            "type": "object",
            "required": [
                "items",
                "summary",
                "appliedFilters",
                "exportRows",
                "backtestHandoff",
                "metadata",
            ],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/ScreenerCandidate"},
                },
                "summary": {"type": "object", "additionalProperties": True},
                "appliedFilters": {"type": "object", "additionalProperties": True},
                "interpretedPrompt": {"type": "string"},
                "exportRows": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "backtestHandoff": {"type": "object", "additionalProperties": True},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "ScreenerCandidate": {
            "type": "object",
            "required": ["symbol", "name", "price", "changePercent", "score"],
            "properties": {
                "symbol": {"type": "string"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "changePercent": {"type": "number"},
                "score": {"type": "number"},
                "matchedRules": {"type": "array", "items": {"type": "string"}},
                "factorSummary": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": True,
        },
        "ScreenerExportResponse": {
            "type": "object",
            "required": ["format", "columns", "rows", "metadata"],
            "properties": {
                "format": {"type": "string", "enum": ["json", "csv"]},
                "columns": {"type": "array", "items": {"type": "string"}},
                "rows": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
        },
        "DiagnosisOverviewResponse": {
            "type": "object",
            "required": ["status", "sections", "metadata"],
            "properties": {
                "status": {"type": "string", "enum": ["ready", "limited", "disabled"]},
                "sections": {"type": "array", "items": {"type": "string"}},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "DiagnosisRunResponse": {
            "type": "object",
            "required": [
                "symbol",
                "marketContext",
                "indicators",
                "sections",
                "riskNotes",
                "metadata",
            ],
            "properties": {
                "symbol": {"type": "string"},
                "name": {"type": "string"},
                "marketContext": {"type": "object", "additionalProperties": True},
                "indicators": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "sections": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "riskNotes": {"type": "array", "items": {"type": "string"}},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "FactorsOverviewResponse": {
            "type": "object",
            "required": ["status", "supportedFactors", "metadata"],
            "properties": {
                "status": {"type": "string", "enum": ["ready", "limited", "disabled"]},
                "supportedFactors": {"type": "array", "items": {"type": "string"}},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "FactorAnalysisResponse": {
            "type": "object",
            "required": [
                "symbol",
                "window",
                "latestFactors",
                "rankedFactors",
                "summary",
                "metadata",
            ],
            "properties": {
                "symbol": {"type": "string"},
                "window": {"type": "object", "additionalProperties": True},
                "latestFactors": {"type": "object", "additionalProperties": {"type": "number"}},
                "rankedFactors": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "summary": {"type": "object", "additionalProperties": True},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "PortfolioOverviewResponse": {
            "type": "object",
            "required": ["status", "objectives", "metadata"],
            "properties": {
                "status": {"type": "string", "enum": ["ready", "limited", "disabled"]},
                "objectives": {"type": "array", "items": {"type": "string"}},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "PortfolioOptimizationResponse": {
            "type": "object",
            "required": ["objective", "window", "allocations", "statistics", "metadata"],
            "properties": {
                "objective": {"type": "string"},
                "window": {"type": "object", "additionalProperties": True},
                "allocations": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "statistics": {"type": "object", "additionalProperties": {"type": "number"}},
                "metadata": {"$ref": "#/components/schemas/CapabilityMetadata"},
            },
            "additionalProperties": True,
        },
        "OpenApiDocument": {
            "type": "object",
            "required": ["openapi", "info", "paths", "components"],
            "additionalProperties": True,
        },
    }

    schemas = _promote_defs(schemas)
    return {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Bearer token returned by POST /api/v1/auth/login.",
            }
        },
        "schemas": schemas,
        "parameters": {
            "Limit": {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {"type": "integer", "minimum": 1, "maximum": 100},
            }
        },
    }


def _promote_defs(schemas: dict[str, Any]) -> dict[str, Any]:
    promoted = deepcopy(schemas)
    for schema in list(promoted.values()):
        defs = schema.pop("$defs", None)
        if isinstance(defs, dict):
            for name, definition in defs.items():
                promoted.setdefault(name, definition)
    return promoted
