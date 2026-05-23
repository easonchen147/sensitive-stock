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
        description="提交标的篮子、时间窗口和优化目标，返回目标权重、统计指标与风险信息。"
        metrics={[
          { label: "执行链路", value: "组合优化", note: "受保护服务" },
          { label: "优化目标", value: "4", note: "等权、方差、夏普、风险平价" },
        ]}
        meta={["配置权重", "组合统计", "目标元数据"]}
      />
      <PortfolioWorkbench />
    </>
  );
}
