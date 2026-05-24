import { afterEach, describe, expect, it, vi } from "vitest";

import {
  evaluateMarketPredictionRun,
  getMarketNewsPredictions,
  getMarketPredictionDetail,
  getMarketPredictionHistory,
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

describe("market prediction API helpers", () => {
  it("passes DeepSeek mode overrides through the backend proxy", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      mockJsonResponse({
        source: "stub",
        requestedLimit: 20,
        degraded: false,
        items: [],
        keywords: [],
        sectorHints: [],
        predictionMetadata: {
          provider: "stub",
          model: "deepseek-v4-flash",
          requestMode: "remote",
          degraded: false,
          cached: false,
          schemaVersion: "market-news-prediction/v1",
          cacheKey: "cache",
          inputDigest: "digest",
          thinkingType: "disabled",
          reasoningEffort: "max",
          newsItemCount: 0,
          keywordCount: 0,
          sectorHintCount: 0,
          symbolCount: 1,
        },
        predictions: [],
        riskNotes: [],
        backtestHandoff: {
          endpoint: "/api/v1/backtests/run",
          suggestedPreset: "ma_cross",
          symbols: ["000001"],
          defaultParams: {},
        },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await getMarketNewsPredictions(20, ["000001"], {
      thinking: "disabled",
      reasoningEffort: "max",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/backend/market/news/predictions?limit=20&symbols=000001&thinking=disabled&reasoningEffort=max",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("loads prediction history, detail, and evaluation routes", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [],
          metadata: { source: "local_jsonl", degraded: false },
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          runId: "pred_abc",
          createdAt: "2026-05-23T00:00:00+00:00",
          source: "stub",
          requestedLimit: 10,
          degraded: false,
          items: [],
          keywords: [],
          sectorHints: [],
          predictionMetadata: {
            provider: "stub",
            model: "deepseek-v4-flash",
            requestMode: "remote",
            degraded: false,
            cached: false,
            schemaVersion: "market-news-prediction/v1",
            cacheKey: "cache",
            inputDigest: "digest",
            thinkingType: "enabled",
            reasoningEffort: "high",
            newsItemCount: 0,
            keywordCount: 0,
            sectorHintCount: 0,
            symbolCount: 0,
          },
          predictions: [],
          riskNotes: [],
          backtestHandoff: {
            endpoint: "/api/v1/backtests/run",
            suggestedPreset: "ma_cross",
            symbols: [],
            defaultParams: {},
          },
        }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          runId: "pred_abc",
          evaluatedAt: "2026-05-23T00:00:00+00:00",
          evaluationSummary: {
            total: 0,
            assessable: 0,
            hit: 0,
            miss: 0,
            neutral: 0,
            pending: 0,
            hitRate: null,
          },
          evaluationItems: [],
          metadata: { source: "latest_quotes", degraded: false },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await getMarketPredictionHistory(8);
    await getMarketPredictionDetail("pred_abc");
    await evaluateMarketPredictionRun("pred_abc");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/backend/market/news/prediction-history?limit=8",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/backend/market/news/predictions/pred_abc",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "/api/backend/market/news/predictions/pred_abc/evaluate",
      expect.objectContaining({ method: "GET" }),
    );
  });
});
