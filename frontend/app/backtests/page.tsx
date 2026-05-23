import { BacktestConsole } from "@/components/backtest-console";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function BacktestsPage() {
  await requireAuthenticatedPage("/backtests");

  return (
    <>
      <WorkbenchHero
        eyebrow="回测验证"
        title="量化回测台"
        description="策略预设、参数说明、执行、成本、风控假设、结果洞察和交易解释在同一个研究页面里闭环展示。"
        metrics={[
          { label: "运行引擎", value: "量化回测引擎", note: "通过受保护服务执行" },
          { label: "成交模式", value: "2", note: "执行假设全程可见" },
        ]}
        meta={["分组输入", "假设回放", "结构化报告"]}
      />

      <BacktestConsole />
    </>
  );
}
