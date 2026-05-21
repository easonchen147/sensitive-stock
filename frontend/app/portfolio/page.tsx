import { PortfolioWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function PortfolioPage() {
  await requireAuthenticatedPage("/portfolio");

  return (
    <>
      <WorkbenchHero
        eyebrow="Portfolio"
        title="组合优化工作台"
        description="以 OpenAPI 契约提交标的篮子、时间窗口和优化目标，返回权重、统计指标与元数据。"
        metrics={[
          { label: "Endpoint", value: "/portfolio/optimize", note: "formal API" },
          { label: "Objectives", value: "4", note: "equal, min-var, Sharpe, risk parity" },
        ]}
        meta={["Allocation weights", "Portfolio statistics", "Objective metadata"]}
      />
      <PortfolioWorkbench />
    </>
  );
}
