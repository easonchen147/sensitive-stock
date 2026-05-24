import { describe, expect, it } from "vitest";

import {
  applyQuickProfile,
  buildBacktestFormSummary,
  buildBacktestPayload,
  parseSymbolsInput,
  validateBacktestForm,
} from "./backtests";

const BASE_FORM = {
  symbolsInput: "000001,600000",
  startDate: "2025-01-01",
  endDate: "2025-03-31",
  benchmarkSymbol: "159919",
  strategyMode: "preset" as const,
  strategyPreset: "ma_cross",
  strategyCode: "def generate_signals(data, ctx):\n    return ctx.new_signal()\n",
  initialCapital: 100000,
  positionSize: 0.9,
  lotSize: 100,
  volumeLimitPct: 0.2,
  executionMode: "next_open" as const,
  tradingFee: 0.0005,
  stampTax: 0.001,
  slippage: 0,
  minCommission: 5,
  transferFeeRate: 0.00002,
  adjust: "qfq" as const,
  stopLoss: 0,
  takeProfit: 0,
  maxDrawdown: 0.1,
  maxDailyLoss: 800,
  maxPositionSize: 2000,
  reduceOnlyAfterRisk: true,
  riskCooldownBars: 2,
  params: {
    fast_window: 5,
    slow_window: 20,
  },
};

describe("parseSymbolsInput", () => {
  it("keeps up to five normalized symbols", () => {
    expect(parseSymbolsInput("000001, 600000, ,000002,300001, 688001, 002594"))
      .toEqual(["000001", "600000", "000002", "300001", "688001"]);
  });
});

describe("buildBacktestPayload", () => {
  it("transforms workbench form values into structured backend request payload", () => {
    expect(
      buildBacktestPayload({
        ...BASE_FORM,
      }),
    ).toEqual({
      market: {
        symbols: ["000001", "600000"],
        startDate: "2025-01-01",
        endDate: "2025-03-31",
        adjust: "qfq",
        benchmarkSymbol: "159919",
      },
      strategy: {
        mode: "preset",
        presetId: "ma_cross",
        code: "def generate_signals(data, ctx):\n    return ctx.new_signal()\n",
        params: {
          fast_window: 5,
          slow_window: 20,
        },
      },
      execution: {
        mode: "next_open",
        positionSize: 0.9,
        lotSize: 100,
        volumeLimitPct: 0.2,
      },
      costs: {
        tradingFee: 0.0005,
        stampTax: 0.001,
        slippage: 0,
        minCommission: 5,
        transferFeeRate: 0.00002,
      },
      risk: {
        stopLoss: 0,
        takeProfit: 0,
        maxDrawdown: 0.1,
        maxDailyLoss: 800,
        maxPositionSize: 2000,
        reduceOnlyAfterRisk: true,
        riskCooldownBars: 2,
      },
      initialCapital: 100000,
    });
  });
});

describe("validateBacktestForm", () => {
  it("rejects empty symbols and reversed dates", () => {
    expect(
      validateBacktestForm({
        ...BASE_FORM,
        symbolsInput: "",
        startDate: "2025-04-01",
        endDate: "2025-03-31",
      }),
    ).toEqual([
      "请至少输入 1 个股票代码。",
      "结束日期不能早于开始日期。",
    ]);
  });
});

describe("applyQuickProfile", () => {
  it("applies the cost-aware profile defaults", () => {
    expect(applyQuickProfile(BASE_FORM, "cost_aware")).toMatchObject({
      executionMode: "next_open",
      positionSize: 0.75,
      volumeLimitPct: 0.15,
      tradingFee: 0.0003,
      stampTax: 0.001,
      slippage: 0.0002,
      minCommission: 5,
      transferFeeRate: 0.00002,
      stopLoss: 0.05,
      takeProfit: 0.16,
      maxDrawdown: 0.12,
      maxDailyLoss: 800,
      reduceOnlyAfterRisk: true,
      riskCooldownBars: 2,
    });
  });
});

describe("buildBacktestFormSummary", () => {
  it("builds summary rows for the workbench sidebar", () => {
    expect(buildBacktestFormSummary(BASE_FORM, "双均线策略")).toEqual([
      { label: "标的范围", value: "2 个标的 / 基准 159919" },
      { label: "策略", value: "双均线策略 / 预设模式" },
      { label: "执行", value: "次日开盘成交 / 仓位 90% / 成交量限制 20.00%" },
      { label: "成本与风控", value: "佣金 0.05% / 滑点 0.00% / 止损 关闭 / 回撤阈值 10.00%" },
    ]);
  });
});
