import { FactorWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function FactorsPage() {
  await requireAuthenticatedPage("/factors");

  return (
    <>
      <WorkbenchHero
        eyebrow="Factors"
        title="因子分析工作台"
        description="面向单标的窗口分析，展示最新因子快照、IC 排名、摘要统计和有效分析区间。"
        metrics={[
          { label: "Endpoint", value: "/factors/analyze", note: "formal API" },
          { label: "Output", value: "IC ranking", note: "top factors and metadata" },
        ]}
        meta={["Latest factors", "Ranked IC", "Window metadata"]}
      />
      <FactorWorkbench />
    </>
  );
}
