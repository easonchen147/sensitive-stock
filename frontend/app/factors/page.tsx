import { FactorWorkbench } from "@/components/research-workbenches";
import { WorkbenchHero } from "@/components/workbench-layout";
import { requireAuthenticatedPage } from "@/lib/server-auth";

export default async function FactorsPage() {
  await requireAuthenticatedPage("/factors");

  return (
    <>
      <WorkbenchHero
        eyebrow="因子研究"
        title="因子分析工作台"
        description="面向单标的窗口分析，展示最新因子快照、IC 排名、摘要统计和有效分析区间。"
        metrics={[
          { label: "接口", value: "/factors/analyze", note: "正式后端接口" },
          { label: "输出", value: "IC 排名", note: "高相关因子与元数据" },
        ]}
        meta={["最新因子", "IC 排名", "窗口元数据"]}
      />
      <FactorWorkbench />
    </>
  );
}
