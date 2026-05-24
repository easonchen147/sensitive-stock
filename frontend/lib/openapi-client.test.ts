import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  buildOpenApiProxyPath,
  OPENAPI_ROUTE_BINDINGS,
  type OpenApiRouteKey,
} from "./openapi-client";

const currentDir = dirname(fileURLToPath(import.meta.url));
const openApi = JSON.parse(
  readFileSync(resolve(currentDir, "../../openapi.json"), "utf8"),
) as {
  paths: Record<string, Record<string, { security?: Array<Record<string, string[]>> }>>;
};

function getOperation(binding: { method: string; path: string }) {
  return openApi.paths[binding.path]?.[binding.method.toLowerCase()];
}

describe("OpenAPI governed frontend route bindings", () => {
  it("binds every frontend route key to an existing OpenAPI path and method", () => {
    Object.entries(OPENAPI_ROUTE_BINDINGS).forEach(([key, binding]) => {
      const pathItem = openApi.paths[binding.path];
      expect(pathItem, `${key} is missing from openapi.json`).toBeTruthy();
      expect(pathItem[binding.method.toLowerCase()], `${key} method mismatch`).toBeTruthy();
    });
  });

  it("covers every published OpenAPI operation with a frontend binding", () => {
    Object.entries(openApi.paths).forEach(([path, pathItem]) => {
      Object.keys(pathItem).forEach((method) => {
        const route = Object.values(OPENAPI_ROUTE_BINDINGS).find(
          (binding) =>
            binding.path === path && binding.method.toLowerCase() === method.toLowerCase(),
        );
        expect(route, `${method.toUpperCase()} ${path} has no frontend binding`).toBeTruthy();
      });
    });
  });

  it("keeps the major workbench endpoints covered by the binding table", () => {
    const requiredKeys: OpenApiRouteKey[] = [
      "capabilities",
      "backtestPresets",
      "backtestRun",
      "marketOverview",
      "marketQuotes",
      "marketSectors",
      "marketNews",
      "marketNewsIntelligence",
      "marketNewsPredictions",
      "marketPredictionHistory",
      "marketPredictionDetail",
      "marketPredictionEvaluation",
      "screenerRun",
      "screenerExport",
      "diagnosisRun",
      "factorsAnalyze",
      "portfolioOptimize",
    ];

    requiredKeys.forEach((key) => {
      expect(OPENAPI_ROUTE_BINDINGS[key]).toBeTruthy();
    });
  });

  it("builds frontend proxy paths from OpenAPI route keys", () => {
    expect(buildOpenApiProxyPath("marketNews", { limit: 10 })).toBe(
      "/api/backend/market/news?limit=10",
    );
    expect(buildOpenApiProxyPath("marketNewsPredictions", { limit: 20 })).toBe(
      "/api/backend/market/news/predictions?limit=20",
    );
    expect(
      buildOpenApiProxyPath("marketPredictionDetail", undefined, { runId: "pred_abc" }),
    ).toBe("/api/backend/market/news/predictions/pred_abc");
    expect(
      buildOpenApiProxyPath("marketPredictionEvaluation", undefined, {
        runId: "pred_abc",
      }),
    ).toBe("/api/backend/market/news/predictions/pred_abc/evaluate");
    expect(buildOpenApiProxyPath("portfolioOptimize")).toBe(
      "/api/backend/portfolio/optimize",
    );
  });

  it("marks only public OpenAPI operations as public", () => {
    const publicKeys = Object.entries(OPENAPI_ROUTE_BINDINGS)
      .filter(([, binding]) => binding.public)
      .map(([key]) => key)
      .sort();

    expect(publicKeys).toEqual(["authLogin", "health", "openapiJson"]);
  });

  it("aligns public/protected binding flags with OpenAPI security declarations", () => {
    Object.entries(OPENAPI_ROUTE_BINDINGS).forEach(([key, binding]) => {
      const operation = getOperation(binding);
      expect(operation, `${key} operation is missing`).toBeTruthy();
      if (binding.public) {
        expect(operation.security, `${key} should be public in openapi.json`).toEqual([]);
        return;
      }

      expect(operation.security, `${key} should require bearer auth`).toEqual([
        { bearerAuth: [] },
      ]);
    });
  });

  it("only treats protected OpenAPI operations as backend proxy eligible", async () => {
    const { isProtectedOpenApiPath } = await import("./openapi-client");

    expect(isProtectedOpenApiPath("/api/v1/market/news")).toBe(true);
    expect(isProtectedOpenApiPath("/api/v1/market/news/predictions/pred_abc")).toBe(true);
    expect(isProtectedOpenApiPath("/api/v1/openapi.json")).toBe(false);
    expect(isProtectedOpenApiPath("/api/v1/auth/login")).toBe(false);
    expect(isProtectedOpenApiPath("/api/v1/not-registered")).toBe(false);
  });
});
