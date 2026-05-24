import type { BacktestRunPayload, ExecutionMode, StrategyMode } from "@/types/api";
import { displayExecutionMode, displayRatioPercent } from "@/lib/display";

export type BacktestFormValues = {
  symbolsInput: string;
  startDate: string;
  endDate: string;
  benchmarkSymbol: string;
  strategyMode: StrategyMode;
  strategyPreset: string;
  strategyCode: string;
  initialCapital: number;
  executionMode: ExecutionMode;
  positionSize: number;
  lotSize: number;
  volumeLimitPct: number;
  tradingFee: number;
  stampTax: number;
  slippage: number;
  minCommission: number;
  transferFeeRate: number;
  adjust: "" | "qfq" | "hfq";
  stopLoss: number;
  takeProfit: number;
  maxDrawdown: number;
  maxDailyLoss: number;
  maxPositionSize: number;
  reduceOnlyAfterRisk: boolean;
  riskCooldownBars: number;
  params: Record<string, unknown>;
};

export type BacktestQuickProfileId =
  | "research_default"
  | "cost_aware"
  | "trend_following";

export type BacktestQuickProfile = {
  id: BacktestQuickProfileId;
  label: string;
  description: string;
  values: Pick<
    BacktestFormValues,
    | "executionMode"
    | "positionSize"
    | "lotSize"
    | "volumeLimitPct"
    | "tradingFee"
    | "stampTax"
    | "slippage"
    | "minCommission"
    | "transferFeeRate"
    | "stopLoss"
    | "takeProfit"
    | "maxDrawdown"
    | "maxDailyLoss"
    | "maxPositionSize"
    | "reduceOnlyAfterRisk"
    | "riskCooldownBars"
  >;
};

export type BacktestSummaryItem = {
  label: string;
  value: string;
};

export const BACKTEST_QUICK_PROFILES: BacktestQuickProfile[] = [
  {
    id: "research_default",
    label: "研究默认",
    description: "接近当前研究台默认设置，适合先快速看策略轮廓。",
    values: {
      executionMode: "close",
      positionSize: 1,
      lotSize: 100,
      volumeLimitPct: 0.25,
      tradingFee: 0.0005,
      stampTax: 0.001,
      slippage: 0,
      minCommission: 5,
      transferFeeRate: 0.00002,
      stopLoss: 0,
      takeProfit: 0,
      maxDrawdown: 0,
      maxDailyLoss: 0,
      maxPositionSize: 0,
      reduceOnlyAfterRisk: false,
      riskCooldownBars: 0,
    },
  },
  {
    id: "cost_aware",
    label: "保守成交",
    description: "更偏重成交摩擦和风险约束，适合先做现实性校验。",
    values: {
      executionMode: "next_open",
      positionSize: 0.75,
      lotSize: 100,
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
      maxPositionSize: 0,
      reduceOnlyAfterRisk: true,
      riskCooldownBars: 2,
    },
  },
  {
    id: "trend_following",
    label: "趋势放大",
    description: "偏向中强趋势研究，持仓更积极，容忍更大波动。",
    values: {
      executionMode: "next_open",
      positionSize: 0.95,
      lotSize: 100,
      volumeLimitPct: 0.25,
      tradingFee: 0.0005,
      stampTax: 0.001,
      slippage: 0.0005,
      minCommission: 5,
      transferFeeRate: 0.00002,
      stopLoss: 0.08,
      takeProfit: 0.24,
      maxDrawdown: 0.18,
      maxDailyLoss: 0,
      maxPositionSize: 0,
      reduceOnlyAfterRisk: false,
      riskCooldownBars: 0,
    },
  },
];

export function parseSymbolsInput(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 5);
}

export function validateBacktestForm(values: BacktestFormValues): string[] {
  const errors: string[] = [];
  if (!parseSymbolsInput(values.symbolsInput).length) {
    errors.push("请至少输入 1 个股票代码。");
  }

  if (values.startDate && values.endDate && values.endDate < values.startDate) {
    errors.push("结束日期不能早于开始日期。");
  }

  if (values.strategyMode === "preset" && !values.strategyPreset) {
    errors.push("预设模式下必须选择一个策略预设。");
  }

  if (values.strategyMode === "custom" && !values.strategyCode.trim()) {
    errors.push("自定义模式下必须提供策略代码。");
  }

  return errors;
}

export function applyQuickProfile(
  values: BacktestFormValues,
  profileId: BacktestQuickProfileId,
): BacktestFormValues {
  const profile = BACKTEST_QUICK_PROFILES.find((item) => item.id === profileId);
  if (!profile) {
    return values;
  }

  return {
    ...values,
    ...profile.values,
  };
}

export function buildBacktestPayload(values: BacktestFormValues): BacktestRunPayload {
  return {
    market: {
      symbols: parseSymbolsInput(values.symbolsInput),
      startDate: values.startDate,
      endDate: values.endDate,
      adjust: values.adjust,
      benchmarkSymbol: values.benchmarkSymbol || undefined,
    },
    strategy: {
      mode: values.strategyMode,
      presetId: values.strategyPreset || undefined,
      code: values.strategyCode,
      params: values.params,
    },
    execution: {
      mode: values.executionMode,
      positionSize: values.positionSize,
      lotSize: values.lotSize,
      volumeLimitPct: values.volumeLimitPct,
    },
    costs: {
      tradingFee: values.tradingFee,
      stampTax: values.stampTax,
      slippage: values.slippage,
      minCommission: values.minCommission,
      transferFeeRate: values.transferFeeRate,
    },
    risk: {
      stopLoss: values.stopLoss,
      takeProfit: values.takeProfit,
      maxDrawdown: values.maxDrawdown,
      maxDailyLoss: values.maxDailyLoss,
      maxPositionSize: values.maxPositionSize,
      reduceOnlyAfterRisk: values.reduceOnlyAfterRisk,
      riskCooldownBars: values.riskCooldownBars,
    },
    initialCapital: values.initialCapital,
  };
}

export function buildBacktestFormSummary(
  values: BacktestFormValues,
  strategyLabel?: string,
): BacktestSummaryItem[] {
  const symbols = parseSymbolsInput(values.symbolsInput);
  return [
    {
      label: "标的范围",
      value: `${symbols.length} 个标的 / 基准 ${values.benchmarkSymbol || "未设置"}`,
    },
    {
      label: "策略",
      value: `${strategyLabel || values.strategyPreset || "自定义策略"} / ${
        values.strategyMode === "preset" ? "预设模式" : "自定义模式"
      }`,
    },
    {
      label: "执行",
      value: `${displayExecutionMode(values.executionMode)} / 仓位 ${(
        values.positionSize * 100
      ).toFixed(0)}% / 成交量限制 ${toPercent(values.volumeLimitPct)}`,
    },
    {
      label: "成本与风控",
      value: `佣金 ${toPercent(values.tradingFee)} / 滑点 ${toPercent(values.slippage)} / 止损 ${
        values.stopLoss > 0 ? toPercent(values.stopLoss) : "关闭"
      } / 回撤阈值 ${values.maxDrawdown > 0 ? toPercent(values.maxDrawdown) : "关闭"}`,
    },
  ];
}

export function formatMetricValue(value: number | null | undefined): string {
  return displayRatioPercent(value);
}

export function formatDecimal(value: number | null | undefined, digits = 2): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "暂无";
  }
  return value.toFixed(digits);
}

function toPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}
