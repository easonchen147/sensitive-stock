import { PortfolioWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function PortfolioPage() {
  await requireAuthenticatedPage("/portfolio");

  return (
    <>
      <WorkbenchHero
        eyebrow="组合研究"
        title="组合优化工作台"
        description="以 OpenAPI 契约提交标的篮子、时间窗口和优化目标，返回权重、统计指标与元数据。"
        metrics={[
          { label: "接口", value: "/portfolio/optimize", note: "正式后端接口" },
          { label: "优化目标", value: "4", note: "等权、方差、夏普、风险平价" },
        ]}
        meta={["配置权重", "组合统计", "目标元数据"]}
      />
      <PortfolioWorkbench />
    </>
  );
}
