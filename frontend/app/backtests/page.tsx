import { BacktestConsole } from "@/components/backtest-console";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function BacktestsPage() {
  await requireAuthenticatedPage("/backtests");

  return (
    <>
      <WorkbenchHero
        eyebrow="Backtest Workbench"
        title="AKQuant-backed 回测台"
        description="策略预设、参数说明、执行/成本/风控假设、结果 insight 和交易解释在同一个研究页面里闭环展示。"
        metrics={[
          { label: "Runtime", value: "AKQuant", note: "via backend adapter" },
          { label: "Mode", value: "close / next_open", note: "execution assumptions visible" },
        ]}
        meta={["Grouped inputs", "Assumption replay", "Structured report"]}
      />

      <BacktestConsole />
    </>
  );
}
