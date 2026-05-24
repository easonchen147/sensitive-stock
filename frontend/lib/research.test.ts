import { afterEach, describe, expect, it, vi } from "vitest";

import {
  analyzeFactors,
  optimizePortfolio,
  runDiagnosis,
  runScreener,
} from "./api";

function mockJsonResponse(payload: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("research API helpers", () => {
  it("posts screener requests through the backend proxy", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      mockJsonResponse({
        items: [],
        summary: {},
        appliedFilters: {},
        interpretedPrompt: "",
        exportRows: [],
        backtestHandoff: { endpoint: "/api/v1/backtests/run", payload: {} },
        metadata: { source: "stub", degraded: false },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await runScreener({
      universe: ["000001"],
      filters: { minChangePercent: 0 },
      sortBy: "score",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/backend/screener/run",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("posts diagnosis, factor, and portfolio requests to formal endpoints", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      mockJsonResponse({
        symbol: "000001",
        metadata: { source: "stub", degraded: false },
        sections: [],
        indicators: [],
        riskNotes: [],
        marketContext: {},
        rankedFactors: [],
        latestFactors: {},
        summary: {},
        window: {},
        allocations: [],
        statistics: {},
        objective: "equal_weight",
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await runDiagnosis({ symbol: "000001", startDate: "2025-01-01", endDate: "2025-01-31" });
    await analyzeFactors({ symbol: "000001", startDate: "2025-01-01", endDate: "2025-01-31" });
    await optimizePortfolio({
      symbols: ["000001", "600000"],
      startDate: "2025-01-01",
      endDate: "2025-01-31",
      objective: "equal_weight",
    });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/backend/diagnosis/run",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/backend/factors/analyze",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/api/backend/portfolio/optimize",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
